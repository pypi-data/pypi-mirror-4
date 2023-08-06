import unittest
from kforge.django.apps.kui.views.test.base import ViewTestCase
from kforge.django.apps.kui.views.admin import AdminIndexView
from kforge.django.apps.kui.views.admin import AdminModelView
from kforge.django.apps.kui.views.admin import AdminListView
from kforge.django.apps.kui.views.admin import AdminCreateView
from kforge.django.apps.kui.views.admin import AdminReadView
from kforge.django.apps.kui.views.admin import AdminUpdateView
from kforge.django.apps.kui.views.admin import AdminDeleteView
from kforge.django.apps.kui.views.admin import AdminListHasManyView
from kforge.django.apps.kui.views.admin import AdminCreateHasManyView
from kforge.django.apps.kui.views.admin import AdminReadHasManyView
from kforge.django.apps.kui.views.admin import AdminUpdateHasManyView
from kforge.django.apps.kui.views.admin import AdminDeleteHasManyView
from kforge.ioc import *
from django.utils.datastructures import MultiValueDict

def suite():
    suites = [
        unittest.makeSuite(TestIndexView),
        unittest.makeSuite(TestModelView),
        unittest.makeSuite(TestListView),
        unittest.makeSuite(TestCreateView),
        unittest.makeSuite(TestReadView),
        unittest.makeSuite(TestUpdateView),
        unittest.makeSuite(TestDeleteView),
        unittest.makeSuite(TestListHasManyView),
        unittest.makeSuite(TestCreateHasManyView),
        unittest.makeSuite(TestReadHasManyView),
        unittest.makeSuite(TestUpdateHasManyView),
        unittest.makeSuite(TestDeleteHasManyView),
    ]
    return unittest.TestSuite(suites)


class AdminTestCase(ViewTestCase):

    projectName = 'administration'

    fixtureKeyName    = 'AdminTestCaseFixture'
    fixtureEmail      = 'test@test.com'
    fixtureFullname   = 'Admin TestCase Fixture'
    fixtureSystemRole = '/roles/Administrator'
    fixtureState      = '/states/active'

    def setUp(self):
        super(AdminTestCase, self).setUp()

        self.deletePerson()
       
        register = self.getPersonRegister()
        while 'AdminTestCaseUser' in register.getAll():
            person = register.getAll()['AdminTestCaseUser']
            person.delete()
            person.purge()
        adminTestCaseUser = register.create('AdminTestCaseUser')
        roleRegister = self.getRoleRegister()
        adminTestCaseUser.role = roleRegister['Administrator']
        adminTestCaseUser.save()
        self.view.session = adminTestCaseUser.sessions.create()

    def tearDown(self):
        register = self.getPersonRegister()
        while 'AdminTestCaseUser' in register.getAll():
            person = register.getAll()['AdminTestCaseUser']
            for session in person.sessions:
                session.delete()
            person.delete()
            person.purge()
        while self.fixtureKeyName in register.getAll():
            person = register.getAll()[self.fixtureKeyName]
            person.delete()
            person.purge()
        super(AdminTestCase, self).tearDown()
        
    def test_checkAdminAccess(self):
        self.failUnless(self.view.checkAccessControl())

    def createPerson(self):
        if self.isPerson():
            self.deletePerson()
        self.failIf(self.isPerson())
        personRegister = self.getPersonRegister()
        person = personRegister.create(self.fixtureKeyName)
        person.fullname = self.fixtureFullname
        person.save()
        self.failUnless(self.isPerson())

    def deletePerson(self):
        personRegister = self.getPersonRegister()
        while self.fixtureKeyName in personRegister:
            person = personRegister[self.fixtureKeyName]
            person.delete()
            person.purge()
        self.failIf(self.isPerson())

    def isPerson(self):
        personRegister = self.getPersonRegister()
        return self.fixtureKeyName in personRegister

    def getProjectRegister(self):
        registry = RequiredFeature('DomainRegistry')
        projectClass = registry.getDomainClass('Project')
        projectRegister = projectClass.createRegister()
        return projectRegister

    def getPersonRegister(self):
        registry = RequiredFeature('DomainRegistry')
        personClass = registry.getDomainClass('Person')
        personRegister = personClass.createRegister()
        return personRegister

    def getRoleRegister(self):
        registry = RequiredFeature('DomainRegistry')
        roleClass = registry.getDomainClass('Role')
        roleRegister = roleClass.createRegister()
        return roleRegister


class TestIndexView(AdminTestCase):

    viewClass = AdminIndexView


class TestModelView(AdminTestCase):

    viewClass = AdminModelView


class AdminClassTestCase(AdminTestCase):

    fixtureClassName = 'Person'

    def buildView(self):
        if not self.viewClass:
            raise "No viewClass set on view test class."
        view = self.viewClass(
            request=self.request,
            domainClassName=self.fixtureClassName
        )
        self.failUnlessEqual(view.domainClassName, self.fixtureClassName)
        return view


class TestListView(AdminClassTestCase):

    viewClass = AdminListView
    

class TestCreateView(AdminClassTestCase):

    viewClass = AdminCreateView

    def buildRequest(self):
        request = super(TestCreateView, self).buildRequest() 
        request.POST = MultiValueDict()
        request.POST['name']     = self.fixtureKeyName
        request.POST['fullname'] = self.fixtureFullname
        request.POST['password'] = self.fixtureKeyName
        request.POST['email']    = self.fixtureKeyName +"@"+ self.fixtureKeyName +".com"
        request.POST['role']     = self.fixtureSystemRole
        request.POST['state']    = self.fixtureState
        return request

    def test_getResponse(self):
        self.failIf(self.isPerson())
        self.view.getResponse()
        self.failUnless(self.isPerson())
        self.deletePerson()
        self.failIf(self.isPerson())


