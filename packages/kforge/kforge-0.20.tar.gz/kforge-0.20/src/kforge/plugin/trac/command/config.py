from kforge.plugin.trac.command.base import TracEnvironmentCommand

class SetTracConfigOptions(TracEnvironmentCommand):

    def __init__(self, tracProject, settings):
        super(SetTracConfigOptions, self).__init__(tracProject)
        self.settings = settings

    def execute(self):
        tracConfig = self.getEnv().config
        for section, option, value in self.settings:
            if value != None:
                tracConfig.set(section, option, value)
            else:
                tracConfig.remove(section, option)
        tracConfig.save()

