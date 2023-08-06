"""
Manipulate system service filesystems.
"""

import os
import sys
import shutil
import re 

class EditConfiguration(object):
    """Substitute for key, value pairs in a configuration file
    """

    def __init__(self, templateFile, substitutions):
        """
        @param templateFile: a file-like object containing the template
        """
        self.template = ''
        self.result = ''
        self.template = templateFile.read()
        self.substitutions = substitutions

    def execute(self):
        """
        WARNING: no support for sections so must hope a given key name is
        unique across sections
        """
        pat = '^(#\s*)?%s\s*[=:].*'
        for key, value in self.substitutions.items():
            tpat = re.compile(pat % key, re.MULTILINE)
            self.template = re.sub(tpat, '%s = %s' % (key, value), self.template)
        self.result = self.template

