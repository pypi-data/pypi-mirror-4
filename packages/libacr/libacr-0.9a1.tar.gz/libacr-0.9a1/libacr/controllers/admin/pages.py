from tg import expose, flash, require, url, request, redirect, tmpl_context, validate, TGController
from pylons.i18n import ugettext as _, lazy_ugettext as l_
from pylons.controllers.util import abort
from tg import predicates
import codecs

from libacr import acr_zones, forms
from libacr.lib import url, current_user_id, language, user_can_create_children_in_page, \
                       user_can_create_children_of_ancestors, user_can_modify
from libacr.views.manager import ViewsManager
from libacr.model.core import DBSession
from libacr.model.content import Tag, Page, Slice, Content, ContentData
from libacr.model.attributes import Attribute

from base import BaseAdminController

from sqlalchemy import or_

__all__ = ['PagesAdminController']

edit_page_form = forms.EditPageForm(DBSession)

class PagesAdminController(BaseAdminController):
    @expose('libacr.templates.admin.pages_index')
    @require(predicates.in_group("acr"))
    def index(self, **kw):
        pages = DBSession.query(Page).order_by(Page.parent_uid)
        return dict(pages=pages, section_title="Pages Management",
                     create_page_form=edit_page_form, values=kw)

    @expose()
    @validate(edit_page_form, error_handler=index)
    @require(predicates.in_group("acr"))
    def new(self, **kw):
        parent = DBSession.query(Page).filter_by(uid=kw['parent']).first()

        if not user_can_create_children_in_page(parent):
            flash('You do not have permissions to create children of this page', 'error')
            return redirect(url('/admin/pages'))

        p = Page(uri=kw['uri'], title=kw['title'], parent=parent)
        DBSession.add(p)

        for attribute in kw.get('attributes', []):
            name = attribute['name']
            value = attribute['value']
            DBSession.add(Attribute(name=name, value=value, page=p))

        flash('Page successfully created')
        return redirect(url(p.url))

    @expose()
    @require(predicates.in_group("acr"))
    def delete(self, page_id):
        p = DBSession.query(Page).get(page_id)
        if p and user_can_create_children_of_ancestors(p):
            DBSession.delete(p)
        else:
            flash('You do not have permissions to delete this page', 'error')
            return redirect(url('/admin/pages'))

        flash('Page successfully removed')
        return redirect(url('/admin/pages'))

    @expose('libacr.templates.admin.pages_edit')
    @require(predicates.in_group("acr"))
    def edit(self, **kw):
        page = DBSession.query(Page).get(kw.get('uid', kw.get('page')))
        values = {'uid':page.uid, 'uri':page.uri,
                  'title':page.title, 'parent':page.parent_uid,
                  'attributes':[dict(name=attr.name, value=attr.value) for attr in page.attributes]}

        return dict(page=page, section_title="Edit Page '%s'" % page.title,
                    edit_page_form=edit_page_form, values=values)

    @expose()
    @validate(edit_page_form, error_handler=edit)
    @require(predicates.in_group("acr"))
    def update(self, **kw):
        page = DBSession.query(Page).get(kw['uid'])

        if not user_can_modify(page):
            flash('You do not have permissions to edit this page', 'error')
            return redirect(url('/admin/pages'))

        page.uri = kw['uri']
        page.parent = kw['parent'] and DBSession.query(Page).get(kw['parent'])
        page.title = kw['title']
        page.attributes = []
        for attribute in kw.get('attributes', []):
            name = attribute['name']
            value = attribute['value']

            if isinstance(value, unicode):
                value = value.encode('ascii', 'xmlcharrefreplace')

            DBSession.add(Attribute(name=name, value=value, page=page))


        flash('Page successfully updated')
        return redirect(url('/admin/pages/edit', uid=kw['uid']))
