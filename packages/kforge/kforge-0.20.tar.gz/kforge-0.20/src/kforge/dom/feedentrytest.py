import unittest
from kforge.dom.testunit import TestCase
import kforge.dom.feedentry
from kforge.exceptions import *

def suite():
    suites = [
        unittest.makeSuite(TestFeedEntry),
    ]
    return unittest.TestSuite(suites)

class TestFeedEntry(TestCase):
    "TestCase for the FeedEntry class."
    
    def setUp(self):
        super(TestFeedEntry, self).setUp()
        self.feed = self.registry.feedentries

    def test_update(self):
        self.feed.readSources([
            'http://kforge.appropriatesoftware.net/kforge/trac/timeline?ticket=on&changeset=on&milestone=on&wiki=on&max=50&daysback=90&format=rss',
            'http://kforge.appropriatesoftware.net/domainmodel/trac/timeline?ticket=on&changeset=on&milestone=on&wiki=on&max=50&daysback=90&format=rss',
        ])

