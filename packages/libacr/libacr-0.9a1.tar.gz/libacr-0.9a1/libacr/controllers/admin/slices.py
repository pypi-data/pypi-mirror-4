from tg import expose, flash, require, url, request, redirect, tmpl_context, validate
from pylons.i18n import ugettext as _, lazy_ugettext as l_
from pylons.controllers.util import abort
from tg import predicates
from sqlalchemy import not_

from libacr import acr_zones, forms
from libacr.lib import url, current_user_id, language, icons, user_can_modify, odict, known_languages
from libacr.model.core import DBSession
from libacr.model.content import Tag, Page, Slice, Content, ContentData
from libacr.model.attributes import Attribute

from tw.api import WidgetsList
import tw.forms as widgets
from formencode import validators
from libacr.views.manager import ViewsManager
from libacr.forms import order_values

from datetime import datetime
from base import BaseAdminController, _create_node
from libacr.model.user_permission import AcrUserPermission

__all__ = ['SlicesAdminController']

clone_slice_form = forms.CloneSliceForm(DBSession)
edit_slice_form = forms.EditSliceForm(DBSession)

class EditContentForm(WidgetsList):
    uid = widgets.HiddenField()
    slice_uid = widgets.HiddenField()
    lang = widgets.HiddenField()
    revision = widgets.HiddenField()

class CreateContentForm(WidgetsList):
    page = widgets.HiddenField()
    name = widgets.TextField(label_text="Name:", validator=validators.NotEmpty())
    zone = widgets.SingleSelectField(label_text="Zone:", options=zip(acr_zones, acr_zones))
    tags = widgets.MultipleSelectField(label_text='Tags:', options=lambda : (p.name for p in DBSession.query(Tag).filter(not_(Tag.name.like('_depo_%')))))
    lang = widgets.SingleSelectField(label_text="Language", options=known_languages, default='en')

