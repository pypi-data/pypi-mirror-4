from dm.view.api import ApiView

class KForgeApiView(ApiView):

    def isAuthorised(self, **kwds):
        # Involve project in access control, so member roles are involved.
        kwds['project'] = self.getProject()
        return super(KForgeApiView, self).isAuthorised(**kwds)

    def getProject(self):
        # Breakdown the registry path, look for a project.
        path = self.getRequestRegistryPath()
        pathParts = path.strip('/').split('/')
        if len(pathParts) >= 2 and pathParts[0] == 'projects':
            projectPath = '/%s/%s' % (pathParts[0], pathParts[1])
            project = self.registry.dereference(projectPath).target
        else:
            project = None
        return project


def api(request):
    view = KForgeApiView(request=request)
    return view.getResponse()
