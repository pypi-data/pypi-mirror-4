# -*- coding: utf-8 -*-
"""Main Controller"""

from tg import expose, flash, require, url, request, response, redirect, tmpl_context, TGController, validate, session
from tg import config
from tg.i18n import set_lang
from formencode import validators
from pylons.i18n import ugettext as _, lazy_ugettext as l_
from pylons.controllers.util import abort, etag_cache
import cgi, os

from tg import predicates

from comments import CommentsController
from rdisk import RDiskController
from libacr.plugins.controller import PluginsController

from admin.dashboard import AdminController

from libacr import model
from libacr.model.core import DBSession
from libacr.model.content import Page, Slice, Content, View, ContentData, Tag
from libacr.lib import url, get_page_from_urllist, current_user_id, language, user_can_modify
from libacr.rss import rss_for_slicegroup
from libacr.views.manager import ViewsManager

from datetime import datetime
import mimetypes, base64, time, StringIO, Image

from turbomail import Message
from turbomail.control import interface

from tg.controllers import WSGIAppController
try:
    from tg.controllers import CUSTOM_CONTENT_TYPE
except:
    CUSTOM_CONTENT_TYPE = None

from paste.urlparser import StaticURLParser

__all__ = ['AcrRootController']

class AssetsFilesController(TGController):
    @expose()
    def lookup(self, *args):
        public_dir = config.get('public_dir')
        assets_path = os.path.join(public_dir, 'assets')
        return WSGIAppController(StaticURLParser(assets_path)), args
    _lookup = lookup

