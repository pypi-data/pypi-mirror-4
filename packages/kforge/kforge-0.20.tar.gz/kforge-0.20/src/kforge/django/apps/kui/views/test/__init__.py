import kforge.django.apps.kui.views.test.manipulator
import kforge.django.apps.kui.views.test.welcome
import kforge.django.apps.kui.views.test.accesscontrol
import kforge.django.apps.kui.views.test.project
import kforge.django.apps.kui.views.test.person
import kforge.django.apps.kui.views.test.service
import kforge.django.apps.kui.views.test.member
import kforge.django.apps.kui.views.test.admin
import kforge.django.apps.kui.views.test.api
import unittest

# Just check these modules can actually be imported.
# Todo: Do this elsewhere.
import kforge.django.settings.urls.main  
import kforge.django.settings.main  

def suite():
    suites = [
        kforge.django.apps.kui.views.test.manipulator.suite(),
        kforge.django.apps.kui.views.test.welcome.suite(),
        kforge.django.apps.kui.views.test.accesscontrol.suite(),
        kforge.django.apps.kui.views.test.project.suite(),
        kforge.django.apps.kui.views.test.person.suite(),
        kforge.django.apps.kui.views.test.service.suite(),
        kforge.django.apps.kui.views.test.member.suite(),
        kforge.django.apps.kui.views.test.admin.suite(),
        kforge.django.apps.kui.views.test.api.suite(),
    ]
    return unittest.TestSuite(suites)

