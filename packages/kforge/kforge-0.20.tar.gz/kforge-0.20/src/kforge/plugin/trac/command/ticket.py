from kforge.plugin.trac.command.base import TracModelCommand
from kforge.plugin.trac.command.db import TracDbCommand
from kforge.plugin.trac.exceptions import TracTicketNotFound


class TracTicketCols(object):

    cols  = ['id', 'priority', 'summary', 'type', 'owner', 'reporter', 'cc', 'status', 'description', 'changetime', 'keywords']


class TracTicketCommand(TracTicketCols, TracModelCommand):

    def createTicket(self, data):
        from trac.ticket.model import Ticket
        tkt = Ticket(self.getEnv())
        for k,v in data.items():
            tkt[k] = v
        tkt.insert()
        return tkt

    def readTicket(self, id):
        from trac.ticket.model import Ticket
        return Ticket(self.getEnv(), id)

    def updateTicket(self, id, data):
        tkt = self.readTicket(id)
        for k,v in data.items():
            tkt[k] = v
        tkt.save_changes(author='system', comment='changed by system')

    def deleteTicket(self, id):
        tkt = self.readTicket(id)
        tkt.delete()


class CreateTracTicket(TracTicketCommand):

    def __init__(self, tracProject, ticketData):
        super(CreateTracTicket, self).__init__(tracProject)
        self.ticketData = ticketData

    def execute(self):
        ticketData = {}
        for col in self.cols:
            if col != 'id' and col in self.ticketData:
                ticketData[col] = self.ticketData[col]
        ticket = self.createTicket(ticketData)
        return ticket.id


class ReadTracTicket(TracTicketCommand):

    def __init__(self, tracProject, ticketId):
        super(ReadTracTicket, self).__init__(tracProject)
        self.ticketId = ticketId

    def execute(self):
        if not self.ticketId:
            msg = "Couldn't find ticket for id: %s" % self.ticketId
            raise TracTicketNotFound, msg
        data = {}
        ResourceNotFound = self.getResourceNotFoundClass()
        try:
            ticket = self.readTicket(self.ticketId)
        except ResourceNotFound, inst:
            msg = "Couldn't find ticket for id: %s" % self.ticketId
            msg += ": %s" % str(inst)
            raise TracTicketNotFound, msg
        for col in self.cols:
            data[col] = ticket[col]
        return data


class UpdateTracTicket(TracTicketCommand):

    def __init__(self, tracProject, ticketId, ticketData):
        super(UpdateTracTicket, self).__init__(tracProject)
        self.ticketId = ticketId
        self.ticketData = ticketData

    def execute(self):
        ticketData = {}
        for col in self.cols:
            if col != 'id' and col in self.ticketData:
                ticketData[col] = self.ticketData[col]
        self.updateTicket(self.ticketId, ticketData)


class DeleteTracTicket(TracTicketCommand):

    def __init__(self, tracProject, ticketId):
        super(DeleteTracTicket, self).__init__(tracProject)
        self.ticketId = ticketId

    def execute(self):
        self.deleteTicket(self.ticketId)


class ListTracTickets(TracTicketCols, TracDbCommand):

    def execute(self):
        results = self.select("%s FROM ticket" % ",".join(self.cols))
        return self.getDataFromResults(results)
        
    def getDataFromResults(self, results):
        tickets = []
        for result in results:
            data = {}
            for (i, col) in enumerate(self.cols):
                data[col] = result[i]
            tickets.append(data)
        return tickets
        

class ListTracTicketIds(ListTracTickets):

    cols = ['id']

    def getDataFromResults(self, results):
        return [r[0] for r in results]


###################
# Comands that depend on the db commands.
###################

# Commands to create or update tickets.

class CreateOrUpdateTicket(object):

    def __init__(self, tracProject, tracTicketId):
        self.tracProject = tracProject
        self.tracTicketId = tracTicketId

    def execute(self):
        tracTicketData = ReadTracTicket(self.tracProject, self.tracTicketId).execute()
        if tracTicketData == None:
            return
        tracTicketData['ref'] = str(self.tracTicketId)
        if 'changetime' in tracTicketData:
            # Make value timezone unaware (otherwise get error "TypeError: 
            # can't compare offset-naive and offset-aware datetimes.")
            changetime = tracTicketData['changetime']
            changetime = changetime.replace(tzinfo=None)
            tracTicketData['changetime'] = changetime
        if 'id' in tracTicketData:
            del(tracTicketData['id'])
        tickets = self.tracProject.tickets.all.findDomainObjects(ref=str(self.tracTicketId))
        if len(tickets) == 0:
            # Create new ticket.
            if tracTicketData['status'] != 'closed':
                try:
                    self.tracProject.tickets.create(**tracTicketData)
                except Exception, inst:
                    msg = "Couldn't create ticket. Ticket ID: %s. Ticket data: %s. Exception: %s" % (self.tracTicketId, tracTicketData, inst) 
                    raise Exception, msg
        elif len(tickets) == 1:
            # Update existing ticket. 
            ticket = tickets[0]
            for (key, value) in tracTicketData.items():
                setattr(ticket, key, value)
            ticket.saveSilently()
            if ticket.status == 'closed' and ticket.isActive():
                # Delete closed ticket.
                ticket.delete()
            elif ticket.status != 'closed' and ticket.isDeleted():
                # Activate reopened ticket.
                ticket.undelete()
        else:
            msg = "Unexpected number of tickets (%s) for ticket id '%s'." % (len(tickets), self.tracTicketId)
            raise Exception, msg



