from tg import expose, flash, require, request, response, redirect, tmpl_context, validate
from pylons.i18n import ugettext as _, lazy_ugettext as l_
from pylons.controllers.util import abort
from tg import predicates

from libacr.views.manager import ViewsManager
from libacr.lib import url, get_page_from_urllist, user_can_create_children_in_page, user_can_edit

from base import BaseAdminController, _create_node
from pages import PagesAdminController
from slices import SlicesAdminController
from views import ViewsAdminController
from assets import AssetsController

from tw.api import WidgetsList
import tw.forms as widgets
from formencode import validators

from libacr.views.manager import ViewsManager
from libacr.plugins.manager import PluginsManager
from libacr import acr_zones
from libacr.forms import order_values
from libacr.model.core import DBSession, User, Group
from libacr.model.content import Tag, Content, Slice, ContentData, Page
from libacr.model.user_permission import AcrUserPermission

try:
    from sets import Set as set
    from sets import ImmutableSet as frozenset
except:
    pass

import mimetypes, base64

__all__ = ['AdminController']

class CreateSliceGroupForm(WidgetsList):
    page= widgets.SingleSelectField(label_text="Page:",
                                       options=lambda : [(None, '----------')] + \
                                                        [(p.uid, p.title) for p in DBSession.query(Page)])
    name = widgets.TextField(label_text="Name", validator=validators.NotEmpty())
    filter_tag = widgets.SingleSelectField(label_text='Filter',
                                           validator=validators.NotEmpty(),
                                           options=lambda : (p.name for p in DBSession.query(Tag)))
    preview = widgets.SingleSelectField(label_text='Preview',
                                        options=((0, "No"), (1, "Yes")))
    paginate = widgets.SingleSelectField(label_text='Paginate',
                                         options=((0, "Disabled"),
                                                  (5, "5"),
                                                  (10, "10"),
                                                  (20, "20")))
    orderer = widgets.SingleSelectField(label_text='Order',
                                         options=(('', "Ascending Time"),
                                                  ('content_time', "Descending Time")))
create_slicegroup_form = widgets.TableForm(fields=CreateSliceGroupForm(), submit_text="Create")

class CreateTagForm(WidgetsList):
    name = widgets.TextField(label_text="Name:", validator=validators.NotEmpty())
    visibility = widgets.SingleSelectField(label_text="Visibility:", options=['public', 'internal'], default='public')
create_tag_form = widgets.TableForm(fields=CreateTagForm(), submit_text="Create")

class CreateUserForm(WidgetsList):
    user_name = widgets.TextField(label_text="User Name:", validator=validators.NotEmpty())
create_user_form = widgets.TableForm(fields=CreateUserForm(), submit_text="Add")

