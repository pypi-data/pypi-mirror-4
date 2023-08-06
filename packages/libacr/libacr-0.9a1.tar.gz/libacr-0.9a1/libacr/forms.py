from tg import predicates

from tw.api import WidgetsList
from tw.forms import SingleSelectField, TextArea, TextField, FieldSet, MultipleSelectField
from tw.dynforms import GrowingRepeater, GrowingTableFieldSet
from sprox.formbase import EditableForm, AddRecordForm
from sprox.widgets import PropertyMultipleSelectField
from tw.forms.fields import HiddenField

from libacr.model.core import DBSession
from libacr.model.content import Slice, Page, Content, View, Tag
from libacr import acr_zones
from libacr.views.manager import ViewsManager
from libacr.lib import url
import tw.forms as widgets

from sqlalchemy import not_

def form_factory(template, form_parent):
    return type(template.__name__ + form_parent.__name__, (form_parent,), dict(template.__dict__))

order_values = [0]
order_values.extend(xrange(-10, 0))
order_values.extend(xrange(1, 11))

class AttributesFieldSet(GrowingTableFieldSet):
    children = [
        TextField('name', label_text = "Name", attrs=dict(style="width:75px")),
        TextField('value', label_text = "Value", attrs=dict(style="width:115px"))
    ] 

class EditSliceForm(EditableForm):
    __model__ = Slice
    __base_widget_args__ = {'attrs':{"onsubmit": "twd_blank_deleted()"}}
    __omit_fields__ = ['view_uid', 'content_uid', 'page_uid', 'view', 'slice_order', 'content']
    __hide_fields__ = ['uid']
    __field_order__ = ['uid', 'name', 'page', 'zone', 'tags', 'attributes']
    __dropdown_field_names__ = {'page' : 'title'}
    zone = SingleSelectField('zone', options=zip(acr_zones, acr_zones))
    tags = MultipleSelectField('tags', options=lambda : ((p.uid, p.name) for p in DBSession.query(Tag).filter(not_(Tag.name.like('_depo_%')))))
    attributes = AttributesFieldSet('attributes')

class CloneSliceForm(EditableForm):
    __model__ = Slice
    __omit_fields__ = ['view_uid', 'content_uid', 'page_uid', 'view', 'slice_order', 
                       'content', 'zone', 'name', 'tags', 'attributes']
    __hide_fields__ = ['uid']
    __field_order__ = ['uid']
    __dropdown_field_names__ = {'page' : 'title'}

class EditPageForm(EditableForm):
    __model__ = Page
    __base_widget_args__ = {'attrs':{"onsubmit": "twd_blank_deleted()"}}
    __omit_fields__ = ['children', 'parent_uid', 'slices']
    __hide_fields__ = ['uid']
    __dropdown_field_names__ = {'page' : 'title'}
    __field_order__ = ['uid', 'parent', 'uri', 'title']
    __require_fields__ = ['uri', 'title']
    attributes = AttributesFieldSet('attributes')

class EditContentForm(EditableForm):
    __model__ = Content
    __base_widget_args__ = {'attrs':{'target':'_top'}}
    __require_fields__ = ['name']
    __omit_fields__ = ['uid', 'slices', 'all_data']
    data = TextArea('data')

class EditTagForm(EditableForm):
    __model__ = Tag
    __require_fields__ = ['name']
    __omit_fields__ = ['uid']

class EditViewForm(EditableForm):
    __model__ = View
    __require_fields__ = ['name', 'code', 'viewfields', 'preview']
    __hide_fields__ = ['uid']
    __omit_fields__ = ['type']
    viewfields = TextArea('viewfields', label_text="Fields Definition")
    preview = TextArea('preview', label_text="Preview Template")
