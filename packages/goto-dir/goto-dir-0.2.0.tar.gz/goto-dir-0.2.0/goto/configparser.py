# coding: utf-8
from ConfigParser import *


class UnicodeConfigParser(SafeConfigParser):
    """"""

    def write(self, fp):
        """
        Fixes broken SafeConfigParser.write function. The current code
        is almost identical to the original.

        hg.python.org/cpython/file/70273d53c1dd/Lib/ConfigParser.py#399
        """
        if self._defaults:
            fp.write("[%s]\n" % DEFAULTSECT)
            for (key, value) in self._defaults.items():
                fp.write("%s = %s\n" % (key, str(value).replace('\n', '\n\t')))
            fp.write("\n")
        for section in self._sections:
            fp.write("[%s]\n" % section)
            for (key, value) in self._sections[section].items():
                if key == "__name__":
                    continue
                if (value is not None) or (self._optcre == self.OPTCRE):
                    key = " = ".join((key, value.replace('\n', '\n\t')))
                fp.write("%s\n" % (key))
            fp.write("\n")
