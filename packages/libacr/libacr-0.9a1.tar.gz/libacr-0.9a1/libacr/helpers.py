from tg import tmpl_context, url, request, config, session
from lib import url as acr_url
from lib import rdisk_url, icons, language
import genshi
import urllib2
import pkg_resources
import logging, traceback, sys

from libacr.model.core import DBSession
from libacr.model.content import Page, Slice
from urllib2 import URLError

log = logging.getLogger(__name__)

def acr_delete_slice(slice_uid):
    return "javascript:acr_delete_slice('%s', %s)" % (acr_url('/admin/slices/delete'), str(slice_uid))

def acr_move_slice(slice_uid, value):
    return "javascript:acr_move_slice('%s', %s, %s)" % (acr_url('/move_slice'), str(slice_uid), str(value))

def slice_languages(slice):
    langs = {}
    if slice.content:
        for cnt in slice.content.all_data:
            langs[cnt.lang] = False
    return langs.keys()

def page_languages(page):
    langs = {}
    for slice in page.slices:
        for lang in slice_languages(slice):
            langs[lang] = False

    return langs.keys()

def slice_authors(slice):
    auths = {}
    if slice.content:
        for cnt in slice.content.all_data:
            if cnt.author:
                auths[cnt.author.user_name] = False
    return auths.keys()

def page_authors(page):
    auths = {}
    for slice in page.slices:
        for auth in slice_authors(slice):
            auths[auth] = False

    return auths.keys()

def preview_slice(page, slice):
    try:
        view_manager = config['pylons.app_globals'].acr_viewmanager
    except:
        return u'<div class="acr_wrong_view">Unable to access view manager, have you set up an instance of acr.lib.views.ViewManager inside your app_globals as acr_viewmanager?</div>'

    result = u'<div class="%s_preview acr_slice_%s_preview">' % (slice.name, slice.view)

    renderer = view_manager.find_view(slice.view)
    if renderer:
        try:
            result += renderer.preview(page, slice, slice.content.data)
        except Exception, e:
            tb = traceback.extract_tb(sys.exc_info()[2])
            log.warning(''.join(traceback.format_list(tb)))
            result += str(e)
    else:
        result += u'<div class="acr_wrong_view">Unsupported View Type</div>'

    result += u'</div>'
    return result

def render_slice(page, slice):
    try:
        view_manager = config['pylons.app_globals'].acr_viewmanager
    except:
        return u'<div class="acr_wrong_view">Unable to access view manager, have you set up an instance of acr.lib.views.ViewManager inside your app_globals as acr_viewmanager?</div>'

    tag_names = ' '.join(('acr_tag_' + tag.name for tag in slice.tags))
    result = u'<div class="%s acr_slice_%s %s">' % (slice.name, slice.view, tag_names)
    if slice.view != 'script' and tmpl_context.identity and 'acr' in tmpl_context.identity['groups']:
        result = result[0:-1] + "onmouseover='acr_show_slice_bar(this, 1)' onmouseout='acr_show_slice_bar(this, 0)'>"
        result += u'''<div class="acr_edit_container">
                        <div class="acr_edit_button">
                          <div style="float:left;">
                            <a href="#"
                               onclick="jQuery(this).parents('.acr_edit_container').hide(); event.stopPropagation(); return false;">
                                hide
                            </a>
                            &nbsp;
                            <a href="'''+acr_move_slice(slice.uid, -1)+u'''">&lt;</a>
                            '''+str(slice.slice_order)+u'''
                            <a href="'''+acr_move_slice(slice.uid, 1)+u'''">&gt;</a>
                            &nbsp;<strong>'''+slice.name+u'''</strong>
                          </div>
                          <a href="#" onclick="acrAddToSelected(this, '''+str(slice.uid)+u''')">Select</a>
                          <a href="'''+acr_delete_slice(slice.uid)+u'''">X</a>
                          <a id="edit_slice_'''+str(slice.uid)+u'''"
                                 href="%s"">EDIT</a>
                          <div style="clear:both;"></div>
                        </div>
                      </div>'''  % ( acr_url('/admin/slices/edit',uid=slice.uid) )


    if slice.getattr('force-preview'):
        result += preview_slice(page, slice)
    else:
        renderer = view_manager.find_view(slice.view)
        if renderer:
            try:
                result += renderer.render(page, slice, slice.content.data)
            except Exception, e:
                tb = traceback.extract_tb(sys.exc_info()[2])
                log.warning(''.join(traceback.format_list(tb)))
                result += str(e)
        else:
            result += u'<div class="acr_wrong_view">Unsupported View Type</div>'

    result += u'</div>'
    return result

