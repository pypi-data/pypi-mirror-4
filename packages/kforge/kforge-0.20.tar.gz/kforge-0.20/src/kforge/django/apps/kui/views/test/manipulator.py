import unittest
from kforge.django.apps.kui.views.testunit import TestCase
from dm import webkit
#if webkit.webkitName == 'django' and webkit.webkitVersion == '1.0':
#    from kforge.django.apps.kui.views.manipulator import PasswordField
#    from kforge.django.apps.kui.views.manipulator import ProjectNameField
#    from kforge.django.apps.kui.views.manipulator import PersonNameField
#    from kforge.django.apps.kui.views.manipulator import ServiceNameField
from kforge.django.apps.kui.views.manipulator import PersonCreateManipulator
from kforge.django.apps.kui.views.manipulator import PersonUpdateManipulator
from kforge.django.apps.kui.views.manipulator import DomainObjectManipulator
from kforge.django.apps.kui.views.manipulator import HasManyManipulator
from django.utils.datastructures import MultiValueDict
from kforge.ioc import *
from dm.dom.pickers import *
from dm.exceptions import *

def suite():
    suites = [
    #    unittest.makeSuite(TestPersonCreateManipulator),
    #    unittest.makeSuite(TestPersonUpdateManipulator),
    #    unittest.makeSuite(TestProjectCreateManipulator),
    #    unittest.makeSuite(TestProjectUpdateManipulator),
        # Todo: Move these to dm.
        unittest.makeSuite(TestDomainObjectManipulatorValidate),
        unittest.makeSuite(TestDomainObjectManipulatorCreate),
        unittest.makeSuite(TestDomainObjectManipulatorUpdate),
        unittest.makeSuite(TestHasManyManipulator),
    ]
    #suites = [
    #    unittest.makeSuite(TestDomainObjectManipulator),
    #    unittest.makeSuite(TestHasManyManipulator),
    #]
    return unittest.TestSuite(suites)


class ManipulatorTestCase(TestCase):

    def setUp(self):
        super(ManipulatorTestCase, self).setUp()
        self.manipulator = self.createManipulator()

    def tearDown(self):
        self.manipulator = None
        super(ManipulatorTestCase, self).tearDown()
    
    def checkFormField(self, name, valids, invalids):
        field = self.manipulator.fields[name]
        for v in valids:
            try:
                field.clean(v)
            except ValidationError, inst:
                self.fail("Should be valid: %s %s %s" % (v, self.field, inst)) 
        for v in invalids:
            try:
                field.clean(v)
            except ValidationError:
                pass
            else:
                self.fail("Should be invalid: %s %s" % (v, field))

    def testExists(self):
        self.failUnless(self.manipulator)
        self.failUnless(self.manipulator.fields)
    
    def createManipulator(self):
        raise Exception, "Abstract method not implemented."


class PersonManipulatorTestCase(ManipulatorTestCase):

    fixtureName = 'PersonManipulatorTestCase'

    def setUp(self):
        super(PersonManipulatorTestCase, self).setUp()
        self.tearDownFixtures()
        self.validData = MultiValueDict()
        self.validData['name'] = self.fixtureName
        self.invalidData = MultiValueDict()
        self.invalidData['name'] = '%%'

    def tearDown(self):
        super(PersonManipulatorTestCase, self).tearDown()
        self.tearDownFixtures()
        
    def tearDownFixtures(self):
        if self.fixtureName in self.registry.people.getAll():
            person = self.registry.people.getAll()[self.fixtureName]
            person.delete()
            person.purge()


