"""app objects for vcsfile web interface

:organization: Logilab
:copyright: 2007-2012 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""

__docformat__ = "restructuredtext en"


from cubicweb import typed_eid
from cubicweb.selectors import match_form_params
from cubicweb.web import Redirect, RequestError
from cubicweb.web.controller import Controller


class RefreshLocalRepoCachesController(Controller):
    """Control used to refresh the local cache of a single vcs repository given
    its eid in the web request form"""
    __regid__ = 'refresh_repository'
    __select__ = Controller.__select__ & match_form_params('eid')

    def publish(self, rset=None):
        eid = typed_eid(self._cw.form['eid'])
        vcsrepo = self._cw.entity_from_eid(eid)
        if vcsrepo.e_schema.type != 'Repository':
            raise RequestError('a repository is expected')
        # async=False so that users see changes immediately, if any
        self._cw.cnx.call_service('refresh_repository', async=False,
                                  eids=(vcsrepo.eid,))
        raise Redirect(vcsrepo.absolute_url())
