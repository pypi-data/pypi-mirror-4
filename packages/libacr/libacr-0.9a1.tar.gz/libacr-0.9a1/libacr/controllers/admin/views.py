from tg import expose, flash, require, url, request, redirect, tmpl_context, validate
from pylons.i18n import ugettext as _, lazy_ugettext as l_
from pylons.controllers.util import abort
from tg import predicates

from libacr import acr_zones, forms
from libacr.lib import url, current_user_id, language, icons, user_can_modify
from libacr.model.core import DBSession
from libacr.model.content import Tag, Page, Slice, Content, ContentData, View

from tw.api import WidgetsList
import tw.forms as widgets
from formencode import validators
from libacr.views.manager import ViewsManager
from libacr.forms import order_values

from datetime import datetime
from base import BaseAdminController, _create_node
from libacr.model.user_permission import AcrUserPermission

__all__ = ['ViewsAdminController']

edit_view_form = forms.EditViewForm(DBSession)

class ViewsAdminController(BaseAdminController):
    @expose('libacr.templates.admin.list_views')
    @require(predicates.in_group("acr"))
    def index(self):
        views = DBSession.query(View).filter_by(type='template').all()
        return dict(views=views)

    @expose('libacr.templates.admin.edit_view')
    @require(predicates.in_group("acr"))
    def edit(self, view_uid=None, **kw):
        view = DBSession.query(View).filter_by(uid=view_uid).first()
        if view:
            fields_declaration_name = '%s_fields' % view.name
            fields = DBSession.query(View).filter_by(name=fields_declaration_name).first()
            if fields:
                viewfields = fields.code
            else:
                viewfields = ''

            preview_declaration_name = '%s_preview' % view.name
            preview = DBSession.query(View).filter_by(name=preview_declaration_name).first()
            if preview:
                preview = preview.code
            else:
                preview = ''

            values = dict(uid=view.uid, code=view.code, name=view.name, viewfields=viewfields, preview=preview)
        else:
            values = dict()

        return dict(edit_form=edit_view_form, values=values)
           

    @expose()
    @require(predicates.in_group("acr"))
    @validate(form=edit_view_form, error_handler=edit)
    def save(self, *args, **kw):
        if kw.get('uid'):
            view = DBSession.query(View).filter_by(uid=kw.get('uid')).first()
        else:
            view = View(type='template')
            DBSession.add(view)

        view.code = kw['code']
        view.name = kw['name']

        fields_declaration_name = '%s_fields' % view.name
        fields = DBSession.query(View).filter_by(name=fields_declaration_name).first()
        if fields:
            fields.code = kw['viewfields']
        else:
            DBSession.add(View(type='fields', name=fields_declaration_name, code=kw['viewfields']))

        preview_template_name = '%s_preview' % view.name
        preview = DBSession.query(View).filter_by(name=preview_template_name).first()
        if preview:
            preview.code = kw['preview']
        elif kw.get('preview'):
            DBSession.add(View(type='preview_template', name=preview_template_name, code=kw['preview']))

        flash('View Registered')
        return redirect(url('/admin'))

    @expose()
    @require(predicates.in_group("acr"))
    def delete(self, view_uid):
        view = DBSession.query(View).filter_by(uid=view_uid).first()
        if not view:
            flash(_('View not found'))
            return redirect(url('/admin'))

        try:
            del ViewsManager.forms[request.host][view.name]
        except KeyError:
            pass

        fields_declaration_name = '%s_fields' % view.name
        preview_template_name = '%s_preview' % view.name

        fields = DBSession.query(View).filter_by(name=fields_declaration_name).first()
        if fields:
            DBSession.delete(fields)

        preview = DBSession.query(View).filter_by(name=preview_template_name).first()
        if preview:
            DBSession.delete(preview)

        for s in DBSession.query(Slice).filter_by(view=view.name):
            DBSession.delete(s)

        DBSession.delete(view)
        flash(_('View and Slices successfully deleted'))
        return redirect(url('/admin'))
