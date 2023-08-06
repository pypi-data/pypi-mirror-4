from dm.dom.stateful import *

def getPlugins():
    return DomainRegistry().plugins

import kforge.regexps

projectNameRegex = '^(?!%s)%s$' % (
    kforge.regexps.reservedProjectName,
    kforge.regexps.projectName
)

class HideableObject(SimpleObject):

    isHidden = Boolean()
    readableBy = String(isSystem=True)

    def resetReadableBy(self, names):
        raise Exception, "Method not implemented on: %s" % type(self)

    def getReadableByNames(self):
        raise Exception, "Method not implemented on: %s" % type(self)


class Project(HideableObject, StandardObject):
    "Registered project."

    searchAttributeNames = ['name', 'title', 'description']

    name = String(isIndexed=True, isUnique=True, isImmutable=True, 
        regex=projectNameRegex, minLength=3, maxLength=256)
    title = String(regex='.*\S.*')
    description = Text()
    licenses = AggregatesMany('ProjectLicense', 'license')
    members = AggregatesMany('Member', 'person')
    services = AggregatesMany('Service', 'name')

    isUnique = False
    sortOnName = 'title'

    def getLabelValue(self):
        return self.title.strip() or self.name

    def resetReadableBy(self):
        members = [m for m in self.members]
        memberNames = [m.person.name for m in members]
        adminRole = self.registry.roles['Administrator']
        siteadmins = self.registry.people.findDomainObjects(role=adminRole)
        siteadminNames = [p.name for p in siteadmins]
        names = set(memberNames).union(set(siteadminNames))
        readableBy = ''
        if self.isHidden:
            readableBy = ':%s:' % ':'.join(names)
        if self.readableBy != readableBy:
            self.readableBy = readableBy
            self.saveSilently()
        for member in members:
            isChanged = False
            if member.readableBy != readableBy:
                member.readableBy = readableBy
                isChanged = True
            if member.isHidden != self.isHidden:
                member.isHidden = self.isHidden
                isChanged = True
            if isChanged:
                member.saveSilently()

    def getTracServices(self):
        return [s for s in self.services if s.plugin.name == 'trac']

