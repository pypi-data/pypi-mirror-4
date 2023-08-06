from dm.view.base import *
from kforge.django.apps.kui.views.base import KforgeView
from kforge.django.apps.kui.views.kui import HomeView
from kforge.django.apps.kui.views import manipulator
import kforge.command
from kforge.exceptions import KforgeCommandError
import random

class PersonView(AbstractClassView, KforgeView):

    domainClassName = 'Person'
    majorNavigationItem = '/people/'
    minorNavigationItem = '/people/'

    def __init__(self, **kwds):
        super(PersonView, self).__init__(**kwds)
        self.person = None

    def isSshPluginEnabled(self):
        if not hasattr(self, '_isSshPluginEnabled'):
            self._isSshPluginEnabled = 'ssh' in self.registry.plugins
        return self._isSshPluginEnabled


class PersonClassView(PersonView):

    def setMinorNavigationItems(self):
        self.minorNavigation = []
        self.minorNavigation.append({'title': 'Index', 'url': '/people/'})
        self.minorNavigation.append({'title': 'Search', 'url': '/people/search/'})

           
class PersonListView(AbstractListView, PersonClassView):

    templatePath = 'person/list'

    def canAccess(self):
        return self.canReadPerson()


class PersonSearchView(AbstractSearchView, PersonClassView):

    templatePath = 'person/search'
    minorNavigationItem = '/people/search/'
    
    def canAccess(self):
        return self.canReadPerson()


class PersonCreateView(HomeView, AbstractCreateView, PersonClassView):

    templatePath = 'person/create'
    minorNavigationItem = '/people/create/'

    def getManipulatorClass(self):
        return manipulator.PersonCreateManipulator

    def canAccess(self):
        return self.canCreatePerson()
        
    def setContext(self):
        super(PersonCreateView, self).setContext()
        if self.dictionary[self.dictionary.words.CAPTCHA_IS_ENABLED]:
            captchaHash = self.captcha.name
            captchaUrl = self.makeCaptchaUrl(captchaHash)
            self.context.update({
                'isCaptchaEnabled'  : True,
                'captchaHash'       : captchaHash,
                'captchaUrl'        : captchaUrl,
            })
        else:
            self.context.update({
                'isCaptchaEnabled'  : False,
            })

    def makePostManipulateLocation(self):
        return '/login/'


# todo: returnPath support
# todo: captcha support


#    def makeForm(self):
#        if self.dictionary['captcha.enable']:
#            if self.requestParams.get('captchahash', False):
#                hash = self.requestParams['captchahash']
#                try:
#                    self.captcha = self.registry.captchas[hash]
#                except:
#                    self.makeCaptcha()
#                    self.requestParams['captchahash'] = self.captcha.name
#                    self.requestParams['captcha'] = ''
#            else:
#                self.makeCaptcha()
#                self.requestParams['captchahash'] = self.captcha.name
#                self.requestParams['captcha'] = ''
#                
#        self.form = manipulator.FormWrapper(
#            self.manipulator, self.requestParams, self.formErrors
#        )
#
#    # todo: delete old and deleted captchas, and their image files - cron job?
#
#    def makeCaptcha(self):
#        word = self.makeCaptchaWord()
#        hash = self.makeCaptchaHash(word)
#        try:
#            self.captcha = self.registry.captchas.create(hash, word=word)
#        except:
#            hash = self.makeCaptchaHash(word)
#            self.captcha = self.registry.captchas.create(hash, word=word)
#        
#        fontPath = self.dictionary['captcha.font_path']
#        if not fontPath:  # todo: instead, check file exists
#            raise Exception("No 'captcha.font_path' in system dictionary.")
#        fontSize = int(self.dictionary['captcha.font_size'])
#        path = self.makeCaptchaPath(hash)
#        import kforge.utils.captcha
#        kforge.utils.captcha.gen_captcha(word, fontPath, fontSize, path)
#
#    def makeCaptchaWord(self):
#        wordlength = 5
#        word = ''.join(random.sample('ABCDEFGHIJKLMNOPQRSTUVWXYZ', wordlength))
#        return word
#
#    def makeCaptchaHash(self, word):
#        return self.makeCheckString(word)
#
#    def makeCaptchaPath(self, captchaHash):
#        mediaRoot = self.dictionary['www.media_root']
#        captchaRoot = mediaRoot + '/images/captchas'
#        captchaPath = captchaRoot + '/%s.png' % captchaHash
#        return captchaPath
#
#    def makeCaptchaUrl(self, captchaHash):
#        mediaHost = self.dictionary['www.media_host']
#        mediaPort = self.dictionary['www.media_port']
#        captchaUrl = 'http://%s:%s/images/captchas/%s.png' % (
#            mediaHost,
#            mediaPort,
#            captchaHash,
#        )
#        return captchaUrl
#
#    def createPerson(self):
#        personName = self.requestParams.get('name', '')
#        command = kforge.command.PersonCreate(personName)
#        try:
#            command.execute()
#        except:
#            # todo: log error
#            self.person = None
#            return None
#        else:
#            command.person.fullname = self.requestParams.get('fullname', '')
#            command.person.email = self.requestParams.get('email', '')
#            command.person.setPassword(self.requestParams.get('password', ''))
#            command.person.save()
#            self.person = command.person
#        return self.person


