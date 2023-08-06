# todo: delete?

from dm.command import Command

class LicenseCommand(Command):
    "Abstract License command."
        
    def __init__(self, id):
        super(LicenseCommand, self).__init__()
        self.id = id
        self.license = None
        self.licenses = self.registry.licenses

class LicenseRead(LicenseCommand):
    "Command to read a registered license."

    def __init__(self, id):
        super(LicenseRead, self).__init__(id)

    def execute(self):
        "Make it so."
        super(LicenseRead, self).execute()
        id = self.id
        if self.licenses.has_key(id):
            self.license = self.licenses[id]
        else:
            self.raiseError("No license found with id '%s'." % id)

class LicenseList(LicenseCommand):
    "Command to list registered licenses."

    def __init__(self):
        super(LicenseList, self).__init__(None)

    def execute(self):
        "Make it so."
        super(LicenseList, self).execute()

