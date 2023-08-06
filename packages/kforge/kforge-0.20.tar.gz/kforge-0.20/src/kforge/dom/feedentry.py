from dm.dom.stateful import *
from rawdoglib import feedparser
import datetime
from kforge.dictionarywords import FEED_LENGTH, FEED_SUMMARY_LENGTH

class Feed(Register):

    def listAll(self):
        length = self.dictionary[FEED_LENGTH]
        return self.listMax(length)

    def listSummary(self):
        length = self.dictionary[FEED_SUMMARY_LENGTH]
        return self.listMax(length)

    def listMax(self, length):
        return list(self)[:int(length)]

    def truncate(self):
        length = self.dictionary[FEED_LENGTH]
        for entry in list(self)[int(length):]:
            entry.delete()
              
    def readSources(self, sources):
        for source in sources:
            self.readSource(source)

    def readSource(self, source):
        response = feedparser.parse(source)
        feedData = response['feed']
        entriesData = response['entries']
        entriesKwds = []
        for entryData in entriesData:
            uid = entryData['id']
            updated = datetime.datetime(
                entryData['updated_parsed'][0],
                entryData['updated_parsed'][1],
                entryData['updated_parsed'][2],
                entryData['updated_parsed'][3],
                entryData['updated_parsed'][4],
                entryData['updated_parsed'][5],
            )
            source = feedData['title']
            entryKwds = {
                'uid': entryData['id'],
                'title': entryData['title'],
                'updated': updated,
                'link': entryData['link'],
                'summary': entryData['summary'],
                'source': source,
            }
            entriesKwds.append(entryKwds)
        lastEntryUpdated = None
        for entryKwds in entriesKwds:
            existingEntries = self.findDomainObjects(**entryKwds)
            if existingEntries:
                domainObject = existingEntries.pop(0)
                for entry in existingEntries:
                    entry.delete()
            # Ignore most entries from new Trac services.
            elif entryKwds['updated'] != lastEntryUpdated:
                try:
                    self.create(**entryKwds)
                except KforgeDomError:
                    pass
            lastEntryUpdated = entryKwds['updated']


class FeedEntry(SimpleObject):

    isObjectIdSignificant = False  # To speed data migration.

    uid = String(isRequired=True)
    title = String(isRequired=True)
    updated = DateTime(isRequired=True)
    authors = String()
    content = String()
    link = String()
    summary = String()
    categories = String()
    contributors = String()
    published = String()
    source = String()
    rights = String()

    registerClass = Feed

    sortOnName = 'updated'
    sortAscending = False
    nextAscending = False

    def strfUpdated(self):
        return self.updated.strftime('%c')
