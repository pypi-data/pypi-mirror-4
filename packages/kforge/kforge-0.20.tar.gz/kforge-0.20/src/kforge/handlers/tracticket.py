from kforge.handlers.base import GetServiceFromUri
from kforge.plugin.trac.command.ticket import CreateOrUpdateTicket
import re

class TracTicketFromHeaders(object):

    def __init__(self, headers):
        self.headers = headers

    def execute(self):
        # Look for Location header.
        url = None
        for header in self.headers:
            if header[0] == 'Location':
                url = header[1]
                break
        if url == None:
            return
        url = url.strip('/')
        # Todo: This needs to cut out the uriPrefix.
        parts = url.split('://')[1].split('/')[1:]

        # Get service object and ticketId (uses parts).
        ticketPath = '/' + '/'.join(parts)
        service = GetServiceFromUri(ticketPath).execute()
        if not service or service.plugin.name != 'trac':
            return
        tracProject = service.getExtnObject()
        if not tracProject:
            return
        if len(parts) <= 2:
            return
        if parts[-2] != 'ticket':
            return
        ticketRef = parts[-1].split('#')[0]
        if not re.match('^\d+$', ticketRef):
            return
        ticketId = int(ticketRef)
        CreateOrUpdateTicket(tracProject, ticketId).execute()

