# -*- coding: utf-8 -*-
from datetime import datetime
from tg import expose, flash, require, request, redirect, tmpl_context, TGController
from libacr.plugins.base import AdminEntry, AcrPlugin, PluginStatic, plugin_expose
from libacr.controllers.admin.base import _create_node, BaseAdminController
from libacr.model.core import DBSession
from libacr.model.content import Tag, Page, Slice, Content, ContentData
from libacr.lib import url, current_user_id, language, icons, user_can_modify
from libacr.views.base import EncodedView
from tg import predicates
from tw.api import WidgetsList, CSSLink, JSLink
import tw.forms as twf

class SlideshowController(BaseAdminController):
    @plugin_expose('create')
    @require(predicates.in_group("acr"))
    def create(self):
        class CreateSlideshowForm(WidgetsList):
            page = twf.SingleSelectField(label_text="Page:", options=[(p.uid, p.title) for p in DBSession.query(Page)])
            tag = twf.SingleSelectField(label_text="Members Tag:", options=[(t.uid, t.name) for t in DBSession.query(Tag)])
            effect = twf.SingleSelectField(label_text="Effect:", default='fade',
                                            options=['blindX', 'blindY', 'blindZ',
                                                    'cover', 'curtainX', 'curtainY'
                                                    'fade', 'fadeZoom', 'growX', 'growY',
                                                    'none',
                                                    'scrollUp', 'scrollDown', 'scrollLeft',
                                                    'scrollRight', 'scrollHorz', 'scrollVert',
                                                    'shuffle', 'slideX', 'slideY', 'toss',
                                                    'turnUp', 'turnDown', 'turnLeft', 'turnRight',
                                                    'uncover', 'wipe', 'zoom'])
        slideshow_form = twf.TableForm(fields=CreateSlideshowForm(), submit_text="Create")
        return dict(form=slideshow_form)

    @expose()
    @require(predicates.in_group("acr"))
    def save(self, page, tag, effect):
        tag = DBSession.query(Tag).filter_by(uid=tag).first()
        slicegroup_id = 'slideshow_%s' % tag.name

        node_args = {}
        node_args['page'] = page
        node_args['name'] = slicegroup_id
        node_args['zone'] = 'main'
        node_args['order'] = 0
        node_args['tags'] = []
        node_args['view'] = 'slicegroup'
        node_args['data'] = EncodedView().from_dict(dict(filter_tag=tag.name,
                                                         preview=0))
        _create_node(**node_args)

        node_args['name'] += '_script'
        node_args['view'] = 'script'
        node_args['data'] = """
    jQuery('.%(sid)s .acr_group_%(tag)s_entries').cycle({fx: '%(effect)s'});
""" % dict(sid=slicegroup_id, tag=tag.name, effect=effect)

        _create_node(**node_args)

        flash('Slideshow successfully created')
        return redirect(url('/admin'))

class Slideshow(AcrPlugin):
    uri = 'slideshow'

    def __init__(self):
        self.admin_entries = [AdminEntry(self, 'Create Slideshow', 'create', section="Templates", icon="slideshow_plugin.png")]
        self.js_resources = [JSLink(link=PluginStatic(self, 'jquery.cycle.js'))]
        self.controller = SlideshowController()
