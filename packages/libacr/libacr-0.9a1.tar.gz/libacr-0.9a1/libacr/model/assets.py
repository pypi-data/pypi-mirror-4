from tg import config
from sqlalchemy import *
from sqlalchemy.orm import mapper, relation
from sqlalchemy import Table, ForeignKey, Column, asc, desc
from sqlalchemy.types import Integer, Unicode
from sqlalchemy.orm import relation, backref
from sqlalchemy.orm.interfaces import MapperExtension
from datetime import datetime
from libacr.lib import url as acr_url
from core import DeclarativeBase, DBSession
import mimetypes, os, threading, Image
mimetypes.init()

import logging
from libacr.model.attributes import UnrelatedAttribute

log = logging.getLogger('libacr')

THUMBS = {'icon': (64, 64),
          'small': (140, 140),
          'medium': (320, 320),
          'big': (480, 480),
          'huge':(640, 640)}

VIDEO_CONVERSION = {'png':"ffmpeg -y -i '%(path)s' -intra -ss 0:0:5.0 -vframes 1  -vcodec png  -y -f image2 '%(path)s.png'",
                    'ogv':"ffmpeg2theora '%(path)s' -x 480 -y 368 --optimize -o '%(path)s.ogv'",
                    'mp4':"ffmpeg -y -i '%(path)s' -acodec libfaac -s 480x368 -vcodec libx264 -vpre baseline -vpre fast -vb 600k -r 20 -ac 1 -ab 64k '%(path)s.mp4'"}

def try_unlink(path):
    try:
        if os.path.exists(path):
            os.unlink(path)
    except Exception, e:
        log.warning('Failed to remove asset, %s' % e)

def run_background(asset, cmd):
    class BackgroundJob(threading.Thread):
        def __init__(self, asset, action):
            super(BackgroundJob, self).__init__()
            self.asset = asset
            self.asset_path = asset.path
            self.action = action

        def run(self):
            self.action(self.asset, self.asset_path)

    bg = BackgroundJob(asset, cmd)
    bg.daemon = True
    bg.start()

def perform_video_conversion(asset, asset_path):
    for video_format in (key for key in VIDEO_CONVERSION if key != 'png'):
        if os.system(VIDEO_CONVERSION[video_format] % dict(path=asset_path)):
            log.error('Failed to perform video conversion of asset %s' % asset.name)
            break

class Asset(DeclarativeBase):
    class Hooks(MapperExtension):
        def before_delete(self, mapper, connection, instance):
            for thumb_type in THUMBS.keys():
                try_unlink(instance.thumb_path(thumb_type))

            for video_format in VIDEO_CONVERSION.keys():
                try_unlink('%s.%s' % (instance.path, video_format))

            try_unlink(instance.path)
            
    __mapper_args__ = {'extension': Hooks()}
    __tablename__ = 'acr_cms_assets'
    
    uid = Column(Integer, primary_key=True)
    name = Column(Unicode(255), nullable=False, index=True)
    content_type = Column(Unicode(64), nullable=False, index=True)

    @property
    def filename(self):
        file_ext = mimetypes.guess_extension(self.content_type, False)
        #avoid unpredictability in jpeg images extension
        if file_ext in ('.jpe', '.jpeg'):
            file_ext = '.jpg'
        return '%(asset_id)s%(extension)s' % dict(asset_id=self.uid, extension=file_ext)

    @property
    def path(self):
        public_dir = config.get('public_dir')
        assets_path = os.path.join(public_dir, 'assets')
        return os.path.join(assets_path, self.filename)        

    @property
    def url(self):
        return acr_url('/assets/%s' % self.filename)

    def thumbname(self, thumb_type):
        if thumb_type == 'video':
            return self.filename + '.png'
        else:
            return '%(asset_id)s_%(thumb_type)s.png' % dict(asset_id=self.uid, thumb_type=thumb_type)

    def thumb_path(self, thumb_type):
        public_dir = config.get('public_dir')
        assets_path = os.path.join(public_dir, 'assets')
        return os.path.join(assets_path, self.thumbname(thumb_type))

    def thumb_url(self, thumb_type):
        return acr_url('/assets/%s' % self.thumbname(thumb_type))

    @property
    def is_video(self):
        return self.content_type.startswith('video')

    @property
    def is_image(self):
        return self.content_type.startswith('image')

    def make_thumbnail(self, thumb_type):
        if self.is_image:
            original_image = self.path
        elif self.is_video:
            original_image = self.path+'.png'
        else:
            original_image = os.path.join(os.path.dirname(__file__), '..', 'static', 'icons', 'iconDocument.png')
            
        thumb = Image.open(original_image)
        thumb.thumbnail(THUMBS[thumb_type])
        thumb.save(self.thumb_path(thumb_type))
       
    @property
    def ready(self):
        if self.is_video:
            if not os.path.exists(self.thumb_path('video')):
                return False

            for vformat in VIDEO_CONVERSION.keys():
                if not os.path.exists('%s.%s' % (self.filename, vformat)):
                    return False
        elif self.is_image:
            for thumb in THUMBS:
                if not os.path.exists(self.thumb_path(thumb)):
                    return False

        return True
 
    def write(self, data):
        f = open(self.path, 'wb')
        while 1:
            copy_buffer = data.read(1048576)
            if copy_buffer:
                f.write(copy_buffer)
            else:
                break
        f.flush()
        f.close()

        try:
            if self.is_video:
                os.system(VIDEO_CONVERSION['png'] % dict(path=self.path))

            for thumb in THUMBS:
                self.make_thumbnail(thumb)
        except:
            log.error('Failed to generate thumbnails of asset %s' % self.name)

        if self.is_video:
            run_background(self, perform_video_conversion)

    @property
    def category(self):
        attr = UnrelatedAttribute.of_object(self, 'category')
        return getattr(attr, 'value', 'none')
