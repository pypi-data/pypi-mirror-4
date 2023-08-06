"""entity classes for vcsfile content types

:organization: Logilab
:copyright: 2007-2011 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"
import os.path as osp

from logilab.common.decorators import cached, clear_cache
from logilab.common.compat import any
from logilab.common.deprecation import deprecated

from cubicweb import QueryError, Binary, Unauthorized
from cubicweb.selectors import is_instance
from cubicweb.entities import AnyEntity, fetch_config, adapters

from cubes.vcsfile import queries

def rql_revision_content(repoeid, revnum, branch=None):
    """return rql query to get the repository content at a given revision"""
    args = {'rev': revnum, 'x': repoeid, 'branch': branch}
    return ('Any V,REV,F,D,N ORDERBY D,N WHERE '
            'V content_for F, F directory D, F name N, '
            'V from_revision VR, VR revision REV, '
            'V at_revision AVR, AVR revision %(rev)s, AVR branch %(branch)s, '
            'AVR from_repository R, R eid %(x)s'
            ), args

_MARKER = object()

def remove_authinfo(url):
    try:
        base, remaining = url.split('@')
    except ValueError:
        return url
    try:
        scheme, authinfo = base.split('://')
    except ValueError:
        return url
    return u'%s://***@%s' % (scheme, remaining)

class Repository(AnyEntity):
    """customized class for Repository entities"""
    __regid__ ='Repository'

    __permissions__ = ('write',)
    fetch_attrs, cw_fetch_order = fetch_config(['source_url', 'title', 'subpath', 'type'])
    rest_attr = 'eid' # see #XXX, using path cause pb w/ apache redirection

    def dc_title(self):
        if self.title:
            return self.title
        if self.source_url:
            return remove_authinfo(self.source_url)
        if self.path: # None if user isn't authorized to see path attribute
            title = '%s:%s' % (self.type, self.path)
            if self.subpath:
                title += ' (%s)' % self.subpath
        else:
            title = self._cw._('%(type)s repository #%(eid)s') % {
                'type': self.type, 'eid': self.eid}
        return title

    def cw_clear_all_caches(self):
        super(Repository, self).cw_clear_all_caches()
        clear_cache(self, 'branch_head')

    def printable_value(self, attr, *args, **kwargs):
        if attr == 'source_url':
            if args:
                value = args[0]
            elif 'value' in kwargs:
                value = kwargs['value']
            else:
                value = self.source_url
            if value:
                return remove_authinfo(value)
            return u''
        return super(Repository, self).printable_value(attr, *args, **kwargs)

    # navigation in versioned content #########################################

    def latest_known_revision(self):
        """return the number of the latest known revision"""
        latestrev = self._cw.execute(
            'Any MAX(REVR) WHERE R eid %(r)s, REV from_repository R, '
            'REV revision REVR', {'r' : self.eid})[0][0]
        if latestrev is None:
            return -1
        return latestrev

    def heads_rset(self):
        """return a result set containing head revision (eg revisions without
        children)
        """
        return self._cw.execute(
            'Any REV WHERE R eid %(r)s, REV from_repository R, '
            'NOT CREV parent_revision REV', {'r' : self.eid})

    def branches(self):
        """return existing branches"""
        rql = 'DISTINCT Any B WHERE R eid %(r)s, REV from_repository R, REV branch B'
        branches = [b for b, in self._cw.execute(rql, {'r' : self.eid})]
        if not branches:
            branches = [self.default_branch()]
        return branches

    @cached
    def branch_head(self, branch=_MARKER):
        """return latest revision of the given branch"""
        if branch is _MARKER:
            branch = self.default_branch()
        rset = self._cw.execute(
            'Any REV WHERE REV from_repository R, R eid %(r)s, REV revision RR '
            'WITH RR BEING (Any MAX(RR) WHERE '
            '  REV from_repository R, R eid %(r)s, REV branch %(branch)s, '
            '  REV revision RR)',
            {'r': self.eid, 'branch': branch})
        if not rset:
            return None
        return rset.get_entity(0, 0)

    def versioned_file(self, directory, filename):
        rset = self._cw.execute(
            'Any X WHERE X is VersionedFile, X from_repository R, '
            'R eid %(repo)s, X directory %(dir)s, X name %(name)s',
            {'repo' : self.eid, 'dir' : directory, 'name' : filename})
        return rset and rset.get_entity(0, 0) or None

    # vcs write support ########################################################

    def default_branch(self):
        return {'subversion': None, 'mercurial': u'default'}[self.type]

    def make_revision(self, msg=None, author=_MARKER, branch=_MARKER,
                      parentbranch=_MARKER):
        """parameters:
        :msg: the check-in message (string)
        :author: the check-in author (string)
        :branch: the branch in which the revision should be done (string)
        :parentbranch: when a branch is created, the parent branch of the revision
        """
        if branch is _MARKER:
            branch = self.default_branch()
        if author is _MARKER:
            author = self._cw.user.login
        parent = self.branch_head(branch)
        if parent is None and branch != parentbranch:
            parent = self.branch_head(parentbranch)
        #assert parent
        args = {'description' : msg, 'author': author, 'branch': branch,
                'repoeid' : self.eid, 'parent': parent and parent.eid}
        rset = self._cw.execute(queries.new_revision_rql(parent), args)
        return rset.get_entity(0, 0)

    def vcs_add(self, filedir, filename, stream, strict=False,
                extraattrs=None, **kwargs):
        """add the file into the repository, as <filedir>/<filename>, with
        content specified in <stream> (Binary instance).

        If strict and the file already exists in the repository, an error will
        be raised, else a new revision will be simply uploaded.

        If you've an extended versioned file's schema you can give additional
        attributes to create_entity using the extraattrs argument (expected to
        be a dict)

        Return the VersionedFile instance.
        """
        vf = self.versioned_file(filedir, filename)
        if not vf:
            if extraattrs is None:
                extraattrs = {}
            vf = self._cw.create_entity('VersionedFile',
                                        from_repository=self, directory=filedir,
                                        name=filename, **extraattrs)
        elif strict:
            raise Exception('attempting to add an already existing file')
        vf.vcs_upload_revision(stream, **kwargs)
        return vf


class Revision(AnyEntity):
    """customized class for Revision entities"""
    __regid__ ='Revision'
    fetch_attrs, cw_fetch_order = fetch_config(['revision', 'changeset', 'branch',
                                             'author', 'description', 'creation_date'],
                                            order='DESC')

    def dc_title(self):
        if self.changeset:
            return u'#%(rev)s:%(changeset)s' % {
                'rev': self.revision, 'changeset': self.changeset}
        return u'#%s' % self.revision

    def dc_long_title(self):
        try:
            return self._cw._('%(rev)s of repository %(repo)s') % {
                'rev': self.dc_title(), 'repo': self.repository.dc_title()}
        except Unauthorized:
            return self._cw._('%(rev)s of a private repository') % {
                'rev': self.dc_title()}

    def sortvalue(self, rtype=None):
        if rtype is None:
            return self.revision
        return super(Revision, self).sortvalue(rtype)

    # navigation in versioned content #########################################

    @property
    def repository(self):
        return self.from_repository[0]

    @property
    def file_revisions(self):
        return self.reverse_from_revision

    @property
    def children_revisions(self):
        return self.reverse_parent_revision


class VersionedFile(AnyEntity):
    """customized class for VersionedFile entities"""
    __regid__ ='VersionedFile'
    fetch_attrs, cw_fetch_order = fetch_config(['directory', 'name'])

    # XXX branches
    def dc_title(self):
        if self.deleted_in_branch():
            return u'%s (%s)' % (self.path, self._cw._('DELETED'))
        return self.path

    def dc_long_title(self):
        try:
            return self._cw._('%(path)s (from %(repotype)s repository: %(repo)s)') % {
                'path': self.dc_title(), 'repo': self.repository.dc_title(),
                'repotype': self.repository.type}
        except Unauthorized:
            return self._cw._('%(path)s (from private repository)') % {
                'path': self.dc_title(),}

    def cw_clear_all_caches(self):
        super(VersionedFile, self).cw_clear_all_caches()
        clear_cache(self, 'version_content')
        clear_cache(self, 'branch_head')

    # navigation in versioned content #########################################

    @property
    def repository(self):
        return self.from_repository[0]

    @property
    def path(self):
        if self.directory:
            return u'%s/%s' % (self.directory, self.name)
        return self.name

    @property
    def revisions(self):
        """return an ordered list of versions'content for this file"""
        return self.reverse_content_for

    @property
    @cached
    def head(self):
        """return latest [deleted] version content for this file"""
        rset = self._cw.execute(
            'Any V WHERE X eid %(x)s, V content_for X, V at_revision R, '
            'R revision RR WITH RR BEING '
            '(Any MAX(RR) WHERE X eid %(x)s, V content_for X, V at_revision R, '
            ' R revision RR)',
            {'x': self.eid})
        # content_for relation is not mandatory on VersionedFile entities
        if not rset:
            return None
        return rset.get_entity(0, 0)

    @cached
    def version_content(self, revnum):
        if revnum is None:
            return self.branch_head()
        rset = self._cw.execute(
            'Any C,VF,R WHERE C content_for VF, C from_revision R, '
            'R revision %(rnum)s, VF eid %(x)s',
            {'rnum' : int(revnum), 'x' : self.eid})
        if rset:
            return rset.get_entity(0, 0)
        return None

    @cached
    def branch_head(self, branch=_MARKER):
        """return latest [deleted] version content for this file in the given
        branch
        """
        if branch is _MARKER:
            branch = self.repository.default_branch()
        rset = self._cw.execute(
            'Any V WHERE X eid %(x)s, V content_for X, V at_revision R, '
            'R revision RR WITH RR BEING '
            '(Any MAX(RR) WHERE X eid %(x)s, V content_for X, V at_revision R, '
            ' R branch %(branch)s, R revision RR)',
            {'x': self.eid, 'branch': branch})
        # content_for relation is not mandatory on VersionedFile entities
        if not rset:
            return None
        return rset.get_entity(0, 0)

    def deleted_in_branch(self, branch=_MARKER):
        """deleted in branch != does not even exist in branch
        """
        head = self.branch_head(branch)
        return head and head.is_deletion() or False

    # vcs write support #######################################################

    def vcs_rm(self, rev=None, **kwargs):
        """remove this file from the vcs

        takes a rev or a kwargs having keys: branch, msg, author
        """
        if not isinstance(self.branch_head(kwargs.get('branch', _MARKER)),
                          VersionContent):
            # already deleted
            raise QueryError(self._cw._('%s is already deleted from the vcs')
                             % self.path)
        if rev is None:
            if not 'msg' in kwargs:
                kwargs['msg'] = self._cw._('deleted %s') % self.dc_title()
            rev = self.repository.make_revision(**kwargs)
        self._cw.execute(
            'INSERT DeletedVersionContent D: D content_for X, '
            'D from_revision R WHERE X eid %(x)s, R eid %(r)s',
            {'x' : self.eid, 'r' : rev.eid})

    def vcs_upload_revision(self, stream, rev=None, **kwargs):
        """upload a new revision for this file to the vcs

        either takes a rev or a kwargs having keys: branch, msg, author

        return the newly created version content entity
        """
        if rev is None:
            rev = self.repository.make_revision(**kwargs)
        return self._cw.execute(queries.new_file_content_rql(),
                                {'vfeid' : self.eid, 'reveid' : rev.eid,
                                 'data' : Binary(stream.read())}).get_entity(0, 0)


