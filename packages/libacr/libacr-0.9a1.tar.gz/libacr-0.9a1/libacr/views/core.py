# -*- coding: utf-8 -*-
import logging
import traceback
import genshi
from genshi.template import MarkupTemplate
import sys
from libacr.contrib.ckeditor.widgets import CKEditor
from libacr.lib import url as acr_url
from libacr.lib import get_slices_with_tag, get_page_from_urllist
from libacr.model.depot import Depot
import libacr.helpers as h
import tw.forms as twf
from base import EncodedView
from tg import request
from tg.util import Bunch

log = logging.getLogger(__name__)

class LinkRenderer(object):
    def __init__(self):
        self.name = 'link'
        self.exposed = True
        self.form_fields = [twf.TextField('data', label_text="Url:", validator=twf.validators.URL(not_empty=True, strip=True))]

    def render(self, page, slice, data):
        return data

    def preview(self, page, slice, data):
        return 'Preview not Implemented'

    def to_dict(self, data):
        return {'data':data}

    def from_dict(self, dic):
        return dic['data']

class HTMLRenderer(object):
    def __init__(self):
        self.name = 'html'
        self.form_fields = [CKEditor('data', label_text="")]
        self.exposed = True

    def render(self, page, slice, data):
        return data

    def preview(self, page, slice, data):
        page = slice.page
        if page:
            link = acr_url('/page', pageid=page.uid)
        else:
            link = acr_url('/slice', sliceid=slice.uid)
        text = slice.preview()

        result = '<div class="acr_preview">'
        #result += '<h1>%s</h1>' % '<a href="%s">%s</a>' % (link, page and page.title or slice.name)
        result += ' <span>%s</span>' % slice.content.time.strftime('%Y-%m-%d %H:%M')
        result += ' <div>'+text+'</div>'
        result += '</div>'

        return result

    def to_dict(self, data):
        return {'data':data}

    def from_dict(self, dic):
        return dic['data']

class BlogPostRenderer(EncodedView):
    def __init__(self):
        self.name = 'blogpost'
        self.exposed = True

        self.form_fields = [twf.TextField('title', label_text="Title:", validator=twf.validators.String(not_empty=True, strip=True)),
                            CKEditor('content', label_text="")]

        self.template = MarkupTemplate(u'''
<html xmlns:py="http://genshi.edgewall.org/" py:strip="">
    <h2><a py:strip="not link" href="${link}">${title}</a></h2>
    <div class="post_info">${author} - ${date}</div>
    <div class="post_content">
        ${Markup(content)}
    </div>
</html>''')

    def render(self, page, slice, data):
        data = self.to_dict(data)

        try:
            t = self.template.generate(title=data['title'], content=data['content'], link=None,
                                       author=slice.content.data_instance.author,
                                       date=slice.content.data_instance.time.strftime('%Y-%m-%d %H:%M'))
            return t.render('xhtml').decode('utf-8')
        except Exception, e:
            return str(e)

    def preview(self, page, slice, data):
        page = slice.page
        if page:
            link = page.url
        else:
            link = acr_url('/slice', sliceid=slice.uid)

        data = self.to_dict(data)
        text = slice.preview(data=data['content'], omit_link=True)

        t = self.template.generate(title=data['title'], content=text, link=link,
                                   author=slice.content.data_instance.author,
                                   date=slice.content.data_instance.time.strftime('%Y-%m-%d %H:%M'))
        return t.render('xhtml').decode('utf-8')

class GenshiRenderer(object):
    def __init__(self):
        self.name = 'genshi'
        self.form_fields = [twf.TextArea('data', label_text="", validator=twf.validators.String(not_empty=True),
                                                 rows=20, attrs={'style':'width:600px;height:400px;'})]
        self.exposed = True
        self.acr_dict = Bunch({'slices_with_tag':get_slices_with_tag,
                             'page_from_urllist':get_page_from_urllist,
                             'preview_slice':h.preview_slice,
                             'render_slice':h.render_slice,
                             'acr_url':h.acr_url,
                             'markup':genshi.Markup,
                             'depot':Depot,
                             'request':request})

    def render(self, page, slice, data):
        try:
            t = MarkupTemplate(u'<html xmlns:py="http://genshi.edgewall.org/" py:strip="">%s</html>' % data)
            t = t.generate(page=page, slice=slice, acr=self.acr_dict)
            return t.render('xhtml').decode('utf-8')
        except Exception, e:
            tb = traceback.extract_tb(sys.exc_info()[2])
            log.warning(''.join(traceback.format_list(tb)))
            return str(e)

    def preview(self, page, slice, data):
        content = self.render(page, slice, data)
        return HTMLRenderer().preview(page, slice, content)

    def to_dict(self, data):
        return {'data':data}

    def from_dict(self, dic):
        return dic['data']

class ScriptRenderer(object):
    def __init__(self):
        self.name = 'script'
        self.form_fields = [twf.TextArea('data', label_text="", validator=twf.validators.String(not_empty=True),
                                                 rows=20, attrs={'style':'width:600px;height:400px;'})]
        self.exposed = True

    def render(self, page, slice, data):
        return '<script>%s</script>' % data

    def preview(self, page, slice, data):
        return '<script>%s</script>' % data

    def to_dict(self, data):
        return {'data':data}

    def from_dict(self, dic):
        return dic['data']

class AjaxRenderer(object):
    def __init__(self):
        self.name = 'ajax'
        self.form_fields = [twf.TextField('data', label_text="Url:", validator=twf.validators.URL(not_empty=True, strip=True))]
        self.exposed = True

        self.url_map = {}
        self.url_id = 0

    def render(self, page, slice, data):
        uri = data

        if not self.url_map.has_key(uri):
            self.url_id += 1
            self.url_map[uri] = self.url_id

        id = self.url_map[uri]
        id = "acr_ajax_load_%s" % str(id)
        txt = '<div id="%s"><img style="margin:10px auto;display:block;" src="/images/spinner.gif"/></div><script>jQuery("#%s").load("%s");</script>' % (id, id, uri)
        return txt

    def preview(self, page, slice, data):
        return 'Preview not Implemented'

    def to_dict(self, data):
        return {'data':data}

    def from_dict(self, dic):
        return dic['data']
