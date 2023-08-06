from sqlalchemy import *
from sqlalchemy.orm import mapper, relation
from sqlalchemy import Table, ForeignKey, Column, asc, desc
from sqlalchemy.types import Integer, Unicode
from sqlalchemy.orm import relation, backref
from sqlalchemy.orm.interfaces import MapperExtension
from datetime import datetime

from BeautifulSoup import BeautifulSoup
from core import DeclarativeBase, DBSession
import re
from ConfigParser import ConfigParser
from StringIO import StringIO

class Attribute(DeclarativeBase):
    __tablename__ = 'acr_cms_attributes'

    uid = Column(Integer, primary_key=True)
    name = Column(Unicode(128), nullable=False, index=True)
    value = Column(Binary(4*1024*1024))
   
    slice_uid = Column(Integer, ForeignKey('acr_cms_slice.uid'))
    slice = relation('Slice', backref=backref('attributes', cascade='all, delete-orphan'))
    
    page_uid = Column(Integer, ForeignKey('acr_cms_page.uid'))
    page = relation('Page', backref=backref('attributes', cascade='all, delete-orphan'))

class UnrelatedAttribute(DeclarativeBase):
    __tablename__ = 'acr_cms_unrelated_attrs'

    uid = Column(Integer, primary_key=True)
    name = Column(Unicode(128), nullable=False)
    value = Column(Unicode(255), index=True)
    related_to_entity = Column(Unicode(32), index=True)
    related_to_entity_id = Column(Integer, index=True)

    @classmethod
    def existence_check(cls):
        return DBSession.get_bind().has_table(cls.__tablename__)

    @classmethod
    def of_object(cls, obj, name=None):
        if not cls.existence_check():
            return None
        attrs = DBSession.query(cls).filter(cls.related_to_entity==obj.__class__.__name__,
            cls.related_to_entity_id==obj.uid)
        if name is not None:
            return attrs.filter(cls.name==name).first()
        return attrs.all()

    @classmethod
    def add(cls, name, value, object):
        if not cls.existence_check():
            return
        attr_exist = DBSession.query(cls).filter(cls.name==name, cls.related_to_entity==object.__class__.__name__,
            cls.related_to_entity_id==object.uid).first()
        attr = attr_exist if attr_exist else cls()
        attr.name = name
        attr.value = value
        attr.related_to_entity = object.__class__.__name__
        attr.related_to_entity_id = object.uid
        DBSession.add(attr)
        DBSession.flush()
