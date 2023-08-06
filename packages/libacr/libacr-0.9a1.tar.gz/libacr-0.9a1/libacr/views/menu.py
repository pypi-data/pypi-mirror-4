from tg import tmpl_context, request
from libacr.lib import url as acr_url
from libacr.lib import language
from libacr.form_fields import AcrOtherSingleSelectField
from genshi.template import MarkupTemplate

from libacr.model.core import DBSession
from libacr.model.content import Page
import tw.forms as twf
from base import EncodedView
import sys

class MenuRenderer(EncodedView):
    def __init__(self):
        self.name = 'menu'
        self.exposed = True
        self.form_fields = [AcrOtherSingleSelectField('root', label_text="Menu Root:", default='root',
                                                          options=(('parent', 'Parent Page'),
                                                                   ('root', 'Site Root'),
                                                                   ('current', 'Viewed Page'))),
                            twf.SingleSelectField('align', label_text="Alignment:", default='horizontal',
                                                           options=(('horizontal', 'Horizontal'),
                                                                    ('vertical', 'Vertical'))),
                            twf.TextField('depth', label_text="Menu Depth:", default=1,
                                                   validator=twf.validators.Int(not_empty=True, strip=True))]
        
    def preview(self, page, slice, data):
        return 'Preview not Implemented'

    def render(self, page, slice, data):
        def recursive_render_menu(max_depth, entries, level):
            menu = '<ul class="menu_level_%s">' % (level)
            
            for m_page in entries:
                if m_page.getattr('hidden'):
                    continue

                if not m_page.is_visible(request.identity):
                    continue

                if m_page.slices and m_page.slices[0].view == 'link':
                    uri = m_page.slices[0].content.data
                elif m_page.getattr('link'):
                    uri = m_page.getattr('link')
                else:
                    uri = '/' + m_page.uri
                    cpage = m_page
                    while cpage.parent != None:
                        cpage = cpage.parent
                        uri = '/' + cpage.uri + uri
                    uri = acr_url(uri)
                        
                if m_page.uid == page.uid:
                    style = 'class="acr_menu_selected"'
                else:
                    style= ''
                menu += '<li %s><a href="%s">%s</a>' % (style, uri, m_page.i18n_menu_title)
                
                if max_depth > level:
                    menu += recursive_render_menu(max_depth, sort_menu_entries(m_page.children), level+1)
                    
                menu += '</li>'
                    
            menu += '</ul>'
            return menu     
       
        def sort_menu_entries(children):
            def cmp(p1, p2):
                p1_weight = p1.getattr('menu-weight')
                p2_weight = p2.getattr('menu-weight')
                if p1_weight is None:
                    p1_weight = sys.maxsize
                if p2_weight is None:
                    p2_weight = sys.maxsize
                return int(p1_weight) - int(p2_weight)
            return sorted(children, cmp=cmp)
 
        config = self.to_dict(data)
        depth = int(config.get('depth', '1'))
        align = config.get('align', 'horizontal')
        root = config.get('root', 'root')
        
        menu = '<div class="%s_menu">' % (align)

        if root == 'root':
            children = DBSession.query(Page).filter_by(parent=None).filter(Page.uri!='default').all()
        elif root == 'current':
            children = page.children
        elif root == 'parent':
            page_for_menu = page.parent
            if not page_for_menu:
                page_for_menu = page
            children = page_for_menu.children
        else:
            root_page = DBSession.query(Page).filter(Page.uri==root).first()
            if not root_page:
                return '<p>Unsupported menu root specification</p>'
            else:
                children = DBSession.query(Page).filter_by(parent=root_page).all()

        children = sort_menu_entries(children)
        menu += recursive_render_menu(depth, children, 1)
        menu += '<div style="clear:both;"></div>'
        menu += '</div>'
        return menu