class AcrRootController(TGController):
    comments = CommentsController()
    admin = AdminController()
    plugins = PluginsController()
    assets = AssetsFilesController()

    @expose('libacr.templates.page')
    def default(self, *args, **kwargs):
        if not args:
            args = ['index']

        try:
            migrations_manager = self.migrations_manager
        except AttributeError:
            from libacr.migrations import MigrationsManager
            migrations_manager = self.migrations_manager = MigrationsManager
        migrations_manager.check_and_evolve()

        page = get_page_from_urllist(args)
        if not page or not page.is_visible(request.identity):
            return abort(404, "Page not found")

        session['last_page_id'] = page.uid
        session.save()

        return dict(page=page)

    _default = default

    @expose('libacr.templates.page')
    def page(self, pageid, *args, **kwargs):
        try:
            page = DBSession.query(Page).filter_by(uid=pageid).one()
        except:
            return redirect('/')
            
        if not page.is_visible(request.identity):
            return abort(404, "Page not found")

        session['last_page_id'] = pageid
        session.save()

        return dict(page=page)

    @expose('libacr.templates.slice')
    def slice(self, sliceid):
        try:
            slice = DBSession.query(Slice).filter_by(uid=sliceid).one()
        except:
            abort(404, "Slice not found")

        page = DBSession.query(Page).filter_by(uri='default').one()
        return dict(page=page, slice=slice)

    @expose(content_type="application/rss+xml")
    def rss(self, sliceid):
        from libacr.views.slice_group import SliceGroupRenderer
        try:
            slice = DBSession.query(Slice).filter_by(uid=sliceid).one()
            u = slice.page.url
        except:
            abort(404, "Slice not found")

        if slice.view != 'slicegroup':
            abort(403, "Invalid slice type")

        return rss_for_slicegroup(slice)

    @expose('libacr.templates.search')
    def search(self, searchid, what):
        search_slice = DBSession.query(Slice).filter_by(uid=searchid).first()
        if not search_slice:
            abort(404, "Invalid Search")

        from libacr.views.search import SearchRenderer
        results = SearchRenderer.perform(search_slice, what)

        return dict(page=search_slice.page, what=what, results=results, showpage=True)

    @expose('libacr.templates.search')
    def filter_tag(self, tag):
        results = []
        tag = DBSession.query(Tag).filter_by(name=tag).first()
        if tag:
            results = tag.slices

        page = DBSession.query(Page).filter_by(uri='default').one()
        return dict(page=page, what=tag.name, results=results, showpage=False)

    @expose()
    def set_language(self, lang):
        set_lang(lang)
        return 'OK'

    @expose()
    @require(predicates.in_group("acr"))
    def move_slice(self, sliceid, value):
        try:
            slice = DBSession.query(Slice).filter_by(uid=sliceid).one()
            slice.slice_order += int(value)
        except Exception, e:
            abort(404, "Slice not found")
        return ''

    @expose(content_type=CUSTOM_CONTENT_TYPE)
    @validate(validators=dict(thumb=validators.Int(), entryid=validators.Int(not_empty=True)))
    def data(self, entryid, field, entry_type='slice', thumb=0, **kw):
        if entry_type == 'slice':
            try:
                slice = DBSession.query(Slice).filter_by(uid=entryid).one()
            except Exception, e:
                abort(404, "Slice not found")

            data_instance = slice.content.data_instance

            del response.headers['Cache-Control']
            del response.headers['Pragma']
            response.last_modified = data_instance.time
            response.cache_expires(120)
            etag_cache('%s-%s' % (entryid, data_instance.uid))

            slice_data = ViewsManager.decode(slice.view, data_instance.value)
            field_data = slice_data[field]
        elif entry_type == 'content':
            try:
                content = DBSession.query(Content).filter_by(uid=entryid).one()
            except Exception, e:
                abort(404, "Content not found")
            field_data = content.data_instance.get_property(None, field)

        if not field_data.startswith('data'):
            abort(403, "Content is not data")

        #data:mime/mime;base64,encoded_data
        info, encoded_data = field_data.split(',', 1)
        mtype, encoding = info.rsplit(';', 1)
        mtype = mtype.split(':', 1)[1]

        response.headers['Content-Type'] = str(mtype)
        response.headers['Content-Disposition'] = str('inline;filename=%s' % (field + mimetypes.guess_extension(mtype)))

        if thumb and mtype.startswith('image'):
            imgfile = StringIO.StringIO(base64.b64decode(encoded_data))
            imginst = Image.open(imgfile)
            imginst.thumbnail((96,96))
            imgout = StringIO.StringIO()
            imginst.save(imgout, "PNG")
            return imgout.getvalue()

        return base64.b64decode(encoded_data)

    @expose()
    def process_form(self, **kw):
        form_content = ''
        form_data = ''
        missing_value = ''
        files = []
        try:
            slice = DBSession.query(Slice).filter_by(uid=kw['slice_id']).one()
        except Exception, e:
            abort(404, "Slice not found")

        config = ViewsManager.find_view(slice.view).to_dict(slice.content.data)
        email_address = config.get('email_address')
        subject = config.get('subject')
        save_tag = config.get('save_tag')
        save_tag = False if save_tag == "do not save" else save_tag
        del kw['slice_id']

        if not email_address and not save_tag:
            flash('Form is not correctly configured')
            return redirect('/')

        if save_tag:
            form_content = Content(name='_acr_form_%s_data_%s' % (save_tag, str(time.time())))
            form_content.tags.append(DBSession.query(Tag).filter_by(name=save_tag).one())
            form_data = ContentData(content=form_content, revision=0)

        content = '<html><body>'
        content += '<table>'

        for item in kw:
                value = kw[item]
                isfile = isinstance(value, cgi.FieldStorage)

                if item.startswith('*') and not value:
                    missing_value += item + ',  '

                if isfile:
                    files.append(value)
                    saved_value = "data:%s;base64," % (mimetypes.guess_type(value.filename)[0] or "application/octet-stream")
                    saved_value += base64.b64encode(value.file.read())
                else:
                    saved_value = value

                content += '<tr>'
                content += '<td> %s </td>' % (item.lstrip('*'))
                content += '<td> = </td>'
                content += '<td> %s </td>' % (isfile and value.filename or value)
                content += '</tr>'

                if save_tag:
                    form_data.set_property('form_data', item.lstrip('*'), saved_value)

        content += '</table>'
        content += '</body></html>'

        if missing_value != '':
           flash('Please specify the following fields: ' + missing_value)
           return redirect(request.headers['Referer'])

        if save_tag:
            DBSession.add(form_content)
            DBSession.add(form_data)

        if email_address:
            msg = Message(author="acr@acrcms.org",
                          to=email_address,
                          subject=subject,
                          plain="email",
                          rich=content,
                          encoding="utf-8")
            for item in files:
                item.file.seek(0)
                msg.attach(item.file, item.filename)
            msg.send()

        flash('Form has been submitted')
        return redirect(request.headers['Referer'])

    @expose()
    def perform(self, name, *args, **kw):
        try:
            slice = DBSession.query(Slice).filter_by(name=name, view='genshi').one()
        except:
            abort(404, "Slice not found")

        if slice.page_uid is not None:
            abort(403, 'Forbidden')

        renderer = ViewsManager.find_view(slice.view)
        if not renderer:
            abort(404, "Renderer not available")

        return renderer.render(None, slice, slice.content.data)
