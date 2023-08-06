from tg import tmpl_context
from libacr.lib import url as acr_url
from libacr.lib import language
from genshi.template import MarkupTemplate

from libacr.model.core import DBSession
from libacr.model.content import Page
from libacr.model.assets import Asset
import os
from tg import config
import Image

import tempfile
import tw.forms as twf
from base import EncodedView
from libacr.form_fields import AssetField

class VideoRenderer(EncodedView):
    def __init__(self):
        self.name = 'video'
        self.exposed = True

        self.form_fields = [AssetField('path', label_text="Asset:",
                                                  validator=twf.validators.String(not_empty=True, strip=True)),
                            twf.TextField('title', label_text="Title:",
                                                  validator=twf.validators.String(not_empty=True, strip=True)),
                            twf.SingleSelectField('show_title', label_text="Show Title", default='none',
                                                                options=(('none', "No"),
                                                                         ('top', "On Top"),
                                                                         ('bottom', 'Under Image'))),
                            twf.TextField('size', label_text="Size (auto or 320x240):", default='auto',
                                                  validator=twf.validators.String(not_empty=True, strip=True))]

    def adapt_path(self, path):
        if path.startswith('asset'):
            asset = DBSession.query(Asset).filter_by(uid=path.split(':')[1]).first()
            return (asset.url+'.ogv', asset.url+'.mp4')
        else:
            video_p=os.path.splitext(path)[0]
            name_video=video_p.split('/')[2]
            return ("/rdisk/video/video_%s.ogg" % video_name, 
                    "/rdisk/video/video_%s.mov" % video_name)

    def thumbnail(self, video_path, poster=False):
        if video_path.startswith('asset'):
            asset = DBSession.query(Asset).filter_by(uid=video_path.split(':')[1]).first()
            if not poster:
                return asset.thumb_url('medium')
            else:
                return asset.thumb_url('video')

        #Backward compatible for videos uploaded from RDisk
        if video_path.startswith('/rdisk/'):
            video_path = video_path[len('/rdisk/'):]

        full_path = os.path.join(config.get('public_dir'), 'rdisk', video_path).strip()
        thumb_path = os.path.splitext(video_path)[0] + '.png'
        thumb_uri = '/rdisk/thumbs/'+thumb_path
        thumb_full_path = os.path.join(config.get('public_dir'), 'rdisk', 'thumbs', thumb_path)
        return thumb_uri
  
    def preview(self, page, slice, data):
        config = self.to_dict(data)

        video_path = config.get('path')
        video_title = config.get('title')
        video_size = config.get('size', 'auto')
        video_show = config.get('show_title')
        
        uri = slice.page and slice.page.uri or video_path
        video = '<div class="acr_video_preview">'
        video += '<a href="%s" title="%s">' % (uri, video_title)

        if video_show == 'top':
           video += '<div class="video_title">%s</div>' % video_title
        
        if video_path.startswith('/rdisk/'):
            video_path = video_path[len('/rdisk/'):]

        video += '<img src="%s"/>' % self.thumbnail(video_path)
        
        if video_show == 'bottom':
           video += '<div class="video_title">%s</div>' % video_title
        
        video += '</a> </div>'
        return video
   
    def render(self, page, slice, data):
        config = self.to_dict(data)
        
        path= config.get('path')
        title= config.get('title')
        size= config.get('size', 'auto')
        show_title= config.get('show_title')
        
        video = '<div class="acr_video">'
        if show_title=='top':
           video += '<div class="video_title">%s</div>' %(title)

        if size == 'auto':
           video += '<video  controls="true" poster="%s">' % self.thumbnail(path, poster=True)
        else: 
           size2 = size.split('x')
           video += '<video  controls="true" poster="%s" style="width:%spx;height:%spx;">'% (self.thumbnail(path, poster=True),size2[0],size2[1])

        ogv_url, mov_url = self.adapt_path(path)
        video += '<source src="%s"/>'% (mov_url)
        video += '<source src="%s" type="video/ogg"/>'% (ogv_url)
        video += '</video>'

        if show_title=='bottom':
           video += '<div class="video_title">%s</div>' %(title)

        video +='</div>'
        return video
