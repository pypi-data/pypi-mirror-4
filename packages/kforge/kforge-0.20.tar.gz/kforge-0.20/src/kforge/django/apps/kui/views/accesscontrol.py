from kforge.django.apps.kui.views.base import KforgeView
from kforge.django.apps.kui.views.kui import HomeView
import kforge.command
from dm.command.emailpassword import EmailNewPassword
from kforge.exceptions import KforgeCommandError
import random

class AuthenticateView(HomeView):

    def __init__(self, **kwds):
        super(AuthenticateView, self).__init__(**kwds)
        self.isAuthenticateFail = False
        self.forgotPassword = False

    def canAccess(self):
        return True

    def authenticate(self):
        if self.session:
            return True
        name = self.request.POST.get('name', '')
        password = self.request.POST.get('password', '')
        command = kforge.command.PersonAuthenticate(name, password)
        try:
            command.execute()
        except KforgeCommandError, inst:
            msg = "Login authentication failure for person name '%s'." % name
            self.logger.warn(msg)
        else:
            self.startSession(command.person)

    def setContext(self):
        super(AuthenticateView, self).setContext()
        self.setAuthenticationContext()
        self.context.update({
            'isAuthenticateFail': self.isAuthenticateFail,
            'forgotPassword': self.forgotPassword,
        })

    def setAuthenticationContext(self):
        if self.request.POST:
            params = self.request.POST.copy()
            self.context.update({
                'name': params.get('name', ''),
                'password': params.get('password', ''),
            })


class LoginView(AuthenticateView):

    templatePath = 'login'

    def __init__(self, returnPath='', **kwds):
        self.returnPathArg = returnPath
        super(LoginView, self).__init__(**kwds)

    def getResponse(self):
        if self.request.POST:
            # Try to authenticate login credentials.
            self.authenticate()
            returnPath = self.request.POST.get('returnPath', '')
            if self.session:
                # Authenticated credentials.
                if returnPath.startswith('http://') or returnPath.startswith('https://'):
                    # Leave absolute URIs alone.
                    pass
                elif returnPath and returnPath[0] != '/': 
                    # Sometimes the leading slash gets lost (in URL parsing).
                    returnPath = '/%s' % returnPath
                # Substitute "profile page" alias.
                if returnPath == '/people/home/':
                    returnPath = '/people/%s/' % self.session.person.name
                # Default to profile page.
                if not returnPath or returnPath == '/logout/':
                    returnPath = '/people/%s/' % self.session.person.name
                if returnPath:
                    self.setRedirect(returnPath)
            else:
                # Not Authenticated.
                # Signal authentication failed.
                self.isAuthenticateFail = True
                # Pass return path forward.
                self.returnPath = returnPath
        elif 'returnPath' in self.request.GET:
            # Pass return path forward.
            self.returnPath = self.request.GET.get('returnPath', '')
        else:
            # Pass return path forward.
            self.returnPath = self.returnPathArg
        return super(LoginView, self).getResponse()

    def getMajorNavigationItem(self):
        return '/people/home/'
        if self.returnPath:
            # Try to keep navigation constant when redirecting to login.
            majorItems = [i['url'] for i in self.majorNavigation]
            majorItems.sort(reverse=True)
            majorItem = '/' + self.returnPath.lstrip('/')
            for item in majorItems:
                if majorItem.startswith(item):
                    majorItem = item
                    break
        else:
            majorItem = '/'
        return majorItem

    def getMinorNavigationItem(self):
        return '/login/'


class LogoutView(AuthenticateView):

    templatePath = 'logout'
    minorNavigationItem = '/logout/'

    def getResponse(self):
        if self.session:
            self.stopSession()
        return super(LogoutView, self).getResponse()


class AccountRecoverView(AuthenticateView):

    templatePath = 'recover'
    minorNavigationItem = '/recover/'

    def getResponse(self):
        self.personName = self.request.POST.get('name', '')
        self.emailAddress = self.request.POST.get('email', '')
        self.isRecoverError = None
        self.person = None
        if self.personName and self.personName in self.registry.people:
            self.person = self.registry.people[self.personName]
        elif self.emailAddress:
            emailAddressClass = self.registry.getDomainClass('EmailAddress')
            emailAddressRegister = emailAddressClass.createRegister()
            emailAddresses = emailAddressRegister.findDomainObjects(emailAddress=self.emailAddress)
            if len(emailAddresses) == 1:
                self.person = emailAddresses[0].person
                pass
        if self.person:
            try:
                cmd = EmailNewPassword(self.person)
                cmd.execute()
            except KforgeCommandError, inst:
                msg = "Password reset command failed for '%s': %s" % (self.person, inst)
                self.logger.error(msg)
                self.isRecoverError = True
        return super(AccountRecoverView, self).getResponse()

    def setContext(self):
        super(AccountRecoverView, self).setContext()
        self.context.update({
            'personName': self.personName,
            'emailAddress': self.emailAddress,
            'person': self.person,
            'isRecoverError': self.isRecoverError,
        })


def login(request, returnPath=''):
    return LoginView(request=request, returnPath=returnPath).getResponse()

def logout(request):
    return LogoutView(request=request).getResponse()

def recover(request):
    return AccountRecoverView(request=request).getResponse()
