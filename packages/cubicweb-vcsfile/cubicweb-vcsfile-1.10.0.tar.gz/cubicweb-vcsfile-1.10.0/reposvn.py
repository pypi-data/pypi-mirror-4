"""repository abstraction for a subversion repository

:organization: Logilab
:copyright: 2007-2010 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

from os.path import join, sep, split
from datetime import datetime
from cStringIO import StringIO

from logilab.common.decorators import cached

from svn import fs, repos, core, delta, ra

from cubicweb import Binary, QueryError

from cubes.vcsfile import repo, bridge

def _read_file_content(root, path):
    content = Binary()
    try:
        stream = fs.file_contents(root, path)
    except Exception:
        return None
    while 1:
        data = core.svn_stream_read(stream, core.SVN_STREAM_CHUNK_SIZE)
        content.write(data)
        if len(data) < core.SVN_STREAM_CHUNK_SIZE:
            break
    core.svn_stream_close(stream)
    return content

class SVNRepository(repo.VCSRepository):
    type = 'svn'

    def __init__(self, *args, **kwargs):
        super(SVNRepository, self).__init__(*args, **kwargs)
        # svn uses utf-8 internally; we should not try to contradict that
        self.encoding = 'utf-8'

    def canonicalize(self, fspath):
        fspath = core.svn_path_canonicalize(fspath)
        repos.open(fspath) # throwaway, just check it's a valid svn repository
        return fspath

    def import_content(self, repoentity, commitevery=10):
        """import content from the subversion repository

        NOTE: server side only method
        """
        try:
            repo = repos.open(self.path)
            fsrep = repos.fs(repo)
        except core.SubversionException, ex:
            self.error('Impossible to open repository %s (%s)', self, ex)
            return
        callbacks = ra.Callbacks()
        #ra_ctx = ra.open2('file://' + self.path, callbacks, None, None)
        rev = repoentity.latest_known_revision()
        if rev == -1:
            rev = 0
        actualrev = fs.youngest_rev(fsrep)
        session = repoentity._cw
        while rev < actualrev:
            base_root = fs.revision_root(fsrep, rev)
            rev += 1
            if session.execute('Any X WHERE X from_repository R, R eid %(repo)s,'
                               'X revision %(rev)s',
                               {'repo': repoentity.eid, 'rev': rev}):
                self.warning('skip revision %s, seems already imported', rev)
                continue
            self.info('importing content of %s for revision %s', self, rev)
            # the base of the comparison
            editor = SVNImporter(repoentity, fsrep, base_root, rev,
                                 import_revision_content = repoentity.import_revision_content)
            try:
                editor.import_revision()
            except Exception:
                self.critical('error while importing revision %s of %s',
                              rev, repoentity.path, exc_info=True)
                raise
            if not rev % commitevery:
                # give a change to threads waiting for a pool by freeing it then
                # reacquiring it
                session.commit()
                session.set_cnxset()

    def _file_content(self, path, rev):
        """extract a binary string with the content of the file at `path` for
        revision `rev` in the repository
        """
        rev = int(rev)
        fsrep = repos.fs(repos.open(self.path))
        root = fs.revision_root(fsrep, rev)
        return _read_file_content(root, path)

    def revision_transaction(self, session, entity):
        """open a transaction to create a new revision corresponding to the
        given entity
        """
        if session.transaction_data.get('%s_info' % self.eid):
            repoptr, fsrep = session.transaction_data.get('%s_info' % self.eid)
        else:
            repoptr = repos.open(self.path)
            fsrep = repos.fs(repoptr)
            session.transaction_data['%s_info' % self.eid] = (repoptr, fsrep)
        # open a transaction against HEAD
        return SVNTransaction(repoptr, fsrep,
                              self.encode(entity.cw_attr_cache.get('author', u'')),
                              self.encode(entity.cw_attr_cache.get('description', u'')))

    def add_versioned_file_content(self, session, transaction, vf, entity, data):
        """add a new revision of a versioned file"""
        root = transaction.root
        # check if the parent directory exists in the repository
        directory = vf.directory.encode(self.encoding)
        if directory:
            parts = directory.split(sep)
            for i in xrange(len(parts)):
                directory = sep.join(parts[:i+1])
                kind = fs.check_path(root, directory)
                if kind == core.svn_node_none:
                    fs.make_dir(root, directory)
        # check if the file exists in the repository
        fname = join(directory, vf.name.encode(self.encoding))
        kind = fs.check_path(root, fname)
        if kind == core.svn_node_none:
            self.info('file %r does not exist in repo %s, creating...',
                      fname, self)
            fs.make_file(root, fname)
        else:
            self.info('updating file %r in repo %s', fname, self)
        handler, baton = fs.apply_textdelta(root, fname, None, None)
        delta.svn_txdelta_send_string(data.getvalue(), handler, baton)
        transaction.modified.add(fname)
        return fname.decode(self.encoding)

    def add_versioned_file_deleted_content(self, session, transaction, vf, entity):
        """add a new revision of a just deleted versioned file"""
        root = transaction.root
        # check if the file exists in the repository
        directory = vf.directory.encode(self.encoding)
        fname = join(directory, vf.name.encode(self.encoding))
        kind = fs.check_path(root, fname)
        if kind == core.svn_node_none:
            self.debug('file %r does not exist in repo %s',
                      fname, self)
            raise Exception('file %r does not exist' % fname)
        self.info('deleting %r from repo', fname)
        fs.delete(root, fname)
        transaction.modified.add(fname)
        return fname.decode(self.encoding)


class SVNTransaction(object):
    def __init__(self, repoptr, fsrep, author, msg):
        self.modified = set()
        rev = fs.youngest_rev(fsrep)
        txn = repos.fs_begin_txn_for_commit(repoptr, rev, author, msg)
        root = fs.txn_root(txn)
        #rev_root = fs.revision_root(fsrep, rev)
        self.root = root
        self.rev = rev+1
        self.txn = txn
        self.repoptr = repoptr

    def precommit(self):
        if not self.modified:
            raise QueryError('nothing changed')

    def commit(self):
        repos.fs_commit_txn(self.repoptr, self.txn)

    def rollback(self):
        fs.abort_txn(self.txn)


class SVNImporter(delta.Editor):
    def __init__(self, repoentity, fsrep, base_root, rev,
                 import_revision_content=True):
        self.repoeid = repoentity.eid
        self.encoding = repoentity.encoding
        self.session = repoentity._cw
        self.import_revision_content = import_revision_content
        path_filter = repoentity.subpath
        if isinstance(path_filter, unicode):
            # if we don't encode we may get unicode error when comparing files'
            # path against the path filter
            path_filter = path_filter.encode(self.encoding)
        self.path_filter = path_filter
        self.fsrep = fsrep
        #self.svnrepo = repo
        #self.ra_ctx = ra_ctx
        self.base_root = base_root
        self.rev = rev
        self.root = fs.revision_root(fsrep, rev)
        self.execute = self.session.execute
        revkwargs = self.base_rev_content()
        self.reveid = bridge.import_revision(self.session, self.repoeid,
                                             **revkwargs)
        self.date = revkwargs['date']

    def import_revision(self):
        def authz_cb(root, path, pool):
            return 1
        # construct the editor
        e_ptr, e_baton = delta.make_editor(self)
        # compute the delta
        repos.dir_delta(self.base_root, '', '', self.root, '',
                        e_ptr, e_baton, authz_cb, 0, 1, 0, 0)
        bridge.set_at_revision(self.session, self.reveid)

    def base_rev_content(self):
        revdata = {'revision': self.rev}
        author = fs.revision_prop(self.fsrep, self.rev,
                                  core.SVN_PROP_REVISION_AUTHOR)
        revdata['author'] = unicode(author, self.encoding, 'replace')
        rawdate = fs.revision_prop(self.fsrep, self.rev,
                                   core.SVN_PROP_REVISION_DATE)
        if rawdate:
            aprtime = core.svn_time_from_cstring(rawdate)
            # aprtime is microseconds; make seconds
            # assume secs in local TZ XXX we don't really know the TZ, do we?
            revdata['date'] = datetime.fromtimestamp(aprtime / 1000000)
        else:
            revdata['date'] = datetime.now()
        description = fs.revision_prop(self.fsrep, self.rev,
                                       core.SVN_PROP_REVISION_LOG)
        revdata['description'] = unicode(description, self.encoding,
                                       'replace')
        parent = self.execute('Revision X WHERE X revision %(rev)s, '
                              'X from_repository R, R eid %(r)s',
                              {'rev': self.rev - 1, 'r': self.repoeid})
        revdata['parents'] = parent and parent[0]
        return revdata

#     def rev_content(self, path):
#         # XXX code below may be used to get branches/tags information
#         # note mergeinfo require svn >= 1.5 (an update of the repo backend may
#         # be necessary)
##         print path, self.rev
##         print 'LOCS', ra.get_locations(self.ra_ctx, path, self.rev, range(1, self.rev))
##         print core.SVN_PROP_MERGEINFO, fs.node_prop(self.root, path, core.SVN_PROP_MERGEINFO)
##         try:
##             print 'FMI {',
##             minfos = repos.fs_get_mergeinfo(self.svnrepo, [path], self.rev,
##                                             core.svn_mergeinfo_inherited,
##                                             False, None, None)
##             for mf, mfinfos in minfos.iteritems():
##                 print mf, ': {',
##                 for mergedf, revranges in mfinfos.iteritems():
##                     print mergedf, [(rev.start, rev.end) for rev in revranges], ',',
##                 print '}',
##             print '}'
##         except core.SubversionException:
##             print 'not supported'
#         return fdata

    def match_path(self, path):
        return self.path_filter is None or path.startswith(self.path_filter)

    # svn generated events ####################################################

    def open_root(self, base_revision, dir_pool):
        #print 'open_root', base_revision, dir_pool
        pass

    def change_dir_prop(self, dir_baton, name, value, pool):
        #print 'change_dir_prop', dir_baton, name, value, pool
        pass

    def open_directory(self, path, *args):
        #print 'open_directory', path
        pass

    def close_directory(self, baton):
        #print 'close_directory', baton
        pass

    def _mark_importing(self, path):
        dir, name = split(path)
        self.session.transaction_data['vcs_importing'] = (self.repoeid, dir,
                                                          name, self.rev)
    def add_file(self, path, *args):
        if self .import_revision_content and self.match_path(path):
            self._mark_importing(path)
            upath = unicode(path, self.encoding, 'replace')
            bridge.import_version_content(
                self.session, self.repoeid, self.reveid, upath, self.date,
                data=_read_file_content(self.root, path))

    def add_directory(self, path, *args):
        #print 'add_directory', path
        pass

    def change_file_prop(self, file_baton, name, value, pool):
        #print 'change_file_prop', file_baton, name, value, pool
        pass

    def open_file(self, path, *args):
        #print 'open file', path
        if self.match_path(path):
            self._mark_importing(path)
            upath = unicode(path, self.encoding, 'replace')
            bridge.import_version_content(
                self.session, self.repoeid, self.reveid, upath, self.date,
                data=_read_file_content(self.root, path))

    def close_file(self, file_baton, text_checksum):
        pass

    def delete_entry(self, path, revision, parent_baton, pool):
        if self.match_path(path):
            # can't use svn property, return svn_core_none for deleted items
            upath = unicode(path, self.encoding, 'replace')
            directory, name = split(upath)
            if self.execute(
                'Any X WHERE X is VersionedFile, X directory %(path)s, '
                'X name %(name)s, X from_repository R, R eid %(r)s',
                {'path': directory, 'name': name, 'r': self.repoeid}):
                # deleted file
                bridge.import_deleted_version_content(
                    self.session, self.repoeid, self.reveid, upath, self.date)
                return
            # deleted directory
            for childdir, childname in self.execute(
                'Any XD, XN WHERE X is VersionedFile, X directory ~= %(path)s, '
                'X from_repository R, R eid %(r)s, X directory XD, X name XN',
                {'path': path + '%', 'r': self.repoeid}):
                upath = join(childdir, childname)
                bridge.import_deleted_version_content(
                    self.session, self.repoeid, self.reveid, upath, self.date)

    def apply_textdelta(self, file_baton, base_checksum):
        #print 'apply_textdelta', file_baton, base_checksum
        pass
