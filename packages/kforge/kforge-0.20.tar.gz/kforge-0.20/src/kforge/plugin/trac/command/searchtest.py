import unittest
from kforge.plugin.trac.command.basetest import TracCommandTestCase
from kforge.plugin.trac.command.search import SearchTracProject
from kforge.plugin.trac.command.search import SearchTracProjects

def suite():
    suites = [
        unittest.makeSuite(TestSearchTracProject),
        unittest.makeSuite(TestSearchTracProjects),
    ]
    return unittest.TestSuite(suites)


class TestSearchTracProject(TracCommandTestCase):

    def test(self):
        query = 'q=wiki&wiki=on'
        cmd = SearchTracProject(self.tracProject, query=query, personName='levin')
        results = cmd.execute()
        self.failUnless(results)
        self.failUnless(cmd.results)


class TestSearchTracProjects(TracCommandTestCase):

    def test(self):
        query = 'q=wiki&wiki=on'
        cmd = SearchTracProjects(query=query, person=self.registry.people['levin'])
        results = cmd.execute()
        self.failUnless(results)
        self.failUnless(cmd.results)

