from sqlalchemy import *
from sqlalchemy.orm import mapper, relation
from sqlalchemy import Table, ForeignKey, Column, asc, desc
from sqlalchemy.types import Integer, Unicode
from sqlalchemy.orm import relation, backref
from sqlalchemy.orm.interfaces import MapperExtension
from datetime import datetime

from core import DeclarativeBase, DBSession

class AcrUserPermission(DeclarativeBase):
    __tablename__ = 'acr_users_permissions'

    permission_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('tg_user.user_id'), nullable=False)
    user = relation ('User', backref=backref('acr_users_permissions'))
    page = Column(Unicode(100), nullable=False)
    can_edit = Column(Integer, default=0)
    can_create_children = Column(Integer, default=0)