class SlicesAdminController(BaseAdminController):
    @expose('libacr.templates.admin.slice_edit')
    @require(predicates.in_group("acr"))
    def edit(self, **kw):
        slice = DBSession.query(Slice).get(kw['uid'])
        prop_values = {'uid':slice.uid, 'name':slice.name, 'zone':slice.zone,
                       'page':slice.page and slice.page.uid,
                       'tags':[tag.uid for tag in slice.tags],
                       'attributes':[dict(name=attr.name, value=attr.value) for attr in slice.attributes]}

        return dict(slice=slice, section_title="Slice Editing",
                    edit_slice_form=edit_slice_form, clone_slice_form=clone_slice_form,
                    prop_values=prop_values)

    @expose()
    @require(predicates.in_group("acr"))
    @validate(edit_slice_form, error_handler=edit)
    def update(self, **kw):
        slice = DBSession.query(Slice).get(kw['uid'])
        if not user_can_modify(slice.page):
            flash('You do not have permissions to edit this page', 'error')
            return redirect(url('/admin/slices'))

        slice.name = kw['name']
        slice.zone = kw['zone']

        if kw['page']:
            slice.page = DBSession.query(Page).get(kw['page'])
        else:
            slice.page = None

        slice.tags = []        
        for tag_id in kw.get('tags', []):
            try:
                tag = DBSession.query(Tag).filter_by(uid=tag_id).one()
                slice.tags.append(tag)
            except:
                pass

        slice.attributes = []
        for attribute in kw.get('attributes', []):
            name = attribute['name']
            value = attribute['value']
            DBSession.add(Attribute(name=name, value=value, slice=slice))

        flash('Slice Properties successfully updated')
        return redirect(url('/admin/slices/edit', uid=kw['uid']))

    @expose('libacr.templates.admin.content_edit')
    @require(predicates.in_group("acr"))
    def edit_content(self, slice_uid, revision, translation=None, **kw):
        slice = DBSession.query(Slice).get(slice_uid)
        if not user_can_modify(slice.page):
            flash('You do not have permissions to edit this page', 'error')
            return redirect(url('/admin/slices'))

        translate_box = widgets.SingleSelectField('translate', label_text="Translate",
                                                  options=known_languages, default='en')

        edit_form = ViewsManager.create_form(slice.view, EditContentForm)
        values = odict()

        cdata = DBSession.query(ContentData).filter_by(uid=revision).first()
        values.update(ViewsManager.decode(slice.view, cdata.value))

        values['uid'] = slice.content.uid
        values['lang'] = cdata.lang
        values['slice_uid'] = slice.uid
        values['revision'] = revision

        if translation:
            values['lang'] = translation
 
        return dict(slice=slice, translate_box=translate_box,
                    edit_form=edit_form, values=values, revision=revision,
                    action=url('/admin/slices/update_content'),
                    translate_url='/admin/slices/edit_content')
            
    @expose()
    @require(predicates.in_group("acr"))
    @validate(ViewsManager.validator(EditContentForm), error_handler=edit_content)
    def update_content(self, **kw):
        slice = DBSession.query(Slice).get(kw['slice_uid'])
        if not user_can_modify(slice.page):
            flash('You do not have permissions to edit this page', 'error')
            return redirect(url('/admin/slices'))

        last_revision = slice.content.last_revision_for_lang([kw['lang']])
        cd = ContentData(content=slice.content, lang=kw['lang'],
                        value=ViewsManager.encode(kw['view'], kw),
                        revision=last_revision + 1,
                        author_id=current_user_id())
        DBSession.add(cd)

        flash('Content Updated')
        return redirect(url('/admin/slices/edit', uid=kw['slice_uid']))

    @expose()
    @require(predicates.in_group("acr"))
    def delete(self, uid, came_from='js'):
        slice = DBSession.query(Slice).get(uid)
        if not user_can_modify(slice.page):
            flash('You do not have permissions to edit this page', 'error')
            return redirect(url('/admin/slices'))

        page = slice.page
        DBSession.delete(slice)

        flash('Slice successfully deleted')
        if came_from == 'unbound':
            return redirect(url('/admin/unbound'))
        elif came_from == 'pages':
            return redirect(url('/admin/pages/edit', uid=page.uid))
        elif came_from == 'groups':
            return redirect(url('/admin/slice_groups'))
        else:
            return 'OK'

    @expose()
    @require(predicates.in_group("acr"))
    def revert_content(self, uid, revision):
        slice = DBSession.query(Slice).get(uid)
        if not user_can_modify(slice.page):
            flash('You do not have permissions to edit this page', 'error')
            return redirect(url('/admin/slices'))

        data = DBSession.query(ContentData).get(revision)
        last_revision = slice.content.last_revision_for_lang([data.lang])

        cd = ContentData(content=slice.content, lang=data.lang,
                        value=data.value, revision=last_revision + 1,
                        author_id=current_user_id())
        DBSession.add(cd)

        flash('Content Reverted')
        return redirect(url('/admin/slices/edit', uid=uid))

    @expose('libacr.templates.admin.slice_create')
    @require(predicates.in_group("acr"))
    def create(self, page, view, **kw):
        page = DBSession.query(Page).get(page)
        if not user_can_modify(page):
            flash('You do not have permissions to edit this page', 'error')
            return redirect(url(page.url))

        values = {'page':page.uid, 'name':'%s-%s' % (view, datetime.now().strftime('%y%m%d%H%M%S'))}        
        create_form = ViewsManager.create_form(view, CreateContentForm)
        return dict(create_form=create_form, values=values)

    @expose()
    @validate(ViewsManager.validator(CreateContentForm), error_handler=create)
    @require(predicates.in_group("acr"))
    def create_slice_with_content(self, **kw):
        slice_data = {'name': kw['name'], 'page': kw['page'], 'zone': kw['zone'], 'order': 0, 'tags': kw['tags'],
                      'view': kw['view'], 'data': ViewsManager.encode(kw['view'], kw), 'lang': kw['lang']}
        _create_node(**slice_data)

        if kw['page'] is not None:
            page = DBSession.query(Page).get(kw['page'])
            return redirect(url(page.url))
        else:
            return redirect(url('/admin/unbound'))

    @expose()
    @require(predicates.in_group("acr"))
    def clone(self, **kw):
        slice = DBSession.query(Slice).get(kw['uid'])
        page = DBSession.query(Page).get(kw['page'])

        new_slice = Slice(page=page, name=slice.name+'_clone', view=slice.view,
                          slice_order=slice.slice_order, tags=slice.tags, content=slice.content)
        DBSession.add(new_slice)
        DBSession.flush()

        flash('Slice successfully cloned')
        return redirect(url('/admin/slices/edit', uid=new_slice.uid))

    @expose('libacr.templates.admin.slice_create')
    @require(predicates.in_group("acr"))
    def create_unbound(self, view, **kw):
        values = {'page':None, 'name':'%s-%s' % (view, datetime.now().strftime('%y%m%d%H%M%S'))}
        create_form = ViewsManager.create_form(view, CreateContentForm)
        return dict(create_form=create_form, values=values)
