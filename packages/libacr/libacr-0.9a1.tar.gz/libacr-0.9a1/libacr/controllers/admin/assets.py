from itertools import groupby
import json
from tg import expose, flash, require, url, request, redirect, tmpl_context, validate, config
from pylons.i18n import ugettext as _, lazy_ugettext as l_
from pylons.controllers.util import abort
from tg import predicates

from libacr import acr_zones, forms
from libacr.form_fields import AcrOtherSingleSelectField, AcrOtherChoiceValidator
from libacr.lib import url, current_user_id, language, icons, user_can_modify
from libacr.model.attributes import UnrelatedAttribute
from libacr.model.content import Content, ContentData
from libacr.model.core import DBSession
from libacr.model.assets import Asset

from tw.api import WidgetsList
import tw.forms as widgets
from formencode import validators
from libacr.views.manager import ViewsManager
from libacr.forms import order_values

import mimetypes, os
from datetime import datetime
from base import BaseAdminController, _create_node

def get_asset_categories():
    categories = DBSession.query(Content).filter(Content.name=="_acr_config_asset_cat").first()
    if categories is None:
        categories = Content(name="_acr_config_asset_cat")
        cdata = ContentData(content=categories, revision=0)
        cdata.set_property('asset', 'categories', json.dumps([['none', 'None'], ['images', 'Images']]))
        DBSession.add(categories)
        DBSession.add(cdata)
    cdata = categories.get_data_instance_for_lang()
    return json.loads(cdata.get_property('asset', 'categories'))

def set_asset_categories(cats):
    categories = DBSession.query(Content).filter(Content.name=="_acr_config_asset_cat").first()
    cdata = categories.get_data_instance_for_lang()
    cdata.revision += 1
    cdata.set_property('asset', 'categories', json.dumps(cats))
    DBSession.add(cdata)
    return 'ok'

class UploadAssetForm(widgets.TableForm):
    class fields(WidgetsList):
        from_box = widgets.HiddenField(default=0, validator=validators.Int(not_empty=True))
        uid = widgets.HiddenField()
        asset_file = widgets.FileField(label_text="File:",
                                       validator=validators.FieldStorageUploadConverter(not_empty=True))
        category = AcrOtherSingleSelectField('root', label_text="Category:", default='none',
            options=lambda: get_asset_categories(), validator=AcrOtherChoiceValidator())
asset_upload_form = UploadAssetForm()


class AssetsController(BaseAdminController):
    @expose('libacr.templates.admin.assets_index')
    @require(predicates.in_group("acr"))
    def index(self, *args, **kw):
        assets = DBSession.query(Asset).all()
        assets.sort(key=lambda a: a.category)
        groups = []
        keys = []
        for k, g in groupby(assets, lambda a: a.category):
            groups.append(list(g))
            keys.append(k)
        return dict(upload_form=asset_upload_form, values=kw, assets=groups, categories=keys)

    @expose()
    @require(predicates.in_group("acr"))
    @validate(asset_upload_form, error_handler=index)
    def upload(self, from_box, uid, asset_file, category=''):
        categories = get_asset_categories()
        category = category.lower()
        new_cat = [category, category.title()]
        if new_cat not in categories: categories.append(new_cat)
        set_asset_categories(categories)
        self.perform_store(asset_file, uid, category)
        flash('Asset Stored')

        if not from_box:
            return redirect(url('/admin/assets'))
        else:
            return redirect(url('/admin/assets/box'))

    @expose()
    @require(predicates.in_group("acr"))
    @validate({'upload': validators.FieldStorageUploadConverter()})
    def upload_from_ckeditor(self, **kw):
        self.perform_store(kw.get('upload'))
        return "Successfully uploaded..."

    def perform_store(self, asset_file, uid=0, category=None):
        if category is None: category = ""
        if not uid:
            asset = Asset(name=asset_file.filename, content_type=self.guess_mime(asset_file.filename))
            DBSession.add(asset)
            DBSession.flush()
        else:
            asset = DBSession.query(Asset).get(uid)
        asset.content_type=self.guess_mime(asset_file.filename)
        self.store_file(asset, asset_file.file)
        if category:
            UnrelatedAttribute.add('category', category, asset)

    @expose()
    @require(predicates.in_group("acr"))
    def delete(self, uid):
        asset = DBSession.query(Asset).filter_by(uid=uid).first()
        if asset:
            DBSession.delete(asset)
        flash('Asset Removed')
        return redirect(url('/admin/assets'))

    @expose('libacr.templates.admin.assets_box')
    @require(predicates.in_group("acr"))
    def box(self, uid=None, **kw):
        assets = DBSession.query(Asset).all()
        assets.sort(key=lambda a: a.category)
        groups = []
        keys = []
        for k, g in groupby(assets, lambda a: a.category):
            groups.append(list(g))
            keys.append(k)
        try:
            uid = int(uid)
        except:
            pass
        return dict(upload_form=asset_upload_form, selected_asset_id=uid,
            assets=groups, categories=keys, ckeditor_func=kw.get('CKEditorFuncNum'))

    def guess_mime(self, name):
        mimetypes.init()
        mime = mimetypes.guess_type(name, False)[0]
        if not mime:
            mime = 'application/octet-stream'
        return mime

    def store_file(self, asset, data):
        public_dir = config.get('public_dir')
        assets_path = os.path.join(public_dir, 'assets')

        if not os.path.exists(assets_path):
            os.makedirs(assets_path)

        asset.write(data)
