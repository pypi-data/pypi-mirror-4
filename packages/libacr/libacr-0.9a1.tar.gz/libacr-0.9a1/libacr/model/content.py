from sqlalchemy import *
from sqlalchemy.orm import mapper, relation
from sqlalchemy import Table, ForeignKey, Column, asc, desc
from sqlalchemy.types import Integer, Unicode
from sqlalchemy.orm import relation, backref
from sqlalchemy.orm.interfaces import MapperExtension
from datetime import datetime

from tg.decorators import cached_property

from BeautifulSoup import BeautifulSoup
from core import DeclarativeBase, DBSession
import re
from ConfigParser import ConfigParser, NoOptionError
from StringIO import StringIO
from paste.util.multidict import MultiDict
from attributes import Attribute
from libacr.unicodecfp import UnicodeConfigParser

#Force Sprox to use one line fields for entries as big as 128 chars.
try:
    import sprox.sa.widgetselector
    sprox.sa.widgetselector.text_field_limit = 128
except ImportError:
    pass

acr_lib = None

tag_content_map = Table('acr_cms_map_content_tag', DeclarativeBase.metadata,
                        Column('tag_uid', Integer, ForeignKey('acr_cms_tag.uid')),
                        Column('content_uid', Integer, ForeignKey('acr_cms_content.uid'))
                       )

tag_slice_map = Table('acr_cms_map_slice_tag', DeclarativeBase.metadata,
                        Column('tag_uid', Integer, ForeignKey('acr_cms_tag.uid')),
                        Column('slice_uid', Integer, ForeignKey('acr_cms_slice.uid'))
                     )

class Tag(DeclarativeBase):
    __tablename__ = 'acr_cms_tag'

    uid = Column(Integer, primary_key=True)
    name = Column(Unicode(128), nullable=False, index=True, unique=True)
    tag_group = Column(Integer, ForeignKey('tg_group.group_id'))
    contents = relation('Content', secondary=tag_content_map)
    slices = relation('Slice', secondary=tag_slice_map)
    group = relation('Group', uselist=False)

class Content(DeclarativeBase):
    __tablename__ = 'acr_cms_content'

    uid = Column(Integer, primary_key=True)
    name = Column(Unicode(128), nullable=False, index=True, unique=True)
    time = Column(DateTime, default=datetime.now)
    slices = relation('Slice', backref=backref('content', uselist=False))
    tags = relation(Tag, secondary=tag_content_map)

    def has_data_for_lang(self, lang):
        data = DBSession.query(ContentData).filter_by(content_id=self.uid).filter_by(lang=lang).order_by(desc(ContentData.revision)).first()

        if data:
            return data.revision
        else:
            return None

    @property
    def authors(self):
        auths = {}

        for cd in DBSession.query(ContentData).filter_by(content_id=self.uid):
            auths[cd.author and cd.author.user_name or 'None'] = True

        return auths.keys()

    @property
    def available_languages(self):
        langs = {}

        for cd in DBSession.query(ContentData).filter_by(content_id=self.uid):
            langs[cd.lang] = True

        return langs.keys()

    def get_data_instance_for_lang(self, langs=None, fallback=True):
        global acr_lib
        if acr_lib is None:
            from libacr import lib as acr_lib

        if not langs:
            langs = acr_lib.language()

        data = None
        for lang in langs:
            data = DBSession.query(ContentData).filter_by(content_id=self.uid).filter_by(lang=lang).order_by(desc(ContentData.revision)).first()
            if data:
                return data

        if fallback:
            data = DBSession.query(ContentData).filter_by(content_id=self.uid).order_by(desc(ContentData.revision)).first()

        return data

    def last_revision_for_lang(self, langs=None):
        ld = self.get_data_instance_for_lang(langs, False)
        if ld:
            return ld.revision
        else:
            return 0

    @property
    def last_revision(self):
        return self.last_revision_for_lang()

    def get_data_for_lang(self, langs=None):
        data = self.get_data_instance_for_lang(langs)

        if data:
            return data.value
        else:
            return data

    @property
    def data_instance(self):
        return self.get_data_instance_for_lang(None)

    @property
    def data(self):
        return self.get_data_for_lang()

    @staticmethod
    def find_by_property(prop, value, OType=None, views=None):
        from libacr.views.manager import ViewsManager

        if not OType:
            OType = Content

        cur_entries = DBSession.query(OType)
        if OType == Slice and views:
            cur_entries = cur_entries.filter(or_(*views))

        if OType != Content:
            cur_entries = cur_entries.join(Content)

        cur_entries = cur_entries.join(ContentData)\
                                 .filter(ContentData.value.like('%'+value+'%')).all()

        results = []
        for entry in cur_entries:
            data = ViewsManager.decode(entry.view, entry.content.data)
            if (data.has_key(prop)) and (data[prop] == value):
                results.append(entry)
        return results

