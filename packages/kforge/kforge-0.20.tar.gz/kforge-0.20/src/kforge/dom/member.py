from dm.dom.stateful import *
from kforge.dictionarywords import MEMBER_ROLE_NAME

from kforge.dom.project import HideableObject

class Member(HideableObject, DatedStatefulObject):
    """
    Registers membership of a project by a person. 
    Associates a Person, a Project, and a Role.
    """

    project = HasA('Project', isImmutable=True, isUnique=True)
    person = HasA('Person', isImmutable=True, isUnique=True)
    role = HasA('Role', default=StatefulObject.dictionary[MEMBER_ROLE_NAME])

    isUnique = False

    ownerAttrNames = ['project', 'members']

    sortOnName = None

    def initialise(self, register=None):
        super(Member, self).initialise(register)
        if not self.role:
            roleName = self.dictionary[MEMBER_ROLE_NAME]
            self.role = self.registry.roles[roleName]
            self.isChanged = True

    def purge (self):
        super(Member, self).purge()
        # Todo: Refector to drop these references by reflection off the model (the are all 'HasA').
        self.project = None
        self.person = None
        self.role = None

    def getLabelValue(self):
        return "%s-%s" % (
            self.person.getLabelValue(),
            self.project.getLabelValue(),
        )   


