# -*- coding: utf-8 -*-
from tg import tmpl_context
from libacr.lib import url as acr_url
from libacr.lib import language
from genshi.template import MarkupTemplate

from libacr.model.core import DBSession
from libacr.model.content import Page, Tag
import tw.forms as twf

from base import EncodedView
from ConfigParser import ConfigParser
from StringIO import StringIO

from paste.util.multidict import MultiDict

class FormRenderer(EncodedView):
    def __init__(self):
        self.name = 'form'

        self.exposed = True
        self.form_fields = [twf.TextField('email_address', label_text="Destination Email:",
                                                           validator=twf.validators.Email(strip=True)),
                            twf.TextField('subject', label_text="Subject:",
                                                           validator=twf.validators.String(not_empty=True, strip=True)),
                            twf.TextArea('fields', label_text="Fields:", validator=twf.validators.String(not_empty=True),
                                                   rows=20, attrs={'style':'width:600px;height:400px;'}),
                            twf.SingleSelectField('save_tag', label_text="Save with tag",
                                                  options=lambda : (["do not save"] + [p.name for p in DBSession.query(Tag)]))
                           ]

    def parse_fields(self, fields):
        try:
            pfields = ConfigParser(dict_type=MultiDict)
        except:
            pfields = ConfigParser()
        pfields.readfp(StringIO('[fields]\n' + fields))
        return pfields.items('fields')

    def to_dict(self, data):
        config = super(FormRenderer, self).to_dict(data)
       
        d = MultiDict({'email_address' : config.get('email_address', ''),
                             'subject' : config.get('subject'),
                            'save_tag' : config.get('save_tag')})

        fields = ''
        for field in config.items():
            if field[0] not in d.keys():
                fields += '%s=%s\n' % (field[0], field[1])

        d['fields'] = fields
        return d
        
    def from_dict(self, dic):
        d = MultiDict()
        d['email_address'] = dic['email_address']
        if d['email_address'] is None:
            d['email_address'] = ''

        d['subject'] = dic['subject']
        d['save_tag'] = dic['save_tag']
        
        for field in self.parse_fields(dic['fields']):
            d[field[0]] = field[1]

        return super(FormRenderer, self).from_dict(d)

    def preview(self, page, slice, data):
        return 'Preview not Implemented'

    def render(self, page, slice, data):
        config = self.to_dict(data)
        items = self.parse_fields(config['fields'])

        list_items = []
        form = '<div class="form">'
        form += '<form enctype="multipart/form-data" method="post" action=%s >' % (acr_url('/process_form'))

        form += '<table>'
        for item in items:
            form += '<tr class="%s_field">' % (item[0])
            form += '<td class="form_label %s"> %s </td>' % (item[0][0]=='*' and 'required' or '', item[0].lstrip('*'))
            
            item1 = item[1]
            if item1[0] == '[':
                form += '<td class="form_field"><select name="%s">' % (item[0])
                list_items = item[1].lstrip('[').rstrip(']').split(',')
                for value in list_items:
                    form += '<option value="%s">%s</option>' % (value, value)
                form += '</select></td>'
            elif item[1].lower() == 'textarea':
                form += '<td class="form_field"> <textarea name="%s">' % (item[0])
                form += '</textarea> </td>'
            elif item[1].lower() == 'file':
                form += '<td class="form_field"> <input type="file" name="%s" />' % (item[0])
                form += '</td>'
            else:
                form += '<td class="form_field"><input type="%s" name="%s"/> </td>' % (item[1], item[0])

            form += '</tr>'
        form += '</table>'

        form += '<div> <input type="hidden" name="slice_id" value="%s" />' % (slice.uid)
        form += '<input type="submit" value="submit" /></div>'

        form += '</form>'
        form += '</div>'
        return form
