# -*- coding: utf-8 -*-
"""makes the bridge between repository handlers and related cubicweb entities

:organization: Logilab
:copyright: 2007-2011 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
from __future__ import with_statement

__docformat__ = "restructuredtext en"

import sys
from os.path import join

from logilab.common.modutils import LazyObject
from logilab.mtconverter import guess_mimetype_and_encoding
from yams import ValidationError

from cubicweb import Binary, QueryError, typed_eid
from cubicweb.server.session import security_enabled
from cubes.vcsfile import queries

_VCSTYPES = {'subversion': LazyObject('cubes.vcsfile.reposvn', 'SVNRepository'),
             'mercurial': LazyObject('cubes.vcsfile.repohg', 'HGRepository'),
             }
_REPOHDLRS = {}


class VCSException(Exception):
    def __init__(self, repoeid, attr, msgid, msgargs=()):
        self.repoeid = repoeid
        self.attr = attr
        self.msgid = msgid
        self.msgargs = msgargs

    def __str__(self):
        return '%s.%s: %s' % (self.repoeid, self.attr,
                              self.msgid % self.msgargs)

    def to_validation_error(self, translate):
        msg = translate(self.msgid)
        if self.msgargs:
            msg %= self.msgargs
        return ValidationError(self.repoeid, {self.attr: msg})


def repository_handler(repoent):
    """get repository handler for the given repository entity"""
    # deactivate read security first, potentially needed to get access to
    # path/local_cache
    session = repoent._cw
    with security_enabled(session, read=False):
        try:
            repohdlr = _REPOHDLRS[repoent.eid]
            repohdlr.encoding = repoent.encoding # in case it changed
            return repohdlr
        except KeyError:
            try:
                path = repoent.path
                if not path:
                    if not repoent.local_cache:
                        msg = session._('no local access to repository')
                        raise ValidationError(repoent.eid, {'source_url': msg})
                    path = join(session.vreg.config.local_repo_cache_root,
                                repoent.local_cache)
                repohdlr = _VCSTYPES[repoent.type](repoent.eid, path,
                                                   repoent.encoding)
            except KeyError:
                msg = session._('%s is not a known repository type')
                raise ValidationError(repoent.eid, {'type': msg % repoent.type})
            except ImportError:
                msg = session._('missing python bindings to support %s repositories')
                raise ValidationError(repoent.eid, {'type': msg % repoent.type})
            _REPOHDLRS[repoent.eid] = repohdlr
            return repohdlr


def import_content(session, commitevery=10, raise_on_error=False):
    """synchronize content of known vcs repositories
    """
    for vcsrepo in session.execute(
        'Any X,T,U,P,L,SP,E WHERE X is Repository, '
        'X type T, X source_url U, X path P, X local_cache L, '
        'X subpath SP, X encoding E').entities():
        try:
            repohdlr = repository_handler(vcsrepo)
        except VCSException, ex:
            if raise_on_error:
                raise
            session.error(str(ex))
            continue
        import_vcsrepo_content(session, repohdlr, vcsrepo,
                               commitevery=commitevery,
                               raise_on_error=raise_on_error)


def import_vcsrepo_content(session, repohdlr, vcsrepo, commitevery=10,
                           raise_on_error=False):
    """synchronize content of given vcs repository"""
    try:
        repohdlr.import_content(vcsrepo, commitevery)
        # give other threads a chance to run: commit will release the cnxset, get
        # it back afterwards
        session.commit()
    except Exception:
        if raise_on_error:
            raise
        # clear in cases new files have been added in cache, but entities will
        # be rollbacked
        repohdlr.vf_path_cache.clear()
        try:
            vcsrepo._cw.set_cnxset() # ensure a cnxset is set
            title = vcsrepo.dc_title()
        except Exception:
            title = str(vcsrepo)
        repohdlr.exception(
            'error while importing content for vcs repo %s', title)
        session.rollback()
    session.set_cnxset()


def set_at_revision(session, reid, parent_lrevs=None, safetybelt=False):
    """at_revision is an internal relation used to know the full content of a
    repository at any revision. This function set this relation for newly
    created revision.

    `parent_lrevs` should be an ordered list of parent revision, the first
    one being the one into which others are merged
    """
    sql = session.system_sql
    if safetybelt:
        sql("DELETE FROM at_revision_relation WHERE eid_to='%s'" % reid)
    # link to version content generated by this revision
    # rql = 'SET VC at_revision REV WHERE REV eid %(rev)s, VC from_revision REV'
    sqlrestr = ('SELECT VC.cw_eid, %s FROM cw_%%s AS VC '
                'WHERE VC.cw_from_revision=%s' % (reid, reid))
    sql('INSERT INTO at_revision_relation(eid_from,eid_to) '
        '%s UNION %s' % (sqlrestr % 'VersionContent',
                         sqlrestr % 'DeletedVersionContent'))
    # link to version content of files in parent revisions but not modified by
    # this revision
    # rql = ('SET VC at_revision REV WHERE VC is VersionContent, '
    #        'REV eid %(rev)s, VC at_revision PREV, '
    #        'REV parent_revision PREV, '
    #        'NOT EXISTS(VC2 from_revision REV, VC content_for VF, '
    #        'VC2 content_for VF)')
    if parent_lrevs is None or len(parent_lrevs) == 1:
        sql('INSERT INTO at_revision_relation(eid_from,eid_to) '
            'SELECT DISTINCT VC.cw_eid, %(reid)s '
            'FROM at_revision_relation AS ar, parent_revision_relation AS pr, cw_VersionContent AS VC '
            'WHERE VC.cw_eid=ar.eid_from AND pr.eid_from=%(reid)s AND pr.eid_to=ar.eid_to '
            'AND NOT EXISTS('
            '  SELECT 1 FROM cw_VersionContent AS VC2 '
            '  WHERE VC2.cw_from_revision=%(reid)s AND VC2.cw_content_for=VC.cw_content_for '
            '  UNION '
            '  SELECT 1 FROM cw_DeletedVersionContent AS VC2 '
            '  WHERE VC2.cw_from_revision=%(reid)s AND VC2.cw_content_for=VC.cw_content_for)'
            % {'reid': reid})
    elif len(parent_lrevs) > 1:
        # getting back files "at_revision" parent revision from the first parent
        # revision is enough: other changes get back from merged parents as
        # version content "from_revision" the current revision
        sql('INSERT INTO at_revision_relation(eid_from,eid_to) '
            'SELECT DISTINCT VC.cw_eid, %(reid)s '
            'FROM at_revision_relation AS ar, parent_revision_relation AS pr, '
            '     cw_VersionContent AS VC, cw_Revision as R '
            'WHERE VC.cw_eid=ar.eid_from AND pr.eid_from=%(reid)s AND pr.eid_to=ar.eid_to '
            ' AND pr.eid_to=R.cw_eid AND R.cw_revision=%(plrev)s '
            ' AND NOT EXISTS('
            '  SELECT 1 FROM cw_VersionContent AS VC2 '
            '  WHERE VC2.cw_from_revision=%(reid)s AND VC2.cw_content_for=VC.cw_content_for '
            '  UNION '
            '  SELECT 1 FROM cw_DeletedVersionContent AS VC2 '
            '  WHERE VC2.cw_from_revision=%(reid)s AND VC2.cw_content_for=VC.cw_content_for)'
            % {'reid': reid, 'plrev': parent_lrevs.pop(0)})


def import_revision(session, repoeid, date, **kwargs):
    """import a new revision from a repository"""
    args = {'date': date}
    args['repoeid'] = repoeid
    for attr in ('revision', 'author', 'description', 'changeset', 'branch'):
        args[attr] = kwargs.get(attr)
    prevs = kwargs['parents']
    if prevs:
        args['parent'] = prevs[0]
    reveid = session.execute(queries.new_revision_rql(prevs, True), args)[0][0]
    if len(prevs) > 1:
        for preveid in prevs[1:]:
            session.execute('SET R parent_revision PR WHERE R eid %(r)s, PR eid %(pr)s',
                            {'r': reveid, 'pr': preveid})
    return reveid

def import_versioned_file(session, repoeid, date, directory, name):
    """import a version controlled file from a repository"""
    args = {'directory': directory, 'name': name, 'repoeid': repoeid}
    return session.execute(
        'INSERT VersionedFile X: X directory %(directory)s, '
        'X name %(name)s, X from_repository R '
        'WHERE R eid %(repoeid)s', args)[0][0]

def import_version_content(session, repoeid, reveid, upath, date, **kwargs):
    """import a new file revision from a repository"""
    repohdlr = repository_handler(session.entity_from_eid(repoeid, 'Repository'))
    vfeid = repohdlr.vf_eid(session, upath, date)
    # done in a hook but doing it here as well to avoid an additional query to
    # lookup filename
    mt, enc = guess_mimetype_and_encoding(
        fallbackencoding=repohdlr.encoding, fallbackmimetype=None,
        filename=upath)
    args = {'vf': vfeid, 'rev': reveid, 'data': kwargs['data'],
            'df': mt and unicode(mt) or None,
            'de': enc and unicode(enc) or None}
    rql = ('INSERT VersionContent X: X from_revision REV, X content_for VF, '
           'X data_format %(df)s, X data_encoding %(de)s, X data %(data)s')
    for inlinerel in ('vc_copy', 'vc_rename'):
        if inlinerel in kwargs:
            args[inlinerel] = kwargs[inlinerel]
            rql += ', X %s %%(%s)s' % (inlinerel, inlinerel)
    rql += ' WHERE REV eid %(rev)s, VF eid %(vf)s'
    return session.execute(rql, args)[0][0], vfeid


def import_deleted_version_content(session, repoeid, reveid, upath, date):
    """import a new deleted file revision from a repository"""
    repohdlr = repository_handler(session.entity_from_eid(repoeid, 'Repository'))
    vfeid = repohdlr.vf_eid(session, upath, date)
    args = {'vf': vfeid, 'rev': reveid}
    rql = ('INSERT DeletedVersionContent X: X from_revision REV, X content_for VF '
           ' WHERE REV eid %(rev)s, VF eid %(vf)s')
    return session.execute(rql, args)[0][0], vfeid


from cubicweb import QueryError
from cubicweb.server.sources import storages

class VCSStorage(storages.Storage):
    """store Bytes attribute value in a version content system"""

    def callback(self, source, session, value):
        repoeid, dir, name, revnum = source.binary_to_str(value).split('\x01')
        repoeid = typed_eid(repoeid)
        try:
            vcsrepohdlr = repository_handler(session.entity_from_eid(repoeid, 'Repository'))
        except Exception, ex:
            source.critical("can't get repository handler for eid %s: %s",
                            repoeid, ex, exc_info=sys.exc_info())
            return None
        try:
            return vcsrepohdlr.file_content(dir, name, revnum)
        except Exception, ex:
            source.critical("can't get content for %s/%s at revision %s in vcs "
                            "repository %s: %s",
                            dir, name, revnum, vcsrepohdlr, ex,
                            exc_info=sys.exc_info())
            return None

    def entity_added(self, entity, attr):
        """an entity using this storage for attr has been added"""
        try:
            data = entity.cw_edited.pop(attr)
        except KeyError:
            pass
        else:
            session = entity._cw
            # don't create vcs transaction if the revision is being imported
            # from the vcs repository
            try:
                repoeid, dir, name, revnum = session.transaction_data['vcs_importing']
            except KeyError:
                vf = entity._vc_vf()
                repoeid = vf.repository.eid
                vcsrepohdlr, transaction = entity._vc_prepare(repoeid)
                dir = vcsrepohdlr.encode(vf.directory)
                name = vcsrepohdlr.encode(vf.name)
                revnum = transaction.rev
                vcsrepohdlr.add_versioned_file_content(session, transaction,
                                                       vf, entity, data)
            vckey = (str(repoeid), dir, name, str(revnum))
            entity.cw_edited[attr] = Binary('\x01'.join(vckey))
            return data

    def entity_updated(self, entity, attr):
        """an entity using this storage for attr has been updatded"""
        # XXX create a new revision to make this storage usable for arbitrary
        # attributes
        raise QueryError('read-only attribute')

    def entity_deleted(self, entity, attr):
        """an entity using this storage for attr has been deleted"""
        # XXX delete from repository to make this storage usable for arbitrary
        # attributes (unless vcs-importing, meaning a strip has been detected)
        pass
