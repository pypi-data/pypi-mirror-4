DBSession = None
DeclarativeBase = None
metadata = None
User=None
Group=None

def init_acr_model(app_DBSession, app_DeclarativeBase,app_User,app_Group):
    global DBSession, DeclarativeBase, metadata, User, Group
    
    DBSession = app_DBSession
    DeclarativeBase = app_DeclarativeBase
    metadata = app_DeclarativeBase.metadata
    User=app_User
    Group=app_Group

    from comments import Comment
    from content import Content, ContentData, Tag, Page, Slice, View
    from assets import Asset
    from attributes import Attribute, UnrelatedAttribute
    from user_permission import AcrUserPermission
    return Content, ContentData, Tag, Page, Slice, View, Comment
