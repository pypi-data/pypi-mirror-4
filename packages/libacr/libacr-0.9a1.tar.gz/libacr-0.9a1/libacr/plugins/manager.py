import os, tg, imp, inspect
from base import AcrPlugin

class PluginsManager(object):
    def __init__(self):
        self.plugins = {}

    def __call__(self):
        if not self.plugins:
            self.load_plugins(self.builtin_plugins_path)
            self.load_plugins(self.site_plugins_path)
            self.inject_resources()
        return self

    def __getitem__(self, what):
        return self.plugins[what]

    @property
    def builtin_plugins_path(self):
        import libacr
        return os.path.dirname(libacr.plugins.__file__)

    @property
    def site_plugins_path(self):
        return os.path.join(os.path.dirname(tg.config.package.__file__), 'acr_plugins')

    def load_plugins(self, plugins_dir):
        print 'Loading ACR Plugins from', plugins_dir
        for root, dirs, files in os.walk(plugins_dir):
            if root != plugins_dir:
                continue

            for name in dirs:
                path = os.path.join(root, name)
                module_name = 'acr_plugin_'+name
                print 'Loading', name, '...', 
                try:
                    mfile, pathname, description = imp.find_module(name, [root])
                    module = imp.load_module(module_name, mfile, pathname, description)
                    for class_name, cls in inspect.getmembers(module, inspect.isclass):
                        if issubclass(cls, AcrPlugin) and cls != AcrPlugin:
                            self.plugins[cls.uri] = cls()
                    print 'SUCCESS'
                except Exception, e:
                    import traceback
                    print 'FAILED', e
                    traceback.print_exc()

    def inject_resources(self):
        css_resources = []
        js_resources = []

        for uri, plugin in self.plugins.iteritems():
            try:
                css_resources.extend(plugin.css_resources)
            except:
                pass

            try:
                js_resources.extend(plugin.js_resources)
            except:
                pass

        from libacr.lib import full_acr_js, acr_css
        for r in css_resources:
            acr_css.resources.append(r)

        for r in js_resources:
            full_acr_js.resources.append(r)

    def admin_actions(self):
        sections = {}
        for plugin in self.plugins.itervalues():
            try:
                entries = plugin.admin_entries
            except:
                entries = []

            for action in entries:
                sections.setdefault(action.section, []).append(action)
        return sections

PluginsManager = PluginsManager()
