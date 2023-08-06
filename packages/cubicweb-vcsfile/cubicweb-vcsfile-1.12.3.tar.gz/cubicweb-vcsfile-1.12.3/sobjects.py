from mercurial import cmdutil
from mercurial import patch
from mercurial import ui as uimod

from cubicweb import Binary
from cubicweb.server import Service

from . import bridge


class RevisionExportService(Service):
    """return the patch version of a revision
    """

    __regid__ = 'vcs.export-rev'

    def call(self, repo, nodeid):
        repo = self._cw.entity_from_eid(repo)
        if repo.type != 'mercurial':
            # no svn support yet (use a selector when we have multiple versions)
            return None
        ui = uimod.ui()
        diffopts = patch.diffopts(ui, {'git': True,
                                       'showfunc': True,
                                       'unified': 5,
                                       })
        hdrepo = bridge.repository_handler(repo)
        hgrepo = hdrepo.hgrepo()
        if nodeid not in hgrepo:
            # local cache miss
            return None
        revs = [nodeid]
        output = Binary()
        cmdutil.export(hgrepo, revs, fp=output, opts=diffopts)
        return output.getvalue()
