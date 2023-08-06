import unittest
import kforge.testunit

from kforge.dictionarywords import *

def suite():
    suites = [
        unittest.makeSuite(PluginTest),
        ]
    return unittest.TestSuite(suites)

from kforge.plugin.notify import EmailNotifyCommand

class MockEmailNotifyCommand(EmailNotifyCommand):

    def dispatchEmailMessage(self, msgFrom, msgToList, msgSubject, msgBody):
        MockEmailNotifyCommand.dispatchedMessage = {}
        MockEmailNotifyCommand.dispatchedMessage['from'] = msgFrom
        MockEmailNotifyCommand.dispatchedMessage['to'] = msgToList
        MockEmailNotifyCommand.dispatchedMessage['subject'] = msgSubject
        MockEmailNotifyCommand.dispatchedMessage['body'] = msgBody


class PluginTest(kforge.testunit.TestCase):

    def setUp(self):
        super(PluginTest, self).setUp()
        self.origEmailNotifyChanges = self.dictionary[EMAIL_NOTIFY_CHANGES]
        self.dictionary[EMAIL_NOTIFY_CHANGES] = 'on'
        self.msgStack = []
        pluginName = 'notify'
        if not self.registry.plugins.has_key(pluginName):
            self.registry.plugins.create(pluginName)
        self.plugin = self.registry.plugins[pluginName]
        self.pluginSystem = self.plugin.getSystem()
        self.project = self.registry.projects['annakarenina']
        self.person = self.registry.people['levin']
        self.origCommandClass = self.pluginSystem.notifyCommandClass
        self.pluginSystem.notifyCommandClass = MockEmailNotifyCommand

    def tearDown(self):
        self.pluginSystem.notifyCommandClass = self.origCommandClass
        self.dictionary[EMAIL_NOTIFY_CHANGES] = self.origEmailNotifyChanges
        super(PluginTest, self).tearDown()
   
    def failUnlessDispatched(self, *args):
        dispatched = MockEmailNotifyCommand.dispatchedMessage
        self.failUnless(dispatched['from'], dispatched)
        self.failUnless(dispatched['to'], dispatched)
        self.failUnless(dispatched['subject'], dispatched)
        self.failUnless(dispatched['body'], dispatched)
        for arg in args:
            self.failUnless(arg in dispatched['body'], dispatched)
    
    def test_onProjectCreate(self):
        self.plugin.getSystem().onProjectCreate(self.project)
        self.failUnlessDispatched('Project', 'created', self.project.name)

    def test_onProjectDelete(self):
        self.plugin.getSystem().onProjectDelete(self.project)
        self.failUnlessDispatched('Project', 'deleted', self.project.name)

    def test_onPersonCreate(self):
        self.plugin.getSystem().onPersonCreate(self.person)
        self.failUnlessDispatched('Person', 'created', self.person.name)

    def test_onPersonDelete(self):
        self.plugin.getSystem().onPersonDelete(self.person)
        self.failUnlessDispatched('Person', 'deleted', self.person.name)

    # Todo: Add tests for member and service changes...
