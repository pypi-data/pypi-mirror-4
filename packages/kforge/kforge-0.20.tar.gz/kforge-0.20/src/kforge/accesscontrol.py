from dm.accesscontrol import AccessControlRequest, SystemAccessController
from kforge.exceptions import *

class ProjectAccessController(SystemAccessController):
    "Introduces project role possibilities to access controller."

    def isAccessAuthorised(self, person=None, actionName=None, 
            protectedObject=None, project=None, avoidMemos=False):
        return super(ProjectAccessController, self).isAccessAuthorised(
            person=person, actionName=actionName, 
            protectedObject=protectedObject, project=project, 
            avoidMemos=avoidMemos)

    def assertAccessNotAuthorised(self, result):
        self.assertMembershipNotAuthorised(result)
        super(ProjectAccessController, self).assertAccessNotAuthorised(result)

    def assertMembershipNotAuthorised(self, result):
        if result.request.project:
            try:
                role = result.request.person.memberships[result.request.project].role
            except KforgeRegistryKeyError, inst:
                pass
            else:
                msg = "project %s role" % role.name.lower()
                self.assertRoleNotAuthorised(result, role, msg)
            if not self.alsoCheckVisitor(result):
                return
            try:
                role = self.getVisitor().memberships[result.request.project].role
            except KforgeRegistryKeyError, inst:
                pass
            else: 
                msg = "visitor's project %s role" % role.name.lower()
                self.assertRoleNotAuthorised(result, role, msg)

    def makeMemoName(self, request):
        # Make sure service plugin memo names are distinct between projects.
        # Todo: Change service access control to use service object.
        memoName = super(ProjectAccessController, self).makeMemoName(request)
        if request.project:
            projectTag = request.project.id
        else:
            projectTag = None
        return "Project.%s.%s" % (projectTag, memoName)

