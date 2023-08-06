import dm.application
import kforge.builder
from dm.ioc import RequiredFeature

class Application(dm.application.Application):
    "Provides single entry point for clients."

    builderClass = kforge.builder.ApplicationBuilder

    fileSystem = RequiredFeature('FileSystem')
    accessController = RequiredFeature('AccessController')

