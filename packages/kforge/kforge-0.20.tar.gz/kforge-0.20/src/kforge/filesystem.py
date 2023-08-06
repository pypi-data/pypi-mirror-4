from kforge.dictionarywords import PROJECTS_PATH
from dm.filesystem import FileSystem as BaseFileSystem
import os.path

class FileSystem(BaseFileSystem):
    """
    Directory layout:
    =================
    
    KFORGEHOME/
        etc/
        bin/
        lib/
            python/
        var/
            plugin_data
                ${plugin}/
                    
                e.g. /svn, /wiki, ...
            project_data/
                ${project}/
                    ${plugin}/
                        ${service_id}
    """

    def __init__(self):
        super(FileSystem, self).__init__()
        path = self.dictionary[PROJECTS_PATH]
        self.projectDataPath = os.path.normpath(path)

    def getTrashPath(self):
        """
        Returns filesystem path for trash folder.
        """
        return os.path.join(self.projectDataPath, '__trash__')
 
    def getLocksPath(self):
        """
        Returns filesystem path for locks folder.
        """
        return os.path.join(self.projectDataPath, '__locks__')
 
    def getProjectPath(self, project):
        """
        Returns filesystem path for a project.
        """
        return os.path.join(self.projectDataPath, project.name)

    def getServicesPath(self, project, plugin):
        """
        Return filesystem path for all project services of a plugin.
        """
        if not project:
            raise Exception("No project passed.")
        if not plugin:
            raise Exception("No plugin passed.")
        return os.path.join(self.getProjectPath(project), plugin.name)
   
    # Deprecated in favour of getServicesPath(). 
    def getProjectPluginPath(self, project, plugin):
        return self.getServicesPath(project, plugin)
    
    def getServicePath(self, service): 
        """
        Return filesystem path for a service.
        """
        servicesPath = self.getProjectPluginPath(service.project, service.plugin)
        return os.path.join(servicesPath, str(service.id))

    def assertTrashFolder(self):
        path = self.getTrashPath()
        self.assertFolder(path, "trash")
    
    def assertProjectFolder(self, project):
        path = self.getProjectPath(project)
        self.assertFolder(path, "'%s' project" % project.name)
    
    def assertServicesFolder(self, project, plugin):
        path = self.getServicesPath(project, plugin)
        self.assertFolder(path, "'%s' project '%s' services" % (project.name, plugin.name))
    
    def assertServiceFolder(self, service):
        path = self.getServicePath(service)
        self.assertFolder(path, "'%s' project '%s' service" % (service.project.name, service.name))

    # Rename coerceFolder()?
    def assertFolder(self, folderPath, folderPurpose):
        if not os.path.exists(folderPath):
            msg = "%s: Making %s folder: %s" % (
                self.__class__.__name__, folderPurpose, folderPath
            )
            self.logger.info(msg)
            try:
                os.makedirs(folderPath)
            except Exception, inst:
                msg = "%s: Couldn't make %s folder: %s: %s" % (
                    self.__class__.__name__, folderPurpose, 
                    folderPath, str(inst)
                )
                self.logger.error(msg)
                raise Exception(msg)
   
    # Rename assertExists()?
    def assertPath(self, path, purpose='node'):
        if not os.path.exists(path):
            message = "%s doesn't exist on path %s" % (purpose, path)
            self.logger.error(message)
            raise Exception(message)

