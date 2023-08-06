"""repository abstraction for supported repositories

:organization: Logilab
:copyright: 2007-2010 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"
_ = unicode

from os.path import exists, split, join
from logging import getLogger

from cubicweb import set_log_methods

from cubes.vcsfile import bridge

class VCSRepository(object):
    type = None # to set in concret classes

    def __init__(self, eid, path, encoding):
        # eid of the associate Repository entity
        self.eid = eid
        if not path:
            msg = _('bad repository path: %s')
            raise bridge.VCSException(eid, 'path', msg, path)
        if not encoding:
            msg = _('bad repository encoding: %s')
            raise bridge.VCSException(eid, 'encoding', msg, encoding)
        # encoding of files, messages... Normalize for later comparison
        self.encoding = encoding.lower()
        # path to the repository
        if isinstance(path, unicode):
            fspath = path.encode(encoding)
        else:
            fspath = path
        try:
            fspath = self.canonicalize(fspath)
        except Exception:
            self.exception('invalid repository')
            msg = _('%(repopath)s is not a valid %(repotype)s repository')
            raise bridge.VCSException(eid, 'path', msg, {'repopath': path,
                                                         'repotype': self.type})
        self.path = fspath
        self.vf_path_cache = {}

    def __str__(self):
        return '%s:%s' % (self.type, self.path)

    def encode(self, ustring):
        if ustring:
            return ustring.encode(self.encoding)
        return ''

    def decode(self, string):
        if string:
            return string.decode(self.encoding)
        return u''

    def canonicalize(self, path):
        return path

    def import_content(self, repoentity, commitevery=10):
        """import content from the repository"""
        raise NotImplementedError()

    def vf_eid(self, session, path, date):
        """get versioned file eid for the given path, inserting it if necessary
        """
        try:
            return self.vf_path_cache[path]
        except KeyError:
            directory, fname = split(path)
            rset = session.execute(
                'Any X WHERE X directory %(dir)s, X name %(name)s, '
                'X from_repository R, R eid %(r)s',
                {'dir': directory, 'name': fname, 'r': self.eid})
            if rset:
                eid = rset[0][0]
            else:
                eid = bridge.import_versioned_file(session, self.eid, date,
                                                   directory, fname)
            self.vf_path_cache[path] = eid
            return eid

    def file_content(self, directory, fname, rev):
        """extract a binary string with the content of the file at `directory` /
        `fname` for revision `rev` in the repository
        """
        if isinstance(fname, unicode):
            fname = self.encode(fname)
        if directory is not None:
            if isinstance(directory, unicode):
                directory = self.encode(directory)
            path = join(directory, fname)
        else:
            path = fname
        return self._file_content(path, rev)

    def _file_content(self, path, rev):
        raise NotImplementedError()

    def revision_transaction(self, session, entity):
        """open a transaction to create a new revision corresponding to the
        given entity
        """
        raise NotImplementedError()

    def add_versioned_file_content(self, session, transaction, vf, entity,
                                   data):
        """add a new revision of a versioned file"""
        raise NotImplementedError()

    def add_versioned_file_deleted_content(self, session, transaction, vf,
                                           entity):
        """add a new revision of a just deleted versioned file"""
        raise NotImplementedError()

set_log_methods(VCSRepository, getLogger('cubicweb.vcs'))