class TestPersonCreateManipulator(PersonManipulatorTestCase):

    def setUp(self):
        super(TestPersonCreateManipulator, self).setUp()
        self.manipulator.create(self.validData)

    def createManipulator(self):
        return PersonCreateManipulator(objectRegister=self.registry.people, pickerClass=GetEditableAttributes)

    def testCreate(self):
        person = self.registry.people[self.fixtureName]
        self.failUnlessEqual(person.name, self.validData['name'])
    
    def testFormFields(self):
        self.checkFormField('name',
            valids = ['..', 'jo', 'joh', 'john', 'john99', 'johnbywater', 'john-bywater', 'john.bywater', 'john_bywater', 'johnbywaterrrrrrrrrr'],
            invalids = ['', '.', '', 'm', '1', ' ', 'home', 'create', 'find', 'search', 'update', 'delete', 'purge', 'login', 'logout', 'johnbywaterrrrrrrrrrrz'],
        )


class TestPersonUpdateManipulator(PersonManipulatorTestCase):

    def setUp(self):
        super(TestPersonUpdateManipulator, self).setUp()
        self.manipulator.create(self.validData)

    def testUpdate(self):
        person = self.registry.people[self.fixtureName]
        self.failUnlessEqual(person.name, self.validData['name'])
        self.validData['email'] = 'john@doe.com'
        self.manipulator.update(self.validData)
        person = self.registry.people[self.fixtureName]
        self.failUnlessEqual(person.email, self.validData['email'])

    def createManipulator(self):
        return PersonUpdateManipulator(objectRegister=self.registry.people, pickerClass=GetEditableAttributes)


class ProjectManipulatorTestCase(ManipulatorTestCase):

    fixtureName = 'ProjectManipulatorTestCase'
    fixtureDescription = 'Project manipulator test case.'

    def setUp(self):
        super(ProjectManipulatorTestCase, self).setUp()
        self.tearDownFixtures()
        self.validData = MultiValueDict()
        self.validData['name'] = self.fixtureName
        self.validData['description'] = self.fixtureDescription
        self.invalidData = MultiValueDict()
        self.invalidData['wrong'] = 'wrong'

    def tearDown(self):
        super(ProjectManipulatorTestCase, self).tearDown()
        self.tearDownFixtures()

    def tearDownFixtures(self):
        if self.fixtureName in self.registry.projects.getAll():
            project = self.registry.projects.getAll()[self.fixtureName]
            project.delete()
            project.purge()


class TestProjectCreateManipulator(ProjectManipulatorTestCase):

    def setUp(self):
        super(TestProjectCreateManipulator, self).setUp()
        self.manipulator.create(self.validData)

    def testCreate(self):
        project = self.registry.projects[self.fixtureName]
        self.failUnlessEqual(project.name, self.validData['name'])
    
    def createManipulator(self):
        return DomainObjectManipulator(objectRegister=self.registry.projects, pickerClass=GetInitableAttributes)

    def testFormFields(self):
        self.checkFormField('name',
            valids = ['mem', 'meme', 'mem99' ],
            invalids = ['', 'm', 'me', 'meme.', 'meme-', 'meme_', 'home' ,'create' ,'find' ,'search' ,'update' ,'delete' ,'purge' ,'admin' ,'person' ,'project' ,'login' ,'media', 'sixteencharsssss'],
        )


class TestProjectUpdateManipulator(ProjectManipulatorTestCase):

    def setUp(self):
        super(TestProjectUpdateManipulator, self).setUp()
        self.manipulator.create(self.validData)

    def testUpdate(self):
        project = self.registry.projects[self.fixtureName]
        self.failUnlessEqual(project.name, self.validData['name'])
        self.validData['description'] = 'Blah blah blah'
        self.manipulator.update(self.validData)
        project = self.registry.projects[self.fixtureName]
        self.failUnlessEqual(project.description, self.validData['description'])

    def createManipulator(self):
        return DomainObjectManipulator(objectRegister=self.registry.projects, pickerClass=GetEditableAttributes)


