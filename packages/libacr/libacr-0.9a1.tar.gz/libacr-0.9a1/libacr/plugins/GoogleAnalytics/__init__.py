from datetime import datetime
from tg import expose, flash, require, request, redirect, tmpl_context, TGController, config
from tg.controllers import WSGIAppController
from paste.urlparser import StaticURLParser
from libacr.plugins.base import AdminEntry, AcrPlugin, plugin_expose, PluginStatic, PluginUrl
from libacr.controllers.admin.base import _create_node, BaseAdminController
from libacr.model.core import DBSession
from libacr.model.content import Tag, Page, Slice, Content, ContentData
from libacr.lib import url, current_user_id, language, icons, user_can_modify
from tg import predicates
from tw.api import WidgetsList, CSSLink, JSLink
from string import Template
import tw.forms as twf
import os, libacr

class GoogleAnalyticsStaticsController(TGController):
    @expose()
    def lookup(self, *args):
        site_dir = os.path.join(config.get('public_dir'), 'ga')
        return WSGIAppController(StaticURLParser(site_dir)), args
    _lookup = lookup

class GoogleAnalyticsController(BaseAdminController):
    statics = GoogleAnalyticsStaticsController()
    
    @plugin_expose('create')
    @require(predicates.in_group("acr"))
    def create(self):
        class CreateGoogleAnalyticsForm(WidgetsList):
            tracking_code = twf.TextField(label_text="Google Analytics Tracking Code")
        google_analytics_form = twf.TableForm(fields=CreateGoogleAnalyticsForm(), submit_text="Create")
        return dict(form=google_analytics_form)

    @expose()
    @require(predicates.in_group("acr"))
    def save(self, tracking_code):
        ga_site_script_file_name = os.path.join(config.get('public_dir'), 'ga', "google_analytics.js")

        string_template = """
var gaJsHost = (("https:" == document.location.protocol) ? "https://ssl." : "http://www.");
document.write(unescape("%3Cscript src='" + gaJsHost + "google-analytics.com/ga.js' type='text/javascript'%3E%3C/script%3E"));

try{
    var pageTracker = _gat._getTracker("${tracking_code}");
    pageTracker._trackPageview();
} catch(err) {}
"""
        ga_template = Template(string_template).substitute(tracking_code=tracking_code)
        if not os.path.exists(os.path.join(config.get('public_dir'), 'ga')):
            os.makedirs(os.path.join(config.get('public_dir'), 'ga'))
        ga_site_script_file = file(ga_site_script_file_name, 'w')
        ga_site_script_file.writelines(ga_template)

        flash('Google Analytics correctly configured')
        return redirect(url('/admin'))

class GoogleAnalyticsPlugin(AcrPlugin):
    uri = 'ga'

    def __init__(self):
        self.admin_entries = [AdminEntry(self, 'Add Google Analytics', 'create', section="General Settings", icon='ga_plugin.png')]
        self.js_resources = [JSLink(link=PluginUrl(self, 'statics/google_analytics.js'))]
        self.controller = GoogleAnalyticsController()
