from tg import tmpl_context
from libacr.lib import url as acr_url
from libacr.lib import language
from genshi.template import MarkupTemplate

from libacr.model.core import DBSession
from libacr.model.content import Slice, Content, ContentData, Tag
import tw.forms as twf

from base import EncodedView

class TagCloudRenderer(EncodedView):
    def __init__(self):
        self.name = 'tagcloud'
        self.exposed = True
        self.form_fields = [twf.TextField('expose', label_text="Filter Tag:", default='', validator=twf.validators.String(strip=True))]

    def render(self, page, slice, data):
        filter_tag = self.to_dict(data)['expose']

        if filter_tag:
            tag = DBSession.query(Tag).filter_by(name=filter_tag).first()
            if tag:
                slices = tag.slices
            else:
                slices = []
        else:
            slices = DBSession.query(Slice)

        tagmax = 0
        tags = {}
        for slice in slices:
            for tag in slice.tags:
                if not tag.group:     
                    occurrences = tags.get(tag.name, 0) + 1
                    tags[tag.name] = occurrences
                    tagmax = max(tagmax, occurrences)

        template = u'''
<div class="acr_tagcloud acr_${filter_tag}_tagcloud">
    <span py:for="tagname, count in tags.iteritems()" class="acr_tag_${int(round((count / tagmax) * 10))}">
        <a href="${acr_url('/filter_tag', tag=tagname)}">${tagname}</a>
    </span>
</div>
'''
        t = MarkupTemplate(u'<html xmlns:py="http://genshi.edgewall.org/" py:strip="">%s</html>' % template)
        t = t.generate(filter_tag=filter_tag, tags=tags, tagmax=tagmax, acr_url=acr_url)
        return t.render('xhtml').decode('utf-8')

        result = u'''
<div class="acr_tagcloud acr_%(filter_tag)s_tagcloud">
</div>''' % dict(filter_tag=filter_tag)

        return result

    def preview(self, page, slice, data):
        return 'Preview not Implemented'
        

class SearchRenderer(EncodedView):
    def __init__(self):
        self.name = 'search'
        self.exposed = True
        self.form_fields = [twf.TextField('expose', label_text="Filter Tag:", default='', validator=twf.validators.String(strip=True))]
    
    def render(self, page, slice, data):
        result = u'''
<div class="acr_search">
  <form action=%s>
    <input type="hidden" name="searchid" value="%s"/>
    <input type="text" name="what" class="acr_search_text" value="search..." 
           onfocus="if (this.value=='search...') {this.value='';}"
           onblur="if (this.value=='') {this.value = 'search...';}"/>
    <input type="submit" value="GO" class="acr_search_btn"/>
  </form>
</div>''' % (acr_url('/search'), unicode(slice.uid))

        return result

    def preview(self, page, slice, data):
        return 'Preview not Implemented'
        
    @staticmethod
    def perform(slice, what):
        search_def = slice.content.data
        config = EncodedView().to_dict(search_def)
        expose_tag = config.get('expose', '')

        res = DBSession.query(Slice).join(Content).join(ContentData)
        if expose_tag.strip():
            res = res.filter(Slice.tags.any(name=expose_tag.strip()))
        res = res.filter(ContentData.value.like('%' + what + '%'))
       
        return res
        
