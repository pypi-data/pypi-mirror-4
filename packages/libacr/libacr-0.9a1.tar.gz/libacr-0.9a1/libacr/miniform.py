import tw.forms as twf
from libacr.contrib.ckeditor.widgets import CKEditor
from libacr.form_fields import AdvancedFileField, AssetField

from paste.util.multidict import MultiDict
import json

VALIDATORS = {'email':twf.validators.Email,
              'text':twf.validators.UnicodeString,
              'file':twf.validators.FieldStorageUploadConverter}

WIDGETS = {'text':twf.TextField,
           'textarea':twf.TextArea,
           'html':CKEditor,
           'select':twf.SingleSelectField,
           'file':AdvancedFileField,
           'asset':AssetField}

def form_loads(definition):
    dict_def = json.loads(definition, object_pairs_hook=MultiDict)
    return form_build(dict_def)

def form_build(definition):
    return twf.TableForm(fields=form_collect_fields(definition), submit_text="Save")

def form_collect_fields(definition):
    fields = []
    for uid, data in definition:
        if data.get('type') is None:
            field = twf.TableFieldSet(uid, fields=form_collect_fields(data))
        else:
            validator_config = {'not_empty':data.pop('required', False)}
            validator_type = VALIDATORS[data.pop('validate', 'text')]
            validator = validator_type(**validator_config)

            if 'value' in data:
                data['default'] = data.pop('value')
            data['label_text'] = data.pop('label', None)
            if data['label_text'] is None:
                data['label_text'] = '%s:' % uid.capitalize()

            field_type = WIDGETS[data.pop('type', 'text')]
            field = field_type(uid, validator=validator, **data)
        fields.append(field)
    return fields