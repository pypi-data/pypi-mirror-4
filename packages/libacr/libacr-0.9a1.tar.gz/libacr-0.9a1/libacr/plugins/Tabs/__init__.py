from libacr.controllers.admin.base import _create_node, BaseAdminController
from libacr.lib import url
from libacr.model.content import Tag, Page
from libacr.model.core import DBSession
from libacr.plugins.base import AdminEntry, AcrPlugin, plugin_expose, PluginStatic
from tg import predicates
from tg import expose, flash, require, redirect
from tw.api import WidgetsList, CSSLink, JSLink
import tw.forms as twf

from libacr.views.base import EncodedView

class TabsController(BaseAdminController):
    @plugin_expose('create')
    @require(predicates.in_group("acr"))
    def create(self):
        class CreateTabsForm(WidgetsList):
            page = twf.SingleSelectField(label_text="Page:",
                                         options=[(p.uid, p.title) for p in DBSession.query(Page)])
            tag = twf.SingleSelectField(label_text="Members Tag:",
                                        options=[(t.uid, t.name) for t in DBSession.query(Tag)])
        tabs_form = twf.TableForm(fields=CreateTabsForm(), submit_text="Create")

        return dict(form=tabs_form)

    @expose()
    @require(predicates.in_group("acr"))
    def save(self, page, tag):
        tag = DBSession.query(Tag).filter_by(uid=tag).first()
        slicegroup_id = 'tabs_%s' % tag.name

        node_args = {}
        node_args['page'] = page
        node_args['name'] = slicegroup_id
        node_args['zone'] = 'main'
        node_args['order'] = 0
        node_args['tags'] = []
        node_args['view'] = 'slicegroup'
        node_args['data'] = EncodedView().from_dict(dict(filter_tag=tag.name,
                                                         preview=1,
                                                         type='li'))
        _create_node(**node_args)

        node_args['name'] += '_script'
        node_args['view'] = 'script'
        node_args['data'] = """
jQuery(document).ready(function(){
    jQuery('.acr_group_%(tag)s_entries li').hide();
    jQuery(jQuery('.acr_group_%(tag)s_entries li')[0]).show();
    jQuery('.acr_group_%(tag)s').prepend('<ul id="acr_tab_%(tag)s_header"></ul>');
    jQuery('.acr_group_%(tag)s_entries li').each(function(idx, el) {
        tab_header = jQuery(jQuery(el).find('p')[0]);
        head_class = "acr_tabhead-" + idx;
        if (idx == 0) {
            head_class += " acr_active_tab";
        }
        tab_head = jQuery('<li class="'+head_class+'">');
        tab_header.appendTo(tab_head);
        jQuery('#acr_tab_%(tag)s_header').append(tab_head);

        tab_head.click(function() {
            jQuery('.acr_group_%(tag)s .acr_active_tab').removeClass('acr_active_tab');
            clicked_tab = jQuery(this).attr('class').substring(12);
            jQuery(this).addClass('acr_active_tab');
            jQuery('.acr_group_%(tag)s_entries li').hide();
            jQuery(jQuery('.acr_group_%(tag)s_entries li')[clicked_tab]).show();
        });
    });
});
""" % dict(tag=tag.name)
        _create_node(**node_args)

        flash('Tabs successfully created')
        return redirect(url('/admin'))

class Tabs(AcrPlugin):
    uri = 'tabs'

    def __init__(self):
        self.admin_entries = [AdminEntry(self, 'Tabs', 'create', section="Templates", icon='tabs_icon.png')]
        self.controller = TabsController()
