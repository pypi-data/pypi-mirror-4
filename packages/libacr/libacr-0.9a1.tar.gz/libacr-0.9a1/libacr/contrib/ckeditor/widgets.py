"""
CKEditor for ToscaWidget

Bundles CKEditor from http://ckeditor.com/

Copyright 2012 Simone Marzola <simone.marzola@axant.it>

freely inspired by TinyMCE plugin (Alberto Valverde Gonzalez)

Licensed under the GNU GPL Open Source License.
"""
import collections
import os
import re
from warnings import warn

from pkg_resources import resource_filename

from tw.api import JSLink, js_function
from tw.forms import TextArea
from tw.forms.validators import UnicodeString

from genshi.core import Markup, stripentities

__all__ = ["CKEditor", "MarkupConverter",
           "ckeditor_js"]

class MarkupConverter(UnicodeString):
    """Will make sure the text that reaches python will be unicode un-xml-escaped
    HTML content.

    Will also remove any trailing <br />
    """
    cleaner = re.compile(r'(\s*<br />\s*)+$').sub
    if_missing = ''

    def _to_python(self, value, state=None):
        value = super(MarkupConverter, self)._to_python(value, state)
        if value:
            value = Markup(stripentities(value)).unescape()
            return self.cleaner('', value)


def _get_available_languages():
    filename_re = re.compile(r'(\w+)\.js')
    locale_dir = resource_filename("libacr.contrib.ckeditor", "static/lang")
    langs = []
    for filename in os.listdir(locale_dir):
        match = filename_re.match(filename)
        if match:
            langs.append(match.groups(0)[0])
    return langs

from tw.jquery.base import jquery_js

ckeditor_js = JSLink(
    modname = "libacr.contrib.ckeditor",
    filename = 'static/ckeditor.js',
    javascript = [jquery_js],
    replace = js_function('CKEDITOR.replace'),
    )

#using the same configuration of tgapp.smallpress editor
ckeditor_config = {
    'width': 630,
    'height': 400,
    'toolbar_Smallpress': [
            {'name': 'document', 'items': ['Source','-','Save','NewPage','DocProps','Preview','Print','-','Templates']},
            {'name': 'clipboard', 'items': ['Cut','Copy','Paste','PasteText','PasteFromWord','-','Undo','Redo']},
            {'name': 'editing', 'items': ['Find','Replace','-','SelectAll','-','SpellChecker', 'Scayt']},
            {'name': 'forms', 'items': ['Form', 'Checkbox', 'Radio', 'TextField', 'Textarea', 'Select', 'Button', 'ImageButton', 'HiddenField']},
            {'name': 'basicstyles', 'items': ['Bold','Italic','Underline','Strike','Subscript','Superscript','-','RemoveFormat']},
            {'name': 'paragraph', 'items': ['NumberedList','BulletedList','-','Outdent','Indent','-','Blockquote','CreateDiv','-','JustifyLeft','JustifyCenter','JustifyRight','JustifyBlock','-','BidiLtr','BidiRtl']},
            {'name': 'links', 'items': ['Link','Unlink','Anchor']},
            {'name': 'insert', 'items': ['Image','Flash','Table','HorizontalRule','Smiley','SpecialChar','PageBreak']},
            {'name': 'styles', 'items': ['Styles','Format','Font','FontSize']},
            {'name': 'colors', 'items': ['TextColor']},
            {'name': 'tools', 'items': ['Maximize', 'ShowBlocks','-','About']}
    ],
    'toolbar': 'Smallpress',
    'uiColor': '#F9ECE5',
    'filebrowserBrowseUrl': '/acr/admin/assets/box',
    'filebrowserWindowWidth': '640',
    'filebrowserWindowHeight': '480',
    'filebrowserUploadUrl': '/acr/admin/assets/upload_from_ckeditor'
}


class CKEditor(TextArea):
    """CKEditor WYSIWYG text editor.

    You can pass options directly to CKEDITOR JS object at construction or
    display via the ``ck_config`` dict parameter.

    Allows localization. To see available languages peek into the ``langs``
    attribute of the CKEDITOR class. Language codes can be passed as the
    ``locale`` parameter to display or provide a default at construction
    time. To dynamically switch languages based on HTTP headers a callable
    can be passed to return a language code by parsing/fetching headers
    whereever the app/framework makes them available. Same technique can be
    used to use cookies, session data or whatever.

    If a custom validator is supplied, it is recommended that it inherits from
    ``MarkupConverter`` to deal with markup
    conversion and unicode issues.
    """
    javascript = [ckeditor_js]
    langs = _get_available_languages()
    locale = 'en'
    params = ["ck_config", "locale"]
    cols = 79
    rows = 25
    ck_config = {}
    validator = MarkupConverter
    css_class = 'ck_editor' #avoid to triggers the automatic replacement


    def update_params(self, d):
        super(CKEditor, self).update_params(d)
        config = ckeditor_config.copy()
        config.update(d.ck_config)
        if isinstance(d.locale, collections.Callable): d.locale=d.locale()
        if d.locale not in self.langs:
            warn("Language file for '%s' not available, using en" % d.locale)
            d.locale = 'en'
        config['language'] = d.locale

        self.add_call(ckeditor_js.replace(d.id, config))
