from datetime import datetime
from tg import expose, flash, require, request, redirect, tmpl_context, TGController
from libacr.plugins.base import AdminEntry, AcrPlugin, plugin_expose, PluginStatic
from libacr.controllers.admin.base import _create_node, BaseAdminController
from libacr.model.core import DBSession
from libacr.model.content import Tag, Page, Slice, Content, ContentData
from libacr.lib import url, current_user_id, language, icons, user_can_modify
from tg import predicates
from tw.api import WidgetsList, CSSLink, JSLink
import tw.forms as twf
import urllib2

class UserVoiceController(BaseAdminController):
    @plugin_expose('create')
    @require(predicates.in_group("acr"))
    def create(self):
        class CreateUserVoiceFeedbackForm(WidgetsList):
            page = twf.SingleSelectField(label_text="Page:",
                                         options=[(p.uid, p.title) for p in DBSession.query(Page)])
            uservoice_key = twf.TextField(label_text="User Voice Key")
        user_voice_form = twf.TableForm(fields=CreateUserVoiceFeedbackForm(), submit_text="Create")

        return dict(form=user_voice_form)

    @expose()
    @require(predicates.in_group("acr"))
    def save(self, page, uservoice_key):

        node_args = {}
        node_args['page'] = page
        node_args['zone'] = 'main'
        node_args['order'] = 0
        node_args['tags'] = []
        node_args['name'] = 'user_voice_script'
        node_args['view'] = 'script'
        node_args['data'] = """
var uservoiceOptions = {
  /* required */
  key: '%s',
  host: '%s.uservoice.com',
  forum: '%s',
  showTab: true,
  /* optional */
  alignment: 'left',
  background_color:'#f00',
  text_color: 'white',
  hover_color: '#06C',
  lang: 'en'
};

function _loadUserVoice() {
  var s = document.createElement('script');
  s.setAttribute('type', 'text/javascript');
  s.setAttribute('src', ("https:" == document.location.protocol ? "https://" : "http://") + "cdn.uservoice.com/javascripts/widgets/tab.js");
  document.getElementsByTagName('head')[0].appendChild(s);
}
_loadSuper = window.onload;
window.onload = (typeof window.onload != 'function') ? _loadUserVoice : function() { _loadSuper(); _loadUserVoice(); };
""" % (uservoice_key, uservoice_key, self.retrieve_forum_id(uservoice_key))
        _create_node(**node_args)

        flash('Uservoice feedback tab created')
        return redirect(url('/admin'))

    def retrieve_forum_id(self, uservoice_key):
        forum_url = "http://%s.uservoice.com/" % uservoice_key
        response = urllib2.urlopen(forum_url)
        return response.geturl().split("/")[4].split("-")[0]

class UserVoiceFeedback(AcrPlugin):
    uri = 'uservoice'

    def __init__(self):
        self.admin_entries = [AdminEntry(self, 'Uservoice Feedback Tab', 'create', section="Templates", icon='uservoice_plugin.png')]
        self.controller = UserVoiceController()
