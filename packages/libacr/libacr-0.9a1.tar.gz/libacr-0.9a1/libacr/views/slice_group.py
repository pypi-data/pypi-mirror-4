from sqlalchemy.orm import join
import libacr.helpers as h
from tg import request, tmpl_context

from libacr.model.core import DBSession
from libacr.model.content import Content, Slice, Tag
import tw.forms as twf

from base import EncodedView

class SliceGroupRenderer(EncodedView):
    slice_orderers = {'content_time': lambda x : x.order_by(Content.time.desc())}
    
    def __init__(self):
        self.name = 'slicegroup'
        self.exposed = False
        self.form_fields = [twf.SingleSelectField('filter_tag', label_text="Filter Tag:",
                                                        validator=twf.validators.String(not_empty=True, strip=True),
                                                        options=lambda : (p.name for p in DBSession.query(Tag))),
                            twf.SingleSelectField('preview', label_text="Use Preview:", default='0',
                                                          options=(('0', 'No'),
                                                                   ('1', 'Yes'))),
                            twf.TextField('size', label_text="Items per Page (0 unlimited):", default='0',
                                                  validator=twf.validators.Int(not_empty=True, strip=True)),
                            twf.SingleSelectField('type', label_text="Render As:", default='div',
                                                          options=(('li', 'List'),
                                                                   ('div', 'Div'))),
                            twf.SingleSelectField('orderer', label_text="Order By", default=' ',
                                                             options=(('', "Ascending Time"),
                                                                      ('content_time', "Descending Time")))]
                                                  
       
    def preview(self, page, slice, data):
        return 'Preview not Implemented'
        
    def render(self, page, slice, data):
        def url_for_page(parg, page_num):
            args = tmpl_context.form_values.copy()
            args[parg] = str(page_num)
            uri = request.urlargs.current(**args)
            return uri

        config = self.to_dict(data)                
        per_page = int(config.get('size', '0'))
        filter_tag = config.get('filter_tag', '')
        preview = int(config.get('preview', '0'))
        type = config.get('type', 'div')
        
        try:
            orderer = config.get('orderer')
            orderer = SliceGroupRenderer.slice_orderers[orderer]
        except:
            orderer = lambda x : x
                
        paginator_arg = str('%s_sgoffset' % (filter_tag))
        current_page = int(tmpl_context.form_values.get(paginator_arg, 1))
        
        slices = DBSession.query(Slice).\
                select_from(join(Slice, Content)).\
                filter(Slice.tags.any(name=filter_tag))
        slices = orderer(slices)
        if per_page:
            range_begin = (current_page-1)*per_page
            total = slices.count()
            last_page = (total // per_page) 
            if (total % per_page):
                last_page += 1
            slices = slices[range_begin:range_begin+per_page]
            
            next_uri = url_for_page(paginator_arg, current_page+1)         
            prev_uri = url_for_page(paginator_arg, current_page-1)

        
        result = '<div class="acr_group_%s">' % (filter_tag)
        result += '<%s class="acr_group_%s_entries">\n' % (type=='li' and 'ul' or 'div', filter_tag)
        for slice in slices:
            result += '<%s class="acr_group_entry">\n' % (type)
            if preview:
                result += h.preview_slice(page, slice)
            else:
                result += h.render_slice(page, slice)
            result += '</%s>\n' % (type)
        result += '</%s>\n' % (type=='li' and 'ul' or 'div')    
        
        if per_page:
            result += '<div class="acr_group_paginator">\n'
            if current_page > 1:
                result += '<span class="acr_group_paginator_prev"><a href="%s">Prev</a></span>' % (prev_uri)
                
            for i in xrange(1, last_page+1):
                if i == current_page:
                    result += '<span class="acr_group_paginator_current_page">%s</span>' % (i)
                else:
                    result += '<span class="acr_group_paginator_page"><a href="%s">%s</a></span>' % (url_for_page(paginator_arg, i), i)
            
            if current_page < last_page:
                result += '<span class="acr_group_paginator_next"><a href="%s">Next</a></span>' % (next_uri)
                
            result += '</div>\n'             
        result += '</div>'
        
        return result
