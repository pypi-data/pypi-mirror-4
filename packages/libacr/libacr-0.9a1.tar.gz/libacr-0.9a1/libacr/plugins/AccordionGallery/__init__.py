from libacr.controllers.admin.base import _create_node, BaseAdminController
from libacr.lib import url
from libacr.model.content import Tag, Page
from libacr.model.core import DBSession
from libacr.plugins.base import AdminEntry, AcrPlugin, plugin_expose, PluginStatic
from libacr.views.base import EncodedView
from tg import predicates
from tg import expose, flash, require, redirect
from tw.api import WidgetsList, CSSLink, JSLink
import tw.forms as twf

class AccordionGalleryController(BaseAdminController):
    @plugin_expose('create')
    @require(predicates.in_group("acr"))
    def create(self):
        class CreateAccordionGalleryForm(WidgetsList):
            page = twf.SingleSelectField(label_text="Page:",
                                         options=[(p.uid, p.title) for p in DBSession.query(Page)])
            tag = twf.SingleSelectField(label_text="Members Tag:",
                                        options=[(t.uid, t.name) for t in DBSession.query(Tag)])
            width = twf.TextField(label_text="Gallery Width")
            height = twf.TextField(label_text="Gallery Height")
        gallery_form = twf.TableForm(fields=CreateAccordionGalleryForm(), submit_text="Create")

        return dict(form=gallery_form)

    @expose()
    @require(predicates.in_group("acr"))
    def save(self, page, tag, width, height):
        tag = DBSession.query(Tag).filter_by(uid=tag).first()
        slicegroup_id = 'accordion_gallery_%s' % tag.name

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
jQuery(document).ready(function(){
    var accordion_slider = jQuery(".%s");
    accordion_slider.width(%s);
    accordion_slider.height(%s);
    accordion_slider.addClass('acr_accordion');

    jQuery(accordion_slider).kricordion({
        animationSpeed: 900,
        autorotation: true,
        autorotationSpeed:5,
        event: 'mouseover',
        imageShadow:true,
        imageShadowStrength:0.4
    });
});
""" % (slicegroup_id, width, height)
        _create_node(**node_args)

        flash('Accordion Gallery successfully created')
        return redirect(url('/admin'))

class AccordionPhotoGallery(AcrPlugin):
    uri = 'accordion_gallery'

    def __init__(self):
        self.admin_entries = [AdminEntry(self, 'Accordion Gallery', 'create', section="Templates", icon='accordion_icon.png')]
        self.css_resources = [CSSLink(link=PluginStatic(self, 'acr_accordion_gallery.css'))]
        self.js_resources = [JSLink(link=PluginStatic(self, 'jquery.accordion_gallery.js')),
                             JSLink(link=PluginStatic(self, 'jquery.easing.1.3.js'))]
        self.controller = AccordionGalleryController()
