from kforge.django.apps.kui.views.personHasMany import PersonHasManyView
from dm.view.base import AbstractListHasManyView
from dm.view.base import AbstractCreateHasManyView
from dm.view.base import AbstractReadHasManyView
from dm.view.base import AbstractUpdateHasManyView
from dm.view.base import AbstractDeleteHasManyView
import kforge.command

class SshKeyView(PersonHasManyView):

    hasManyKeyName = 'SshKey'

    def __init__(self, **kwds):
        super(SshKeyView, self).__init__(hasManyName='sshKeys', **kwds)
        if not self.isSshPluginEnabled():
            self.setRedirect('/people/home/')

    def setContext(self):
        super(SshKeyView, self).setContext()
        self.context.update({
            'sshKey'         : self.getAssociationObject(),
        })

#    def setMajorNavigationItem(self):
#        self.majorNavigationItem = '/people/home/'

    def canCreateSshKey(self):
        return self.canUpdatePerson()
    
    def canReadSshKey(self):
        return self.canUpdatePerson()

    def canDeleteSshKey(self):
        return self.canUpdatePerson()


class SshKeyCreateView(SshKeyView, AbstractCreateHasManyView):

    templatePath = 'sshKey/create'

    def canAccess(self):
        return self.canCreateSshKey()
        
    def getMinorNavigationItem(self):
        return '/people/%s/sshKeys/create/' % self.domainObjectKey

    def makePostManipulateLocation(self):
        return '/people/%s/sshKeys/create/' % self.domainObjectKey


class SshKeyDeleteView(SshKeyView, AbstractDeleteHasManyView):

    templatePath = 'sshKey/delete'
    
    def canAccess(self):
        return self.canDeleteSshKey()

    def getMinorNavigationItem(self):
        return '/people/%s/sshKeys/create/' % self.domainObjectKey

    def makePostManipulateLocation(self):
        return '/people/%s/sshKeys/create/' % self.domainObjectKey



def create(request, personName, returnPath=''):   
    view = SshKeyCreateView(request=request, domainObjectKey=personName)
    return view.getResponse()

def delete(request, personName, sshKeyId):
    view = SshKeyDeleteView(request=request, domainObjectKey=personName, hasManyKey=sshKeyId)
    return view.getResponse()

