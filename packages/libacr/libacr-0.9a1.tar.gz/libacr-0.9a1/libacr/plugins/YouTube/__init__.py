from datetime import datetime
from tg import expose, flash, require, request, redirect, tmpl_context, TGController
from libacr.plugins.base import AdminEntry, AcrPlugin, plugin_expose
from libacr.controllers.admin.base import _create_node, BaseAdminController
from libacr.model.core import DBSession
from libacr.model.content import Tag, Page, Slice, Content, ContentData
from libacr.lib import url, current_user_id, language, icons, user_can_modify
from tg import predicates
from tw.api import WidgetsList
import tw.forms as twf

class YouTubeController(BaseAdminController):
    @plugin_expose('create')
    @require(predicates.in_group("acr"))
    def create(self):
        class InsertYoutubeForm(WidgetsList):
            page = twf.SingleSelectField(label_text="Page:", options=[(p.uid, p.title) for p in DBSession.query(Page)])
            vurl = twf.TextField(label_text="Url:")
        youtube_form = twf.TableForm(fields=InsertYoutubeForm(), submit_text="Insert")

        return dict(form=youtube_form)

    @expose()
    @require(predicates.in_group("acr"))
    def save(self, page, vurl=None):
        import urlparse, cgi
        if not vurl:
            flash('You must specify the url of a youtube video')
            return redirect(url('/plugins/youtube/create'))

        query = urlparse.urlparse(vurl).query
        try:
            query = urlparse.parse_qs(query)
        except:
            query = cgi.parse_qs(query)

        if not query.has_key('v'):
            flash('Specified url is not a valid youtube video url')
            return redirect(url('/plugins/youtube/create'))

        slicegroup_id = 'youtube_%s' % (datetime.now().strftime('%y%m%d%H%M%S'))
        node_args = {}
        node_args['page'] = page
        node_args['name'] = slicegroup_id
        node_args['zone'] = 'main'
        node_args['order'] = 0
        node_args['tags'] = []
        node_args['view'] = 'genshi'
        node_args['data'] = """
        <object width="480" height="368">
            <param name="movie" value="http://www.youtube.com/v/%s"></param>
            <param name="allowFullScreen" value="true"></param>
            <param name="allowscriptaccess" value="always"></param>
            <embed src="http://www.youtube.com/v/%s" type="application/x-shockwave-flash" allowscriptaccess="always" allowfullscreen="true" width="480" height="368"></embed>
        </object>
""" % (query['v'][0], query['v'][0])
        _create_node(**node_args)

        flash('Video successfully embedded')
        return redirect(url('/admin'))

class YouTube(AcrPlugin):
    uri = 'youtube'

    def __init__(self):
        self.admin_entries = [AdminEntry(self, 'Insert YouTube Video', 'create', section="Templates", icon="youtube_plugin.png")]
        self.controller = YouTubeController()