class AdminInstanceTestCase(AdminClassTestCase):

    def setUp(self):
        super(AdminInstanceTestCase, self).setUp()
        self.createPerson()
        
    def buildView(self):
        if not self.viewClass:
            raise "No viewClass set on view test class."
        self.failUnless(self.fixtureClassName)
        self.failUnless(self.fixtureKeyName)
        view = self.createView()
        self.failUnlessEqual(view.domainClassName, self.fixtureClassName)
        self.failUnlessEqual(view.domainObjectKey, self.fixtureKeyName)
        return view

    def createView(self):
        view = self.viewClass(
            request=self.request,
            domainClassName=self.fixtureClassName,
            domainObjectKey=self.fixtureKeyName,
        )
        return view


class TestReadView(AdminInstanceTestCase):

    viewClass = AdminReadView

    def test_getResponse(self):
        self.view.getResponse()
        domainObject = self.view.getDomainObject()
        self.failUnlessEqual(domainObject.name, self.fixtureKeyName)
        self.failUnlessEqual(domainObject.fullname, self.fixtureFullname)


class TestUpdateView(AdminInstanceTestCase):

    viewClass = AdminUpdateView

    def buildRequest(self):
        request = super(TestUpdateView, self).buildRequest() 
        request.POST = MultiValueDict()
        request.POST['name']     = self.fixtureKeyName
        request.POST['fullname'] = self.fixtureFullname + " Updated"
        request.POST['password'] = self.fixtureKeyName
        request.POST['email']    = self.fixtureKeyName +"@"+ self.fixtureKeyName +".com"
        request.POST['role']     = self.fixtureSystemRole
        request.POST['state']    = self.fixtureState
        return request

    def test_getResponse(self):
        self.view.getResponse()
        domainObject = self.view.getManipulatedDomainObject()
        self.failUnlessEqual(domainObject.fullname, self.fixtureFullname + " Updated")


class TestDeleteView(AdminInstanceTestCase):

    viewClass = AdminDeleteView

    def test_getResponse(self):
        self.failUnless(self.isPerson())
        self.view.getResponse()
        self.deletePerson()
        self.failIf(self.isPerson())


class AdminHasManyTestCase(AdminInstanceTestCase):

    fixtureHasManyName = 'memberships'
    fixtureHasManyKey = 'example'

    def setUp(self):
        super(AdminHasManyTestCase, self).setUp()
        self.createMember()
        
    def tearDown(self):
        super(AdminHasManyTestCase, self).tearDown()
        
    def createMember(self):
        if self.isMember():
            self.deleteMember()
        self.failIf(self.isMember())
        personRegister = self.getPersonRegister()
        person = personRegister[self.fixtureKeyName]
        projectRegister = self.getProjectRegister()
        project = projectRegister[self.fixtureHasManyKey]
        member = project.members.create(person)
        self.failUnless(self.isMember())

    def isMember(self):
        personRegister = self.getPersonRegister()
        projectRegister = self.getProjectRegister()
        person = personRegister[self.fixtureKeyName]
        project = projectRegister[self.fixtureHasManyKey]
        return person in project.members

 
class TestListHasManyView(AdminHasManyTestCase):

    viewClass = AdminListHasManyView

    def createView(self):
        view = self.viewClass(
            request=self.request,
            domainClassName=self.fixtureClassName,
            domainObjectKey=self.fixtureKeyName,
            hasManyName=self.fixtureHasManyName,
        )
        return view

    def test_members(self):
        self.view.getResponse()
        domainObject = self.view.getDomainObject()
        self.failUnless(hasattr(domainObject, 'memberships'), domainObject)


class TestCreateHasManyView(TestListHasManyView):

    viewClass = AdminCreateHasManyView
    requiredResponseClassName = 'HttpResponseRedirect'
    requiredRedirect = '/admin/model/Person/AdminTestCaseFixture/memberships/'

    def createMember(self):
        pass
        
    def buildRequest(self):
        request = super(TestCreateHasManyView, self).buildRequest() 
        request.POST = MultiValueDict()
        request.POST['project'] = '/projects/warandpeace'
        request.POST['role']   = self.fixtureSystemRole
        return request

    def createView(self):
        view = self.viewClass(
            request=self.request,
            domainClassName=self.fixtureClassName,
            domainObjectKey=self.fixtureKeyName,
            hasManyName=self.fixtureHasManyName,
        )
        return view


class TestReadHasManyView(TestListHasManyView):

    viewClass = AdminReadHasManyView

    def createView(self):
        view = self.viewClass(
            request=self.request,
            domainClassName=self.fixtureClassName,
            domainObjectKey=self.fixtureKeyName,
            hasManyName=self.fixtureHasManyName,
            hasManyKey=self.fixtureHasManyKey,
        )
        return view


class TestUpdateHasManyView(TestListHasManyView):

    viewClass = AdminUpdateHasManyView

    def createView(self):
        view = self.viewClass(
            request=self.request,
            domainClassName=self.fixtureClassName,
            domainObjectKey=self.fixtureKeyName,
            hasManyName=self.fixtureHasManyName,
            hasManyKey=self.fixtureHasManyKey,
        )
        return view


class TestDeleteHasManyView(TestListHasManyView):

    viewClass = AdminDeleteHasManyView

    def createView(self):
        view = self.viewClass(
            request=self.request,
            domainClassName=self.fixtureClassName,
            domainObjectKey=self.fixtureKeyName,
            hasManyName=self.fixtureHasManyName,
            hasManyKey=self.fixtureHasManyKey,
        )
        return view

