from dm.dom.stateful import *

class Ticket(DatedStatefulObject):

    isUnique = False

    #sortOnName = 'lastModified'
    sortOnName = 'changetime'
    sortAscending = False

    service = HasA('Service') # Service supports tickets.
    ref = String(isRequired=False)
    priority = String(isRequired=False)
    status = String(isRequired=False, default='new')
    summary = String(isRequired=False)
    type = String(isRequired=False, default='defect')
    owner = String(isRequired=False)
    reporter = String(isRequired=False)
    cc = String(isRequired=False)
    description = String(isRequired=False)
    keywords = String(isRequired=False)
    comments = String(isRequired=False)
    changetime = DateTime(isRequired=False)

    ownerNames = ['service', 'tickets']

    searchAttributeNames = ['owner', 'priority', 'reporter', 'summary', 'status', 'type', 'description', 'comments', 'keywords']

