import tg
import libacr.model.core as m_core
import libacr.model.content as m_cms
import libacr.model.user_permission as m_perm
from tg.i18n import get_lang
import tw.api
from tw.jquery import jquery_js

class odict(dict):
    def __init__(self, *args, **kw):
        self._ordering = []
        dict.__init__(self, *args, **kw)

    def __setitem__(self, key, value):
        if key in self._ordering:
            self._ordering.remove(key)
        self._ordering.append(key)
        dict.__setitem__(self, key, value)

    def keys(self):
        return self._ordering

    def clear(self):
        self._ordering = []
        dict.clear(self)

    def getitem(self, n):
        return self[self._ordering[n]]

    def iteritems(self):
        for item in self._ordering:
            yield item, self[item]

    def items(self):
        return [i for i in self.iteritems()]

    def itervalues(self):
        for item in self._ordering:
            yield self[item]

    def values(self):
        return [i for i in self.itervalues()]

    def __delitem__(self, key):
        self._ordering.remove(key)
        dict.__delitem__(self, key)

    def pop(self):
        item = self._ordering[-1]
        del self[item]

    def __str__(self):
        return str(self.items())

def user_can_create_children_of_ancestors(target_page):
    if not tg.request.identity:
        return False

    user = tg.request.identity['user']
    permissions = m_core.DBSession.query(m_perm.AcrUserPermission).filter_by(page='all').filter_by(user_id=user.user_id).first()
    if permissions and permissions.can_create_children:
        return True

    if not target_page:
        return False

    for page in target_page.ancestors:
        permissions = m_core.DBSession.query(m_perm.AcrUserPermission).filter_by(page=page.url).filter_by(user_id=user.user_id).first()
        if permissions:
            if not permissions.can_create_children:
                return False
            else:
                return True

    return False

def user_can_edit(target_page):
    if not tg.request.identity:
        return False

    user = tg.request.identity['user']
    permissions = m_core.DBSession.query(m_perm.AcrUserPermission).filter_by(page='all').filter_by(user_id=user.user_id).first()
    if permissions and permissions.can_edit:
        return True

    if not target_page:
        return False

    permissions = m_core.DBSession.query(m_perm.AcrUserPermission).filter_by(page=target_page.url).filter_by(user_id=user.user_id).first()
    if permissions and permissions.can_edit:
        return True

    return False

def user_can_create_children_in_page(target_page):
    if not tg.request.identity:
        return False

    if target_page:
      user = tg.request.identity['user']
      permissions = m_core.DBSession.query(m_perm.AcrUserPermission).filter_by(page=target_page.url).filter_by(user_id=user.user_id).first()
      if permissions and permissions.can_create_children:
          return True

    return user_can_create_children_of_ancestors(target_page)

def user_can_modify(page):
    permission = user_can_edit(page)
    if not permission:
        permission = user_can_create_children_of_ancestors(page)

    return permission

def current_user_id():
    try:
        return tg.request.identity and tg.request.identity['user'].user_id or None
    except:
        return None

def language():
    langs = []

    forced_lang = tg.request.GET.get('lang')
    if forced_lang:
        langs.append(forced_lang)

    try:
        lang = tg.session.get(tg.config.get('lang_session_key', 'tg_lang'))
        if lang:
            if isinstance(lang, list):
                langs.extend(lang)
            else:
                langs.append(lang)
    except:
        pass

    try:
        browser_languages = tg.request.languages
    except:
        browser_languages = []

    for lang in browser_languages:
        try:
            ltype, lsubtype = lang.split('-', 1)
        except:
            ltype, lsubtype = lang, lang

        if ltype != lsubtype.lower():
            langs.append(lang)
        langs.append(ltype)

    langs.append(tg.config.get('default_language', 'en'))
    return langs

def url(uri_path, *args, **kwargs):
    acr_root = tg.config.get('acr_root', '')
    if uri_path[0] == '/':
        uri_path = acr_root + uri_path
    uri_path = tg.url(uri_path, params=kwargs)
    return uri_path

def rdisk_url(uri_path, *args, **kwargs):
    rdisk_root = tg.config.get('rdisk_root', '')
    if uri_path[0] == '/':
        uri_path = rdisk_root + uri_path
    uri_path = tg.url(uri_path, params=kwargs)
    return uri_path