class AdminController(BaseAdminController):
    pages = PagesAdminController()
    slices = SlicesAdminController()
    views = ViewsAdminController()
    assets = AssetsController()

    @require(predicates.in_group("acr"))
    @expose('libacr.templates.admin.main')
    def index(self):
        return dict(views=ViewsManager.view_names(),
                    plugin_actions=PluginsManager.admin_actions())

    @expose('libacr.templates.admin.unbound')
    @require(predicates.in_group("acr"))
    def unbound(self):
        unbound_slices = DBSession.query(Slice).filter_by(page=None).all()
        unbound_contents = DBSession.query(Content).outerjoin(Slice).filter(Slice.uid == None).all()
        return dict(uslices=unbound_slices, ucontents=unbound_contents,
                     section_title="Manage Unbound Entities")

    @expose()
    @require(predicates.in_group("acr"))
    def delete_content(self, uid, came_from):
        if came_from != 'unbound' and not user_can_edit(None):
            flash('You cannot delete this content', 'error')
            return redirect(url('/admin'))

        cnt = DBSession.query(Content).get(uid)
        DBSession.delete(cnt)

        flash('Content successfully deleted')
        if came_from == 'unbound':
            return redirect(url('/admin/unbound'))

    @expose('libacr.templates.admin.slicegroups')
    @require(predicates.in_group("acr"))
    def slice_groups(self, **kw):
        slice_groups = DBSession.query(Slice).filter_by(view='slicegroup').all()
        return dict(slice_groups=slice_groups, create_form=create_slicegroup_form,
                     section_title="Slice Groups")

    @expose()
    @validate(create_slicegroup_form, error_handler=slice_groups)
    @require(predicates.in_group("acr"))
    def create_slicegroup(self, **kw):
        content = '[group]\n'
        content += 'filter_tag=%s\n' % kw['filter_tag']
        content += 'size=%s\n' % kw['paginate']
        content += 'preview=%s\n' % kw['preview']
        if kw['orderer']:
            content += 'orderer=%s\n' % kw['orderer']

        node_args = {}
        node_args['page'] = kw['page']
        node_args['name'] = kw['name']
        node_args['zone'] = 'main'
        node_args['order'] = 0
        node_args['tags'] = []
        node_args['view'] = 'slicegroup'
        node_args['data'] = content

        _create_node(**node_args)
        flash('SliceGroup successfully created')
        return redirect(url('/admin/slice_groups'))

    @expose('libacr.templates.admin.tags')
    @require(predicates.in_group("acr"))
    def tags(self, **kw):
        tags = DBSession.query(Tag).all()
        return dict(tags=tags, create_form=create_tag_form,
                     section_title="Tags")

    @expose('libacr.templates.admin.tag_members')
    @require(predicates.in_group("acr"))
    def tag_members(self, **kw):
        tag = DBSession.query(Tag).filter_by(name=kw['tag']).one()
        contents=[]
        props=set()
        
        for i in tag.contents:
            i_props = i.data_instance._properties
            section = i_props.sections()[0]

            data = dict(i_props.items(section))
            props |= frozenset(data.keys())
            contents.append(dict(item=i, data=data, binaries=[p for p,v in data.iteritems() if v.startswith('data:')]))
        
        return dict(tag=tag, props=props, contents=contents, section_title="Tags")

    @expose()
    @validate(create_tag_form, error_handler=tags)
    @require(predicates.in_group("acr"))
    def create_tag(self, **kw):
        visibility = kw.get('visibility', 'public')

        t = Tag(name=kw['name'])
        if visibility != 'public':
            internal_tags_group = DBSession.query(Group).filter_by(group_name='acr_internal_tags').first()
            if not internal_tags_group:
                internal_tags_group = Group(group_name='acr_internal_tags')
                DBSession.add(internal_tags_group)
            t.group = internal_tags_group
        DBSession.add(t)

        flash('Tag successfully created')
        return redirect(url('/admin/tags'))

    @expose()
    @require(predicates.in_group("acr"))
    def delete_tag(self, uid):
        t = DBSession.query(Tag).get(uid)
        DBSession.delete(t)

        flash('Tag successfully deleted')
        return redirect(url('/admin/tags'))


    @expose('libacr.templates.admin.users')
    @require(predicates.in_group("managers"))
    def user_permission(self, **kw):
        users_permissions = DBSession.query(AcrUserPermission).order_by(AcrUserPermission.user_id).all()
        return dict(users=users_permissions, create_form=create_user_form)

    @expose()
    @require(predicates.in_group("managers"))
    def update_user(self, can_edit=None, can_create_children=None, **kw):
        uri = kw['uri']
        permission_id = kw['permission_id']
        user_permission = DBSession.query(AcrUserPermission).filter_by(permission_id=int(permission_id)).first()
        if uri == "all":
            user_permission.page = 'all'
            if can_edit and can_create_children:
               user_permission.can_edit = 1
               user_permission.can_create_children = 1
            else:
                 user_permission.can_edit = 0
                 user_permission.can_create_children = 0
            flash('Permissions successfully added')
            redirect(url('/admin/user_permission'))
        else:
            page_url = uri[1:].strip()
            page = get_page_from_urllist(page_url.split('/'))
            if not page:
               flash('Invalid page url')
               redirect(url('/admin/user_permission'))

            edit = 0
            children = 0
            if can_edit: edit = 1
            if can_create_children: children = 1
            user_permission.page = page.url
            user_permission.can_edit = edit
            user_permission.can_create_children = children

            flash('Permission successfully added')
            redirect(url('/admin/user_permission'))

    @expose()
    @require(predicates.in_group("managers"))
    def add_user(self, **kw):
        user_name = kw['user_name']
        user = DBSession.query(User).filter_by(user_name=user_name).first()
        if user == None:
           flash('NO USER NAME')
           redirect(url('/admin/user_permission'))
        group = DBSession.query(Group).filter_by(group_name='acr').first()
        user_present = DBSession.query(User).filter_by(user_name=user_name).filter(User.groups.contains(group)).first()
        if user_present == None:
           user.groups.append(group)
        permission = AcrUserPermission(user=user, page='all', can_edit=0, can_create_children=0)
        DBSession.add(permission)
        flash('User added successfully')
        return redirect(url('/admin/user_permission'))

    @expose()
    @require(predicates.in_group("managers"))
    def deleteUserPermission(self, permission_id=None, **kw):
        user_permission = DBSession.query(AcrUserPermission).filter_by(permission_id=permission_id).first()
        DBSession.delete(user_permission)

        flash('Permission successfully deleted')
        redirect(url('/admin/user_permission'))
