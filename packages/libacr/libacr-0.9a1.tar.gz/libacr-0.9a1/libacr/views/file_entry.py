from tg import config
from libacr.lib import url as acr_url
import mimetypes, os
import Image
from libacr.lib import icons
import tw.forms as twf
from libacr.form_fields import AssetField

from libacr.model.core import DBSession
from libacr.model.assets import Asset

from base import EncodedView

class FileRenderer(EncodedView):
    def __init__(self):
        self.name = 'file'
        self.exposed = True
        self.form_fields = [AssetField('path', label_text="Asset:",
                                                       validator=twf.validators.String(not_empty=True, strip=True)),
                            twf.TextField('title', label_text="Title:",
                                                        validator=twf.validators.String(not_empty=True, strip=True)),
                            twf.TextArea('desc', label_text="Description:",
                                                      validator=twf.validators.String())]

    def to_dict(self, data):
        try:
            return super(FileRenderer, self).to_dict(data)
        except:
            #backward compatible data loading from old odd format
            data = data.split('\n', 3)
            file_path = data[0].strip()
            file_title = data[1]
            file_desc = data[2]

            d = {'path' : data[0].strip(),
                'title' : data[1],
                'desc' : data[2]}

            return d
  
    def adapt_path(self, file_path):
        if file_path.startswith('asset'):
            asset = DBSession.query(Asset).filter_by(uid=file_path.split(':')[1]).first()
            return asset.url, asset.content_type
        else:
            return file_path, mimetypes.guess_type(file_path)[0]

    def preview(self, page, slice, data):
        d = self.to_dict(data)
        file_path = d.get('path', '').strip()
        file_title = d.get('title', '')
        file_desc = d.get('desc', '')

        file_path, file_type = self.adapt_path(file_path)
        
        result = '<div class="acr_file_preview">'

        result += '<table>'
        result += '<tr>'
        result += '<td>'
        if file_type.startswith('application'):
           result += '<img src="%s" />'% (icons['pdf'].link)
        elif file_type.startswith('audio'):
           result += '<img src="%s" />'% (icons['audio'].link)
        elif file_type.startswith('image'):
           result += '<img src="%s" />'% (icons['asset'].link)
        elif file_type.startswith('video'):
           result += '<img src="%s" />'% (icons['asset'].link)
        else:
           result += '<img src="%s" />'% (icons['document'].link)
        result += '</td>'

        result += '<td>'
        result +='<a href="%s" >' % (file_path)
        result += '<h3>%s</h3>' % (file_title)
        result += '</a>'
        result += '</td>'

        result += '</tr>'
        result += '</table>'
        
        result += '</div>'
                
        return result

    def render(self, page, slice, data):
        d = self.to_dict(data)
        file_path = d.get('path', '').strip()
        file_title = d.get('title', '')
        file_desc = d.get('desc', '')

        file_path, file_type = self.adapt_path(file_path)

        result = '<div class="acr_file_render">'

        result +='<a href="%s" >' % (file_path)
        if file_type.startswith('application'):
           result += '<img src="%s" />'% (icons['pdf'].link)
        elif file_type.startswith('audio'):
           result += '<img src="%s" />'% (icons['audio'].link)
        elif file_type.startswith('image'):
           result += '<img src="%s" />'% (icons['asset'].link)
        elif file_type.startswith('video'):
           result += '<img src="%s" />'% (icons['asset'].link)
        else:
           result += '<img src="%s" />'% (icons['document'].link)
        result += '</a>'
        
        result += '<div class=acr_body_file>'
        result += '<div class="acr_title_file"><h3>%s</h3></div>' %(file_title)
        result += '<div class="acr_desc_file">%s</div>' %(file_desc)
        result += '</div>'

        result += '</div>'
        
        
        return result
    
    