def get_slices_with_tag(tag):
    return m_core.DBSession.query(m_cms.Slice).filter(m_cms.Slice.tags.any(name=tag))

def get_page_from_urllist(args):
    try:
        page = None
        for arg in args:
            tmp_page = m_core.DBSession.query(m_cms.Page).filter_by(uri=arg)
            if page:
                tmp_page = tmp_page.filter_by(parent=page)
            page = tmp_page.first()
            if not page:
                break
    except:
        page = None

    return page

def getitem_for_lang(entries, langs=None, fallback=True):
    if not langs:
        langs = language()

    for lang in langs:
        candidate = entries.get(lang)
        if candidate is not None:
            return candidate

    if fallback:
        return entries['en']
    else:
        return None

class AcrResourceInjector(object):
    def __init__(self, basic_resources=[]):
        super(AcrResourceInjector, self).__init__()
        self.resources = basic_resources

    def inject(self):
        for r in self.resources:
            r.inject()

acr_js = tw.api.JSLink(modname=__name__, filename='static/acr.js')
full_acr_js = AcrResourceInjector([jquery_js, acr_js])

basic_acr_css = tw.api.CSSLink(modname=__name__, filename='static/style.css')
acr_css = AcrResourceInjector([basic_acr_css])
admin_css = tw.api.CSSLink(modname=__name__, filename='static/acr_admin.css')

class IconLink(tw.api.Link):
    """
    A link to an icon.
    """
    template = """<img src="$link" alt="$alt"/>"""

    params = dict(alt="Alternative text when not displaying image")

    def __init__(self, *args, **kw):
        super(IconLink, self).__init__(*args, **kw)
        self.alt = kw.get('alt')

icons = {
    'parent':IconLink(modname=__name__, filename='static/icons/parent.png', alt='Up'),
    'twitter':IconLink(modname=__name__, filename='static/icons/twitter.png', alt='Tweet!'),
    'file':IconLink(modname=__name__, filename='static/icons/file.png', alt='File'),
    'dir':IconLink(modname=__name__, filename='static/icons/dir.png', alt='Directory'),
    'create_page':IconLink(modname=__name__,
                           filename='static/icons/create_page.png', alt='Create Page'),
    'standard_plugin':IconLink(modname=__name__,
                            filename='static/icons/standard_plugin.png', alt='Standard Plugin'),
    'manage_pages':IconLink(modname=__name__,
                            filename='static/icons/manage_pages.png', alt='Manage Pages'),
    'create_node':IconLink(modname=__name__,
                           filename='static/icons/create_node.png', alt='Create Node'),
    'unbound':IconLink(modname=__name__,
                       filename='static/icons/unbound.png', alt='Unbound'),
    'remote_disk':IconLink(modname=__name__,
                        filename='static/icons/remote_disk.png', alt='Remote Disk'),
    'themes':IconLink(modname=__name__,
                        filename='static/icons/themes.png', alt='Themes'),
    'tags':IconLink(modname=__name__,
                        filename='static/icons/tag.png', alt='Tags'),
    'help':IconLink(modname=__name__,
                        filename='static/icons/help.png', alt='Help'),
    'users_permission':IconLink(modname=__name__,
                        filename='static/icons/users_permission.png', alt='User Permissions'),
    'slice_group':IconLink(modname=__name__,
                        filename='static/icons/slicegroup.png', alt='Slice Group'),
    'loading':IconLink(modname=__name__,
                        filename='static/icons/loading.gif', alt='Loading...'),
    'prev':IconLink(modname=__name__,
                        filename='static/icons/prev.gif', alt='Previous'),
    'next':IconLink(modname=__name__,
                        filename='static/icons/next.gif', alt='Next'),
    'close':IconLink(modname=__name__,
                        filename='static/icons/close.gif', alt='Close'),
    'blank':IconLink(modname=__name__,
                        filename='static/icons/blank.gif', alt='Blank'),
    'pdf':IconLink(modname=__name__,
                        filename='static/icons/iconPdf.png', alt='Pdf'),
    'audio':IconLink(modname=__name__,
                        filename='static/icons/iconAudio.jpg', alt='Audio'),
    'document':IconLink(modname=__name__,
                        filename='static/icons/iconDocument.png', alt='Document'),
    'udv_manage':IconLink(modname=__name__,
                        filename='static/icons/udv_manage.png', alt='Manage User Defined Views'),
    'udv_add':IconLink(modname=__name__,
                        filename='static/icons/udv_add.png', alt='Add User Defined View'),
    'asset':IconLink(modname=__name__,
                        filename='static/icons/asset.png', alt='Asset')
}

