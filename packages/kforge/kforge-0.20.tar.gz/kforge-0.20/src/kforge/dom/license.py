from dm.dom.stateful import *

class License(NamedObject):
    "Registered Open Knowledge license."

    isConstant = True
    registerKeyName = 'id'

    def getLabelValue(self):
        return self.name


class ProjectLicense(SimpleObject):
    "Registered usage of a License by a Project."

    project = HasA('Project')
    license = HasA('License')

    isImplicitAssociation = True

    def getLabelValue(self):
        return "%s-%s" % (
            self.project.getLabelValue(),
            self.license.getLabelValue(),
        )
    
