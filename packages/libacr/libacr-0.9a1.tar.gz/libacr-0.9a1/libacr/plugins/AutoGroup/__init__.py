from datetime import datetime
from tg import predicates
from tg.decorators import expose, require
from tw.core.resources import JSLink
from libacr.controllers.admin.base import BaseAdminController, _create_node
from libacr.model.content import Slice, Tag, Page
from libacr.model.core import DBSession, Group
from libacr.plugins.base import AcrPlugin, PluginStatic

__author__ = 'simock85'

class AutoGroupController(BaseAdminController):
    @expose()
    @require(predicates.in_any_group('acr', 'acr_editors'))
    def group(self, page, *slices):
        filter_tag = self._someone_is_grouped(slices)
        if self._someone_is_grouped(slices):
            if self._all_are_grouped(slices, filter_tag):
                return self._ungroup(page, slices, filter_tag)
        return self._group(page, slices, filter_tag)

    def _group(self, page, slices, filter_tag=None):

        #add internal tag if not exists
        if filter_tag is None:
            filter_tag = '_autogroup_%s' % datetime.now().strftime('%Y%m%d%H%M%S')
            tag_obj = Tag(name=filter_tag)
            internal_tags_group = DBSession.query(Group).filter_by(group_name='acr_internal_tags').first()
            if not internal_tags_group:
                internal_tags_group = Group(group_name='acr_internal_tags')
                DBSession.add(internal_tags_group)
            tag_obj.group = internal_tags_group
            DBSession.add(tag_obj)
            DBSession.flush()
        tag_obj = DBSession.query(Tag).filter(Tag.name==filter_tag).first()

        #add tag to slices and remove slices from page
        for slice in slices:
            slice_obj = DBSession.query(Slice).get(int(slice))
            slice_obj.tags.append(tag_obj)
            slice_obj.page = None

        #create content
        content = '[group]\n'
        content += 'filter_tag=%s\n' % filter_tag
        content += 'size=0\n'
        content += 'preview=0\n'
        content += 'orderer=Ascending Time\n'
        node_args = {}
        node_args['page'] = int(page)
        node_args['name'] = filter_tag
        node_args['zone'] = 'main'
        node_args['order'] = 0
        node_args['tags'] = []
        node_args['view'] = 'slicegroup'
        node_args['data'] = content
        node_args['skip_permission'] = True
        _create_node(**node_args)

        return 'OK'


    def _ungroup(self, page_id, slices, filter_tag):
        tag_obj = DBSession.query(Tag).filter(Tag.name==filter_tag).first()
        page = DBSession.query(Page).filter_by(uid=page_id).first()
        for slice in slices:
            slice_obj = DBSession.query(Slice).get(int(slice))
            slice_obj.tags.remove(tag_obj)
            slice_obj.page = page
        slice_group = DBSession.query(Slice).filter(Slice.name==filter_tag).first()
        DBSession.delete(slice_group)
        return 'OK'

    def _someone_is_grouped(self, slices):
        for slice in slices:
            slice_obj = DBSession.query(Slice).get(int(slice))
            tags = [tag.name for tag in slice_obj.tags if '_autogroup' in tag.name]
            if tags:
                return tags[0]
        return None

    def _all_are_grouped(self, slices, filter_tag):
        for slice in slices:
            slice_obj = DBSession.query(Slice).get(int(slice))
            tags = [tag.name for tag in slice_obj.tags if filter_tag in tag.name]
            if not tags:
                return False
        return True


class AutoGroupPlugin(AcrPlugin):
    uri = 'autogroup'

    def __init__(self):
        self.js_resources = [JSLink(link=PluginStatic(self, 'acr_autogroup.js'))]
        self.controller = AutoGroupController()

