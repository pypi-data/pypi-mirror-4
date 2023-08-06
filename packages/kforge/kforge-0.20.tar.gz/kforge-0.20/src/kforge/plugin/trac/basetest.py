from kforge.testunit import TestCase
from kforge.test import RequiresPlugins

class TracTestCase(RequiresPlugins, TestCase):

    requiredPlugins = ['svn', 'trac']

    def setUp(self):
        super(TracTestCase, self).setUp()
        trac = self.registry.plugins['trac']
        svn = self.registry.plugins['svn']
        self.project = self.registry.projects['annakarenina']
        self.svnService = self.project.services.create('svn', plugin=svn)
        self.service = self.project.services.create('trac', plugin=trac)
        self.tracProject = self.service.getExtnObject()
        self.tracProject.svn = self.svnService
        self.tracProject.save()

    def tearDown(self):
        self.service.delete()
        self.svnService.delete()
        super(TracTestCase, self).tearDown()

