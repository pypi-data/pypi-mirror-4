# -*- coding: utf-8 -*-
from tg import tmpl_context

from libacr.lib import url as acr_url
from libacr.lib import language
from genshi.template import MarkupTemplate

from libacr.model.core import DBSession
from libacr.model.assets import Asset
from base import EncodedView
from libacr.model.content import Page
import os
import Image
import tw.forms as twf
from libacr.form_fields import AssetField

class ImageRenderer(EncodedView):
    def __init__(self):
        self.name = 'image'
        self.exposed = True
        self.form_fields = [AssetField('path', label_text="Asset:",
                                                  validator=twf.validators.String(not_empty=True, strip=True)),
                            twf.TextField('title', label_text="Title:",
                                                  validator=twf.validators.String(not_empty=True, strip=True)),
                            twf.TextField('link', label_text="Link:",
                                                  validator=twf.validators.String(strip=True)),
                            twf.TextField('size', label_text="Size (auto or 320x240):", default='auto',
                                                  validator=twf.validators.String(not_empty=True, strip=True)),
                            twf.SingleSelectField('show_title', label_text="Show Title", default='none',
                                                                options=(('none', "No"),
                                                                         ('top', "On Top"),
                                                                         ('bottom', 'Under Image'))),
                            twf.SingleSelectField('show_desc', label_text="Show Description", default='none',
                                                                options=(('none', "No"),
                                                                         ('bottom', "Under Image"))),
                            twf.TextArea('description', label_text="Description:",
                                                        validator=twf.validators.String())]
        
    def thumbnail(self, image_path):
        if image_path.startswith('asset'):
            asset = DBSession.query(Asset).filter_by(uid=image_path.split(':')[1]).first()
            return asset.thumb_url('medium')

        if image_path.startswith('/rdisk/'):
            image_path = image_path[len('/rdisk/'):]

        thumb_path = os.path.splitext(image_path)[0] + '.png'
        full_path = os.path.join(config.get('public_dir'), 'rdisk', image_path)

        thumb_uri = '/rdisk/thumbs/'+thumb_path
        thumb_full_path = os.path.join(config.get('public_dir'), 'rdisk', 'thumbs', thumb_path)

        if not os.path.exists(thumb_full_path):
            try:
                os.makedirs(os.path.split(thumb_full_path)[0])
            except:
                pass

            full_path_path=full_path.rstrip('\r')
            thumb = Image.open(full_path_path)
            thumb.thumbnail((140, 140))
            thumb.save(thumb_full_path, "PNG")

        return thumb_uri

    def adapt_path(self, image_path):
        if image_path.startswith('asset'):
            asset = DBSession.query(Asset).filter_by(uid=image_path.split(':')[1]).first()
            return asset.url
        else:
            return image_path

    def preview(self, page, slice, data):
        config = self.to_dict(data)
        image_path = config.get('path')
        image_title = config.get('title')
        image_size = config.get('size')
        image_show = config.get('show_title')
        image_desc= config.get('description')
        show_desc = config.get('show_desc')

        uri = slice.page and slice.page.uri or image_path
        image = '<div class="acr_image_preview">'
        image += '<a name="%s" href="%s" title="%s">' % (image_path, uri, image_title)

        if image_show=='top':
           image += '<div>%s</div>' % image_title

        image += '<img src="%s" />' % (self.thumbnail(image_path))

        if image_show =='bottom':
           image += '<div>%s</div>' % image_title

        image += '</a>'

        if show_desc=='bottom' and image_desc!='' :
           image +='<p class="acr_image_preview_desc">%s<p>' % (image_desc)

        image += '</div>'
        return image


    def render(self, page, slice, data):
        config = self.to_dict(data)
        path= config.get('path')
        title= config.get('title')
        size= config.get('size')
        link= config.get('link')
        show_title= config.get('show_title')
        desc= config.get('description')
        show_desc = config.get('show_desc')
        path = self.adapt_path(path)

        image = '<div class="acr_image">'
        if link:
           image += '<a href="%s" alt="%s">' % (link, title)
           
        if show_title=='top':
           image += '<div>%s</div>' %(title)

        if size== 'auto':
           image += '<img src="%s"/>' % (path)
        else:
           size2= size.split('x')
           image += '<img src="%s" style="width:%spx; height:%spx;"/>' % (path,size2[0],size2[1])

        if show_title=='bottom':
           image += '<div>%s</div>' %(title)

        if show_desc=='bottom' and desc != '':
           image +='<p class="acr_image_desc">%s<p>' % (desc)

        if link:
            image += '</a>'

        image +='</div>'
        return image
