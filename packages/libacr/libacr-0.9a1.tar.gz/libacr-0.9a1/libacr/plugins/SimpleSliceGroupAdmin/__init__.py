from tg import expose, flash, require, request, redirect, tmpl_context, TGController, config, validate, url
from tg.controllers import WSGIAppController
import libacr

from webob.exc import HTTPFound
from libacr.views.manager import ViewsManager
from libacr.views.base import EncodedView
from libacr.model.core import DBSession
from libacr.lib import url as acr_url, known_languages
from libacr.controllers.admin.base import BaseAdminController
from libacr.plugins.base import AdminEntry, AcrPlugin, plugin_expose
from libacr.model.content import Tag, Page, Slice, Content, ContentData
from libacr.controllers.admin.base import _create_node
from tg import predicates
from tw.api import WidgetsList
import tw.forms as twf
from formencode import validators
from datetime import datetime
from sqlalchemy import join, desc

def fetch_public_tags():
    return (p.name for p in DBSession.query(Tag).filter_by(group=None))

class AddUploadableContentForm(WidgetsList):
    document = twf.FileField(label_text="File:", validator=validators.FieldStorageUploadConverter(not_empty=True))
    filter_tag = twf.HiddenField()
    path = twf.HiddenField()
    tags = twf.MultipleSelectField(label_text='Tags:', options=fetch_public_tags)

class AddSimpleContentForm(WidgetsList):
    filter_tag = twf.HiddenField()
    tags = twf.MultipleSelectField(label_text='Tags:', options=fetch_public_tags)

class EditContentForm(WidgetsList):
    filter_tag = twf.HiddenField()
    uid = twf.HiddenField()
    slice_uid = twf.HiddenField()
    lang = twf.HiddenField()
    revision = twf.HiddenField()

