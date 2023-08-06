import kforge.django.settings.main
from dm.view.base import SessionView
import kforge.url

class KforgeView(SessionView):

    def __init__(self, **kwds):
        super(KforgeView, self).__init__(**kwds)
        self.project = None
        self._canReadProject = None

    def canReadProject(self):
        if self._canReadProject == None:
            if self.project:
                protectedObject = self.project
            else:
                protectedObject = self.getDomainClass('Project')
            self._canReadProject = self.canRead(protectedObject, project=self.getProject())
        return self._canReadProject

    def getProject(self):
        return None

    def setMajorNavigationItems(self):
        self.majorNavigation = []
        if self.session:
            self.majorNavigation.append({
                'title': '%s' % self.session.person.getLabelValue(),
                'url': '/people/%s/' % self.session.person.name
            })
        else:
            self.majorNavigation.append({'title': 'Account Login',      'url': '/login/'})
        if self.canReadProject(): 
            self.majorNavigation.append({'title': 'Projects',  'url': '/projects/'})
        if self.canReadPersons(): 
            self.majorNavigation.append({'title': 'People',    'url': '/people/'})
        if self.canUpdateSystem():
            self.majorNavigation.append({'title': 'Admin', 'url': '/admin/model/'})

    def setContext(self, **kwds):
        super(KforgeView, self).setContext(**kwds)
        url_scheme = kforge.url.UrlScheme()
        self.context.update({
            'kforge_media_url' : url_scheme.url_for('media'),
        })  

