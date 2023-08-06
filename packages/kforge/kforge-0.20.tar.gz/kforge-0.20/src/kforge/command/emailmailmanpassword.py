from dm.command.emailbase import EmailCommand
from kforge.dictionarywords import *

class EmailMailmanPassword(EmailCommand):

    messageTemplate = """Greetings,

Mailing list admin password for %(listName)s is %(password)s

Regards,

The %(siteName)s Team
"""
        
    def __init__(self, password, project, listName):
        self.password = password
        self.project = project
        self.listName = listName
        super(EmailMailmanPassword, self).__init__()

    def getMessageToList(self):
        addresses = []
        adminRole = self.registry.roles['Administrator']
        for member in self.project.members:
            if member.role == adminRole:
                addresses.append(member.person.email)
        return addresses

    def getMessageSubject(self):
        return '%s: Mailing list admin password' % self.listName
    
    def getParams(self):
        return {
            'siteName': self.dictionary[SYSTEM_SERVICE_NAME].decode('utf-8'),
            'password': self.password,
            'listName': self.listName,
        }

