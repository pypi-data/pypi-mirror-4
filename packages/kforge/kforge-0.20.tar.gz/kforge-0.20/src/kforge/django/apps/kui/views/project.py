from dm.view.base import *
from kforge.django.apps.kui.views.base import KforgeView
from kforge.exceptions import KforgeCommandError
import kforge.command
import kforge.accesscontrol
from kforge.command.emailjoinrequest import EmailJoinRequest

class AbstractProjectView(AbstractClassView, KforgeView):

    domainClassName = 'Project'
    majorNavigationItem = '/projects/'


class ProjectClassView(AbstractProjectView):

    minorNavigationItem = '/projects/'
    
    def __init__(self, **kwds):
        super(ProjectClassView, self).__init__(**kwds)
        self._canCreateProject = None
        self._canUpdateProject = None
        self._canDeleteProject = None
        self._canCreateMember = None
        self._canReadMember = None
        self._canUpdateMember = None
        self._canDeleteMember = None
        self._canCreateService = None
        self._canReadService = None
        self._canUpdateService = None
        self._canDeleteService = None

    def setMinorNavigationItems(self):
        self.minorNavigation = [
            {'title': 'Index', 'url': '/projects/'}
        ]
        self.minorNavigation.append(
            {'title': 'Search', 'url': '/projects/search/'}
        )
        if self.canCreateProject():
            self.minorNavigation.append(
                {'title': 'New', 'url': '/projects/create/'}
            )

    def setContext(self):
        super(ProjectClassView, self).setContext()
        self.context.update({
            'project' : self.getDomainObject(),
        })

    def getDomainObject(self):
        super(ProjectClassView, self).getDomainObject()
        self.project = self.domainObject
        return self.project

    def getProject(self):
        return self.getDomainObject()

    def isAuthorised(self, **kwds):
        return self.accessController.isAuthorised(**kwds)

    def canCreateProject(self):
        if self._canCreateProject == None:
            if self.project:
                protectedObject = self.project
            else:
                protectedObject = self.getDomainClass('Project')
            self._canCreateProject = self.canCreate(protectedObject, project=self.getProject())
        return self._canCreateProject

    def canUpdateProject(self):
        if self._canUpdateProject == None:
            if self.project:
                protectedObject = self.project
            else:
                protectedObject = self.getDomainClass('Project')
            self._canUpdateProject = self.canUpdate(protectedObject, project=self.getProject())
        return self._canUpdateProject

    def canDeleteProject(self):
        if self._canDeleteProject == None:
            if self.project:
                protectedObject = self.project
            else:
                protectedObject = self.getDomainClass('Project')
            self._canDeleteProject = self.canDelete(protectedObject, project=self.getProject())
        return self._canDeleteProject

    def canCreateMember(self):
        if self._canCreateMember == None:
            if self.member:
                protectedObject = self.member
            else:
                protectedObject = self.getDomainClass('Member')
            self._canCreateMember = self.canCreate(protectedObject, project=self.getProject())
        return self._canCreateMember

    def canReadMember(self):
        if self._canReadMember == None:
            if self.member:
                protectedObject = self.member
            else:
                protectedObject = self.getDomainClass('Member')
            self._canReadMember = self.canRead(protectedObject, project=self.getProject())
        return self._canReadMember

    def canUpdateMember(self):
        if self._canUpdateMember == None:
            if self.member:
                protectedObject = self.member
            else:
                protectedObject = self.getDomainClass('Member')
            self._canUpdateMember = self.canUpdate(protectedObject, project=self.getProject())
        return self._canUpdateMember

    def canDeleteMember(self):
        if self._canDeleteMember == None:
            if self.member:
                protectedObject = self.member
            else:
                protectedObject = self.getDomainClass('Member')
            self._canDeleteMember = self.canDelete(protectedObject, project=self.getProject())
        return self._canDeleteMember

    def canCreateService(self):
        if self._canCreateService == None:
            if self.service:
                protectedObject = self.service
            else:
                protectedObject = self.getDomainClass('Service')
            self._canCreateService = self.canCreate(protectedObject, project=self.getProject())
        return self._canCreateService

    def canReadService(self):
        if self._canReadService == None:
            if self.service:
                protectedObject = self.service
            else:
                protectedObject = self.getDomainClass('Service')
            self._canReadService = self.canRead(protectedObject, project=self.getProject())
        return self._canReadService

    def canUpdateService(self):
        if self._canUpdateService == None:
            if self.service:
                protectedObject = self.service
            else:
                protectedObject = self.getDomainClass('Service')
            self._canUpdateService = self.canUpdate(protectedObject, project=self.getProject())
        return self._canUpdateService

    def canDeleteService(self):
        if self._canDeleteService == None:
            if self.service:
                protectedObject = self.service
            else:
                protectedObject = self.getDomainClass('Service')
            self._canDeleteService = self.canDelete(protectedObject, project=self.getProject())
        return self._canDeleteService


