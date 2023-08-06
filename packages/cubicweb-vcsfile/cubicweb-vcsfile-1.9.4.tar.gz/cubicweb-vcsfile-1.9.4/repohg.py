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
        # `actualrev` is the *number* of revision, `latestrev` the highest
        # revision number while hg revisions start at 0 , hence the - 1
        actualrev = bw_nb_revisions(repo.changelog) - 1
        session = repoentity._cw
        latestrev = repoentity.latest_known_revision()
        if actualrev < latestrev:
            # striped repo
            # very minimal support, this won't work if local number of
            # revisions has changed due to the strip
            self.warning('%s: strip detected ? latest known revision is %s, '
                         'latest repository revision is %s', self.path,
                         latestrev, actualrev)
            session.execute('DELETE Revision X WHERE X revision > %(rev)s,'
                            'X from_repository R, R eid %(r)s',
                            {'rev': actualrev, 'r': self.eid})
            return
        if latestrev != actualrev:
            self.info('hg repo %s: known revisions up to %s, repo revision %s',
                      self.path, latestrev, actualrev)
        for i in xrange(latestrev + 1, actualrev + 1):
            try:
                self.import_revision(repoentity, repo, i)
            except Exception:
                self.critical('error while importing revision %s of %s',
                              i, self.path, exc_info=True)
                raise
            if not i % commitevery:
                # give a change to threads waiting for a cnxset by freeing it then
                # reacquiring it
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

    # reimport #################################################################

    def check(self, repoentity, start_revision=0, commitevery=1,
              strip=True, import_new=False):
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
        if strip and start_revision != 0:
            raise Exception('must start from revision 0 to strip')
        if strip and not repoentity.import_revision_content:
            for etype in ('DeletedVersionContent', 'VersionContent'):
                rset = session.execute(
                    'DELETE %s X WHERE X from_revision REV, REV from_repository R, R eid %%(r)s' % etype,
                    {'r': self.eid})
                if rset:
                    self.warning("deleted %s %s (content shouldn't be imported)",
                                 len(rset), session._(etype))
            rset = session.execute(
                'DELETE %s X WHERE X is VersionedFile, X from_repository R, R eid %(r)s',
                {'r': self.eid})
            if rset:
                self.warning("deleted %s %s (content shouldn't be imported)",
                             len(rset), session._(etype))
        else:
            rset = session.execute(
                'DELETE VersionedFile X WHERE X from_repository R, R eid %(r)s, '
                'NOT VC content_for X', {'r': self.eid})
            if rset:
                self.warning('deleted %s files without any known revision',
                             len(rset))
        if strip and start_revision == 0: # full check
            stripidx = {}
            stripidx['Revision'] = set(
                (eid for eid, in session.execute(
                    'Revision X WHERE X from_repository R, R eid %(r)s',
                    {'r': self.eid})) )
            stripidx['VersionedFile'] = set(
                (eid for eid, in session.execute(
                    'VersionedFile X WHERE X from_repository R, R eid %(r)s',
                    {'r': self.eid})) )
        else:
            stripidx = None
        # actual rev is the *number* of revision, latest rev the highest
        # revision number while hg revisions start at 0 -> - 1
        actualrev = bw_nb_revisions(repo.changelog) - 1
        latestrev = repoentity.latest_known_revision()
        self.info('hg repo %s: known revisions up to %s, repo revision %s',
                  self.path, latestrev, actualrev)
        if not import_new:
            actualrev = latestrev
        for i in xrange(start_revision, actualrev + 1):
            if i > latestrev:
                self.import_revision(repoentity, repo, i)
            else:
                self.check_revision(repoentity, repo, i, stripidx)
            if not i % commitevery:
                # give a change to threads waiting for a cnxset by freeing it then
                # reacquiring it
                session.commit()
                session.set_cnxset()
        if strip:
            if stripidx['Revision']:
                self.warning('deleted %s revisions not in repository',
                             len(stripidx['Revision']))
                session.repo.glob_delete_entities(session, stripidx['Revision'])
            if stripidx['VersionedFile']:
                self.warning('deleted %s files not in repository',
                             len(stripidx['VersionedFile']))
                session.repo.glob_delete_entities(session, stripidx['VersionedFile'])
        session.commit()

    def check_revision(self, repoentity, repo, i, stripidx):
        self.info('checking revision %s', i)
        session = repoentity._cw
        execute = session.execute
        node = repo.changelog.node(i)
        changeset = unicode(short_hex(node))
        rset = execute('Any X,XR WHERE X revision XR, X from_repository R, '
                       'R eid %(repo)s, X changeset %(cs)s',
                       {'repo': repoentity.eid, 'cs': changeset})
        if len(rset) > 1:
            # will crash on entities referencing this revision has parent,
            # better to stop now
            raise ExecutionError('revision #%s has more than one related '
                                 'entities (%s). Fix this manually first'
                                 % (changeset, rset))
        if rset:
            rev = rset.get_entity(0, 0)
            if rev.revision != i:
                self.warning('revision for changeset #%s has local revision '
                             'number to %s instead of %s',
                             changeset, rev.revision, i)
                # ensure we won't break (from repository, revision) unique
                # together constraint
                execute('SET X revision %(revneg)s WHERE X from_repository R, '
                        'R eid %(repo)s, X revision %(rev)s',
                        {'repo': repoentity.eid, 'rev': i, 'revneg': -i})
                rev.set_attributes(revision=i)
        else:
            rset = execute('Any X WHERE X from_repository R, X changeset NULL, '
                           'R eid %(repo)s, X revision %(rev)s',
                           {'repo': repoentity.eid, 'rev': i})
            if rset:
                self.warning('revision missing changeset: %s (#%s)', i, changeset)
                rev = rset.get_entity(0, 0)
                rev.set_attributes(changeset=changeset)
            else:
                self.warning('revision %s isn\'t imported', changeset)
                self.import_revision(repoentity, repo, i)
                return
        if stripidx is not None:
            stripidx['Revision'].remove(rev.eid)
        ctx = repo.changectx(i)
        date = datetime.fromtimestamp(ctx.date()[0])
        # XXX check revision's attributes
        # revdata = {'date': date, 'revision': i,
        #            'author': unicode(ctx.user(), self.encoding, 'replace'),
        #            'description': unicode(ctx.description(), self.encoding, 'replace'),
        #            'changeset': changeset,
        #            'branch': unicode(ctx.branch()),
        #            }
        parent_changesets = [short_hex(n) for n in repo.changelog.parents(node)
                             if n != nullid]
        if parent_changesets:
            args = {'r': self.eid}
            if len(parent_changesets) == 1:
                restr = 'X changeset %(cs)s'
                args['cs'] = parent_changesets[0]
            else:
                restr = 'X changeset IN (%s)' % ','.join(
                    repr(cs) for cs in parent_changesets)
            parents = execute(
                'Any X,XC,XR WHERE X changeset XC, X revision XR, '
                'X from_repository R, R eid %%(r)s, %s' % restr, args)
            assert len(parents) == len(parent_changesets), 'missing parent: expected %s, got %s' % (
                parents, [e.changeset for e in parents.entities()])
            for values in parents:
                if execute('SET R parent_revision PR WHERE R eid %(r)s, PR eid %(pr)s, '
                           'NOT R parent_revision PR',
                           {'r': rev.eid, 'pr': values[0]}):
                    self.warning('add missing parent revision')
            args['r'] = rev.eid
            if execute('DELETE R parent_revision X WHERE R parent_revision X, '
                       'R eid %%(r)s, NOT %s' % restr, args):
                self.warning('delete erroneous parent revision')
        else:
            parents = []
        if not repoentity.import_revision_content:
            return
        contenteids = set(
            (eid for eid, in session.execute(
                'Any X WHERE X from_revision R, R eid %(r)s', {'r': rev.eid})) )
        changes = repo.status(ctx.parents()[0].node(), ctx.node())[:3]
        modified, added, removed = changes
        path_filter = repoentity.subpath
        for path in modified + added:
            upath = unicode(path, self.encoding, 'replace')
            if not (path_filter is None or upath.startswith(path_filter)):
                continue
            directory, fname = split(path)
            vc = execute('Any VC,VF WHERE VF directory %(d)s, VF name %(n)s, '
                         'VC is VersionContent, VC content_for VF, VC from_revision R, R eid %(r)s',
                         {'d': directory, 'n': fname, 'r': rev.eid})
            if not vc:
                self.warning('add missing file %s modified/added by revision', upath)
                vceid, vfeid = self._import_version_content(
                    session, changeset, rev.eid, removed, path, upath, date, repo, ctx)
                if stripidx is not None:
                    spop(stripidx['VersionedFile'], vfeid)
            else:
                if stripidx is not None:
                    spop(stripidx['VersionedFile'], vc[0][1])
                contenteids.remove(vc[0][0])
                filectx = ctx[path]
                renameinfo = filectx.renamed()
                if renameinfo:
                    pvc, oldfile = self._renamed_vc_rset(session, repo, renameinfo)
                    if pvc:
                        assert len(pvc) == 1
                        if oldfile in removed:
                            if execute('SET X vc_rename Y WHERE X eid %(x)s, '
                                       'Y eid %(y)s, NOT X vc_rename Y',
                                       {'x': vc[0][0], 'y': pvc[0][0]}):
                                self.warning('add rename information on %s', upath)
                        else:
                            if execute('SET X vc_copy Y WHERE X eid %(x)s, '
                                       'Y eid %(y)s, NOT X vc_copy Y',
                                       {'x': vc[0][0], 'y': pvc[0][0]}):
                                self.warning('add copy information on %s', upath)
                    else:
                        self.error('detected copy or rename of %s@%s but unable'
                                   ' to find associated version content',
                                   oldfile, pvc.args['cs'])
        for path in removed:
            upath = unicode(path, self.encoding, 'replace')
            if not (path_filter is None or upath.startswith(path_filter)):
                continue
            directory, fname = split(path)
            vc = execute('Any VC,VF WHERE VF directory %(d)s, VF name %(n)s, '
                         'VC is DeletedVersionContent, VC content_for VF, '
                         'VC from_revision R, R eid %(r)s',
                         {'d': directory, 'n': fname, 'r': rev.eid})
            if not vc:
                self.warning('add missing file %s deleted by revision', upath)
                vceid, vfeid = bridge.import_deleted_version_content(
                    session, self.eid, rev.eid, upath, date)
                if stripidx is not None:
                    spop(stripidx['VersionedFile'], vfeid)
            else:
                if stripidx is not None:
                    spop(stripidx['VersionedFile'], vc[0][1])
                contenteids.remove(vc[0][0])
        if contenteids:
            self.warning('delete %s file revisions actually not modified by this revision',
                         len(contenteids))
            session.repo.glob_delete_entities(session, contenteids)
        parent_idx = dict( ((cs, lrev) for _, cs, lrev in parents) )
        parent_lrevs = [parent_idx[cs] for cs in parent_changesets]
        bridge.set_at_revision(session, rev.eid, parent_lrevs, safetybelt=True)


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
