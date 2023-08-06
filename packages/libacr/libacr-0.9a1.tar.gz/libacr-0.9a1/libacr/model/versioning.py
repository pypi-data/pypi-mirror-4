from sqlalchemy import *
from sqlalchemy.orm import mapper, relation
from sqlalchemy import Table, ForeignKey, Column, asc, desc
from sqlalchemy.types import Integer, Unicode
from sqlalchemy.orm import relation, backref
from sqlalchemy.orm.interfaces import MapperExtension
from datetime import datetime

from core import DeclarativeBase, DBSession

class Version(DeclarativeBase):
    __tablename__ = 'acr_cms_versions'

    uid = Column(Integer, primary_key=True)
    module = Column(Unicode(64), nullable=False, index=True)
    number = Column(Integer, nullable=False, index=True)
 