class ServiceManipulatorTestCase(ManipulatorTestCase):

    fixtureName = 'ServiceManipulatorTestCase'
    pluginFixtureName = 'example'
    projectFixtureName = 'ServiceManipulatorTestCase'

    def setUp(self):
        super(ServiceManipulatorTestCase, self).setUp()
        self.tearDownFixtures()
        self.projectData = MultiValueDict()
        self.projectData['name'] = self.projectFixtureName
        self.pluginFixture = self.registry.plugins[self.pluginFixtureName]
        projectsManipulator = ProjectCreateManipulator(objectRegister=self.registry.projects)
        projectsManipulator.create(self.projectData)
        self.projectFixture = self.registry.projects[self.projectFixtureName]
        self.validData = MultiValueDict()
        self.validData['name'] = self.fixtureName
        self.validData['project'] = self.projectFixtureName
        self.validData['plugin'] = self.pluginFixtureName
        self.invalidData = MultiValueDict()
        self.invalidData['wrong'] = 'wrong'

    def tearDown(self):
        super(ServiceManipulatorTestCase, self).tearDown()
        self.tearDownFixtures()

    def tearDownFixtures(self):
        if self.fixtureName in self.registry.projects.getAll():
            project = self.registry.projects.getAll()[self.fixtureName]
            project.delete()
            project.purge()


# Todo: Put service name validation checks somewhere else.

#class TestServiceCreateManipulator(ServiceManipulatorTestCase):
#
#    def setUp(self):
#        super(TestServiceCreateManipulator, self).setUp()
#        self.manipulator.create(self.validData)
#
#    def testCreate(self):
#        service = self.projectFixture.services[self.fixtureName]
#        self.failUnlessEqual(service.name, self.validData['name'])
#    
#    def createManipulator(self):
#        return ServiceCreateManipulator(objectRegister=self.registry.services, pickerClass=GetInitableAttributes)
#
#    def testFormFields(self):
#        self.checkFormField('name',
#            valids = ['m', 'me', 'mem', 'meme', 'mem99', 'Mem'],
#            invalids = ['', '%', '$', '/', '&', 'seventeencharssss'],
#        )
#
#
#class TestServiceUpdateManipulator(ServiceManipulatorTestCase):
#
#    def setUp(self):
#        super(TestServiceUpdateManipulator, self).setUp()
#        self.manipulator.create(self.validData)
#
#    def testUpdate(self):
#        service = self.projectFixture.services[self.fixtureName]
#        self.failUnlessEqual(service.name, self.validData['name'])
#        newName = 'Blah blah blah'
#        self.validData['name'] = newName
#        self.manipulator.update(self.validData)
#        service = self.projectFixture.services[newName]
#        self.failUnlessEqual(service.name, newName) 
#        self.failUnlessEqual(service.plugin.name, self.validData['plugin'])
#
#    def createManipulator(self):
#        return ServiceUpdateManipulator(objectRegister=self.registry.services, pickerClass=GetEditableAttributes)
#

class DomainObjectManipulatorTestCase(ManipulatorTestCase):

    fixtureName = 'ManipulatorTestCase'

    def setUp(self):
        super(DomainObjectManipulatorTestCase, self).setUp()
        self.validData = MultiValueDict()
        self.validData['name'] = self.fixtureName
        self.validData['fullname'] = '' # Not required.
        self.validData['password'] = 'password'
        self.validData['email'] = 'email@email.com'
        self.validData['role'] = '/roles/Visitor'
        #self.validData['state'] = 'active'
        self.validData.setlist('memberships', ['administration', 'example'])
        self.invalidData = MultiValueDict()
        self.invalidData['name'] = ''
        self.invalidData['password'] = 'password'
        self.invalidData['email'] = 'email@email.com'

    def tearDown(self):
        super(DomainObjectManipulatorTestCase, self).tearDown()
        if self.fixtureName in self.registry.people.getAll():
            person = self.registry.people.getAll()[self.fixtureName]
            person.delete()
            person.purge()

    def createManipulator(self):
        return DomainObjectManipulator(objectRegister=self.registry.people, pickerClass=self.pickerClass)


