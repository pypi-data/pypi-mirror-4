from kforge.django.apps.kui.views.base import KforgeView
from kforge.dictionarywords import SYSTEM_SERVICE_NAME
from kforge.dictionarywords import FEED_LENGTH
from kforge.dictionarywords import FEED_SUMMARY_LENGTH
import kforge.command
import kforge.url
from dm.webkit import HttpResponse

class HomeView(KforgeView):

    majorNavigationItem = '/'

    def setMinorNavigationItems(self):
        self.minorNavigation = [
            {'title': 'Welcome', 'url': '/'},
        ]
        self.minorNavigation.append(
            {'title': 'About',   'url': '/about/'}
        )
        if self.session:
            self.minorNavigation.append(
                {'title': 'Log out',   'url': '/logout/'}
            )
        else:
            if self.canCreatePerson():
                self.minorNavigation.append(
                    {'title': 'Sign up',      'url': '/people/create/'},
                )

    def canAccess(self):
        return self.canReadSystem()


class WelcomeView(HomeView):

    templatePath = 'welcome'
    minorNavigationItem = '/'

    def setContext(self, **kwds):
        super(WelcomeView, self).setContext(**kwds)
        if self.session:
            viewerName = self.session.person.name
        else:
            viewerName = ''
        projectCount = len(self.registry.projects.findDomainObjects(__accessedBy__=viewerName))
        personCount = len(self.registry.people.findDomainObjects(__accessedBy__=viewerName))

        self.context.update({
            'projectCount' : projectCount,
            'personCount'  : personCount,
            'feedUrl' : kforge.url.UrlScheme().url_for('feed') + '/',
            'feedEntries' : self.getFeedSummary()
        })

    # Todo: Limit by time? Add parameters.
    def getFeedSummary(self):
        feedSummaryLength = int(self.dictionary[FEED_SUMMARY_LENGTH])
        return self.registry.feedentries.listMax(feedSummaryLength)


class AboutView(HomeView):

    templatePath = 'about'
    minorNavigationItem = '/about/'


class FeedView(KforgeView):

    templatePath = 'feed'

    def getResponse(self):
        self.content = self.getFeedContent()
        self.response = HttpResponse(self.content)
        #self.response.headers['Content-Type'] = 'text/html'
        return self.response

    def getFeedContent(self):
        from django.utils.feedgenerator import Atom1Feed
        from kforge.url import UrlScheme
        atomFeed = Atom1Feed(
            title='%s Recent Changes' % self.dictionary[SYSTEM_SERVICE_NAME],
            link=UrlScheme().url_for('home'),
            description='Entries are generated from project feeds.',
        )
        feedLength = int(self.dictionary[FEED_LENGTH])
        for entry in self.registry.feedentries.listMax(feedLength):
            atomFeed.add_item(
                title=entry.title,
                link=entry.link,
                description=entry.summary,
                unique_id=entry.uid,
            )
        return atomFeed.writeString('utf-8')


class PageNotFoundView(WelcomeView):

    templatePath = 'pageNotFound'

    def getResponse(self):
        return self.getNotFoundResponse()


class AccessControlView(HomeView):

    templatePath = 'accessDenied'
    minorNavigationItem = ''

    def __init__(self, deniedPath='', **kwds):
        super(AccessControlView, self).__init__(**kwds)
        if self.request.GET:
            params = self.request.GET.copy()
            self.deniedPath = params.get('returnPath', '') # Todo: This supports this mod_handlers, but name needs to be fixed.
        else:
            self.deniedPath = deniedPath
            if self.deniedPath.startswith('/'):
                self.deniedPath.lstrip('/')
            self.deniedPath = '/' + self.deniedPath

    def canAccess(self):
        return True
        #return self.canReadSystem()
        
    def setContext(self, **kwds):
        super(AccessControlView, self).setContext(**kwds)
        self.context.update({
            'deniedPath'  : self.deniedPath,
        })


def welcome(request):
    view = WelcomeView(request=request)
    return view.getResponse()

def about(request):
    view = AboutView(request=request)
    return view.getResponse()

def feed(request):
    view = FeedView(request=request)
    return view.getResponse()

def pageNotFound(request):
    view = PageNotFoundView(request=request)
    return view.getResponse()

def accessDenied(request, deniedPath):
    view = AccessControlView(request=request, deniedPath=deniedPath)
    return view.getResponse()


