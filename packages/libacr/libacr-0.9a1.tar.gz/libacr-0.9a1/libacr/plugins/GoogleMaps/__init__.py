from tg import expose, flash, require, request, redirect, tmpl_context, TGController, config, validate, url
from tg.controllers import WSGIAppController
import libacr
from libacr.views.base import EncodedView
from genshi.template import MarkupTemplate
import urllib, urllib2
from libacr.model.core import DBSession
from libacr.controllers.admin.base import BaseAdminController
from libacr.plugins.base import AdminEntry, AcrPlugin, plugin_expose, PluginUrl, PluginStatic
from libacr.model.content import Tag, Page, Slice, Content, ContentData
from libacr.lib import url as acr_url
from tg import predicates
from libacr.views.manager import ViewsManager
import tw.api
from tw.api import WidgetsList, CSSLink, JSLink, JSSource
import tw.forms as twf
import os
from paste.urlparser import StaticURLParser

default_size = "300x300"

class GMapsStaticsController(TGController):
    @expose()
    def lookup(self, *args):
        site_dir = os.path.join(config.get('public_dir'), 'gmaps')
        return WSGIAppController(StaticURLParser(site_dir)), args
    _lookup = lookup

class ChKeyForm(twf.TableForm):
    class fields(WidgetsList):
        key = twf.TextField(label_text="Google Maps Api Key", validator=twf.validators.String(not_empty=True))

chkeyform = ChKeyForm(submit_text="Change")

class GMapsController(BaseAdminController):
    statics = GMapsStaticsController()
    
    @plugin_expose('index')
    @require(predicates.in_group("acr"))
    def index(self, **kw):
        key = DBSession.query(Content).filter_by(name='_acr_config_gmap').first()
        if not key:
            key = Content(name="_acr_config_gmap")
            kdata = ContentData(content=key, revision=0)
            kdata.set_property('Google Maps', 'Key', '')
            DBSession.add(key)
            DBSession.add(kdata)
        kw['key'] = key.get_data_instance_for_lang().get_property('Google Maps', 'Key')
        return dict(form=chkeyform,values=kw)

    @expose()
    @require(predicates.in_group("acr"))
    @validate(form=chkeyform,error_handler=index)
    def change(self,**kw):
        nkey = kw['key']
        key = DBSession.query(Content).filter_by(name='_acr_config_gmap').first()
        kdata = key.get_data_instance_for_lang()
        if nkey == key :
            flash("The API key was not modified hence is not changed")
            return redirect(acr_url('/admin'))
        kdata.set_property('Google Maps', 'Key', nkey)
        flash("Google Maps Api key updated succesfully")
        return redirect(acr_url('/admin'))

class MapRenderer(EncodedView):
    def __init__(self):
        self.name = 'map'
        self.exposed = True
        self.form_fields = [twf.TextField('location', label_text="Address:",
                                                      validator=twf.validators.String(not_empty=True, strip=True)),
                            twf.TextField('zoom', label_text="Zoom:", default=13,
                                                  validator=twf.validators.Int(not_empty=True, strip=True)),
                            twf.TextField('size', label_text="Size:",default=default_size)]
        
    def _get_geocode(self, api_key, addr):
        root_url = "http://maps.google.com/maps/geo?"
        gkey = api_key

        geodat = [0]
        if addr:
            values = {'q' : addr, 'output':'csv', 'key':gkey}
            data = urllib.urlencode(values)
            url = root_url+data
            req = urllib2.Request(url)
        
            response = urllib2.urlopen(req)
            geodat = response.read().split(',')
            response.close()
        
        code = geodat[0]
        if code == '200':
            code,precision,lat,lng = geodat
            return {'code':code,'precision':precision,'lat':lat,'lng':lng}
        else:
            return {'code':code,'lat':0, 'lng':0}
        
    def _parse_conf(self, data):
        config = self.to_dict(data)
        zoom = int(config.get('zoom', '13'))
        size = config.get('size')
        location = config.get('location')
        
        if not size:
            size = default_size
        size_x, size_y = size.split('x')
        return location, zoom, size, size_x, size_y
    
    def render(self, page, slice, data):
        api_key = DBSession.query(Content).filter_by(name='_acr_config_gmap').first()
        if not api_key:
            raise Exception('Google Maps API key missing inside configuration file, please specify one')
        api_key = api_key.get_data_instance_for_lang().get_property('Google Maps', 'Key')
        if not api_key:
            raise Exception('Google Maps API key missing inside configuration file, please specify one')

        location, zoom, size, size_x, size_y = self._parse_conf(data)
        style = 'style="width:%spx; height:%spx"' % (size_x, size_y)
        div = '<div class="acr_gmap" id="acr_gmap_%s" %s></div>' % (slice.uid, style)
        gmap_call = 'acr_create_gmap("acr_gmap_%s", "%s", %s);' % (slice.uid, location, str(zoom))

        gmap_api = JSLink(modname=__name__, link="http://maps.google.com/maps?file=api&amp;v=2.x&amp;key="+api_key)
        gmap_api.inject()
        
        result = div
        result += MarkupTemplate(JSSource(src=gmap_call).display()).generate().render('xhtml')
        return result
    
    def preview(self, page, slice, data):
        api_key = DBSession.query(Content).filter_by(name='_acr_config_gmap').first().get_data_instance_for_lang().get_property('Google Maps', 'Key')
        if not api_key:
            raise Exception('Google Maps API key missing inside configuration file, please specify one')
        
        location, zoom, size, size_x, size_y = self._parse_conf(data)
        
        location = self._get_geocode(api_key, location)
        
        size = size
        if not size:
            size = "200x200"
        
        link = url('http://maps.google.com/maps', ll='%s,%s' % (location['lat'], location['lng']), z=self.zoom)
        uri = url('http://maps.google.com/staticmap', center='%s,%s' % (location['lat'], location['lng']),
                                                      zoom=self.zoom, size=size, format='jpg',
                                                      markers='%s,%s,redc' % (location['lat'], location['lng']),
                                                      key=api_key, sensor='false')
        
        return '<a class="acr_gmap_preview" href="%s"><img src="%s"/></a>' % (link, uri)
    

class GmapsPlugin(AcrPlugin):
    uri = 'gmaps'

    def __init__(self):
        self.admin_entries = [AdminEntry(self, 'Google Maps', 'index', icon='maps.png', section="General Settings")]
        self.controller = GMapsController()
        ViewsManager.register_view(MapRenderer())
        self.js_resources = [JSLink(link=PluginStatic(self, 'gmap.js'))]
