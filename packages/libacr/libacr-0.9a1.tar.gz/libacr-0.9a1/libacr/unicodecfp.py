from ConfigParser import ConfigParser

class UnicodeConfigParser(ConfigParser):
    def write(self, fp):
        """Write an .ini-format representation of the configuration state."""
        if self._defaults:
            fp.write(u"[%s]\n" % DEFAULTSECT)
            for (key, value) in self._defaults.items():
                fp.write(u"%s = %s\n" % (key, value.replace('\n', '\n\t')))
            fp.write(u"\n")
        for section in self._sections:
            fp.write(u"[%s]\n" % section)
            for (key, value) in self._sections[section].items():
                if key != u"__name__":
                    fp.write(u"%s = %s\n" %
                             (key, value.replace('\n', '\n\t')))