class ContentData(DeclarativeBase):
    __tablename__ = 'acr_cms_content_data'

    uid = Column(Integer, primary_key=True)
    content_id = Column(Integer, ForeignKey('acr_cms_content.uid'), nullable=False)
    content = relation('Content', backref=backref("all_data",
                                                  order_by=desc('acr_cms_content_data.revision'),
                                                  cascade='all, delete-orphan'))

    lang = Column(Unicode(30), nullable=False, index=True, default=u'en')
    time = Column(DateTime, default=datetime.now)
    revision = Column(Integer, nullable=False)

    author_id = Column(Integer, ForeignKey('tg_user.user_id'), nullable=True)
    author = relation('User')

    value = Column(UnicodeText, default=u'')

    @property
    def _properties(self):
        try:
            config = UnicodeConfigParser(dict_type=MultiDict)
        except:
            config = UnicodeConfigParser()

        if self.value:
            config.readfp(StringIO(self.value))

        return config

    def property_is_binary(self, prop):
        return self.get_property(None, prop).startswith('data:')

    def get_binary_property_mimetype(self, prop):
        return self.get_property(None, prop).rsplit(';')[0].rsplit(':')[-1]

    def _update_properties(self, properties):
        data = StringIO()
        properties.write(data)
        self.value = data.getvalue()

    def get_property(self, section, prop):
        if section == None:
            section = self._properties.sections()[0]

        try:
            return self._properties.get(section, prop)
        except NoOptionError:
            return ''

    def set_property(self, section, prop, value):
        config = self._properties
        if not config.has_section(section):
            config.add_section(section)
        config.set(section, prop, value)
        self._update_properties(config)

    @property
    def html(self):
        return BeautifulSoup(self.value)

    @staticmethod
    def decode(data):
        try:
            config = ConfigParser(dict_type=MultiDict)
        except:
            config = ConfigParser() 
        config.readfp(StringIO(data))

        section_name = config.sections()[0]
        attributes = config.options(section_name)

        parsed = MultiDict()
        for attr in attributes:
            parsed[attr] = config.get(section_name, attr)

        return parsed

    @staticmethod
    def encode(attrs):
        try:
            config = ConfigParser(dict_type=MultiDict)
        except:
            config = ConfigParser()

        config.add_section('acr_data')
        for name, value in attrs.iteritems():
            config.set('acr_data', name, value)

        s = StringIO()
        config.write(s)
        return s.getvalue()
        
class View(DeclarativeBase):
    __tablename__ = 'acr_cms_view'

    uid = Column(Integer, primary_key=True)
    name = Column(Unicode(30), nullable=False, index=True, unique=True)
    type = Column(Unicode(32), nullable=False, default=u'text')
    code = Column(UnicodeText, default=u'')

    @property
    def properties(self):
        try:
            config = ConfigParser(dict_type=MultiDict)
        except:
            config = ConfigParser()

        if self.code:
            config.readfp(StringIO(self.code))

        return config

