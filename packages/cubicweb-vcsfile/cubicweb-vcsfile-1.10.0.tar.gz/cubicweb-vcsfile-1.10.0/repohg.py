"""repository abstraction for a mercurial repository

:organization: Logilab
:copyright: 2007-2011 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""

from __future__ import with_statement

__docformat__ = "restructuredtext en"

import urllib2
from os import umask, makedirs
from os.path import split, exists, join, dirname
from datetime import datetime

from mercurial import hg, ui, revlog, context, util, commands as hgcmd
from mercurial.node import nullid, short as short_hex

from logilab.common import tempattr

from cubicweb import Binary, QueryError, ValidationError, ExecutionError
from cubicweb.server.ssplanner import EditedEntity

from cubes.vcsfile import repo, bridge
from cubes.vcsfile.entities import remove_authinfo

_DELETED = object()

def monkeypatch_mercurial_url():
    from mercurial.url import httphandler
    if hasattr(httphandler, '__del__'):
        del httphandler.__del__
monkeypatch_mercurial_url()

def spop(aset, item):
    try:
        aset.remove(item)
    except KeyError:
        pass

class vcsfile_ui(ui.ui):
    """ redirect output to cubicweb log """
    def __init__(self, loggable):
        ui.ui.__init__(self)
        self.cw_loggable = loggable

    def copy(self):
        return self

    def interactive(self):
        return False

    # XXX beware encoding issues wrt localized outputs ...
    def write(self, *args, **kwargs):
        if self._buffers:
            self._buffers[-1].extend([str(a) for a in args])
        else:
            for a in args:
                self.cw_loggable.debug(str(a).strip())

    def write_err(self, *args, **kwargs):
        for a in args:
            self.cw_loggable.error(str(a).strip())


def bw_nb_revisions(changelog):
    """return the number of revisions in a repository's changelog,
    assuring mercurial < 1.1 compatibility
    """
    try:
        return len(changelog)
    except AttributeError: # hg < 1.1
        return changelog.count()


class HGRepository(repo.VCSRepository):
    type = 'hg'

    def pull_or_clone_cache(self, url):
        if not exists(self.path):
            pdir = dirname(self.path)
            if not exists(pdir):
                makedirs(pdir)
            self.info('cloning %s into %s', url, self.path)
            try:
                hgcmd.clone(vcsfile_ui(self), str(url),
                            dest=self.path, stream='compressed', noupdate=True)
            except (util.Abort, urllib2.URLError), ex:
                raise bridge.VCSException(self.eid, 'url', str(ex))
        else:
            self.debug('pulling from %s into %s', remove_authinfo(url), self.path)
            vui = vcsfile_ui(self)
            try:
                hgcmd.pull(vui, hg.repository(vui, self.path), source=str(url))
            except (util.Abort, urllib2.URLError), ex:
                raise bridge.VCSException(self.eid, 'path', str(ex))

    def import_content(self, repoentity, commitevery=10):
        """import content from the mercurial repository"""
        assert self.eid == repoentity.eid
        if not exists(self.path):
            self.info('repository %s not accessible in %s',
                      repoentity.dc_title(), self.path)
            return
        try:
            repo = self.hgrepo()
        except Exception, ex:
            self.exception('Impossible to open repository %s (%s)', self, ex)
            return

        session = repoentity._cw
        knownheads = [(str(r.changeset), r.revision) for r in repoentity.heads_rset().entities()]

        # detect stripped branches
        needsstrip = False
        needsrenumbering = False
        for cset, rev in knownheads:
            if cset not in repo:
                needsstrip = True
                self.warning('%s: strip detected. %s is unknown in local cache',
                             self.path, cset)
        if not needsstrip:
            incoming = repo.revs("not ::%ls", [cset for cset, _rev in knownheads])
            if incoming:
                needsrenumbering = session.execute('Any R WHERE R is Revision, R from_repository REPO, '
                                                   'REPO eid %%(reid)s, R revision IN (%s)'
                                                   % ','.join([str(rev) for rev in incoming]),
                                                   {'reid': repoentity.eid})
            if not needsrenumbering:
                for cset, rev in knownheads:
                    if repo[str(cset)].rev() != rev:
                        needsrenumbering = True
                        break

        if needsstrip or needsrenumbering:
            self.warning('%s: strip and renumbering from %s.',
                         repoentity.dc_title(), self.path)
            # clean all 'revision' attribute to please unicity
            # constraint when renumbering
            session.execute('SET R revision NULL WHERE R from_repository REPO, '
                            'REPO eid %(reid)s', {'reid': repoentity.eid})
            revs = session.execute('Any R WHERE R is Revision, R from_repository REPO, '
                                   'REPO eid %(reid)s', {'reid': repoentity.eid})
            for reventity in revs.entities():
                if str(reventity.changeset) not in repo:
                    reventity.cw_delete()
                else:
                    rev = repo[str(reventity.changeset)].rev()
                    reventity.set_attributes(revision=rev)

            session.commit()
            session.set_cnxset()
            session.execute(
                'DELETE VersionedFile X WHERE X from_repository R, R eid %(r)s, '
                'NOT VC content_for X', {'r': repoentity.eid})
            # commit and give a chance to threads waiting for a cnxset
            # by freeing it then reacquiring it
            session.commit()
            session.set_cnxset()

        for rev in repo.revs("not ::%ls", [cset for cset, _rev in knownheads]):
            try:
                self.import_revision(repoentity, repo, rev)
            except Exception:
                self.critical('error while importing revision %s of %s',
                              rev, self.path, exc_info=True)
                raise
            if not rev % commitevery:
                # give a chance to threads waiting for a cnxset by
                # freeing it then reacquiring it
                session.commit()
                session.set_cnxset()
        session.commit()
        session.set_cnxset()

    def import_revision(self, repoentity, repo, i):
        self.info('importing revision %s', i)
        session = repoentity._cw
        execute = session.execute
        node = repo.changelog.node(i)
        changeset = unicode(short_hex(node))
        if execute('Any X WHERE X from_repository R, R eid %(repo)s, X changeset %(cs)s',
                   {'repo': repoentity.eid, 'cs': changeset}):
            self.warning('skip revision %s, seems already imported',
                         changeset)
            return
        ctx = repo.changectx(i)
        date = datetime.fromtimestamp(ctx.date()[0])
        #taglist = ctx.tags() #repo.nodetags(node)
        revdata = {'date': date, 'revision': i,
                   'author': unicode(ctx.user(), self.encoding, 'replace'),
                   'description': unicode(ctx.description(), self.encoding, 'replace'),
                   'changeset': changeset,
                   'branch': unicode(ctx.branch()),
                   }
        parent_changesets = [short_hex(n) for n in repo.changelog.parents(node)
                   if n != nullid]
        if not parent_changesets:
            parents = []
        elif len(parent_changesets) == 1:
            parents = execute(
                'Any X,XC,XR WHERE X revision XR, X changeset XC, '
                'X changeset %(cs)s, X from_repository R, R eid %(r)s',
                {'cs': parent_changesets[0], 'r': self.eid})
        else:
            parents = execute(
                'Any X,XC,XR WHERE X revision XR, X changeset XC, '
                'X changeset IN (%s), X from_repository R, R eid %%(r)s'
                % ','.join("'%s'"%cs for cs in parent_changesets),
                {'r': self.eid})
        revdata['parents'] = [r[0] for r in parents]
        reveid = bridge.import_revision(session, self.eid, **revdata)
        if not repoentity.import_revision_content:
            return
        changes = repo.status(ctx.parents()[0].node(), ctx.node())[:3]
        modified, added, removed = changes
        path_filter = repoentity.subpath
        for path in modified + added:
            upath = unicode(path, self.encoding, 'replace')
            if not (path_filter is None or upath.startswith(path_filter)):
                continue
            self._import_version_content(session, changeset, reveid, removed,
                                         path, upath, date, repo, ctx)
        for path in removed:
            upath = unicode(path, self.encoding, 'replace')
            if not (path_filter is None or upath.startswith(path_filter)):
                continue
            bridge.import_deleted_version_content(session, self.eid, reveid,
                                                  upath, date)
        parent_idx = dict( ((cs, lrev) for _, cs, lrev in parents) )
        parent_lrevs = [parent_idx[cs] for cs in parent_changesets]
        bridge.set_at_revision(session, reveid, parent_lrevs)

    def _import_version_content(self, session, changeset, reveid, removed, path, upath,
                                date, repo, ctx):
        directory, fname = split(path)
        session.transaction_data['vcs_importing'] = self.eid, directory, fname, changeset
        filectx = ctx[path]
        vcdata = {'data': Binary(filectx.data())}
        renameinfo = filectx.renamed()
        if renameinfo:
            pvc, oldfile = self._renamed_vc_rset(session, repo, renameinfo)
            if pvc:
                assert len(pvc) == 1
                if oldfile in removed:
                    vcdata['vc_rename'] = pvc[0][0]
                else:
                    vcdata['vc_copy'] = pvc[0][0]
            else:
                self.error('detected copy or rename of %s@%s but unable'
                           ' to find associated version content',
                           oldfile, pvc.args['cs'])
        return bridge.import_version_content(session, self.eid, reveid, upath,
                                             date, **vcdata)

    def _renamed_vc_rset(self, session, repo, renameinfo):
        oldfile, fileid = renameinfo
        pfctx = repo.filectx(oldfile, fileid=fileid)
        pcs = short_hex(pfctx.node())
        dir, name = split(unicode(oldfile, self.encoding, 'replace'))
        return session.execute('VersionContent X WHERE '
                               'X from_revision REV, REV changeset %(cs)s, '
                               'REV from_repository R, R eid %(r)s, '
                               'X content_for VF, VF directory %(dir)s, VF name %(name)s',
                               {'cs':  pcs, 'r': self.eid,
                                'dir': dir, 'name': name}), oldfile

    def hgrepo(self):
        return hg.repository(ui.ui(), self.path)

    def _file_content(self, path, rev):
        """extract a binary string with the content of the file at `path` for
        revision `rev` in the repository
        """
        ctx = self.hgrepo().changectx(rev)
        return Binary(ctx[path].data())

    def revision_transaction(self, session, entity):
        """open a transaction to create a new revision corresponding to the
        given entity
        """
        return HGTransaction(self, session, entity)

    def add_versioned_file_content(self, session, transaction, vf, entity,
                                   data):
        """add a new revision of a versioned file"""
        vfpath = self.encode(vf.path)
        transaction.changes[vfpath] = context.memfilectx(
            vfpath, data.getvalue(), islink=False, isexec=False, copied=None)
        return vf.path

    def add_versioned_file_deleted_content(self, session, transaction, vf,
                                           entity):
        """add a new revision of a just deleted versioned file"""
        transaction.changes[self.encode(vf.path)] = _DELETED
        return vf.path


class HGTransaction(object):
    def __init__(self, repohdlr, session, revision):
        self.repohdlr = repohdlr
        self.session = session
        self.revision = revision
        self.repo = repohdlr.hgrepo()
        # see http://mercurial.selenic.com/wiki/LockingDesign
        self._lock = self.repo.lock()
        self.extra = {}
        self.changes = {}

    @property
    def rev(self):
        """newly created revision number"""
        return bw_nb_revisions(self.repo.changelog)

    def _filectx(self, repo, memctx, path):
        """callable receiving the repository, the current memctx object and the
        normalized path of requested file, relative to repository root. It is
        fired by the commit function for every file in 'files', but calls order
        is undefined. If the file is available in the revision being committed
        (updated or added), filectxfn returns a memfilectx object. If the file
        was removed, filectxfn raises an IOError. Moved files are represented by
        marking the source file removed and the new file added with copy
        information (see memfilectx).
        """
        if self.changes[path] is _DELETED:
            raise IOError()
        return self.changes[path]

    def precommit(self):
        if not self.changes:
            raise QueryError('nothing changed')
        # XXX to what commit does here + strip in revert_precommit
        branch = self.repohdlr.encode(
            self.revision.cw_attr_cache.get('branch') or u'default')
        if branch != u'default':
            self.extra['branch'] = branch
        try:
            self.hgparent = p1 = self.repo.branchtags()[branch]
        except KeyError:
            # new branch
            self.hgparent = p1 = self.repo.branchtags().get('default')
        if p1:
            if not self.revision.parent_revision:
                raise ValidationError(self.revision.eid, {'parent_revision': 'missing expected parent'})
            if [short_hex(p1)] != [r.changeset for r in self.revision.parent_revision]:
                raise ValidationError(None, {None: 'concurrency error, please re-upload the revision'})

    def commit(self):
        # XXX: make umask configurable
        oldumask = umask(022)
        try:
            self._commit()
        finally:
            umask(oldumask)

    def _commit(self):
        # XXX merging branches
        repohdlr = self.repohdlr
        revision = self.revision
        author = repohdlr.encode(revision.cw_attr_cache.get('author', u''))
        msg = repohdlr.encode(revision.cw_attr_cache.get('description', u''))
        # ensure mercurial will use configured repo encoding, not locale's
        # encoding
        # XXX modifying module's global is not very nice but I've no other idea
        try:
            # mercurial >= 1.3.1
            from mercurial import encoding
            encoding.encoding = repohdlr.encoding
        except ImportError:
            util._encoding = repohdlr.encoding
        ctx = context.memctx(self.repo, (self.hgparent, None), msg,
                             self.changes.keys(), self._filectx, author,
                             extra=self.extra)
        try:
            # mercurial < 1.3.1
            node = self.repo._commitctx(ctx, force=True, force_editor=False,
                                        empty_ok=True, use_dirstate=False,
                                        update_dirstate=False)
        except AttributeError:
            node = self.repo.commitctx(ctx)
        # update revision's record to set correct changeset
        #
        # take care, self.repo != self.session.repo (eg mercurial repo instance
        # / rql repository)
        source = self.session.repo.system_source
        # remove previous cached value to only save the changeset
        with tempattr(revision, 'cw_edited', EditedEntity(revision)) as rev:
            rev.cw_edited['changeset'] = unicode(short_hex(node))
            source.update_entity(self.session, rev)
        # we need to explicitly commit the connection to the database since this
        # method is actually called from a postcommit event, i.e. once cnxset has
        # already been commited
        self.session.cnxset.connection('system').commit()
        # XXX restore entity's dict?
        self.rollback()

    def rollback(self):
        try:
            from mercurial.lock import release
            release(self._lock)
        except ImportError:
            try:
                # mercurial >= 1.3.1
                self._lock.release()
            except AttributeError:
                del self._lock


from logging import getLogger
from cubicweb import set_log_methods
set_log_methods(HGRepository, getLogger('cubicweb.sources.hg'))