class ProjectListView(AbstractListView, ProjectClassView):

    templatePath = 'project/list'
    minorNavigationItem = '/projects/'

    def canAccess(self):
        return self.canReadProject()

    def getDomainObjectList(self):
        register = self.getManipulatedObjectRegister()
        if self.session:
            viewerName = self.session.person.name
        else:
            viewerName = ''
        return register.findDomainObjects(__accessedBy__=viewerName)


class ProjectSearchView(AbstractSearchView, ProjectClassView):

    templatePath = 'project/search'
    minorNavigationItem = '/projects/search/'
    
    def canAccess(self):
        return self.canReadProject()


class ProjectCreateView(AbstractCreateView, ProjectClassView):

    templatePath = 'project/create'
    minorNavigationItem = '/projects/create/'

    def canAccess(self):
        return self.canCreateProject()
        
    def makePostManipulateLocation(self):
        return '/projects/%s/' % self.getDomainObject().getRegisterKeyValue()

    def manipulateDomainObject(self):
        super(ProjectCreateView, self).manipulateDomainObject()
        if not self.domainObject:
            raise "View did not produce an object."
        memberCommandClass = self.commands['MemberCreate']
        project = self.domainObject
        person = self.session.person
        roleName = 'Administrator'
        role = self.registry.roles[roleName]
        memberCommand = memberCommandClass(
            project=project, person=person, role=role
        )
        memberCommand.execute()


class ProjectInstanceView(ProjectClassView):

    def setMinorNavigationItems(self):
        project = self.getDomainObject()
        projectMenuTitle = project.title or project.name
        self.minorNavigation = []
        self.minorNavigation.append({
                'title': projectMenuTitle,
                'url': '/projects/%s/' % self.domainObjectKey
        })
        if self.canUpdateProject():
            self.minorNavigation.append({
                    'title': 'Settings',
                    'url': '/projects/%s/edit/' % self.domainObjectKey
            })
        self.minorNavigation.append({
                'title': 'Services',
                'url': '/projects/%s/services/' % self.domainObjectKey
        })
        self.minorNavigation.append({
                'title': 'Members',
                'url': '/projects/%s/members/' % self.domainObjectKey
        })

    def setMinorNavigationItem(self):
        self.minorNavigationItem = '/projects/%s/' % self.domainObjectKey


class ProjectReadView(AbstractReadView, ProjectInstanceView):

    templatePath = 'project/read'
    minorNavigationItem = '/projects/'

    def canAccess(self):
        if not self.getDomainObject():
            return False
        return self.canReadProject()

    def canJoinProject(self):
        if self.session is None or self.session.person is None \
            or self.session.person in self.project.members or self.session.person in self.project.members.pending:
            return False
        return True


class ProjectUpdateView(AbstractUpdateView, ProjectInstanceView):

    templatePath = 'project/update'

    def canAccess(self):
        if not self.getDomainObject():
            msg = "Access Denied: No domain object on project update view."
            self.logger.debug(msg)
            return False
        return self.canUpdateProject()

    def makePostManipulateLocation(self):
        return '/projects/%s/' % self.getDomainObject().getRegisterKeyValue()

    def setMinorNavigationItem(self):
        self.minorNavigationItem = '/projects/%s/edit/' % self.domainObjectKey


class ProjectDeleteView(AbstractDeleteView, ProjectInstanceView):

    templatePath = 'project/delete'

    def canAccess(self):
        if not self.getDomainObject():
            return False
        return self.canDeleteProject()

    def makePostManipulateLocation(self):
        return '/projects/'

    def actionReloadsApache(self):
        return True


class ProjectJoinView(AbstractReadView, ProjectInstanceView):

    templatePath = 'project/join'

    def canAccess(self):
        if not self.getDomainObject() or self.session is None or self.session.person is None:
            msg = "Non logged in person attempting to join a project"
            self.logger.debug(msg)
            return False
        # Immediately add person as pending member (no form submission).
        person = self.session.person
        project = self.getDomainObject()
        self.logger.debug("Creating pending member with person '%s' and project '%s'." % (person.name, project.name))
        project.members.pending.create(person)
        # Send notification e-mail to the project administrators.
        emailCommand = EmailJoinRequest(project, person)
        emailCommand.execute()
        return True

def list(request):
    view = ProjectListView(request=request)
    return view.getResponse()

def search(request, startsWith=''):
    view = ProjectSearchView(request=request, startsWith=startsWith)
    return view.getResponse()

def create(request, returnPath=''):
    view = ProjectCreateView(request=request)
    return view.getResponse()

def read(request, projectName=''):
    view = ProjectReadView(request=request, domainObjectKey=projectName)
    return view.getResponse()

def update(request, projectName):
    view = ProjectUpdateView(request=request, domainObjectKey=projectName)
    return view.getResponse()

def delete(request, projectName):
    view = ProjectDeleteView(request=request, domainObjectKey=projectName)
    return view.getResponse()

def join(request, projectName):
    view = ProjectJoinView(request=request, domainObjectKey=projectName)
    return view.getResponse()