class TestDomainObjectManipulatorValidate(DomainObjectManipulatorTestCase):

    pickerClass = GetInitableAttributes

    def testValidate(self):
        self.manipulator.validate(self.validData)
        self.failUnlessRaises(FormError, self.manipulator.validate, self.invalidData)
        self.failUnless(self.manipulator.getErrors())
        self.failUnless(self.manipulator.getErrors()['name'])


class TestDomainObjectManipulatorCreate(DomainObjectManipulatorTestCase):

    pickerClass = GetInitableAttributes

    def testCreate(self):
        self.manipulator.create(self.validData)
        person = self.registry.people[self.fixtureName]
        self.failUnlessEqual(person.name, self.validData['name'])
        self.failUnlessEqual(person.fullname, self.validData['fullname'])
        #self.failUnlessEqual(person.email, self.validData['email'])
        self.failUnlessEqual(person.role.getUri(), self.validData['role'])
        self.failUnlessRaises(FormError, self.manipulator.create, self.invalidData)


class TestDomainObjectManipulatorUpdate(DomainObjectManipulatorTestCase):

    pickerClass = GetAdminEditableAttributes

    def setUp(self):
        super(TestDomainObjectManipulatorUpdate, self).setUp()
        objectRegister = self.registry.people
        manipulator = DomainObjectManipulator(objectRegister=objectRegister, pickerClass=GetInitableAttributes)
        manipulator.create(self.validData)
        domainObject = manipulator.domainObject
        self.manipulator = DomainObjectManipulator(
            objectRegister=objectRegister,
            domainObject=domainObject,
            pickerClass=self.pickerClass
        )

    def tearDown(self):
        super(TestDomainObjectManipulatorUpdate, self).tearDown()
        personName = self.validData['name']
        if personName in self.registry.people:
            person = self.registry.people[personName]
            person.delete()
            person.purge()
        
    def testUpdateString(self):
        self.validData['fullname'] = 'Test Fullname'
        self.manipulator.update(self.validData)
        person = self.registry.people[self.fixtureName]
        self.failUnlessEqual(person.fullname, self.validData['fullname'])

    def testUpdateHasA(self):
        self.validData['role'] = '/roles/Developer'
        self.manipulator.update(self.validData)
        person = self.registry.people[self.fixtureName]
        self.failUnlessEqual(person.role.getUri(), self.validData['role'])

    def testUpdateHasMany(self):
        self.validData.setlist('memberships', ['example'])
        self.manipulator.update(self.validData)
        person = self.registry.people[self.fixtureName]
        adminProject = self.registry.projects['administration']
        self.failIf(adminProject in person.memberships)


class HasManyManipulatorTestCase(ManipulatorTestCase):

    projectName = 'warandpeace'
    personName = 'levin'
    roleName = 'Developer'

    def setUp(self):
        super(HasManyManipulatorTestCase, self).setUp()
        self.person = self.registry.people[self.personName]
        self.validData = MultiValueDict()
        self.validData['person'] = self.personName
        self.validData['role'] = '/roles/%s' % self.roleName
        self.invalidData = MultiValueDict()
        self.invalidData['person'] = self.personName
        self.invalidData['role'] = '/roles/Destroyer'

    def tearDown(self):
        super(HasManyManipulatorTestCase, self).tearDown()
        if self.person in self.project.members:
            membership = self.project.members[self.person]
            membership.delete()
            membership.purge()

    def createManipulator(self):
        self.project = self.registry.projects[self.projectName]
        return HasManyManipulator(objectRegister=self.project.members, pickerClass=GetEditableAttributes)


class TestHasManyManipulator(HasManyManipulatorTestCase):

    def testValidate(self):
        try:
            self.manipulator.validate(self.validData)
        except FormError, inst:
            self.fail("There were form errors: %s" % inst.errors)
        self.failUnlessRaises(FormError, self.manipulator.validate, self.invalidData)