class DeletedVersionContent(AnyEntity):
    """customized class for DeletedVersionContent entities"""
    __regid__ ='DeletedVersionContent'
    fetch_attrs, cw_fetch_order = fetch_config(['from_revision', 'content_for'],
                                               order='DESC')

    def dc_title(self):
        return self._cw._('%(file)s DELETED') % {
            'file': self.file.path, 'revision': self.rev.revision}

    def dc_long_title(self):
        rev = self.rev
        return self._cw._('%(file)s (revision %(revision)s on %(date)s by %(author)s)') % {
            'file': self.dc_title(), 'revision': rev.revision,
            'author': rev.author, 'date': rev.printable_value('creation_date')}

    def dc_description(self, format='text/plain'):
        # override cubicweb's default implementation because it requires
        # 'description' to be a real schema attribute but it's only
        # a class property in our case
        return self.rev.dc_description(format)

    # navigation in versioned content #########################################

    @property
    def repository(self):
        return self.rev.repository

    @property
    def file(self):
        return self.content_for[0]

    @property
    def rev(self):
        return self.from_revision[0]

    @property
    def head(self):
        return self.file.branch_head(self.rev.branch)

    def iter_parent_versions(self):
        done = set([self.eid])
        todo = [self]
        while todo:
            head = todo.pop(0)
            for parent in head.previous_versions():
                if not parent.eid in done:
                    done.add(parent.eid)
                    todo.append(parent)
                    yield parent

    def previous_versions(self):
        return tuple(self._cw.execute(
            'DISTINCT Any VC ORDERBY VC DESC WHERE '
            'X from_revision R, X content_for F, X eid %(x)s, '
            'VC at_revision PR, VC content_for F, NOT VC eid %(x)s, '
            'R parent_revision PR', {'x': self.eid}).entities())

    @deprecated('[vcsfile 1.7.1] use previous_versions() instead')
    def previous_version(self, branch=_MARKER):
        pver = self.previous_versions()
        return pver and pver[0] or None

    def next_versions(self):
        return tuple(self._cw.execute(
            'DISTINCT Any VC ORDERBY VC ASC WHERE '
            'X at_revision R, X content_for F, X eid %(x)s, '
            'VC from_revision PR, VC content_for F, NOT VC eid %(x)s, '
            'PR parent_revision R', {'x': self.eid}).entities())

    @deprecated('[vcsfile 1.7.1] use next_versions() instead')
    def next_version(self, branch=_MARKER):
        nver = self.next_versions()
        return nver and nver[0] or None

    # < 0.7 bw compat properties
    @property
    def revision(self):
        return self.from_revision[0].revision

    @property
    def author(self):
        return self.from_revision[0].author

    @property
    def description(self):
        return self.from_revision[0].description

    def is_head(self, branch=_MARKER):
        """return true if this version content is the head for its file in
        the given branch or in its revision's branch.
        """
        if branch is _MARKER:
            branch = self.rev.branch
        return self.eid == self.file.branch_head(branch).eid

    def is_deletion(self):
        return True

    # data server side internals to be able to create new vcs repo revision
    # using rql queries

    def _vc_vf(self):
        """return versioned file associated to a [Deleted]VersionContent entity"""
        if not hasattr(self, '_vcsrepoinfo'):
            try:
                vfeid = self.cw_attr_cache['content_for']
            except KeyError, ex:
                raise missing_relation_error(self, 'content_for')
            vf = self._cw.execute(
                'Any X, R, FD, FN WHERE X directory FD, X name FN, X eid %(x)s, '
                'X from_repository R', {'x': vfeid}).get_entity(0, 0)
            self._vcsrepo_info = vf
        return self._vcsrepo_info

    def _vc_prepare(self, vcsrepoeid=None):
        try:
            vfeid = self.cw_attr_cache['content_for']
        except KeyError:
            raise missing_relation_error(self, 'content_for')
        session = self._cw
        if vcsrepoeid is None:
            # retrieve associated VersionedFile instance
            vf = session.execute('Any X,D,N,R WHERE X name N, X directory D,'
                                 'X from_repository R, X eid %(x)s',
                                 {'x': vfeid}).get_entity(0, 0)
            vcsrepo = vf.repository
        else:
            vcsrepo = self._cw.entity_from_eid(vcsrepoeid)
        try:
            transaction = session.transaction_data['vctransactions'][vcsrepo.eid]
        except KeyError:
            raise QueryError('you must create a Revision instance before '
                             'adding some content')
        CheckRevisionOp(session, entity=self)
        return bridge.repository_handler(vcsrepo), transaction


from cubes.vcsfile import bridge
try:
    from cubes.vcsfile.hooks import missing_relation_error, CheckRevisionOp
except ImportError:
    # server part not installed
    pass


class VersionContent(DeletedVersionContent):
    """customized class for VersionContent entities"""
    __regid__ = 'VersionContent'

    def dc_title(self):
        return self.file.path

    def is_deletion(self):
        return False

    def size(self):
        return self._cw.execute("Any LENGTH(D) WHERE X eid %(eid)s, X data D",
                                {'eid': self.eid})[0][0]


class VersionContentIDownloadableAdapter(adapters.IDownloadableAdapter):
    __select__ = is_instance('VersionContent')

    def download_url(self, **kwargs):
        return self.entity.absolute_url(vid='download', **kwargs)
    def download_content_type(self):
        return self.entity.data_format
    def download_encoding(self):
        return self.entity.data_encoding
    def download_file_name(self):
        return self.entity.file.name
    def download_data(self):
        return self.entity.data.getvalue()