class Page(DeclarativeBase):
    __tablename__ = 'acr_cms_page'

    uid = Column(Integer, primary_key=True)
    uri = Column(Unicode(128), index=True)
    title = Column(Unicode(128), default=u'')

    parent_uid = Column(Integer, ForeignKey('acr_cms_page.uid', ondelete="CASCADE"))
    children = relation('Page', backref=backref('parent', remote_side='Page.uid'))

    slices = relation('Slice', backref=backref('page', uselist=False), order_by='Slice.slice_order')

    def section(self, part):
        sec = []
        for slice in self.slices:
            if slice.zone == part:
                sec.append(slice)
        return sec

    @cached_property
    def url(self):
        path = []
        page = self

        while page:
            if page.uri == 'default':
                path.insert(0, 'default')
            path.insert(0, page.uri)
            page = page.parent

        return '/' + '/'.join(path)

    @cached_property
    def metatags(self):
        attrs = DBSession.query(Attribute).filter_by(page=self)\
                                          .filter(Attribute.name.like('meta-%'))
        return [(attr.name[5:], attr.value) for attr in attrs]

    @cached_property
    def i18n_titles(self):
        attrs = DBSession.query(Attribute).filter_by(page=self)\
                                          .filter(Attribute.name.like('title-%'))
        titles = dict([(attr.name[6:], attr.value) for attr in attrs])
        if 'en' not in titles:
            titles['en'] = self.title
        return titles

    @cached_property
    def i18n_menu_titles(self):
        titles = self.i18n_titles

        attrs = DBSession.query(Attribute).filter_by(page=self) \
                                          .filter(Attribute.name.like('menu-title-%'))
        titles.update(dict([(attr.name[11:], attr.value) for attr in attrs]))

        return titles

    @cached_property
    def i18n_title(self):
        global acr_lib
        if acr_lib is None:
            from libacr import lib as acr_lib

        return acr_lib.getitem_for_lang(self.i18n_titles)

    @cached_property
    def i18n_menu_title(self):
        global acr_lib
        if acr_lib is None:
            from libacr import lib as acr_lib

        return acr_lib.getitem_for_lang(self.i18n_menu_titles)

    @cached_property
    def ancestors(self):
        ancestor = self.parent
        while ancestor:
            yield ancestor
            ancestor = ancestor.parent

    def is_visible(self, identity):
        rule = self.getattr('visibility')
        if not rule:
            return True

        rule = unicode(rule, 'utf-8')
        if rule == 'public':
            return True

        if rule == 'authenticated' and identity:
            return True

        if rule.startswith('group-'):
            try:
                trash, group = rule.split('-', 1)
            except:
                return False

            if group and (identity and (group in identity['groups'])):
                return True

        if rule == 'supported-languages':
            global acr_lib
            if acr_lib is None:
                from libacr import lib as acr_lib

            langs = [acr_lib.language()[0]]
            return self.get_title_for_lang(langs=langs, fallback=False) is not None

        return False

    def getattr(self, name):
        attr = DBSession.query(Attribute).filter_by(page=self)\
                                         .filter_by(name=name).first()
        if attr:
            return attr.value
        else:
            return None

    def setattr(self, name, value):
        attr = DBSession.query(Attribute).filter_by(page=self)\
                                         .filter_by(name=name).first()
        if attr:
            attr.value = value
        else:
            DBSession.add(Attribute(name=name, value=value, page=self))

class Slice(DeclarativeBase):
    class Hooks(MapperExtension):
        def before_delete(self, mapper, connection, instance):
            if len(instance.content.slices) == 1:
                DBSession.delete(instance.content)

    __mapper_args__ = {'extension': Hooks()}
    __tablename__ = 'acr_cms_slice'

    uid = Column(Integer, primary_key=True)
    name = Column(Unicode(128), nullable=False, index=True, unique=True)
    zone = Column(Unicode(30), default=u'main')
    view = Column(Unicode(30), default=u'html')
    slice_order = Column(Integer, default=0)

    tags = relation(Tag, secondary=tag_slice_map)

    content_uid = Column(Integer, ForeignKey(Content.uid, ondelete="CASCADE"))
    page_uid = Column(Integer, ForeignKey(Page.uid, ondelete="CASCADE"))

    @property
    def desc(self):
        return '%i : %s, %s' % (self.uid, self.view, self.content_uid)

    def preview(self, hightlight=None, omit_link=False, data=None):
        from libacr.lib import url as acr_url
        
        if not data:
            data = self.content.data

        soup = BeautifulSoup(data)
        text = soup.findAll(text=True)
        text = ' '.join(text)

        if not hightlight:
            text = ' '.join(text.split()[:60])
        else:
            boldize = re.compile('(%s)' % hightlight, re.IGNORECASE)

            text = ''.join(text)
            start_from = text.lower().find(hightlight.lower())
            if start_from < 0:
                start_from = 0

            count = 0
            while start_from > 0:
                start_from -= 1
                if text[start_from] == ' ':
                    count += 1

                if count > 3:
                    break

            text = text[start_from:].strip()
            text = ' '.join(text.split()[:60])
            text = boldize.sub(r'<strong>\1</strong>', text)

        if self.page and not omit_link:
            text += ' <a href="%s">[...]</a>' % acr_url(self.page.url)
        else:
            text += ' [...]'

        return text

    def getattr(self, name):
        attr = DBSession.query(Attribute).filter_by(slice=self)\
                                         .filter_by(name=name).first()
        if attr:
            return attr.value
        else:
            return None

    def setattr(self, name, value):
        attr = DBSession.query(Attribute).filter_by(slice=self)\
                                         .filter_by(name=name).first()
        if attr:
            attr.value = value
        else:
            DBSession.add(Attribute(name=name, value=value, slice=self))

