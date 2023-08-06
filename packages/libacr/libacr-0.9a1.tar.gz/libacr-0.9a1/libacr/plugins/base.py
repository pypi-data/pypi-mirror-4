# -*- coding: utf-8 -*-
import os, sys
from tg import expose

class AcrPlugin(object):
    def statics_path(self):
        module_dir = os.path.dirname(sys.modules[self.__module__].__file__)
        return os.path.join(module_dir, 'static')

    def statics_url(self, *args):
        from libacr.lib import url

        temp_url = '/plugins/static/%s' % self.__class__.uri
        for p in args:
            temp_url += '/' + p
        return url(temp_url)

    def plugin_url(self, *args):
        from libacr.lib import url

        temp_url = '/plugins/%s' % self.__class__.uri
        for p in args:
            temp_url += '/' + p
        return url(temp_url)

class PluginStatic(object):
    def __init__(self, plugin, path):
        self.plugin = plugin
        self.path = path

    def __str__(self):
        try:
            return self.plugin.statics_url(self.path)
        except:
            return 'url_called_outside_of_request'

    def __repr__(self):
        return str(self)

class PluginUrl(object):
    def __init__(self, plugin, path):
        self.plugin = plugin
        self.path = path

    def __str__(self):
        try:
            return self.plugin.plugin_url(self.path)
        except:
            return 'url_called_outside_of_request'

    def __repr__(self):
        return str(self)

class AdminEntry(object):
    def __init__(self, plugin, name, action=None, section='Plugins', icon=None):
        self.section = section
        self.icon_url = icon
        self.name = name
        self.plugin = plugin
        self.action = action

    @property
    def url(self):
        from libacr.lib import url
        return url('/plugins/%s/%s' % (self.plugin.__class__.uri, self.action))

    @property
    def icon(self):
        from libacr.helpers import icons

        if self.icon_url:
            return self.plugin.statics_url(self.icon_url)
        else:
            return icons['standard_plugin'].link

def plugin_expose(path):
    def decorated_plugin_expose(method):
        return expose("%s.%s" % (method.__module__, path))(method)
    return decorated_plugin_expose

