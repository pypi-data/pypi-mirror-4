# -*- coding=utf-8 -*-
import unittest
from kforge.django.apps.kui.views.test.base import ViewTestCase
from kforge.django.apps.kui.views.person import PersonListView
from kforge.django.apps.kui.views.person import PersonReadView
from kforge.django.apps.kui.views.person import PersonCreateView
from kforge.django.apps.kui.views.person import PersonUpdateView
from kforge.django.apps.kui.views.person import PersonSearchView
from kforge.django.apps.kui.views.person import PersonApiKeyView
from dm.view.basetest import MultiValueDict

def suite():
    suites = [
        unittest.makeSuite(TestPersonListView),
        unittest.makeSuite(TestPersonReadView),
        unittest.makeSuite(TestPersonApiKeyView),
        unittest.makeSuite(TestPersonCreateView),
        unittest.makeSuite(TestPersonUpdateView),
        unittest.makeSuite(TestPersonUpdateViewPost),
        unittest.makeSuite(TestPersonSearchView),
        unittest.makeSuite(TestPersonSearchView2),
        unittest.makeSuite(TestPersonFindView),
        unittest.makeSuite(TestPersonFindView2),
    ]
    return unittest.TestSuite(suites)


class TestPersonListView(ViewTestCase):

    viewClass = PersonListView

    def getRequiredViewContext(self):
        return {
            'objectCount': self.registry.people.count()
        }


class TestPersonReadView(ViewTestCase):

    viewClass = PersonReadView
    viewKwds = {'domainObjectKey': 'levin'}

    #def createViewKwds(self):
    #    kwds = super(TestPersonReadView, self).createViewKwds()
    #    kwds['domainObjectKey'] = 'levin'
    #    return kwds


class TestPersonApiKeyView(TestPersonReadView):

    viewClass = PersonApiKeyView
    viewerName = 'levin'


class TestPersonCreateView(ViewTestCase):

    viewClass = PersonCreateView


# Todo: Test create form submission (in various ways).


class TestPersonUpdateView(ViewTestCase):

    viewerName = 'levin'
    viewClass = PersonUpdateView

    def createViewKwds(self):
        kwds = super(TestPersonUpdateView, self).createViewKwds()
        kwds['domainObjectKey'] = 'levin'
        return kwds


class TestPersonUpdateViewPost(ViewTestCase):

    viewerName = 'levin'
    viewClass = PersonUpdateView
    viewKwds = {'domainObjectKey': 'levin'}
    requiredResponseClassName = 'HttpResponseRedirect'
    requiredRedirect = '/people/levin/'

    def initPost(self):
        self.POST['personName'] = 'levin'
        self.POST['fullname'] = 'Levin'
        self.POST['email'] = 'levin@appropriatesoftware.net'
        self.POST['password'] = ''
        self.POST['passwordconfirmation'] = ''


# Todo: Test update form submission (in various ways).


class TestPersonSearchView(ViewTestCase):
    """Tests the userQuery parameter."""

    viewClass = PersonSearchView

    def initPost(self):
        self.POST['userQuery'] = 'a'

    def getRequiredViewContext(self):
        return {
            'objectCount': 2
        }


class TestPersonSearchView2(ViewTestCase):

    viewClass = PersonSearchView

    def initPost(self):
        self.POST['userQuery'] = u'εἶναι'  # In *project* 'War and Peace ...'

    def getRequiredViewContext(self):
        return {
            'objectCount': 0
        }


class TestPersonFindView(ViewTestCase):
    """Test the startsWith parameter of the search view."""
    
    viewClass = PersonSearchView
    viewKwds = {'startsWith': u'a'}

    def getRequiredViewContext(self):
        return {
            'objectCount': 1
        }


class TestPersonFindView2(ViewTestCase):
    """Tests the startsWith parameter of the search view."""
    
    viewClass = PersonSearchView
    viewKwds = {'startsWith': u'ἶ'}

    def getRequiredViewContext(self):
        return {
            'objectCount': 0
        }

