from kforge.ioc import *
import kforge.command
import kforge.exceptions
import kforge.accesscontrol

logger     = RequiredFeature('Logger')
dictionary = RequiredFeature('SystemDictionary')

def isAuthenticated(personName, password):
    """
    Authenticate a person with given name and password.
    """
    cmd = kforge.command.PersonAuthenticate(personName, password)
    try:
        cmd.execute()
        return cmd.person
    except kforge.exceptions.KforgeCommandError:
        pass
    return None

def isAccessAuthorised(person, reqUri, httpMethod):
    urlPath = normalizeUrlPath(reqUri)
    if len(urlPath.split( '/' )) <= 2:
        # Everything with fewer than two segments is ok (e.g. /projects).
        return True
    else:
        # Otherwise control access to a service.
        service = getService(urlPath)
        if not service:
            return False
        project = service.project
        plugin = service.plugin
        actionName = getActionName(httpMethod)
        controller = kforge.accesscontrol.ProjectAccessController()
        return controller.isAccessAuthorised(
            person=person,
            actionName=actionName,
            protectedObject=plugin,
            project=project,
        )

def normalizeUrlPath(reqUri):
    if reqUri[-1] == '/':
        reqUri = reqUri[:-1]
    return reqUri

def getService(urlPath):
    """
    Get service domain object which we are trying to access
    """
    url_scheme = kforge.url.UrlScheme()
    #todo: use kforge.url?
    projectName, serviceName = url_scheme.decodeServicePath(urlPath)
    read = kforge.command.ProjectRead(projectName)
    read.execute()
    project = read.project
    try:
        return project.services[serviceName]
    except kforge.exceptions.KforgeRegistryKeyError:
        return None

def getActionName(httpMethod):
    #registry = RequiredFeature('DomainRegistry')
    readList = ['GET', 'PROPFIND', 'OPTIONS', 'REPORT']
    if httpMethod in readList:
        return 'Read'
    else:
        return 'Update'