def draw_slice(page, slicename):
    if not page:
        page = DBSession.query(Page).filter_by(uri='default').one()

    slice = DBSession.query(Slice).filter_by(name=slicename).first()
    return genshi.Markup(render_slice(page, slice))

def draw_section(page, sect):
    if not page:
        page = DBSession.query(Page).filter_by(uri='default').one()

    inherit = page.getattr('inherit')
    if not inherit:
        inherit = 'default'

    if len(page.section(sect)) == 0:
        render_page = DBSession.query(Page).filter_by(uri=inherit).one()
    else:
        render_page = page

    section_context = render_page.section(sect)
    result = u'<div id="acr_section_%s">' % (sect)
    if len(section_context):
        result += u'<div class="acr_section_content">'
    for slice in section_context:
        result += render_slice(page, slice)
    result += u'</div>'
    if len(section_context):
        result += u'</div>'
    return genshi.Markup(result)

def user_in_group(group):
    return request.identity and (group in request.identity['groups'])

def slicegroup_filter(slice):
    from libacr.views.manager import ViewsManager

    if not slice.content or not slice.content.data:
        return ''

    try:
        config = ViewsManager.find_view('slicegroup').to_dict(slice.content.data)
        return config.get('filter_tag')
    except:
        return 'Invalid SliceGroup'

def slicegroup_members(slice):
    filter_tag = slicegroup_filter(slice)

    slices = []
    for slice in DBSession.query(Slice).filter(Slice.tags.any(name=filter_tag)):
        slices.append( (slice.name, acr_url('/admin/slices/edit', uid=slice.uid)) )

    return slices

def render_scripts_menu(page):
    from libacr import acr_zones
    if not page:
        return ''

    script_slices = []
    for zone in acr_zones:
        slices = page.section(zone)
        if not slices:
            slices = DBSession.query(Page).filter_by(uri='default').one().section(zone)

        for s in slices:
            if s.view == 'script':
                script_slices.append(s)

    html = '<ul id="acr_scripts_menu">'
    for s in script_slices:
        html += '''
<li class="acr_scripts_menu_entry">
    <a class="acr_script_del_btn"
       href="javascript:acr_delete_slice('%(delete_uri)s', '%(sid)s')">
        X
    </a>
    <a href="%(action)s">
        %(name)s
    </a>
</li>''' % dict(name=s.name, delete_uri=acr_url('/del_slice'), sid=s.uid,
                action=acr_url('/admin/slices/edit', uid=s.uid))
    html += '</ul>'

    return genshi.Markup(html)

def render_slices_menu(page):
    if not page:
        return ''

    from views.manager import ViewsManager
    html = '<ul id="acr_slices_menu">'
    for view in ViewsManager.all_views:
        if view.exposed == True:
            html += """<li class="acr_slices_menu_entry">
    <a href="%s">%s</a>
</li>""" % (acr_url('/admin/slices/create', page=page.uid, view=view.name), view.name)
    html += '</ul>'
    return genshi.Markup(html)

def check_latest_release():
    try:
        libac_url = "http://pypi.python.org/pypi/libacr/"
        response = urllib2.urlopen(libac_url)
        version = numberize(response.read().split("version=")[2].split('\"')[0])
        libacr_release = numberize(pkg_resources.require("libacr")[0].version)

        if libacr_release < version:
            return version
    except URLError, e:
        log.warning("Failed to check latest release, because of: %s" % str(e))
        return False

def numberize(version):
    return ''.join([letter for letter in version if letter.isdigit()])