class PersonInstanceView(PersonView):

    def setMinorNavigationItems(self):
        isSessionPerson = self.isSessionPerson()
        person = self.getPerson()
        self.minorNavigation = []
        if not self.canUpdatePerson():
            self.minorNavigation.append({
                'title': 'Profile' if isSessionPerson else person.fullname,
                'url': '/people/%s/' % person.name
            })
        if self.canUpdatePerson():
            self.minorNavigation.append({
                'title': 'Settings',
                'url': '/people/%s/edit/' % person.name
            })
            if 'trac' in self.registry.plugins:
                self.minorNavigation.append({
                    'title': 'Tickets', 
                    'url': '/people/%s/tickets/' % person.name
                })
                self.minorNavigation.append({
                    'title': 'Tracs', 
                    'url': '/people/%s/tracsearch/' % person.name
                })
            if self.isSshPluginEnabled():
                self.minorNavigation.append({
                    'title': 'SSH', 
                    'url': '/people/%s/sshKeys/create/' % person.name
                })
            self.minorNavigation.append({
                'title': 'API', 
                'url': '/people/%s/apikey/' % person.name
            })

    def setContext(self):
        super(PersonInstanceView, self).setContext()
        isSessionPerson = self.isSessionPerson()
        person = self.getPerson()
        accessedBy = self.session.person.name if self.session else ''
        kwds = {'__accessedBy__': accessedBy}
        memberships = person.memberships.findDomainObjects(**kwds)
        self.context.update({
            'person': person,
            'isSessionPerson': isSessionPerson,
            'memberships': memberships,
        })


    def getPerson(self):
        if self.person == None:
            self.person = self.getDomainObject()
        return self.person

    def isSessionPerson(self):
        return self.session and self.session.person == self.getPerson()

    def canUpdatePerson(self):
        self.getPerson()
        return super(PersonInstanceView, self).canUpdatePerson()

    def getMajorNavigationItem(self):
        if self.isSessionPerson():
            return '/people/%s/' % self.getPerson().name
        else:
            return '/people/'

    def getMinorNavigationItem(self):
        return '/people/%s/' % self.getPerson().name


class PersonReadView(AbstractReadView, PersonInstanceView):

    templatePath = 'person/read'

    def getDomainObject(self):
        if self.path == '/people/home/' and self.session:
            self.domainObject = self.session.person
            self.person = self.domainObject
        else:
            super(PersonReadView, self).getDomainObject()
        return self.domainObject

    def getMajorNavigationItem(self):
        if self.isSessionPerson():
            return '/people/%s/' % self.getPerson().name
        else:
            return '/people/'

    def getMinorNavigationItem(self):
        return '/people/%s/' % self.getPerson().name

    def canAccess(self):
        return self.getPerson() and self.canReadPerson()


class PersonUpdateView(AbstractUpdateView, PersonReadView):

    templatePath = 'person/update'

    def getManipulatorClass(self):
        return manipulator.PersonUpdateManipulator

    def canAccess(self):
        return self.getPerson() and self.canUpdatePerson()

    def makePostManipulateLocation(self):
        return '/people/%s/' % self.getPerson().name

    def getMinorNavigationItem(self):
        return '/people/%s/edit/' % self.getPerson().name


class PersonDeleteView(AbstractDeleteView, PersonInstanceView):

    templatePath = 'person/delete'
    
    def canAccess(self):
        if not self.getPerson():
            return False
        return self.canDeletePerson()

    def manipulateDomainObject(self):
        super(PersonDeleteView, self).manipulateDomainObject()
        if self.isSessionPerson():
            self.stopSession()

    def makePostManipulateLocation(self):
        return '/people/'


class PersonApiKeyView(PersonReadView):

    templatePath = 'person/apikey'

    def getMinorNavigationItem(self):
        return '/people/%s/apikey/' % self.getPerson().name

    def canAccess(self):
        if not self.getPerson():
            return False
        return self.canUpdatePerson()

    def setContext(self):
        super(PersonApiKeyView, self).setContext()
        apiKeyString = self.getPerson().getApiKey().key
        apiKeyHeader = self.dictionary[API_KEY_HEADER_NAME]
        self.context.update({
            'apiKeyString': apiKeyString,
            'apiKeyHeader': apiKeyHeader
        })


