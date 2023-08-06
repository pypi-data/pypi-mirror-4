"""primary views for entity types defined by the vcsfile package

:organization: Logilab
:copyright: 2007-2011 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"
_ = unicode

from logilab.mtconverter import TransformError, xml_escape

from cubicweb import Unauthorized, tags
from cubicweb.mttransforms import ENGINE
from cubicweb.predicates import is_instance, score_entity
from cubicweb.view import EntityView
from cubicweb.web import uicfg
from cubicweb.web.views import (ibreadcrumbs, idownloadable, tableview,
                                baseviews, primary, tabs, navigation)

# primary view tweaks
_pvs = uicfg.primaryview_section
_pvdc = uicfg.primaryview_display_ctrl
_abaa = uicfg.actionbox_appearsin_addmenu

# internal purpose relation
_pvs.tag_subject_of(('*', 'at_revision', '*'), 'hidden')
_pvs.tag_object_of(('*', 'at_revision', '*'), 'hidden')
_pvs.tag_attribute(('Repository', 'local_cache'), 'hidden')
_pvs.tag_attribute(('Repository', 'source_url'), 'hidden') # custom view
_pvs.tag_object_of(('*', 'from_repository', 'Repository'), 'hidden')

_pvs.tag_attribute(('VersionedFile', 'name'), 'hidden') # in title
_pvs.tag_attribute(('VersionedFile', 'directory'), 'hidden') # in title
_pvs.tag_subject_of(('VersionedFile', 'from_repository', '*'), 'hidden') # in breadcrumb
_pvs.tag_object_of(('*', 'content_for', 'VersionedFile'), 'hidden') # in render_entity_relations

_pvs.tag_subject_of(('Revision', 'parent_revision', 'Revision'), 'attributes')
_pvs.tag_object_of(('Revision', 'parent_revision', 'Revision'), 'attributes')
_pvs.tag_subject_of(('Revision', 'from_repository', '*'), 'hidden') # in breadcrumb
_pvs.tag_object_of(('*', 'from_revision', '*'), 'hidden')

for etype in ('DeletedVersionContent', 'VersionContent'):
    _pvs.tag_subject_of((etype, 'content_for', '*'), 'hidden') # in title
    _pvs.tag_subject_of((etype, 'from_revision', '*'), 'hidden') # in breadcrumb

_pvdc.tag_subject_of(('*', 'from_revision', '*'), {'vid': 'incontext'})
_pvdc.tag_subject_of(('*', 'from_repository', '*'), {'vid': 'incontext'})
_pvdc.tag_subject_of(('*', 'content_for', '*'), {'vid': 'incontext'})

_pvdc.tag_attribute(('Repository', 'source_url'), {'vid': 'urlattr'})

# we don't want automatic addrelated action for the following relations...
for rtype in ('from_repository', 'from_revision', 'content_for',
              'parent_revision'):
    _abaa.tag_object_of(('*', rtype, '*'), False)


def render_entity_summary(self, entity):
    if not entity.is_head(entity.rev.branch):
        msg = self._cw._('this file has newer revisions')
        self.w(tags.div(msg, klass='warning'))
    if entity.description:
        self.field(self._cw._('commit message:'), xml_escape(entity.description),
                   tr=False, table=False)


class RepositoryPrimaryView(tabs.TabbedPrimaryView):
    __select__ = is_instance('Repository')

    tabs = [_('repositoryinfo_tab'), _('repositoryfiles_tab'), _('repositoryhistory_tab')]
    default_tab = 'repositoryinfo_tab'


class RepositoryInfoTab(tabs.PrimaryTab):
    __regid__ = 'repositoryinfo_tab'
    __select__ = is_instance('Repository')

    def render_entity_attributes(self, entity):
        super(RepositoryInfoTab, self).render_entity_attributes(entity)
        if entity.source_url:
            entity.view('vcsfile.repository.checkout', w=self.w)
        rset = self._cw.execute('Any REV, REVB, REVN ORDERBY REVN DESC '
                                'WHERE REV branch REVB, REV revision REVN, REV from_repository R, '
                                'R eid %(r)s, NOT X parent_revision REV',
                                {'r': entity.eid})
        if rset:
            self.w('<h3>%s</h3>' % self._cw._('heads'))
            self.wview('table', rset)


class RepositoryFilesTab(EntityView):
    __regid__ = 'repositoryfiles_tab'
    __select__ = is_instance('Repository') & score_entity(lambda x: x.import_revision_content)
    def cell_call(self, row, col):
        entity = self.cw_rset.get_entity(row, col)
        rset = self._cw.execute(
            'Any VF,VFMD, VFD,VFN ORDERBY VFD,VFN WHERE '
            'VF modification_date VFMD, VF directory VFD, VF name VFN,'
            'VF from_repository X, X eid %(x)s',
            {'x': entity.eid})
        self.wview('vcsfile.table.files', rset, 'noresult')

class VersionedFilesTable(tableview.RsetTableView):
    __regid__ = 'vcsfile.table.files'
    __select__ = is_instance('VersionedFile')
    displaycols = [0, 1]
    cellvids = {0: 'incontext'}
    layout_args = {'display_filter': 'top'}


class RepositoryHistoryTab(EntityView):
    __regid__ = 'repositoryhistory_tab'
    __select__ = is_instance('Repository')

    def cell_call(self, row, col):
        entity = self.cw_rset.get_entity(row, col)
        rset = self._cw.execute(
            'Any R,RB,RA,RD,RCD, RN,RCS ORDERBY RN DESC WHERE '
            'R branch RB, R author RA, R description RD, R creation_date RCD,'
            'R revision RN, R changeset RCS, R from_repository X, X eid %(x)s',
            {'x': entity.eid})
        self.wview('vcsfile.table.revisions', rset, 'noresult')

class RevisionsTable(tableview.RsetTableView):
    __regid__ = 'vcsfile.table.revisions'
    __select__ = is_instance('Revision')
    displaycols = range(5)
    layout_args = {'display_filter': 'top'}


class RepositoryCheckOutInstructionsView(EntityView):
    __regid__ = 'vcsfile.repository.checkout'
    __select__ = is_instance('Repository') & score_entity(lambda x: x.source_url)

    def entity_call(self, entity):
        w = self.w
        _ = self._cw._
        url_scheme = entity.source_url.split(':')[0]
        if url_scheme.startswith('http'):
            w(u'<h3>%s</h3>' % _('Browse source'))
            w(u'<p>%s</p>' % _('You can browse the source code by following <a href="%s">this link</a>.')
              % xml_escape(entity.source_url))
        w(u'<h3>%s</h3>' % _('Command-Line Access'))
        if entity.has_anonymous_access:
            msg = _('Non-members may check out a read-only working copy anonymously over %s.') % xml_escape(url_scheme.upper())
        else:
            msg = _('Members only may check out working copy over %s.') % xml_escape(url_scheme.upper())
        w(u'<p>%s</p>' % msg)
        w(u'<p>%s</p>' % _('Use this command to check out the latest project source code:'))
        w(u'<pre>')
        if entity.type == 'mercurial':
            w(u'hg clone %s' % xml_escape(entity.source_url))
        else: # svn
            w(u'svn checkout %s' % xml_escape(entity.source_url))
        w(u'</pre>')


class DVCPrimaryView(primary.PrimaryView):
    __select__ = is_instance('DeletedVersionContent')

    def render_entity_title(self, entity):
        title = self._cw._('Revision %(revision)s of %(file)s: DELETED') % {
            'revision': entity.revision, 'file': entity.file.view('oneline')}
        self.w('<h1>%s</h1>' % title)
        render_entity_summary(self, entity)


class VCPrimaryView(idownloadable.IDownloadablePrimaryView):
    __select__ = is_instance('VersionContent')

    def render_entity_title(self, entity):
        title = self._cw._('Revision %(revision)s of %(file)s') % {
            'revision': entity.revision, 'file': entity.file.view('oneline')}
        self.w('<h1>%s</h1>' % title)
        render_entity_summary(self, entity)

    def render_data(self, entity, sourcemt, targetmt):
        if entity.data:
            return super(VCPrimaryView, self).render_data(entity, sourcemt, targetmt)
        elif targetmt == 'text/html':
            msg = self._cw._('File content is not accessible.  '
                    'This may mean that the VCS repository is not accessible from the '
                    'web frontend, or that it is no yet updated.')
            self.w(u'<div class="error">%s</div>' % msg)
            return True
        return False


class VCMetaDataView(baseviews.MetaDataView):
    """paragraph view of some metadata"""
    __select__ = is_instance('VersionContent', 'DeletedVersionContent')

    def cell_call(self, row, col):
        _ = self._cw._
        entity = self.cw_rset.get_entity(row, col)
        self.w(u'<div class="metadata">')
        self.w(u'#%s - ' % entity.eid)
        self.w(u'<span>%s</span> ' % _('revision %s of') % entity.revision)
        self.w(u'<span class="value">%s</span>,&nbsp;'
               % xml_escape(entity.file.path))
        self.w(u'<span>%s</span> ' % _('created on'))
        self.w(u'<span class="value">%s</span>'
               % entity.rev.printable_value('creation_date'))
        if entity.author:
            self.w(u'&nbsp;<span>%s</span> ' % _('by'))
            self.w(tags.span(entity.author, klass='value'))
        self.w(u'</div>')

class VCRevisionView(EntityView):
    __regid__ = 'revision'
    __select__ = is_instance('VersionContent', 'DeletedVersionContent')

    def cell_call(self, row, col):
        vc = self.cw_rset.get_entity(row, col)
        self.w(u'<a href="%s">' % vc.absolute_url())
        vc.rev.view('shorttext', w=self.w)
        self.w(u'</a>')

class RevisionShortView(EntityView):
    __regid__ = 'shorttext'
    __select__ = is_instance('Revision')
    content_type = 'text/plain'

    def cell_call(self, row, col):
        rev = self.cw_rset.get_entity(row, col)
        if rev.changeset:
            self.w(u'#%s:%s' % (rev.revision, rev.changeset))
        else:
            self.w(u'#%s' % rev.revision)


class VFPrimaryView(primary.PrimaryView):
    __select__ = is_instance('VersionedFile')

    def render_entity_attributes(self, entity):
        super(VFPrimaryView, self).render_entity_attributes(entity)
        self.w(u'<div class="content">')
        _ = self._cw._
        head = entity.head
        if head is None:
            self.w(_('versioned file without revision, needs check'))
        elif head.is_deletion():
            self.w(_('this file head is currently a deletion'))
        else:
            contenttype = head.cw_adapt_to('IDownloadable').download_content_type()
            self.field('head', head.rev.view('incontext'))
            if contenttype.startswith('image/'):
                self.wview('image', head.cw_rset, row=head.cw_row)
            else:
                try:
                    if ENGINE.has_input(contenttype):
                        self.w(head.printable_value('data'))
                except TransformError:
                    pass
                except Exception, ex:
                    msg = self._cw.__("can't display data, unexpected error: %s") % ex
                    self.w('<div class="error">%s</div>' % xml_escape(msg))
        self.w(u'</div>')

    def render_entity_relations(self, entity):
        super(VFPrimaryView, self).render_entity_relations(entity)
        self.w(u'<h3>%s</h3>' % self._cw._('Revisions for this file'))
        rset = self._cw.execute(
            'Any VC,RB,RA,RD,RC, R ORDERBY R DESC WHERE '
            'VC content_for VF, VC from_revision R, '
            'R branch RB, R author RA, R description RD, R creation_date RC,'
            'VF eid %(x)s',
            {'x': entity.eid})
        self.wview('vcsfile.table.revisions', rset, 'noresult')


class VersionedFileRevisionsTable(RevisionsTable):
    __select__ = is_instance('DeletedVersionContent', 'VersionContent')
    cellvids = {0: 'revision'}


class RevisionPrimaryView(primary.PrimaryView):
    __select__ = is_instance('Revision')

    def render_entity_relations(self, rev):
        versioned = rev.reverse_from_revision
        if versioned:
            self.w(u'<table class="listing">')
            self.w(u'<tr><th>%s</th></tr>' %
                   self._cw._('files modified by this revision'))
            for obj in versioned:
                self.w(u'<tr><td><a href="%s">%s</a></td></tr>' % (
                    obj.absolute_url(), xml_escape(obj.dc_title())))
            self.w(u'</table>')
        else:
            self.w(u'<p>%s</p>' % self._cw._('this revision hasn\'t modified any files'))


# navigation: breadcrumbs / prevnext adapters ##################################

class RepoContentIBreadCrumbsAdapter(ibreadcrumbs.IBreadCrumbsAdapter):
    __select__ = is_instance('Revision', 'VersionedFile')

    def parent_entity(self):
        try:
            return self.entity.repository
        except Unauthorized:
            return None


class DVCIBreadCrumbsAdapter(ibreadcrumbs.IBreadCrumbsAdapter):
    __select__ = is_instance('VersionContent', 'DeletedVersionContent')

    def parent_entity(self):
        return self.entity.rev


class RevisionIPrevNextAdapter(navigation.IPrevNextAdapter):
    __select__ = is_instance('Revision')

    def previous_entity(self):
        # may have multiple parents, give priority to the one in the same
        # branch.
        parent = None
        for parent in self.entity.parent_revision:
            if parent.branch == self.entity.branch:
                return parent
        return parent

    def next_entity(self):
        # may have multiple children, give priority to the one in the same
        # branch.
        child = None
        for child in self.entity.reverse_parent_revision:
            if child.branch == self.entity.branch:
                return child
        return child


class DVCIPrevNextAdapter(navigation.IPrevNextAdapter):
    __select__ = is_instance('VersionContent', 'DeletedVersionContent')

    def previous_entity(self):
        pver = self.entity.previous_versions()
        return pver and pver[0] or None

    def next_entity(self):
        nver = self.entity.next_versions()
        return nver and nver[0] or None

