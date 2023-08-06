import kforge.url
import unittest
from kforge.testunit import TestCase
from kforge.dictionarywords import *

def suite():
    suites = [
        unittest.makeSuite(UrlSchemeTest),
        unittest.makeSuite(UrlSchemeUriPrefixTest),
    ]
    return unittest.TestSuite(suites)

class UrlSchemeTest(TestCase):

    adjustedPrefix = ''

    def setUp(self):
        self.originalPrefix = self.dictionary[URI_PREFIX]
        self.dictionary[URI_PREFIX] = self.adjustedPrefix
        self.scheme = kforge.url.UrlScheme()

    def tearDown(self):
        self.dictionary[URI_PREFIX] = self.originalPrefix

    def prefix(self, path):
        return self.adjustedPrefix + path

    def test_home(self):
        urlPath = self.scheme.url_for('home')
        self.failUnlessEqual(urlPath, self.prefix('/'))

    def test_media(self):
        urlPath = self.scheme.url_for('media')
        self.failUnlessEqual(urlPath, self.prefix('/media'))
        urlPath = self.scheme.url_for('media', offset='/css/master.css')
        self.failUnlessEqual(urlPath, self.prefix('/media/css/master.css'))
        urlPath = self.scheme.url_for_qualified('media', offset='/css/master.css')
        expect = self.prefix('/media/css/master.css')
        self.failUnless(expect in urlPath, (urlPath, expect))

    def test_login(self):
        urlPath = self.scheme.url_for('login')
        self.failUnlessEqual(urlPath, self.prefix('/login'))

    def test_logout(self):
        urlPath = self.scheme.url_for('logout')
        self.failUnlessEqual(urlPath, self.prefix('/logout'))

    def test_accessDenied(self):
        urlPath = self.scheme.url_for('access_denied')
        self.failUnlessEqual(urlPath, self.prefix('/accessDenied'))

    def test_people(self):
        urlPath = self.scheme.url_for('people')
        self.failUnlessEqual(urlPath, self.prefix('/people'))
        urlPath = self.scheme.url_for('people', action='home')
        self.failUnlessEqual(urlPath, self.prefix('/people/home'))
        urlPath = self.scheme.url_for('people', action='create')
        self.failUnlessEqual(urlPath, self.prefix('/people/create'))
        urlPath = self.scheme.url_for('people', action='read', id=9)
        self.failUnlessEqual(urlPath, self.prefix('/people/9'))
        urlPath = self.scheme.url_for('people', action='delete', id=9)
        self.failUnlessEqual(urlPath, self.prefix('/people/9/delete'))

    def test_project(self):
        urlPath = self.scheme.url_for('projects')
        self.failUnlessEqual(urlPath, self.prefix('/projects'))
        urlPath = self.scheme.url_for('projects', action='search')
        self.failUnlessEqual(urlPath, self.prefix('/projects/search'))
        urlPath = self.scheme.url_for('projects', action='read', id='annakarenina')
        self.failUnlessEqual(urlPath, self.prefix('/projects/annakarenina'))
        urlPath = self.scheme.url_for('projects', action='delete', id='annakarenina')
        self.failUnlessEqual(urlPath, self.prefix('/projects/annakarenina/delete'))

    def test_ProjectAdmin(self):
        urlPath = self.scheme.url_for('projects.admin', project='annakarenina',
                subcontroller='services', action='read', id=3)
        self.failUnlessEqual(urlPath, self.prefix('/projects/annakarenina/services/3'))
        urlPath = self.scheme.url_for('projects.admin', project='annakarenina',
                subcontroller='services', action='create')
        self.failUnlessEqual(urlPath, self.prefix('/projects/annakarenina/services/create'))

    def test_ProjectService(self):
        urlPath = self.scheme.url_for('projects.service', project='annakarenina',
                service='wiki')
        self.failUnlessEqual(urlPath, self.prefix('/annakarenina/wiki'))

    def test_admin(self):
        urlPath = self.scheme.url_for('admin')
        self.failUnlessEqual(urlPath, self.prefix('/admin'))
        urlPath = self.scheme.url_for('admin', offset='Project/read/2')
        self.failUnlessEqual(urlPath, self.prefix('/admin/model/Project/read/2'))

    def test_decodeServicePath(self):
        inpath = self.prefix(u'/annakarenina/wiki')
        out_project, out_service = self.scheme.decodeServicePath(inpath)
        self.failUnlessEqual(out_project, 'annakarenina')
        self.failUnlessEqual(out_service, 'wiki')
        self.failUnlessEqual(type(out_project), str)

    def test_decodeServicePath_2(self):
        inpath = self.prefix('/warandpeace/svn/!svn/vcc/default')
        out_project, out_service = self.scheme.decodeServicePath(inpath)
        self.failUnlessEqual(out_project, 'warandpeace')
        self.failUnlessEqual(out_service, 'svn')

    def test_getServicePath(self):
        projectName = 'a_really_weird_name'
        class ProjectStub:
            name = projectName

        class PluginStub:
            name = 'wiki'

        class ServiceStub:
            project = ProjectStub()
            plugin = PluginStub()
            name = 'service_stub'

        urlPath = self.scheme.getServicePath(ServiceStub())
        self.failUnlessEqual(urlPath, self.prefix('/%s/service_stub' % projectName))

    def test_getServiceUrl(self):
        projectName = 'a_really_weird_name'
        # Todo: Extract stub (from here and above).
        class ProjectStub:
            name = projectName
        class PluginStub:
            name = 'wiki'
        class ServiceStub:
            project = ProjectStub()
            plugin = PluginStub()
            name = 'service_stub'

        serviceUrl = self.scheme.getServiceUrl(ServiceStub())
        urlPath = self.prefix('/%s/service_stub' % projectName)
        self.failUnless(serviceUrl.endswith(urlPath), "Service URL '%s' does not end with URL path '%s'." % (serviceUrl, urlPath))


class UrlSchemeUriPrefixTest(UrlSchemeTest):

    adjustedPrefix = '/myadjustedprefix'


