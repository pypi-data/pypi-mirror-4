import dm.builder
from kforge.ioc import *

class ApplicationBuilder(dm.builder.ApplicationBuilder):
    """
    Extends core builder by adding new application features, and by overriding
    core features with replacements for, or extensions of, core features.
    """

    #
    # Add features.
    
    def construct(self):
        super(ApplicationBuilder, self).construct()
        features.register('UrlScheme', self.findUrlScheme())

    def findUrlScheme(self):
        import kforge.url
        return kforge.url.UrlScheme()
 
    #
    # Replace features.

    def findSystemDictionary(self):
        import kforge.dictionary
        return kforge.dictionary.SystemDictionary()

    def findModelBuilder(self):
        import kforge.dom.builder
        return kforge.dom.builder.ModelBuilder()

    def findCommandSet(self):
        import kforge.command
        return kforge.command.__dict__

    def findFileSystem(self):
        import kforge.filesystem
        return kforge.filesystem.FileSystem()

    def findAccessController(self):
        import kforge.accesscontrol
        return kforge.accesscontrol.ProjectAccessController()

