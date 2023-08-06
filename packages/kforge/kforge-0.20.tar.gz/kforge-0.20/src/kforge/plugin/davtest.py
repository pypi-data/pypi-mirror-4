import unittest
import os
from kforge.testunit import TestCase

def suite():
    suites = [
            unittest.makeSuite(PluginTest),
        ]
    return unittest.TestSuite(suites)

class PluginTest(TestCase):
    
    def setUp(self):
        super(PluginTest, self).setUp()
        if not 'dav' in self.registry.plugins:
            newPlugin = self.registry.plugins.create('dav')
        self.plugin = self.registry.plugins['dav']
        self.project = self.registry.projects['annakarenina']
        if 'dav' in self.project.services:
            service = self.project.services['dav']
            service.delete()
            service.purge()
        self.project.services.create('dav', plugin=self.plugin)
        self.service = self.project.services['dav']
    
    def tearDown(self):
        if self.service != None:
            self.service.delete()
            self.service.purge()

    def test(self):
        pass