known_languages = [('af', 'AFRIKAANS'), ('sq', 'ALBANIAN'), ('am', 'AMHARIC'), ('ar', 'ARABIC'), ('hy', 'ARMENIAN'), ('az', 'AZERBAIJANI'), ('eu', 'BASQUE'), ('be', 'BELARUSIAN'), ('bn', 'BENGALI'), ('bh', 'BIHARI'), ('bg', 'BULGARIAN'), ('my', 'BURMESE'), ('br', 'BRETON'), ('ca', 'CATALAN'), ('chr', 'CHEROKEE'), ('zh', 'CHINESE'), ('zh-CN', 'CHINESE_SIMPLIFIED'), ('zh-TW', 'CHINESE_TRADITIONAL'), ('co', 'CORSICAN'), ('hr', 'CROATIAN'), ('cs', 'CZECH'), ('da', 'DANISH'), ('dv', 'DHIVEHI'), ('nl', 'DUTCH'), ('en', 'ENGLISH'), ('eo', 'ESPERANTO'), ('et', 'ESTONIAN'), ('fo', 'FAROESE'), ('tl', 'FILIPINO'), ('fi', 'FINNISH'), ('fr', 'FRENCH'), ('fy', 'FRISIAN'), ('gl', 'GALICIAN'), ('ka', 'GEORGIAN'), ('de', 'GERMAN'), ('el', 'GREEK'), ('gu', 'GUJARATI'), ('ht', 'HAITIAN_CREOLE'), ('iw', 'HEBREW'), ('hi', 'HINDI'), ('hu', 'HUNGARIAN'), ('is', 'ICELANDIC'), ('id', 'INDONESIAN'), ('iu', 'INUKTITUT'), ('ga', 'IRISH'), ('it', 'ITALIAN'), ('ja', 'JAPANESE'), ('jw', 'JAVANESE'), ('kn', 'KANNADA'), ('kk', 'KAZAKH'), ('km', 'KHMER'), ('ko', 'KOREAN'), ('ku', 'KURDISH'), ('ky', 'KYRGYZ'), ('lo', 'LAO'), ('lo', 'LAOTHIAN'), ('la', 'LATIN'), ('lv', 'LATVIAN'), ('lt', 'LITHUANIAN'), ('lb', 'LUXEMBOURGISH'), ('mk', 'MACEDONIAN'), ('ms', 'MALAY'), ('ml', 'MALAYALAM'), ('mt', 'MALTESE'), ('mi', 'MAORI'), ('mr', 'MARATHI'), ('mn', 'MONGOLIAN'), ('ne', 'NEPALI'), ('no', 'NORWEGIAN'), ('oc', 'OCCITAN'), ('or', 'ORIYA'), ('ps', 'PASHTO'), ('fa', 'PERSIAN'), ('pl', 'POLISH'), ('pt', 'PORTUGUESE'), ('pt-PT', 'PORTUGUESE_PORTUGAL'), ('pa', 'PUNJABI'), ('qu', 'QUECHUA'), ('ro', 'ROMANIAN'), ('ru', 'RUSSIAN'), ('sa', 'SANSKRIT'), ('gd', 'SCOTS_GAELIC'), ('sr', 'SERBIAN'), ('sd', 'SINDHI'), ('si', 'SINHALESE'), ('sk', 'SLOVAK'), ('sl', 'SLOVENIAN'), ('es', 'SPANISH'), ('su', 'SUNDANESE'), ('sw', 'SWAHILI'), ('sv', 'SWEDISH'), ('syr', 'SYRIAC'), ('tg', 'TAJIK'), ('ta', 'TAMIL'), ('tl', 'TAGALOG'), ('tt', 'TATAR'), ('te', 'TELUGU'), ('th', 'THAI'), ('bo', 'TIBETAN'), ('to', 'TONGA'), ('tr', 'TURKISH'), ('uk', 'UKRAINIAN'), ('ur', 'URDU'), ('uz', 'UZBEK'), ('ug', 'UIGHUR'), ('vi', 'VIETNAMESE'), ('cy', 'WELSH'), ('yi', 'YIDDISH')]