import unittest
from kforge.test.customer.plugin.base import PluginTestCase
import shlex
from subprocess import Popen, PIPE
from kforge.dictionarywords import APACHE_PYTHON_MODULE
import os

def suite():
    suites = [
        unittest.makeSuite(TestDav),
    ]
    return unittest.TestSuite(suites)


class TestDav(PluginTestCase):

    requiredPlugins = ['dav']

    def testHttpClient(self):
        url = self.getServicePath('dav')
        self.getAssertCode(url, 404)
        self.createService('dav', 'dav')
        content = 'Index of %s/%s/%s' % (self.uriPrefix, self.kuiProjectName, 'dav')
        self.getAssertContent(url, content, code=200)
        self.logoutPerson()
        self.getAssertCode(url, 401)
        self.setBasicAuthPerson()
        self.getAssertContent(url, content, code=200)

    def testDavfs(self):
        self.createService('dav', 'dav')
        # NB, difficult to automate davfs with authentication.
        params = {
            'person': '/people/visitor',
            'role': '/roles/Friend',
        }
        self.postAssertCode(self.urlProjectMemberCreate, params)
        url = self.getServiceUrl('dav') 
        path = self.makeTempFolder()
        cmd = "sudo mount -t davfs %s %s -o uid=%s" % (url, path, os.environ['USER'])
        #cmd = "sudo mount -t davfs %s %s; sudo chown %s:%s %s" % (url, path, os.environ['USER'], os.environ['USER'], path)
        # Mount, create file, unmount.
        tmpFilePath = os.path.join(path, 'test.txt')
        p = Popen(shlex.split(cmd), stdin=PIPE, stdout=PIPE, stderr=PIPE)
        input = '%s\n%s' % (self.kuiPersonName, self.kuiPersonPassword)
        output = p.communicate(input)
        try:
            if p.wait():
                self.fail("Couldn't mount DAV filesystem: %s" % str(output))
            self.failIf(os.path.exists(tmpFilePath))
            tmpFile = open(tmpFilePath, 'w')
            tmpFile.write('foo')
            tmpFile.close()
        finally:
            self.system("sudo umount %s" % path)

        # Remount, check file, update file, unmount.
        p = Popen(shlex.split(cmd), stdin=PIPE, stdout=PIPE, stderr=PIPE)
        input = '%s\n%s' % (self.kuiPersonName, self.kuiPersonPassword)
        output = p.communicate(input)
        try:
            if p.wait():
                self.fail("Couldn't mount DAV filesystem: %s" % str(output))
            self.failUnless(os.path.exists(tmpFilePath))
            tmpFile = open(tmpFilePath, 'r')
            tmpFileContent = tmpFile.read()
            tmpFile.close()
            self.failUnless('foo' in tmpFileContent)
            self.failIf('bar' in tmpFileContent)
            tmpFile = open(tmpFilePath, 'w')
            tmpFile.write('bar')
            tmpFile.close()
        finally:
            self.system("sudo umount %s" % path)
        # Remount, check file, delete file, unmount.
        p = Popen(shlex.split(cmd), stdin=PIPE, stdout=PIPE, stderr=PIPE)
        input = '%s\n%s' % (self.kuiPersonName, self.kuiPersonPassword)
        output = p.communicate(input)
        try:
            if p.wait():
                self.fail("Couldn't mount DAV filesystem: %s" % str(output))
            self.failUnless(os.path.exists(tmpFilePath))
            tmpFile = open(tmpFilePath, 'r')
            tmpFileContent = tmpFile.read()
            tmpFile.close()
            self.failIf('foo' in tmpFileContent)
            self.failUnless('bar' in tmpFileContent)
            os.remove(tmpFilePath)
        finally:
            self.system("sudo umount %s" % path)
        # Remount, check file doesn't exist, unmount.
        p = Popen(shlex.split(cmd), stdin=PIPE, stdout=PIPE, stderr=PIPE)
        input = '%s\n%s' % (self.kuiPersonName, self.kuiPersonPassword)
        output = p.communicate(input)
        try:
            if p.wait():
                self.fail("Couldn't mount DAV filesystem: %s" % str(output))
            self.failIf(os.path.exists(tmpFilePath))
        finally:
            self.system("sudo umount %s" % path)

