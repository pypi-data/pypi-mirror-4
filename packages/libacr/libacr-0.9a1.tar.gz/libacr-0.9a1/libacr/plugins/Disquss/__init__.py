from tg import expose, flash, require, request, redirect, tmpl_context, TGController, config, validate
from tg.controllers import WSGIAppController
import libacr

from libacr.views.manager import ViewsManager
from libacr.views.base import EncodedView
from libacr.model.core import DBSession
from libacr.controllers.admin.base import BaseAdminController
from libacr.plugins.base import AdminEntry, AcrPlugin, plugin_expose
from libacr.model.content import Tag, Page, Slice, Content, ContentData
from tg import predicates
from tw.api import WidgetsList
import tw.forms as twf

class ChKeyForm(twf.TableForm):
    class fields(WidgetsList):
        key = twf.TextField(label_text="Disqus User ID",validator=twf.validators.String(not_empty=True))
chkeyform = ChKeyForm(submit_text="Change")

class DisqusController(BaseAdminController):

    @plugin_expose('index')
    @require(predicates.in_group("acr"))
    def index(self, **kw):
        key = DBSession.query(Content).filter_by(name='_acr_config_disqus').first()
        if not key:
            key = Content(name="_acr_config_disqus")
            kdata = ContentData(content=key, revision=0)
            kdata.set_property('Disqus', 'Key', '')
            DBSession.add(key)
            DBSession.add(kdata)
        kw['key'] = key.get_data_instance_for_lang().get_property('Disqus', 'Key')
        return dict(form=chkeyform,values=kw)

    @expose()
    @require(predicates.in_group("acr"))
    @validate(form=chkeyform,error_handler=index)
    def change(self,**kw):
        nkey = kw['key']
        key = DBSession.query(Content).filter_by(name='_acr_config_disqus').first()
        kdata = key.get_data_instance_for_lang()
        kdata.set_property('Disqus', 'Key', nkey)
        flash("Disqus User ID updated succesfully")
        return redirect('/acr/admin')

class DisqusRenderer(EncodedView):

    def __init__(self):
        self.name = 'disqus_thread'
        self.form_fields = [twf.TextField('thread_id', label_text="Thread ID:",default='auto')]
        self.exposed = True

    def preview(self, page, slice, data):
        return 'Preview not Implemented'

    def render(self, page, slice, data):
        user_id = DBSession.query(Content).filter_by(name='_acr_config_disqus').first()
        if not user_id:
            raise Exception('Disquss user id missing inside configuration, please specify one')
        user_id = user_id.get_data_instance_for_lang().get_property('Disqus', 'Key')
        if not user_id:
            raise Exception('Disquss user id missing inside configuration, please specify one')
        
        d = self.to_dict(data)
        thread_id = d.get('thread_id', 'auto')
        
        if thread_id == 'auto':
            thread_id = str(slice.uid)
            d['thread_id'] = thread_id
            slice.content.data_instance.value = self.from_dict(d)
            
        result = '<div id="disqus_thread"></div>'
        if config.get("debug"):
            result +=    '<script type="text/javascript">'
            result +=    '  var disqus_developer = true;'
            result +=    '</script>'
        result +=     '<script type="text/javascript">'
        result +=     '  var disqus_identifier = '+thread_id+' ; '
        result +=      ' (function() {'
        result +=      "  var dsq = document.createElement('script'); dsq.type = 'text/javascript'; dsq.async = true;"
        result +=       ' dsq.src = "http://'+user_id+'.disqus.com/embed.js";'
        result +=      "  (document.getElementsByTagName('head')[0] || document.getElementsByTagName('body')[0]).appendChild(dsq);"
        result +=     '  })();'
        result +=    ' </script>'
        return result

class ChangePass(AcrPlugin):
    uri = 'disqus'

    def __init__(self):
        self.admin_entries = [AdminEntry(self, 'Disqus', 'index', icon='unbound.png', section="General Settings")]
        self.controller = DisqusController()
        ViewsManager.register_view(DisqusRenderer())
