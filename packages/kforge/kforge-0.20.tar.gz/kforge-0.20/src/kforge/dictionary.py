"""
Dictionary of system attributes.

"""

import os
import sys
import dm.dictionary
import kforge
import kforge.dictionarywords
from kforge.dictionarywords import *

class SystemDictionary(dm.dictionary.SystemDictionary):

    words = kforge.dictionarywords

    def getSystemName(self):
        return 'kforge'

    def getSystemTitle(self):
        return 'KForge'

    def getSystemServiceName(self):
        return 'KForge'

    def getSystemVersion(self):
        return kforge.__version__
 
    def setDefaultWords(self):
        super(SystemDictionary, self).setDefaultWords()
        self[SITE_HOST] = 'projects.%s' % self[DNS_DOMAIN_NAME]
        self[MEMBER_ROLE_NAME] = 'Friend'
        self[PLUGIN_PACKAGE_NAME] = 'kforge.plugin'
        self[PROJECTS_PATH] = ''
        self[FEED_SUMMARY_LENGTH] = '25'
        self[FEED_LENGTH] = '100'
        self[MODEL_CACHE_CLASSES] = 'Plugin, Person, Project, Member, Service, Session, Ticket, TracProject'
        self[PLUGINS_AVAILABLE] = 'dav, git, mailman, mercurial, moin, notify, ssh, svn, trac, wordpress'

    def setWordsFromWords(self):
        super(SystemDictionary, self).setWordsFromWords()
        if not self[PROJECTS_PATH]:
            path = os.path.join(self[FILESYSTEM_PATH], 'var', 'project')
            self[PROJECTS_PATH] = path

