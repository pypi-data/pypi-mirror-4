# -*- coding=utf-8 -*-
import unittest
from dm.view.basetest import AdminSessionViewTestCase
from kforge.django.apps.kui.views.test.base import ViewTestCase
from kforge.django.apps.kui.views.project import ProjectListView
from kforge.django.apps.kui.views.project import ProjectReadView
from kforge.django.apps.kui.views.project import ProjectCreateView
from kforge.django.apps.kui.views.project import ProjectUpdateView
from kforge.django.apps.kui.views.project import ProjectSearchView

def suite():
    suites = [
        unittest.makeSuite(TestProjectListView),
        unittest.makeSuite(TestProjectReadView),
        unittest.makeSuite(TestProjectCreateView),
        unittest.makeSuite(TestProjectCreateViewLevin),
        unittest.makeSuite(TestProjectCreateViewPost),
        unittest.makeSuite(TestProjectUpdateView),
        unittest.makeSuite(TestProjectUpdateViewPost),
        unittest.makeSuite(TestProjectSearchView),
        unittest.makeSuite(TestProjectSearchView2),
        unittest.makeSuite(TestProjectFindView),
        unittest.makeSuite(TestProjectFindView2),
    ]
    return unittest.TestSuite(suites)


class TestProjectListView(ViewTestCase):

    viewClass = ProjectListView

    def getRequiredViewContext(self):
        return {
            'objectCount': self.registry.projects.count()
        }


class TestProjectReadView(ViewTestCase):

    viewClass = ProjectReadView
    viewKwds = {'domainObjectKey': 'annakarenina'}


class TestProjectCreateView(ViewTestCase):

    viewClass = ProjectCreateView
    requiredResponseClassName = 'HttpResponseRedirect'
    requiredRedirect = '%s/login/' % ViewTestCase.URI_PREFIX


class TestProjectCreateViewLevin(ViewTestCase):

    viewClass = ProjectCreateView
    viewerName = 'levin'

class TestProjectCreateViewPost(ViewTestCase):

    viewClass = ProjectCreateView
    viewerName = 'levin'
    requestPath = '/projects/create/'
    requiredResponseClassName = 'HttpResponseRedirect'
    requiredRedirect = '/projects/testcreateview/'

    def initPost(self):
        self.POST['name'] = 'testcreateview'
        self.POST['title'] = 'Test Create View'
        self.POST['licenses'] = ['/licenses/1']
        self.POST['description'] = 'A project to test the create view.'
        self.POST['isHidden'] = 'on'

    def checkModel(self):
        self.failUnless('testcreateview' in self.registry.projects)
        project = self.registry.projects['testcreateview']
        self.failUnlessEqual(project.name, 'testcreateview')
        self.failUnlessEqual(project.title, 'Test Create View')
        self.failUnlessEqual(project.description, 'A project to test the create view.')
        self.failUnlessEqual(project.isHidden, True)

    def tearDown(self):
        super(TestProjectCreateViewPost, self).tearDown()
        if 'testcreateview' in self.registry.projects:
            del(self.registry.projects['testcreateview'])


class TestProjectUpdateView(ViewTestCase):

    viewClass = ProjectUpdateView
    viewerName = 'levin'
    viewKwds = {'domainObjectKey': 'annakarenina'}


class TestProjectUpdateViewPost(ViewTestCase):

    viewClass = ProjectUpdateView
    viewerName = 'levin'
    viewKwds = {'domainObjectKey': 'annakarenina'}
    requestPath = '/projects/annakarenina/edit/'
    requiredResponseClassName = 'HttpResponseRedirect'
    requiredRedirect = '/projects/annakarenina/'

    def initPost(self):
        self.POST['licenses'] = ['/licenses/2']
        self.POST['title'] = 'Annakarenina'
        self.POST['description'] = 'A project about Annakarenina.'


# Todo: Test update form submission (in various ways).


class TestProjectSearchView(ViewTestCase):

    viewClass = ProjectSearchView

    def initPost(self):
        self.POST['userQuery'] = u'εἶναι'  # substr of 'War and Peace ...'

    def getRequiredViewContext(self):
        return {
            'objectCount': 1
        }


class TestProjectSearchView2(ViewTestCase):

    viewClass = ProjectSearchView

    def initPost(self):
        self.POST['userQuery'] = u'a'

    def getRequiredViewContext(self):
        return {
            'objectCount': 4
        }


class TestProjectFindView(ViewTestCase):

    viewClass = ProjectSearchView
    viewKwds = {'startsWith': u'w'}

    def getRequiredViewContext(self):
        return {
            'objectCount': 1
        }


class TestProjectFindView2(ViewTestCase):

    viewClass = ProjectSearchView
    viewKwds = {'startsWith': u'εἶναι'}

    def getRequiredViewContext(self):
        return {
            'objectCount': 0
        }

