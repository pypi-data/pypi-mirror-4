from tg import TGController, flash, redirect, tmpl_context
import libacr
from libacr.lib import admin_css, url, current_user_id, language, user_can_modify
import os

__all__ = ['BaseAdminController']

class BaseAdminController(TGController):
    def _admin_master_path(self):
        return os.path.join(os.path.dirname(libacr.__file__), 'templates', 'admin', 'admin_master.html')

    def __before__(self, *args, **kw):
        admin_css.inject()
        tmpl_context.acr_admin_master = self._admin_master_path()

    _before = __before__

from tw.api import WidgetsList
import tw.forms as widgets
from formencode import validators
from libacr.views.manager import ViewsManager
from libacr import acr_zones
from libacr.forms import order_values
from libacr.model.core import DBSession
from libacr.model.content import Tag, Content, Slice, ContentData, Page

def _create_node(**kw):
    page = DBSession.query(Page).filter_by(uid=kw['page']).first()

    if not kw.get('skip_permission',False) and not user_can_modify(page):
        flash('You cannot modify that page')
        return redirect(url('/admin'))

    name = kw['name']
    zone = kw['zone']
    order = kw['order']
    tags = kw['tags']
    view = kw['view']
    data = kw['data']
    lang = kw.get('lang', 'en')

    content = Content(name=name)
    cdata = ContentData(content=content, lang=lang, value=data,
                        revision=content.last_revision + 1, author_id=current_user_id())
    slice = Slice(name=name, zone=zone, view=view, slice_order=order,
                  content=content, page=page)

    tag_models = []
    for tag in tags:
        tag_models.append(DBSession.query(Tag).filter_by(name=tag).one())
    slice.tags.extend(tag_models)

    DBSession.add(content)
    DBSession.add(cdata)
    DBSession.add(slice)
