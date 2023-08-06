from kforge.django.apps.kui.views.projectHasMany import ProjectHasManyView
from dm.view.base import AbstractPendingView
from dm.view.base import AbstractListHasManyView
from dm.view.base import AbstractCreateHasManyView
from dm.view.base import AbstractApproveHasManyView
from dm.view.base import AbstractRejectHasManyView
from dm.view.base import AbstractReadHasManyView
from dm.view.base import AbstractUpdateHasManyView
from dm.view.base import AbstractDeleteHasManyView
import kforge.command

from kforge.command.emailjoinrequest import EmailJoinApprove, EmailJoinReject


class MemberView(ProjectHasManyView):

    hasManyClassName = 'Member'

    def __init__(self, **kwds):
        super(MemberView, self).__init__(hasManyName='members', **kwds)

    def setContext(self):
        super(MemberView, self).setContext()
        self.context.update({
            'member' : self.getAssociationObject(),
        })

    def setMinorNavigationItem(self):
        self.minorNavigationItem = '/projects/%s/members/' % self.domainObjectKey


class MemberListView(MemberView, AbstractListHasManyView):

    templatePath = 'member/list'
    
    def canAccess(self):
        return self.canReadProject()


class MemberCreateView(MemberView, AbstractCreateHasManyView):

    templatePath = 'member/create'
    
    def canAccess(self):
        return self.canCreateMember()

    def makePostManipulateLocation(self):
        return '/projects/%s/' % (
            self.domainObjectKey
        )
        #return '/projects/%s/%s/' % (
        #    self.domainObjectKey, self.hasManyName
        #)

    def manipulateDomainObject(self):
        super(MemberCreateView, self).manipulateDomainObject()
        # Make sure that if this member is pending, we remove them from that list.
        # Todo: Push this logic down into the model: on create, if pending
        # register has object by key of created object, then delete pending object?
        project = self.domainObject
        personUri = self.getRequestParam('person')
        person = self.registry.dereference(personUri).target
        if person in project.members.pending:
            project.members.pending[person].delete()
            msg = "Deleted member '%s' from pending list for project %s since they were added as a member" % (person.name, project.name)
            self.logger.debug(msg)


class MemberUpdateView(MemberView, AbstractUpdateHasManyView):

    templatePath = 'member/update'
    
    def canAccess(self):
        return self.canUpdateMember()

    def makePostManipulateLocation(self):
        return '/projects/%s/' % (
            self.domainObjectKey
        )
        #return '/projects/%s/%s/' % (
        #    self.domainObjectKey, self.hasManyName
        #)


class MemberDeleteView(MemberView, AbstractDeleteHasManyView):

    templatePath = 'member/delete'
    
    def canAccess(self):
        self.member = self.getAssociationObject()
        return self.canDeleteMember()

    def makePostManipulateLocation(self):
        if self.session.person == self.member.person:
            return '/people/%s/' % self.session.person.name
        else:
            return '/projects/%s/' % (
                self.domainObjectKey
            )
            #return '/projects/%s/%s/' % (
            #    self.domainObjectKey, self.hasManyName
            #)


class MemberApproveView(MemberView, AbstractApproveHasManyView):

    templatePath = 'member/approve'
    fieldNames = ['role']
    
    def canAccess(self):
        return self.canCreateMember()

    def manipulateDomainObject(self):
        member = self.getManipulatedDomainObject()
        super(MemberApproveView, self).manipulateDomainObject()
        # Send e-mail to the member letting them know they got approved.
        emailCommand = EmailJoinApprove(member.project, member.person)
        emailCommand.execute()

    def makePostManipulateLocation(self):
        return '/projects/%s/members/' % (
            self.domainObjectKey
        )


class MemberRejectView(MemberView, AbstractRejectHasManyView):

    templatePath = 'member/reject'
    
    def canAccess(self):
        return self.canCreateMember()

    def manipulateDomainObject(self):
        member = self.getManipulatedDomainObject()
        super(MemberRejectView, self).manipulateDomainObject()
        # Send an e-mail to the member letting them know they got rejected.
        emailCommand = EmailJoinReject(member.project, member.person)
        emailCommand.execute()

    def makePostManipulateLocation(self):
        return '/projects/%s/members/' % (
            self.domainObjectKey
        )


def list(request, projectName=''):
    view = MemberListView(
        request=request,
        domainObjectKey=projectName,
    )
    return view.getResponse()
    
def create(request, projectName=''):
    view = MemberCreateView(
        request=request,
        domainObjectKey=projectName,
    )
    return view.getResponse()
    
def update(request, projectName='', personName=''):
    view = MemberUpdateView(
        request=request,
        domainObjectKey=projectName,
        hasManyKey=personName,
    )
    return view.getResponse()
    
def delete(request, projectName='', personName=''):
    view = MemberDeleteView(
        request=request,
        domainObjectKey=projectName,
        hasManyKey=personName,
    )
    return view.getResponse()

def approve(request, projectName='', personName=''):
    view = MemberApproveView(
        request=request,
        domainObjectKey=projectName,
        hasManyKey=personName,
    )
    return view.getResponse()

def reject(request, projectName='', personName=''):
    view = MemberRejectView(
        request=request,
        domainObjectKey=projectName,
        hasManyKey=personName,
    )
    return view.getResponse()