class SimpleSliceGroupAdminController(BaseAdminController):
    @plugin_expose('add')
    @require(predicates.in_any_group('acr', 'acr_editors'))
    def add(self, *args, **kw):
        view = kw['view']
        filter_tag = kw['filter_tag']

        if view in (v.name for v in ViewsManager.rdisk_views):
            BaseForm = AddUploadableContentForm
            form_action = libacr.lib.url('/plugins/sgadmin/upload')
        else:
            BaseForm = AddSimpleContentForm
            form_action = libacr.lib.url('/plugins/sgadmin/save')

        kw['path'] = '/' + filter_tag + '_' + view
        return dict(view=view, filter_tag=filter_tag, values=kw,
                    form=ViewsManager.create_form(view, BaseForm),
                    form_action=form_action)

    @expose('libacr.templates.admin.content_edit')
    @require(predicates.in_any_group('acr', 'acr_editors'))
    def edit(self, slice_uid, translation=None, **kw):
        slice = DBSession.query(Slice).get(slice_uid)
        if not translation:
            cdata = slice.content.data_instance
        else:
            cdata = slice.content.get_data_instance_for_lang([translation])
        translate_box = twf.SingleSelectField('translate', label_text="Translate",
                                              options=known_languages, default='en')

        edit_form = ViewsManager.create_form(slice.view, EditContentForm)
        values = {}
        values['uid'] = slice.content.uid
        values['lang'] = cdata.lang
        if translation:
            values['lang'] = translation
        values['slice_uid'] = slice.uid
        values['revision'] = cdata.revision
        values['filter_tag'] = kw.get('filter_tag', slice.tags[0].name)
        values.update(ViewsManager.decode(slice.view, cdata.value))

        return dict(slice=slice, translate_box=translate_box,
                    edit_form=edit_form, values=values, revision=cdata.revision,
                    action=libacr.lib.url('/plugins/sgadmin/update_content'),
                    translate_url='/plugins/sgadmin/edit')

    @expose()
    @validate(ViewsManager.validator(EditContentForm), error_handler=edit)
    @require(predicates.in_any_group('acr', 'acr_editors'))
    def update_content(self, **kw):
        slice = DBSession.query(Slice).get(kw['slice_uid'])

        last_revision = slice.content.last_revision_for_lang([kw['lang']])
        cd = ContentData(content=slice.content, lang=kw['lang'],
                        value=ViewsManager.encode(kw['view'], kw),
                        revision=last_revision + 1)
        DBSession.add(cd)

        flash('Content Updated')
        return redirect(acr_url('/plugins/sgadmin/manage', filter_tag=kw['filter_tag'], view=kw['view']))

    @plugin_expose('manage')
    @require(predicates.in_any_group('acr', 'acr_editors'))
    def manage(self, view, filter_tag, *args, **kw):
        slices = DBSession.query(Slice).join(Content).\
                           filter(Slice.tags.any(name=filter_tag)).\
                           order_by(desc(Slice.uid))

        view_instance = ViewsManager.find_view(view)
        return dict(view=view, filter_tag=filter_tag,
                    slices=slices, view_instance=view_instance)

    @expose()
    @validate(ViewsManager.validator(AddSimpleContentForm), error_handler=add)
    @require(predicates.in_any_group('acr', 'acr_editors'))
    def save(self, *args, **kw):
        slice_data = {}
        slice_data['name'] = kw['filter_tag'] + '_' + datetime.now().strftime('%y%m%d%H%M%S')
        slice_data['page'] = None
        slice_data['zone'] = 'main'
        slice_data['order'] = 0
        slice_data['tags'] = [kw['filter_tag']] + kw.get('tags', [])
        slice_data['view'] = kw['view']
        slice_data['data'] = ViewsManager.encode(kw['view'], kw)
        slice_data['skip_permission'] = True
        _create_node(**slice_data)

        flash('Content correctly created')
        return redirect(acr_url('/plugins/sgadmin/manage', filter_tag=kw['filter_tag'], view=kw['view']))

    @expose()
    @validate(ViewsManager.validator(AddUploadableContentForm), error_handler=add)
    @require(predicates.in_any_group('acr', 'acr_editors'))
    def upload(self, *args, **kw):
        from libacr.controllers.rdisk import RDiskController
        rd = RDiskController()
        try:
            real_groups = request.environ['repoze.what.credentials']['groups'] 
            request.environ['repoze.what.credentials']['groups'] = real_groups + ('acr',)
            rd.add_res(kw.pop('document'), kw.pop('path'), kw.pop('view'), None, [kw['filter_tag']] + kw.get('tags', []), **kw)
            request.environ['repoze.what.credentials']['groups'] = real_groups
        except HTTPFound:
            pass

        return redirect(acr_url('/plugins/sgadmin/manage', filter_tag=kw['filter_tag'], view=kw['view']))

    @expose()
    @require(predicates.in_any_group('acr', 'acr_editors'))
    def drop(self, slice_uid, *args, **kw):
        slice = DBSession.query(Slice).get(slice_uid)
        kw['view'] = slice.view
        DBSession.delete(slice)
        flash('Content removed')
        return redirect(acr_url('/plugins/sgadmin/manage', filter_tag=kw['filter_tag'], view=kw['view']))


class SliceGroupAdminRenderer(EncodedView):

    def __init__(self):
        self.name = 'slicegroup_admin'
        self.form_fields = [twf.SingleSelectField('filter_tag', label_text="Filter Tag:",
                                                        validator=twf.validators.String(not_empty=True, strip=True),
                                                        options=lambda : (p.name for p in DBSession.query(Tag))),
                            twf.SingleSelectField('view_type', label_text="Members View:", default='html',
                                                        validator=twf.validators.String(not_empty=True, strip=True),
                                                        options=lambda : ViewsManager.view_names())]
        self.exposed = True

    def preview(self, page, slice, data):
        return 'Preview not Implemented'

    def render(self, page, slice, data):
        from libacr.plugins.manager import PluginsManager

        data = self.to_dict(data)
        data['add_url'] = url(PluginsManager['sgadmin'].plugin_url('add'),
                              params=dict(view=data['view_type'],
                                          filter_tag=data['filter_tag']))
        data['manage_url'] = url(PluginsManager['sgadmin'].plugin_url('manage'),
                              params=dict(view=data['view_type'],
                                          filter_tag=data['filter_tag']))

        if request.identity:
            result = '''
<div class="acr_group_admin_%(filter_tag)s">
    <a href="%(add_url)s" target="_blank">Add</a>
    <a href="%(manage_url)s" target="_blank">Manage</a>
</div>
''' % data
        else:
            result = ''

        return result

class SliceGroupAdminPlugin(AcrPlugin):
    uri = 'sgadmin'

    def __init__(self):
        self.controller = SimpleSliceGroupAdminController()
        ViewsManager.register_view(SliceGroupAdminRenderer())
