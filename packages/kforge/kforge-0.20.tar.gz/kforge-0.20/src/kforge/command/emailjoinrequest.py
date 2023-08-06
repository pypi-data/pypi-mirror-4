from dm.command.emailbase import EmailCommand
from kforge.dictionarywords import *

class EmailJoinCommand(EmailCommand):

    messageType = ''

    def __init__(self, project, person):
        super(EmailJoinCommand, self).__init__()
        self.project = project
        self.person = person

    def getParams(self):
        baseUrl = 'http://%s%s' % (self.dictionary[SITE_HOST], self.dictionary[URI_PREFIX])
        return {
            'siteName': self.dictionary[SYSTEM_SERVICE_NAME].decode('utf-8'),
            'projectLabel': self.project.getLabelValue(),
            'projectUrl': '%s/projects/%s/' % (baseUrl, self.project.name),
            'personUrl': '%s/people/%s/' % (baseUrl, self.person.name),
            'personLabel': self.person.getLabelValue(),
            'approveUrl': '%s/projects/%s/members/%s/approve/' % (baseUrl, self.project.name, self.person.name),
            'rejectUrl': '%s/projects/%s/members/%s/reject/' % (baseUrl, self.project.name, self.person.name),
        }

    def execute(self):
        super(EmailJoinCommand, self).execute()
        # Log the result.
        if self.isDispatchedOK:
            msg = "%s mail sent for project %s, person %s" % (self.messageType, self.project.name, self.person.name)
            self.logger.info(msg)
        else:
            msg = "%s mail could not be sent for project %s, person %s" % (self.messageType, self.project.name, self.person.name)
            self.logger.warn(msg)


class EmailJoinRequest(EmailJoinCommand):
       
    messageType = 'Join'     
    messageTemplate = """Greetings,

A request has been made to join one of your projects.

Project: %(projectLabel)s
%(projectUrl)s

Person: %(personLabel)s
%(personUrl)s

You may wish to log in and respond to this request.

Approve this request:
%(approveUrl)s

Reject this request:
%(rejectUrl)s

Regards,

The %(siteName)s Team
"""

    def getMessageToList(self):
        emails = []
        adminRole = self.registry.roles['Administrator']
        for member in self.project.members:
            if member.role == adminRole:
                emails.append(member.person.email)
        return emails

    def getMessageSubject(self):
        subject =  '%s membership request' % self.project.name
        return self.wrapMessageSubject(subject)


class EmailJoinApprove(EmailJoinCommand):
        
    messageType = 'Approve' 
    messageTemplate = """Greetings,

Congratulations, the following membership request has been approved by the project administrator:

Project: %(projectLabel)s
%(projectUrl)s

Person: %(personLabel)s
%(personUrl)s

Role: %(roleName)s

You should now be able to access the project when you log into your account.

Regards,

The %(siteName)s Team
"""

    def getParams(self):
        params = super(EmailJoinApprove, self).getParams()
        params['roleName'] = self.project.members[self.person].role.name
        return params

    def getMessageToList(self):
        if self.person is None:
            return []
        return [self.person.email]

    def getMessageSubject(self):
        subject =  '%s membership request approved' % self.project.name
        return self.wrapMessageSubject(subject)


class EmailJoinReject(EmailJoinCommand):
        
    messageType = 'Reject' 
    messageTemplate = """Greetings,

Sorry, the following membership request has been rejected by the project administrator:

Project: %(projectLabel)s
%(projectUrl)s

Person: %(personLabel)s
%(personUrl)s

Regards,

The %(siteName)s Team
"""

    def getMessageToList(self):
        if self.person is None:
            return []
        return [self.person.email]

    def getMessageSubject(self):
        subject =  '%s membership request rejected' % self.project.name
        return self.wrapMessageSubject(subject)

