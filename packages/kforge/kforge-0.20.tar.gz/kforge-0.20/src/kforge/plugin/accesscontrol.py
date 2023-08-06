"""
KForge AccessControl plugin.

"""

import kforge.plugin.base
import os
from dm.strategy import FindInstanceProtectionObject
from dm.strategy import CreateProtectionObject
from dm.dictionarywords import DB_MIGRATION_IN_PROGRESS

class Plugin(kforge.plugin.base.NonServicePlugin):
    "AccessControl plugin."
    
    def __init__(self, domainObject):
        super(Plugin, self).__init__(domainObject)
        name = 'accesscontrol'

    def onPersonCreate(self, person):
        if self.dictionary[DB_MIGRATION_IN_PROGRESS]:
            return
        if person.name == 'visitor':
            return
        protectionObject = CreateProtectionObject(person).create()
        for permission in protectionObject.permissions:
            if not permission in person.grants:
                person.grants.create(permission)
    
    def onPersonPurge(self, person):
        if self.dictionary[DB_MIGRATION_IN_PROGRESS]:
            return
        protectionObject = FindInstanceProtectionObject(person).find()
        protectionObject.delete()

    def onMemberCreate(self, member):
        if self.dictionary[DB_MIGRATION_IN_PROGRESS]:
            return
        if member.person.name == 'visitor':
            return
        protectionObject = CreateProtectionObject(member).create()
        # Grant permission for member.person to delete the member object.
        for permission in protectionObject.permissions:
            if permission.action.name == 'Delete':
                if not permission in member.person.grants:
                    member.person.grants.create(permission)
        # Reset member.project 'readableBy' attribute.
        member.project.resetReadableBy()
    
    def onMemberAfterDelete(self, member):
        # Reset member.project 'readableBy' attribute.
        member.project.resetReadableBy()

    def onProjectUpdate(self, project):
        # Reset member.project 'readableBy' attribute.
        project.resetReadableBy()

    def onMemberPurge(self, member):
        if self.dictionary[DB_MIGRATION_IN_PROGRESS]:
            return
        protectionObject = FindInstanceProtectionObject(member).find()
        protectionObject.delete()

    def onEmailAddressCreate(self, emailAddress):
        if self.dictionary[DB_MIGRATION_IN_PROGRESS]:
            return
        person = emailAddress.person
        # Todo: Test that admins can read.
        protectionObject = CreateProtectionObject(emailAddress).create()
        if person.name == 'visitor':
            return
        for permission in protectionObject.permissions:
            if permission.action.name in ['Read', 'Delete']:
                if not permission in person.grants:
                    person.grants.create(permission)
    
