"""cubicweb-ctl plugin providing the vcscheck command

:organization: Logilab
:copyright: 2011 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

import logging

from cubicweb import typed_eid
from cubicweb.cwctl import CWCTL
from cubicweb.toolsutils import Command

from cubes.vcsfile import bridge, hooks

class VCSCheckCommand(Command):
    """Check imported content of vcs repository against the actual repository.

    <instance id>
      identifier of the instance where directory's content has to be imported.

    <fs directory>
      directory to import (recursivly)
    """
    name = 'vcscheck'
    min_args = 1
    arguments = '<instance id> [repository eids...]'
    options = (
        ("start-at-revision",
         {'short': 's', 'type' : 'int',
          'default': 0,
          'help': 'start to check at the given revision',
          }),
        ('strip',
         {'short': 'S', 'action' : 'store_true',
          'help': 'strip unknown revisions (must start at revision 0)',
          }),
        ('import-new',
         {'short': 'I', 'action' : 'store_true',
          'help': 'import new revisions',
          }),
        )

    def run(self, args):
        """run the command with its specific arguments"""
        from cubicweb.server.serverconfig import ServerConfiguration
        from cubicweb.server.serverctl import repo_cnx
        appid = args.pop(0)
        config = ServerConfiguration.config_for(appid, debugmode=True)
        config.__class__.cube_appobject_path = set(('hooks', 'entities'))
        config.__class__.cubicweb_appobject_path = set(('hooks', 'entities'))
        config.repairing = True # don't check versions
        logging.getLogger('cubicweb').setLevel(logging.ERROR)
        logging.getLogger('cubicweb.sources').setLevel(logging.INFO)
        repo, cnx = repo_cnx(config)
        repo.hm.call_hooks('server_maintenance', repo=repo)
        session = repo.internal_session()
        if not args:
            args = [x for x, in session.execute('Repository X WHERE X cw_source S, S name "system"')]
        else:
            args = [typed_eid(x) for x in args]
        for eid in args:
            session.set_cnxset()
            vcsrepo = session.entity_from_eid(eid)
            assert vcsrepo.__regid__ == 'Repository', 'bad eid %s' % eid
            try:
                repohdlr = bridge.repository_handler(vcsrepo)
            except bridge.VCSException, ex:
                repo.error(str(ex))
                continue
            print 'CHECK REPOSITORY', vcsrepo.dc_title()
            repohdlr.check(vcsrepo, self.config.start_at_revision,
                           strip=self.config.strip,
                           import_new=self.config.import_new)

CWCTL.register(VCSCheckCommand)
