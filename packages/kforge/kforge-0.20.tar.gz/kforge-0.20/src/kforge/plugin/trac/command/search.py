from kforge.plugin.trac.command.base import TracEnvironmentCommand
from trac.loader import load_components
from trac.search.web_ui import SearchModule as TracSearchModule
from trac.web.main import RequestDispatcher
from trac.web.api import Request
from trac.web.api import RequestDone
from trac.perm import PermissionCache
from kforge.dictionarywords import *
from trac.resource import Resource
from StringIO import StringIO
from kforge.command import Command

class SearchTracProjects(Command):
    """Searches through a number of Trac projects and co-mingles the results by
    sorting them all by date."""

    def __init__(self, query, person):
        self.query = query
        self.person = person
    
    def execute(self):
        # Make list of trac project objects.
        tracProjects = []
        try:
            tracPlugin = self.registry.plugins['trac']
        except RegistryKeyError:
            raise Exception, "Trac plugin not enabled."
        for member in self.person.memberships:
            for service in member.project.services.findDomainObjects(plugin=tracPlugin):
                tracProject = service.getExtnObject()
                if tracProject:    
                    tracProjects.append(tracProject)
        # Get search results for each.
        self.results = []
        for tracProject in tracProjects:
            cmd = SearchTracProject(tracProject, self.query, self.person.name)
            cmd.execute()
            for result in cmd.results:
                result['serviceurl'] = "/%s/%s" % (tracProject.service.project.name, tracProject.service.name)
                result['projecttitle'] = tracProject.service.project.getLabelValue()
                self.results.append(result)
        # Sort results by date.
        self.results.sort(key=lambda x: x['lastmodified'], reverse=True)
        return self.results


class SearchTracProject(TracEnvironmentCommand):
    """Searches a Trac project resources with given query string. Results are
    sorted by date."""

    def __init__(self, tracProject, query, personName):
        super(SearchTracProject, self).__init__(tracProject)
        self.query = query
        self.personName = personName
        self.results = []
        self.getEnv()

    def execute(self):
        searchModule = TracSearchModule(self.getEnv())
        environ = {
            'SERVER_PORT': self.dictionary[HTTP_PORT],
            'wsgi.url_scheme': self.dictionary[URL_SCHEME],
            'wsgi.input': StringIO(),
            'SERVER_NAME': self.dictionary[SITE_HOST],
            'REMOTE_USER': self.personName,
            'QUERY_STRING': self.query,
            'REQUEST_METHOD': 'GET',
            'PATH_INFO': '/search',
        }
        def write(data):
            self.data = data
        def start_response(*args, **kwds):
            return write
        request = Request(environ, start_response)
        # Attempt 2: Call the dispatch request class.
        try:
            RequestDispatcher(self.getEnv()).dispatch(request)
        except RequestDone:
            pass
        #raise Exception, "Result: %s" % self.data
        # Attempt 1: Call the search module directly.
        #request.callbacks['perm'] = PermissionCache(self.env, username=self.personName, resource=Resource(None))
        #response = searchModule.process_request(request)
        #data = response[1]
        #raise Exception, type([i for i in data['results']][0]['date'])
        query = request.args.get('q')
        # Somehow that fails in Python 2.6.
        if query == None:
            d = dict([i.split('=') for i in self.query.split('&')])
            query = d.get('q', None)
        if query == None:
            raise Exception, "Couldn't get 'q' from string: %s" % self.query
        terms = searchModule._parse_query(request, query)
        filters = []
        available_filters = []
        for source in searchModule.search_sources:
            available_filters.extend(source.get_search_filters(request) or [])
        filters = searchModule._get_selected_filters(request, available_filters)

        if terms:
            tracResults = searchModule._do_search(request, terms, filters)
        else:
            tracResults = []
        self.results = []
        for tracResult in tracResults:
            result = {
                'resourceurl': tracResult[0],
                'starttext': tracResult[1],
                'lastmodified': tracResult[2],
                'authorname': tracResult[3],
                'matchtext': tracResult[4],
            }
            self.results.append(result)
        return self.results

