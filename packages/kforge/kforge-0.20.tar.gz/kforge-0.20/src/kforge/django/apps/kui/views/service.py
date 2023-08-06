from kforge.django.apps.kui.views.projectHasMany import ProjectHasManyView
from dm.view.base import AbstractUpdateView
from dm.view.base import AbstractListHasManyView
from dm.view.base import AbstractCreateHasManyView
from dm.view.base import AbstractReadHasManyView
from dm.view.base import AbstractUpdateHasManyView
from dm.view.base import AbstractDeleteHasManyView
from kforge.django.apps.kui.views import manipulator
from dm.webkit import webkitName, webkitVersion
from kforge.dictionarywords import *
from dm.view.base import HttpResponse

class ServiceView(ProjectHasManyView):

    hasManyClassName = 'Service'
            
    def __init__(self, **kwds):
        super(ServiceView, self).__init__(hasManyName='services', **kwds)
        self.service = None

    def getService(self):
        if self.service == None:
            self.service = self.getAssociationObject()
        return self.service

    def setContext(self):
        super(ServiceView, self).setContext()
        self.context.update({
            'service' : self.getService(),
        })

    def setMinorNavigationItem(self):
        self.minorNavigationItem = '/projects/%s/services/' % (
            self.domainObjectKey
        )

    def makePostManipulateLocation(self):
        #return '/projects/%s/services/' % (
        return '/projects/%s/' % (
            self.domainObjectKey
        )

    def createDelayedRedirectResponse(self, transitionMsg):
        delay = self.dictionary[APACHE_WSGI_REDIRECT_DELAY]
        try:
            delay = str(int(delay.strip()))
        except:
            delay = '0'
        if int(delay) > 0 and self.redirectRequiresDelay():
            # Redirect after delay to allow server to restart.
            self.response = HttpResponse('Please wait a few moments (%ss) whilst your service is %s....' % (delay, transitionMsg))
            self.response.status_code = 200
            self.response['Refresh'] = '%s; url=%s' % (delay, self.redirect)
        else:
            super(ServiceView, self).createRedirectResponse()


class ServiceListView(ServiceView, AbstractListHasManyView):

    templatePath = 'service/list'
         
    def canAccess(self):
        return self.canReadProject()


class ServiceCreateView(ServiceView, AbstractCreateHasManyView):

    templatePath = 'service/create'
    
    def canAccess(self):
        return self.canCreateService()
        
    def makePostManipulateLocation(self):
        return '/projects/%s/services/%s/' % (
            self.domainObjectKey,
            self.getService().name
        )

    def actionReloadsApache(self):
        return True


class ServiceReadView(ServiceView, AbstractReadHasManyView):

    templatePath = 'service/read'

    def canAccess(self):
        return self.canReadService()

    def getStatusMessage(self):
        service = self.getService()
        if service:
            statusMsg = service.getStatusMessage()
        else:
            statusMsg = "Not found"
        return statusMsg

    def getServiceUserHelp(self):
        try:
            service = self.getService()
            if service:
                userHelp = service.getUserHelp(self.getServiceLocation())
            if webkitName == 'django' and webkitVersion == '1.0':
                from django.utils.safestring import mark_safe
                return mark_safe(userHelp)
            else:
                return userHelp
        except Exception, inst:
            msg = "Error retrieving user help message: %s" % str(inst)
            self.logger.error(msg)
        return ''

    def setContext(self):
        super(ServiceReadView, self).setContext()
        # Todo: Rename location -> locator?
        self.context.update({
            'serviceLocation' : self.getServiceLocation(), 
            'serviceUserHelp': self.getServiceUserHelp(),
        })

    def getServiceLocation(self):
        service = self.getService()
        path = service.getUrlPath()
        return self.buildAbsoluteUri(path)


class ServiceUpdateView(ServiceView, AbstractUpdateHasManyView):

    templatePath = 'service/update'

    def canAccess(self):
        return self.canUpdateService()

    def makePostManipulateLocation(self):
        return '/projects/%s/services/%s/' % (
            self.domainObjectKey,
            self.getAssociationObject().name,
        )

    def actionReloadsApache(self):
        return False


class ServiceDeleteView(ServiceView, AbstractDeleteHasManyView):

    templatePath = 'service/delete'

    def canAccess(self):
        return self.canDeleteService()

    def actionReloadsApache(self):
        return False


def list(request, projectName=''):
    view = ServiceListView(
        request=request,
        domainObjectKey=projectName,
    )
    return view.getResponse()

def create(request, projectName):
    view = ServiceCreateView(
        request=request,
        domainObjectKey=projectName,
    )
    return view.getResponse()
    
def read(request, projectName, serviceName):
    view = ServiceReadView(
        request=request,
        domainObjectKey=projectName,
        hasManyKey=serviceName,
    )
    return view.getResponse()
    
def update(request, projectName, serviceName):
    view = ServiceUpdateView(
        request=request,
        domainObjectKey=projectName,
        hasManyKey=serviceName,
    )
    return view.getResponse()
    
def delete(request, projectName, serviceName):
    view = ServiceDeleteView(
        request=request,
        domainObjectKey=projectName,
        hasManyKey=serviceName,
    )
    return view.getResponse()

