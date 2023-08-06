"template automatic tests"
import os.path as osp
from cubicweb.devtools import testlib

class AutomaticWebTest(testlib.AutomaticWebTest):
    no_auto_populate = ('Repository', 'Revision', 'VersionedFile',
                        'VersionContent', 'DeletedVersionContent',)
    ignored_relations = set(('at_revision', 'parent_revision',
                             'from_repository', 'from_revision', 'content_for',))

    def custom_populate(self, how_many, cursor):
        req = self.request()
        req.create_entity('Repository', type=u'mercurial',
                          path=unicode(osp.join(self.datadir, 'testrepohg')),
                          encoding=u'latin1')

if __name__ == '__main__':
    from logilab.common.testlib import unittest_main
    unittest_main()
