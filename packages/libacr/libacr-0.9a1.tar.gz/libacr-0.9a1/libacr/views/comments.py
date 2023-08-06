from libacr.model.core import DBSession
from libacr.model.comments import Comment
from libacr.lib import url as acr_url
from libacr.lib import icons

from tg import tmpl_context, request

from genshi.template import MarkupTemplate
from sprox.formbase import AddRecordForm
from sprox.widgets import HiddenField
from formencode import validators
import tw.forms as twf

from base import EncodedView

class AddCommentForm(AddRecordForm):
    __model__ = Comment
    __omit_fields__ = ['uid', 'owner_uid', 'owner', 'time']
    thread_id = HiddenField

class CommentsRenderer(EncodedView):
    def __init__(self):
        self.name = 'comments_thread'
        self.form_fields = [twf.TextField('thread_id', label_text="Thread name:", validator=twf.validators.String(strip=True)),
                            twf.SingleSelectField('post', label_text="Permit to:",
                                                          options=(('public', 'public'),
                                                                   ('everyone', 'registered users')))]
        self.exposed = True

    def preview(self, page, slice, data):
        return 'Preview not Implemented'

    def render(self, page, slice, data):
        d = self.to_dict(data)
        post_limit = d.get('post', 'public')
        thread_id = d.get('thread_id', 'auto')
        
        if thread_id == 'auto':
            thread_id = page.uid

        self.add_comment_form = AddCommentForm(DBSession)
        can_post = False
        if post_limit == 'public':
            can_post = True
        elif post_limit == 'everyone' and request.identity:
            can_post = True
        elif request.identity and post_limit in request.identity['groups']:
            can_post = True

        comments = DBSession.query(Comment).filter_by(thread_id=thread_id) \
                                           .order_by(Comment.time.desc())

        result = '<div class="acr_comments acr_comments_thread_%s">' % (thread_id)

        if can_post:
            form_code = self.add_comment_form({'thread_id':thread_id}, action=acr_url('/comments/post'))
            result += '<div class="acr_comments_add">Add New Comment</div>'
            result += MarkupTemplate(form_code).generate().render('xhtml')
 
        for comment in comments:
            result += '<div class="acr_comments_comment">'
            result += '<div class="acr_comments_comment_title">'
            result += '<span class="acr_comments_comment_user">%s</span>' % (comment.owner and comment.owner.display_name or 'anonymous')
            result += '<span class="acr_comments_comment_time">%s</span>' % (comment.time.strftime('%Y-%m-%d %H:%M'))
            twitter_status = tmpl_context.pylons.request.url + ' : ' + comment.content
            result += '<span class="acr_comments_comment_share">'
            result += '<a target="_blank" href="%s">' % ('http://twitter.com/home?status='+twitter_status)
            result += icons['twitter'].render()
            result += '</a>'
            result += '</span>'

            result += '</div>'

            result += MarkupTemplate("""<div xmlns:py="http://genshi.edgewall.org/"
                                             class="acr_comments_comment_content">
                                             ${content}
                                        </div>""").generate(content=comment.content).render('xhtml')

            result += '</div>'
        result += '</div>'
        return result