class TicketView(PersonReadView):

    templatePath = 'person/tickets'

    def canAccess(self):
        if not 'trac' in self.registry.plugins:
            return False
        if not self.getPerson():
            return False
        return self.canUpdatePerson()

    def getMajorNavigationItem(self):
        if self.isSessionPerson():
            return '/people/%s/' % self.getPerson().name
        else:
            return '/people/'

    def getMinorNavigationItem(self):
        return '/people/%s/tickets/' % self.getPerson().name

    def setContext(self):
        super(TicketView, self).setContext()
        person = self.getPerson()
        userQuery = ''
        if self.request.POST and 'userQuery' in self.request.POST:
            userQuery = self.request.POST['userQuery']
        q = userQuery or person.name
        owned = self.registry.tickets.search(q, owner=person.name)
        reported = self.registry.tickets.search(q, reporter=person.name)
        reported_not_owned = [i for i in reported if i not in owned]
        tickets = owned + reported_not_owned
        self.context.update({
            'owned': owned,
            'reported': reported,
            'reported_not_owned': reported_not_owned,
            'tickets': tickets,
            'userQuery': userQuery,
            'lenTickets': len(tickets),
        })

class TracSearchView(PersonReadView):

    # Todo: Write tests for this view.

    templatePath = 'person/tracsearch'

    def canAccess(self):
        if not 'trac' in self.registry.plugins:
            return False
        if not self.getPerson():
            return False
        return self.canUpdatePerson()

    def getMajorNavigationItem(self):
        if self.isSessionPerson():
            return '/people/%s/' % self.getPerson().name
        else:
            return '/people/'

    def getMinorNavigationItem(self):
        return '/people/%s/tracsearch/' % self.getPerson().name

    def setContext(self):
        super(TracSearchView, self).setContext()
        query = self.request.GET.get('query', '')
        if query and 'trac' in self.registry.plugins:
            # Build the Trac query string.
            tracQuery = "q=%s" % query
            tracQuery += "&noquickjump=1"
            filters = ['wiki', 'ticket', 'changeset', 'milestone']
            values = {}
            for f in filters:
                if f in self.request.GET:
                    values[f] = self.request.GET.get(f)
            # NB If no filter is enabled, Trac assumes all are enabled.
            for f in filters:
                if f in values:
                    tracQuery += "&%s=%s" % (f, values[f])

            # Set any submitted filters in the context...
            if len(values):
                for f,v in values.items():
                    self.context[f] = v
            # ...or enable all options if none selected (Trac behaviour).
            else:
                for f in filters:
                    self.context[f] = 'on'

            # Check if we have cached results for this query.
            cachedResults = None
            if hasattr(self.session, '_lastTracSearchQuery'):
                if self.session._lastTracSearchQuery == tracQuery:
                    cachedResults = self.session._lastTracSearchResults
            if cachedResults != None:
                results = cachedResults
            else:
                # Get search results from Trac projects.
                from kforge.plugin.trac.command.search import SearchTracProjects
                results = SearchTracProjects(tracQuery, self.getPerson()).execute()
                self.session._lastTracSearchQuery = tracQuery
                self.session._lastTracSearchResults = results

            lenresults = len(results)
            # Paginate the results if necessary.
            resultsperpage = 10
            if lenresults > resultsperpage:
                # Decide page number.
                page = self.request.GET.get('page', 1)
                try:
                    page = int(page)
                except:
                    page = 1
                if page < 1:
                    page = 1
                if (page - 1) * resultsperpage > lenresults:
                    page = 1 + (lenresults / resultsperpage)
                # Slice results.
                indexfrom = (page - 1)*resultsperpage 
                indexto = page*resultsperpage
                results = results[indexfrom:indexto]
                # Set pagination info in context.
                self.context.update({
                    'page': page,
                    'indexfrom': indexfrom + 1,
                    'indexto': min(indexto, lenresults),
                    'resultsperpage': resultsperpage,
                })
                # Set previous and next if appropriate.
                if page > 1:
                    self.context.update({
                        'previouspage': page - 1 ,
                    })
                if page * resultsperpage < lenresults:
                    self.context.update({
                        'nextpage': page + 1 ,
                    })
            # Set results and query in context.
            self.context.update({
                'results': results,
                'lenresults': lenresults,
                'query': query,
            })
        else:
            # Initialise form data.
            self.context.update({
                'results': [],
                'lenresults': 0,
                'query': '',
                'wiki': 'on',
                'ticket': 'on',
                'changeset': 'on',
                'milestone': 'on',
            })


def list(request):
    view = PersonListView(request=request)
    return view.getResponse()

def search(request, startsWith=''):
    view = PersonSearchView(request=request, startsWith=startsWith)
    return view.getResponse()

def create(request, returnPath=''):   
    view = PersonCreateView(request=request)
    return view.getResponse()

def read(request, personName=''):
    view = PersonReadView(request=request, domainObjectKey=personName)
    return view.getResponse()

def update(request, personName):
    view = PersonUpdateView(request=request, domainObjectKey=personName)
    return view.getResponse()

def delete(request, personName):
    view = PersonDeleteView(request=request, domainObjectKey=personName)
    return view.getResponse()

def apikey(request, personName):
    view = PersonApiKeyView(request=request, domainObjectKey=personName)
    return view.getResponse()

def tickets(request, personName, startsWith=''):
    view = TicketView(request=request, domainObjectKey=personName, startsWith=startsWith)
    return view.getResponse()

def tracsearch(request, personName, query=''):
    view = TracSearchView(request=request, domainObjectKey=personName, query=query)
    return view.getResponse()
 

