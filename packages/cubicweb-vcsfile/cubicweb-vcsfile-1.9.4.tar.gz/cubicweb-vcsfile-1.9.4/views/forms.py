"""custom forms to submit new revision to the svn repository or to edit
some information about existing revisions.

:organization: Logilab
:copyright: 2007-2011 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"
_ = unicode

from copy import copy

from logilab.mtconverter import xml_escape
from logilab.common.decorators import cached

from cubicweb.selectors import (match_form_params, match_kwargs,
                                is_instance, specified_etype_implements,
                                match_edited_type)
from cubicweb.view import EntityView
from cubicweb.web import (Redirect, RequestError, controller, uicfg, form,
                          formfields as ff, formwidgets as fw)
from cubicweb.web.views import autoform, forms, editcontroller

from cubes.vcsfile import IMMUTABLE_ATTRIBUTES

_afs = uicfg.autoform_section
_aff = uicfg.autoform_field
_affk = uicfg.autoform_field_kwargs
_rctl = uicfg.reledit_ctrl
_pvdc = uicfg.primaryview_display_ctrl

for attr in ('path', 'subpath', 'type', 'source_url', 'encoding'):
    _pvdc.tag_attribute(('Repository', attr), {'vid': 'attribute'})
_rctl.tag_attribute(('Repository', 'title'), {'reload': True})
_affk.tag_attribute(('Repository', 'source_url'), {'widget': fw.TextInput})
_affk.tag_attribute(('Repository', 'path'), {'widget': fw.TextInput})
_affk.tag_attribute(('Repository', 'subpath'), {'widget': fw.TextInput})
_afs.tag_attribute(('Repository', 'local_cache'), 'main', 'hidden')

_afs.tag_attribute(('Revision', 'revision'), 'main', 'hidden')
_afs.tag_attribute(('Revision', 'changeset'), 'main', 'hidden')
_affk.tag_attribute(('Revision', 'author'),
                    {'value': lambda form, field: form._cw.user.login})
_afs.tag_subject_of(('Revision', 'parent_revision', 'Revision'), 'main', 'hidden')
_afs.tag_object_of(('Revision', 'parent_revision', 'Revision'), 'main', 'hidden')

_affk.tag_attribute(('VersionedFile', 'directory'), {'widget': fw.TextInput})
_affk.tag_attribute(('VersionedFile', 'name'), {'widget': fw.TextInput})
_afs.tag_object_of(('*', 'content_for', 'VersionedFile'), 'main', 'hidden')

_afs.tag_object_of(('*', 'from_revision', 'Revision'), 'main', 'inlined')

_afs.tag_subject_of(('*', 'content_for', 'VersionedFile'), 'main', 'hidden')
_aff.tag_attribute(('VersionContent', 'data'), ff.EditableFileField)


class RevisionCreationForm(autoform.AutomaticEntityForm):
    # vfeid needed for the inline-creation of VersionContent
    __select__ = specified_etype_implements('Revision') & match_form_params('vfeid')

    def should_display_inline_creation_form(self, rschema, existant, card):
        if rschema == 'from_revision':
            return True
        return super(RevisionCreationForm, self).should_display_inline_creation_form(
            rschema, existant, card)


class RevisionEditController(editcontroller.EditController):
    __select__ = editcontroller.EditController.__select__ & match_edited_type('Revision')

    def _insert_entity(self, etype, eid, rqlquery):
        try:
            repoeid = self.linked_to[('from_repository', 'subject')][0]
        except KeyError:
            raise RequestError('missing repository information')
        self._cw.set_shared_data('vcsrepoeid', repoeid, querydata=True)
        return super(RevisionEditController, self)._insert_entity(etype, eid, rqlquery)

class VCInlinedCreationFormView(autoform.InlineEntityCreationFormView):
    # vfeid needed for the inline-creation of VersionContent
    __select__ = (match_form_params('vfeid') & match_kwargs('peid', 'rtype')
                  & specified_etype_implements('VersionContent'))

    @cached
    def _entity(self):
        """creation view for an entity"""
        vf = self._cw.entity_from_eid(int(self._cw.form['vfeid']))
        self.orig_entity = vf.head
        # need a fully completed entity before doing the copy
        self.orig_entity.complete()
        if self.orig_entity.attr_metadata('data', 'format') in (
            'text/plain', 'text/html', 'text/rest'):
            # fill cache, Bytes fields are not loaded by complete()
            self.orig_entity.data
        entity = copy(self.orig_entity)
        self.initialize_varmaker()
        entity.eid = self.varmaker.next()
        return entity

    def add_hiddens(self, form, entity):
        super(VCInlinedCreationFormView, self).add_hiddens(
            form, entity)
        form.add_hidden('content_for', self.orig_entity.file.eid,
                        eidparam=True)


def filter_out_immutable_rels(func):
    def wrapper(self, *args, **kwargs):
        entity = self.edited_entity
        if entity.has_eid():
            immutable = IMMUTABLE_ATTRIBUTES
        else:
            immutable = ('Revision.revision',)
        for rschema, tschemas, role in func(self, *args, **kwargs):
            if role == 'subject':
                etype = entity.__regid__
            # take care, according to the wrapped function tschemas is a list or
            # a single schema
            elif isinstance(tschemas, list):
                etype = tschemas[0]
            else:
                etype = tschemas
            if '%s.%s' % (etype, rschema) in immutable:
                continue
            yield rschema, tschemas, role
    return wrapper


class VCRevisionEditionForm(autoform.AutomaticEntityForm):
    __select__ = is_instance('Revision', 'VersionedFile',
                            'VersionContent', 'DeletedVersionContent')
    _relations_by_section = filter_out_immutable_rels(
        autoform.AutomaticEntityForm._relations_by_section)


def available_branches(form, field):
    return form.edited_entity.repository.branches()


class NewRevisionForm(forms.EntityFieldsForm):
    __regid__ = 'vfnewrevform'
    __select__ = is_instance('VersionedFile')

    form_renderer_id = 'base'
    form_buttons = [fw.SubmitButton()]

    file = ff.FileField(eidparam=True)
    branch = ff.StringField(required=True, eidparam=True,
                            widget=fw.Select, choices=available_branches,
                            value=lambda form:form.edited_entity.repository.default_branch())
    msg = ff.StringField(label=_('commit message'), eidparam=True)


class VFUploadFormView(form.FormViewMixIn, EntityView):
    """form to upload a new revision of a versioned file"""
    __regid__ = 'vfnewrevform'
    __select__ = is_instance('VersionedFile')

    submitmsg = _('new revision has been checked-in')

    @property
    def action(self):
        return self._cw.build_url('vcsnewrev')

    def call(self, **_kwargs):
        # XXX explain why we would want self.rset.rowcount != 1
        for i in xrange(self.cw_rset.rowcount):
            self.cell_call(i, 0)

    def form_title(self, entity):
        return self._cw._('Upload a new revision of %s') % (
            '<a href="%s">%s</a>' % (xml_escape(entity.absolute_url()),
                                     xml_escape(entity.dc_title())))

    def cell_call(self, row, col, **kwargs):
        entity = self.cw_rset.get_entity(row, col)
        self.w(u'<div class="iformTitle">')
        self.w(self.form_title(entity))
        self.w(u'</div>')
        self.get_form(entity).render(w=self.w)

    def get_form(self, entity):
        return self._cw.vreg['forms'].select(
            'vfnewrevform', self._cw, entity=entity,
            submitmsg=self._cw._(self.submitmsg), action=self.action,
            __redirectpath=entity.rest_path(),)


class VFUploadController(controller.Controller):
    """upload a new revision of an already existing document"""
    __regid__ = 'vcsnewrev'

    def publish(self, rset=None):
        for eid in self._cw.edited_eids():
            formparams = self._cw.extract_entity_params(eid, minparams=2)
            vf = self._cw.entity_from_eid(eid)
            vf.complete()
            self.upload_revision(vf, formparams)
        try:
            kwargs = {'__message': self._cw.form['__message']}
        except KeyError:
            kwargs = {}
        try:
            goto = self._cw.build_url(self._cw.form['__redirectpath'], **kwargs)
        except KeyError:
            goto = vf.absolute_url(**kwargs)
        raise Redirect(goto)

    def upload_revision(self, vf, formparams):
        # [-1] to discard file name and mime type
        stream = formparams['file'][-1]
        vf.vcs_upload_revision(stream, branch=formparams['branch'],
                               msg=formparams['msg'])
        return vf.eid


class VcsRmForm(form.FormViewMixIn, EntityView):
    __regid__ = 'vcsrmform'
    __select__ = is_instance('VersionedFile')

    def cell_call(self, row, col):
        entity = self.cw_rset.get_entity(row, col)
        self.w(u'<div class="iformTitle">')
        self.w(self._cw._('DELETE the versioned file %(file)s') %
                    {'file': entity.view('incontext')})
        self.w(u'</div>')
        # XXX branch
        form = self._cw.vreg['forms'].select('base', self._cw, rset=self.cw_rset,
                                             form_renderer_id='base', entity=entity,
                                             action=self._cw.build_url('vcsrm'),
                                             form_buttons=[fw.SubmitButton()])
        form.append_field(ff.StringField(name='msg', eidparam=True,
                                         value=u'',
                                         label=_('commit message')))
        form.render(w=self.w)


class VcsRmController(controller.Controller):
    """DELETE"""
    __regid__ = 'vcsrm'

    def publish(self, rset=None):
        req = self._cw
        for eid in req.edited_eids():
            formparams = req.extract_entity_params(eid, minparams=2)
            vf = self._cw.entity_from_eid(eid)
            vf.vcs_rm(msg=formparams['msg'])
        msg = req._('file was marked DELETED')
        raise Redirect(vf.absolute_url(__message=msg))
