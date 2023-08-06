import unittest
from kforge.django.apps.kui.views.test.base import ViewTestCase
from kforge.django.apps.kui.views.accesscontrol import LoginView

def suite():
    suites = [
        unittest.makeSuite(TestLoginGet),
        unittest.makeSuite(TestLoginPOST),
        unittest.makeSuite(TestLoginPOSTWrongUsername),
        unittest.makeSuite(TestLoginPOSTWrongPassword),
    ]
    return unittest.TestSuite(suites)


class TestLoginGet(ViewTestCase):

    viewClass = LoginView
    requiredResponseContent = [
        "Log in",
        "Username",
        "Password",
        "Remember me",
        "Forgotten your password",
        "Join",
    ]


class TestLoginPOSTWrongUsername(ViewTestCase):

    viewClass = LoginView
    requiredResponseContent = "Sorry, wrong user name or password."

    def initPost(self):
        self.POST['name'] = 'lev'
        self.POST['password'] = 'levin'


class TestLoginPOSTWrongPassword(ViewTestCase):

    viewClass = LoginView
    requiredResponseContent = "Sorry, wrong user name or password."

    def initPost(self):
        self.POST['name'] = 'levin'
        self.POST['password'] = 'lev'


class TestLoginPOST(ViewTestCase):

    viewClass = LoginView
    requiredResponseClassName = "HttpResponseRedirect"
    requiredRedirect = '/people/levin/'

    def initPost(self):
        self.POST['name'] = 'levin'
        self.POST['password'] = 'levin'

