import unittest
from kforge.testunit import TestCase
import tempfile

import kforge.plugin.mailman

def suite():
    suites = [
        unittest.makeSuite(PluginTest),
    ]
    return unittest.TestSuite(suites)

# todo: extract abstract MailingListPlugin and MailingListUtils classes

class PluginTest(TestCase):
    """
    TestCase for the Mailman plugin.
    """
    tags = [ 'plugin', 'cli' ]
    disable = True
    
    def setUp(self):
        super(PluginTest, self).setUp()
        if not self.registry.plugins.has_key('mailman'):
            self.registry.plugins.create('mailman')
        self.plugin = self.registry.plugins['mailman']
        self.project = self.registry.projects['annakarenina']
        if 'mailman' in self.project.services:
            service = self.project.services['mailman']
            service.delete()
            service.purge()
        self.service = None
    
    def tearDown(self):
        if self.service:
            self.service.delete()
            self.service.purge()
    
    def testCreateService(self):
        self.service = self.project.services.create('mailman', plugin=self.plugin)

    def testCreateAndDeleteMailingList(self):
        self.mailman = self.plugin.getSystem()
        listName = 'annakarenina-dev'
        emailAddress = 'admin@someone.net'  # todo: fix addr
        password = 'pass'
        try:
            self.mailman.createMailingList(
                listName=listName,
                adminEmail=emailAddress,
                adminPass=password
            )
        finally:
            self.mailman.deleteMailingList(
                listName=listName
            )

