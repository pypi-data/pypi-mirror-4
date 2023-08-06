import unittest
from kforge.django.apps.kui.views.test.base import ViewTestCase
from kforge.django.apps.kui.views.kui import WelcomeView

def suite():
    suites = [
        unittest.makeSuite(TestWelcomeView),
    ]
    return unittest.TestSuite(suites)


class TestWelcomeView(ViewTestCase):

    viewClass = WelcomeView
    requiredResponseContent = [
        "Follow projects",
        "Sign up",
        "Make changes",
    ]

