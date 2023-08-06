"""
Gets URLs for Services, and other DomainObjects.
"""

import os.path
import kforge.ioc
import kforge.exceptions

import routes
from kforge.dictionarywords import SITE_HOST
from kforge.dictionarywords import HTTP_PORT
from kforge.dictionarywords import URI_PREFIX

class UrlScheme(object):
    """The URL layout 'scheme'.
    
    Wrap up routes functions so that we can use them nicely.

    The Interface
    =============

    A scheme must provide the following mount points (with associated
    arguments):

        * media
        * system_admin
        * people
        * projects
        * projects_admin
        * projects_service

    """

    def __init__(self):
        self.dictionary = kforge.ioc.RequiredFeature('SystemDictionary')
        self.fqdn = self.dictionary[SITE_HOST]
        if self.fqdn.endswith('/'):
            self.fqdn= self.host[:-1]
        self.port = self.dictionary[HTTP_PORT]
        self.host = 'http://' + self.fqdn
        if self.port != '80':
            self.host += ':' + self.port
        self.uriPrefix = self.dictionary[URI_PREFIX]

        # set up the mapper
        self.mapper = routes.Mapper()
        # Two new args that are available in Routes >= 1.9
        # Here for clarity (not necessary since unchanged from defaults)
         # Boolean used to indicate whether or not Routes should minimize URL's
         # and the generated URL's, or require every part where it appears in
         # the path. Defaults to True
        self.mapper.minimization = True
        #  Whether or not Named Routes result in the default options for the
        #  route being used *or* if they actually force url generation to use
        #  the route. Defaults to False.
        self.mapper.hardcode_names = False
        self._configure_mapper()


    # Todo: Rename 'edit' to 'update', to be consistent with the model.

    def _configure_mapper(self):
        self.mapper.connect('home', '')
        self.mapper.connect('api', 'api', controller='api')
        self.mapper.connect('about', 'about', controller='about')
        self.mapper.connect('feed', 'feed', controller='feed')
        self.mapper.connect('media', 'media*offset', controller='media',
                offset='')
        self.mapper.connect('logout', 'logout', controller='account',
                action='logout')
        self.mapper.connect('login', 'login', controller='account',
                action='login')
        self.mapper.connect('recover', 'recover', controller='account',
                action='recover')
        self.mapper.connect('access_denied', 'accessDenied',
                controller='accessDenied')
        self.mapper.connect('people', 'people/:action/:id',
                controller='people', action='index',
                requirements={'action': 'index|create|search|find|list|home'}
                )
        self.mapper.connect('people', 'people/:id/:action',
                controller='people', action='read',
                requirements={'action': 'edit|delete|read|tickets'}
                )
        self.mapper.connect('people.admin',
                'people/:person/:subcontroller/:action',
                controller='people.admin', id=None, 
                requirements={'subcontroller': 'sshKeys',
                    'action': 'create'}
                )
        self.mapper.connect('people.admin',
                'people/:person/:subcontroller/:id/:action',
                controller='people.admin', action='read',
                requirements={'subcontroller': 'sshKeys',
                    'action': 'edit|delete|read'}
                )
        self.mapper.connect('projects', 'projects/:action/:id',
                controller='projects', action='index',
                requirements={'action': 'index|create|search|find|list|home'}
                )
        self.mapper.connect('projects', 'projects/:id/:action',
                controller='projects', action='read',
                requirements={'action': 'edit|delete|read|join'}
                )
        self.mapper.connect('projects.admin',
                'projects/:project/:subcontroller/:action',
                controller='projects.admin', id=None, 
                requirements={'subcontroller': 'services|members',
                    'action': 'create'}
                )
        self.mapper.connect('projects.admin',
                'projects/:project/:subcontroller/:id/:action',
                controller='projects.admin', action='read',
                requirements={'subcontroller': 'services|members',
                    'action': 'edit|delete|read|reject|approve'}
                )
        # do not really need the controller here since this map is only used in
        # url generation but need it for routes
        self.mapper.connect('projects.service', ':project/:service',
                controller='projects.service', service=None)
        # this is not fully complete as we don't properly deal with subitems.
        # would like to have several maps and recurse but routes does not
        # support multiple mappers very nicely (if only url_for had a a config
        # argument ....)
        self.mapper.connect('admin', 'admin/:model/:offset',
                controller='admin', model='model', action=None, offset=None
                )

    def url_for(self, *args, **kwargs):
        # have to set up request_config as url_for uses it ...
        # have to set it here as it must be set on each request
        # o/w get exceptions talking about thread local issues
        config = routes.request_config()
        config.mapper = self.mapper
        url = routes.url_for(*args, **kwargs)
        url = self.uriPrefix + url
        return url

    def url_for_qualified(self, *args, **kwargs):
        url = self.url_for(*args, **kwargs)
        url = self.host + url
        return url

    def getServicePath(self, service):
        return self.url_for('projects.service',
            project=service.project.name,
            service=service.name
        )

    def getServiceUrl(self, service):
        return self.url_for_qualified('projects.service',
            project=service.project.name,
            service=service.name
        )

    def media_path(self, offset=''):
        raise Exception, "media_path() has been deprecated in favour of dictionary[MEDIA_PREFIX]"
        return self.url_for('media', offset=offset)

    def decodeServicePath(self, offset):
        # do *not* use mapper.match as may have nonstandard stuff
        # (e.g. from svn)
        # TODO: move back to using mapper
        # (this is more robust to future changes in layout of urls ...)
        # one way to do this: since problem is only caused by svn and its !svn
        # url part could deal with this by auto-replacing 'bad' characters (as
        # this will not affect service or project part)
        # 
        # out = self.mapper.match(offset)
        # if out is None: # no match ...
        #     msg = 'UrlScheme.decodeServicePath: failed to decode %s' % offset
        #     raise Exception(msg)
        # project = out['project']
        # service = out['service']
        if self.uriPrefix:
            if not offset.startswith(self.uriPrefix):
                msg = 'No match as %s does not begin with %s' % (offset,
                        self.uriPrefix)
                raise Exception(msg)
            offset = offset[len(self.uriPrefix):]
        parts = offset.split('?')[0].split('/')
        # leading slash will be an item
        if len(parts) < 3:
            msg = '%s is not long enough to be a service path' % offset
            raise Exception(msg)
        project = parts[1]
        service = parts[2]
        # try to convert to standard strings ...
        # domainmodel does not use unicode by default but routes does
        # this leads to problems when later looking up projects
        try:
            project = str(project)
        except:
            pass
        try:
            service = str(service)
        except:
            pass
        return project, service
    
    def getFqdn(self):
        return self.fqdn
    
    def get_host(self):
        return self.host

