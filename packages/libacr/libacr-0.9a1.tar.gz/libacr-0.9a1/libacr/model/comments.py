from sqlalchemy import *
from sqlalchemy.orm import mapper, relation
from sqlalchemy import Table, ForeignKey, Column, asc, desc
from sqlalchemy.types import Integer, Unicode
from sqlalchemy.orm import relation, backref
from datetime import datetime

from core import DeclarativeBase

class Comment(DeclarativeBase):
    __tablename__ = 'acr_plugins_comment'
    
    uid = Column(Integer, primary_key=True)
    thread_id = Column(Unicode(32), index=True, nullable=False)
    time = Column(DateTime, default=datetime.now, index=True)
    content = Column(Unicode(2048), default=u"", nullable=False)
    
    owner_uid = Column(Integer, ForeignKey('tg_user.user_id', ondelete="CASCADE"), nullable=True)
    owner = relation('User', backref=backref('acr_comments'))
