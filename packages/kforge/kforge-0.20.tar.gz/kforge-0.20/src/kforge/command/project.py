from dm.command import *
import kforge.regexps
import re

class ProjectCommand(Command):
    "Abstract Project command."
        
    def __init__(self, name):
        super(ProjectCommand, self).__init__(projectName=name)
        self.name = name
        self.project = None
        self.projects = self.registry.projects


class ProjectList(ProjectCommand):
    "Command to list registered projects."

    def __init__(self, userQuery='', startsWith='', startsWithAttributeName='', viewer=None):
        super(ProjectList, self).__init__('')
        self.userQuery= userQuery
        self.startsWith = startsWith
        self.startsWithAttributeName = startsWithAttributeName
        self.viewer = viewer

    def execute(self):
        "Make it so."
        super(ProjectList, self).execute()
        kwds = {}
        viewerName = self.viewer.name if self.viewer else ''
        kwds['__accessedBy__'] = viewerName
        if self.startsWith:
            selection = self.projects.startsWith(
                value=self.startsWith,
                attributeName=self.startsWithAttributeName,
                **kwds)
            self.results = [p for p in selection]
        elif self.userQuery:
            selection = self.projects.search(
                userQuery=self.userQuery, **kwds)
            self.results = [p for p in selection]
        else:
            self.results = self.projects.findDomainObjects(**kwds)
        return self.results


class ProjectCreate(DomainObjectCreate):
    "Command to create a new project."

    reservedNames = re.compile('^%s$' % kforge.regexps.reservedProjectName)

    def __init__(self, name='', **kwds):
        super(ProjectCreate, self).__init__(
            typeName='Project', objectId=name, objectKwds=kwds
        )
        self.project = None

    def execute(self):
        super(ProjectCreate, self).execute()
        self.project = self.object


class ProjectRead(DomainObjectRead):
    "Command to read a registered project."

    def __init__(self, name='', **kwds):
        super(ProjectRead, self).__init__(
            typeName='Project', objectId=name, objectKwds=kwds
        )
        self.project = None

    def execute(self):
        super(ProjectRead, self).execute()
        self.project = self.object


class ProjectDelete(ProjectCommand):
    "Command to delete a registered project."

    def __init__(self, name):
        super(ProjectDelete, self).__init__(name)

    def execute(self):
        "Make it so."
        super(ProjectDelete, self).execute()
        if not self.name in self.projects:
            message = "No project found with name '%s'." % self.name
            self.raiseError(message)
        project = self.projects[self.name]
        try:
            project.delete()
        except Exception, inst:
            message = "Couldn't delete project: %s" % str(inst)
            self.raiseError(message)
        else:
            self.commitSuccess()


class ProjectUndelete(ProjectCommand):
    "Command to undelete a deleted registered project."

    def __init__(self, name):
        super(ProjectUndelete, self).__init__(name)

    def execute(self):
        "Make it so."
        super(ProjectUndelete, self).execute()
        if not self.name in self.projects.getDeleted():
            message = "No deleted project found with name '%s'." % self.name
            self.raiseError(message)
        project = self.projects.getDeleted()[self.name]
        project.undelete()
        self.commitSuccess()


class ProjectPurge(ProjectCommand):
    "Command to purge a deleted registered project."

    def __init__(self, name):
        super(ProjectPurge, self).__init__(name)

    def execute(self):
        "Make it so."
        super(ProjectPurge, self).execute()
        if not self.name in self.projects.getDeleted():
            message = "No deleted project found with name '%s'." % self.name
            self.raiseError(message)
        project = self.projects.getDeleted()[self.name]
        project.purge()
        self.commitSuccess()


# Todo: Test for deleted projects. They were being missed.
class AllProjectRead(ProjectRead):
    "Command to read any project, regardless of state."

    def createRegister(self):
        register = super(AllProjectRead, self).createRegister()
        return self.registry.projects.getAll()


