from kforge.testunit import TestCase
import unittest
import kforge.apache.urlpermission as urlpermission
import kforge.url

def suite():
    suites = [
        unittest.makeSuite(ParseUrlTest),
    ]
    return unittest.TestSuite(suites)

class ParseUrlTest(TestCase):
    
    def setUp(self):
        self.url_scheme = kforge.url.UrlScheme()
        self.urlPath = self.url_scheme.url_for('projects.service',
                project='annakarenina', service='example')
    
    def testIsAuthenticated(self):
        visitorName = 'visitor'
        person = urlpermission.isAuthenticated('notauser', 'asdfghjkl')
        self.failIf(person)
        person = urlpermission.isAuthenticated('levin', 'levin')
        self.failUnless(person)
        self.failUnlessEqual(person.name, 'levin')
    
    def testGetService(self):
        service = urlpermission.getService(self.urlPath)
        self.failUnless(service.name == 'example')
    
    def testGetActionName(self):
        httpMethods = [ ('GET',      'Read'),
                        ('PROPFIND', 'Read'),
                        ('OPTIONS',  'Read'),
                        ('REPORT',   'Read'),
                        ('POST',     'Update'),
                      ]
        for httpMethod in httpMethods:
            actionName = urlpermission.getActionName(httpMethod[0])
            self.failUnless(actionName == httpMethod[1],
                'Failed with http method: %s' % httpMethod[0])
    
    def testIsAccessAuthorised(self):
        person = self.registry.people['levin']
        out = urlpermission.isAccessAuthorised(person, self.urlPath, 'GET')
        self.failUnless(out, "Levin can't access: %s" % self.urlPath)
        person = self.registry.people['natasha']
        out = urlpermission.isAccessAuthorised(person, self.urlPath, 'GET')
        self.failIf(out, "Natasha can access: %s" % self.urlPath)
    
    def test_isAccessAuthorised2(self):
        "warandpeace allows visitor access"
        urlpath = self.url_scheme.url_for('projects_service',
                project='warandpeace', service='example')
        person = self.registry.people['natasha']
        out = urlpermission.isAccessAuthorised(person, urlpath, 'GET')
        self.failUnless(out, 'natasha not allowed in')
        person = self.registry.people['visitor']
        out = urlpermission.isAccessAuthorised(person, urlpath, 'GET')
        self.failUnless(out, 'visitor not allowed in')
        person = self.registry.people['levin']
        out = urlpermission.isAccessAuthorised(person, urlpath, 'GET')
        self.failUnless(out, 'levin not allowed in')

