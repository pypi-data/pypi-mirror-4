"""cubicweb vcs file source

view a version control system content as entities

:organization: Logilab
:copyright: 2007-2009 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

from warnings import warn

from cubicweb.server.sources import extlite

def get_vcs_source(repo):
    """return the vcs source of the repository (can only have one)"""
    warn('get_vcs_source is deprecated', DeprecationWarning, stacklevel=1)
    vcssources = [s for s in repo.sources if isinstance(s, VCSSource)]
    assert len(vcssources) == 1, "check your source configuration (hint: [vcs]\nadapter=vcsfile)"
    return vcssources[0]



class VCSSource(extlite.SQLiteAbstractSource):
    """VCS repository source"""

    def __init__(self, repo, appschema, source_config, *args, **kwargs):
        super(VCSSource, self).__init__(repo, appschema, source_config,
                                        *args, **kwargs)
        self.check_interval = int(source_config.get('check-revision-interval',
                                                    5*60))
        warn('vcssource is deprecated, remove it from your sources file',
             DeprecationWarning)
