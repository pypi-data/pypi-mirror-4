"""some facets to filter vcsfile entities

:organization: Logilab
:copyright: 2008-2011 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
:license: General Public License version 2 - http://www.gnu.org/licenses
"""
__docformat__ = "restructuredtext en"

from cubicweb.selectors import is_instance
from cubicweb.web import facet

class RepositoryTypeFacet(facet.AttributeFacet):
    __regid__ = 'vcsfile.repo.type'
    __select__ = facet.AttributeFacet.__select__ & is_instance('Repository')
    rtype = 'type'

class RevisionBranchFacet(facet.AttributeFacet):
    __regid__ = 'vcsfile.rev.branch'
    __select__ = facet.AttributeFacet.__select__ & is_instance('Revision')
    rtype = 'branch'
    i18nable = False

class RevisionCreationDateFacet(facet.DateRangeFacet):
    __regid__ = 'vcsfile.rev.cd'
    __select__ = facet.DateRangeFacet.__select__ & is_instance('Revision')
    rtype = 'creation_date'
    order = 4

class VFModificationDateFacet(facet.DateRangeFacet):
    __regid__ = 'vcsfile.vf.cd'
    __select__ = facet.DateRangeFacet.__select__ & is_instance('VersionedFile')
    rtype = 'modification_date'
    order = 4
