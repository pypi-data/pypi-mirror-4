import collections
from libacr.lib import IconLink, url
import formencode
import tw.forms as twf
import tw.dynforms as twdf
from tw.api import JSLink

adv_file_field_js = JSLink(modname='libacr', filename='static/advfile.js')

class AdvancedFileField(twf.FormField):
    icons = {'trash':IconLink(modname='libacr',
                        filename='static/icons/trash.png', alt='Trash'),
             'upload':IconLink(modname='libacr',
                        filename='static/icons/upload.png', alt='Upload')
            }
    params = ['icons']
    template = "libacr.templates.form_fields.advanced_file_field"
    javascript = [adv_file_field_js]
    file_upload = True


class AssetField(twf.FormField):
    template = "libacr.templates.form_fields.asset_field"
    javascript = [JSLink(modname='libacr', filename='static/asset.js')]
    icons = {'upload':IconLink(modname='libacr',
                        filename='static/icons/upload.png', alt='Upload'),
             'choose':IconLink(modname='libacr',
                        filename='static/icons/pick.png', alt='Choose')
            }
    assets_box_url = None
    assets_upload_url = None
    params = ['icons', 'assets_box_url', 'assets_upload_url']

    def prepare_dict(self, value, d, adapt=True):
        from libacr.model.core import DBSession
        from libacr.model.assets import Asset

        d = super(AssetField, self).prepare_dict(value, d, adapt)
        if not d['assets_box_url']:
            d['assets_box_url'] = url('/admin/assets/box')

        if not d['assets_upload_url']:
            d['assets_upload_url'] = url('/admin/assets')

        value = d['value']
        asset = None
        if not value:
            value = ''
        elif hasattr(value, 'startswith') and value.startswith('asset'):
            trash, asset_id = value.split(':')
            asset = DBSession.query(Asset).filter_by(uid=asset_id).first()
        
        d['value_id'] = value

        if asset:
            d['value_name'] = asset.name
        else:
            d['value_name'] = value

        return d

class AcrOtherChoiceValidator(formencode.Schema):
    if_missing = None
    select = formencode.validators.String()
    other = formencode.validators.String()

    def _to_python(self, value, state):
        val = super(AcrOtherChoiceValidator, self)._to_python(value, state)
        if val['select'] == 'other':
            return val['other']
        else:
            return val['select']

class AcrOtherSingleSelectField(twf.FormField):
    template = """
<span id="$id" xmlns:py="http://genshi.edgewall.org/">
    ${children['select'].display(select_value, **args_for(children['select']))}
    <span id="${children['other'].id}.container" py:attrs="args_for(children['other']).get('container_attrs')">$specify_text ${children['other'].display(value, **args_for(children['other']))}</span>
</span>
"""

    def __new__(cls, id=None, parent=None, children=[], **kw):
        children = [
            twdf.HidingSingleSelectField('select', mapping=dict(other=['other'])),
            twf.TextField('other'),
        ]
        return super(AcrOtherSingleSelectField, cls).__new__(cls, id, parent, children, **kw)

    def adapt_value(self, value):
        return value

    def update_params(self, kw):
        kw['select_value'] = 'other'
        _options = self.options() if isinstance(self.options, collections.Callable) else self.options
        for name, disp in _options:
            if name == kw['value']:
                kw['select_value'] = kw['value']

        options = []
        options.extend(_options)
        options.append(('other', 'Other'))
        kw.setdefault('child_args', {})['select'] = {'options': options}

        if kw['select_value'] != 'other':
            kw.setdefault('child_args', {})['other'] = {'container_attrs': {'style':'display:none'}}

        kw['specify_text'] = ''
        return super(AcrOtherSingleSelectField, self).update_params(kw)

    def post_init(self, *args, **kw):
        self.validator = AcrOtherChoiceValidator()