from datetime import datetime
from tg import expose, flash, require, request, redirect, tmpl_context, TGController
from libacr.plugins.base import AdminEntry, AcrPlugin, plugin_expose
from libacr.controllers.admin.base import _create_node, BaseAdminController
from libacr.model.core import DBSession
from libacr.model.content import Tag, Page, Slice, Content, ContentData
from libacr.lib import url, current_user_id, language, icons, user_can_modify
from tg import predicates
from tw.api import WidgetsList
import tw.forms as twf

from libacr.views.base import EncodedView

class NewsBlogController(BaseAdminController):
    @plugin_expose('create')
    @require(predicates.in_group("acr"))
    def create(self):
        class CreateNewsBlogForm(WidgetsList):
            page = twf.SingleSelectField(label_text="Page:", options=[(p.uid, p.title) for p in DBSession.query(Page)])
            tag = twf.SingleSelectField(label_text="Members Tag:", options=[(t.uid, t.name) for t in DBSession.query(Tag)])
        newsblog_form = twf.TableForm(fields=CreateNewsBlogForm(), submit_text="Create")

        return dict(form=newsblog_form)

    @expose()
    @require(predicates.in_group("acr"))
    def save(self, page, tag):
        tag = DBSession.query(Tag).filter_by(uid=tag).first()
        slicegroup_id = 'newsblog_%s-%s' % (tag.name, datetime.now().strftime('%y%m%d%H%M%S'))

        node_args = {}
        node_args['page'] = page
        node_args['name'] = slicegroup_id
        node_args['zone'] = 'main'
        node_args['order'] = 0
        node_args['tags'] = []
        node_args['view'] = 'slicegroup'
        node_args['data'] = EncodedView().from_dict(dict(filter_tag=tag.name,
                                                         preview=1))

        _create_node(**node_args)

        flash('News/Blog successfully created')
        return redirect(url('/admin'))

class NewsBlog(AcrPlugin):
    uri = 'newsblog'

    def __init__(self):
        self.admin_entries = [AdminEntry(self, 'Create News Section', 'create', section="Templates", icon="news_plugin.png")]
        self.controller = NewsBlogController()
