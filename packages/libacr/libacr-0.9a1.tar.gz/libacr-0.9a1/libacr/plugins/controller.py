from tg import expose, flash, require, url, request, redirect, tmpl_context, TGController
from tg.controllers import WSGIAppController
from pylons.controllers.util import abort
from manager import PluginsManager
from paste.urlparser import StaticURLParser
import os, sys

class PluginsController(TGController):
    @expose()
    def lookup(self, plugin=None, *args):
        if plugin == 'static':
            plugin = PluginsManager.plugins.get(args[0])
            if not plugin:
                abort(404, "Plugin not found")
            return WSGIAppController(StaticURLParser(plugin.statics_path())), args[1:]
        else:
            plugin = PluginsManager.plugins.get(plugin)
            if not plugin:
                abort(404, "Plugin not found")
            return plugin.controller, args

    _lookup = lookup

