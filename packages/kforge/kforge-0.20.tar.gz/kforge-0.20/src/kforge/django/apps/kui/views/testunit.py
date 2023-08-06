import kforge.testunit

class TestCase(kforge.testunit.TestCase):
    "Base class for View TestCases."
    
    def buildRequest(self):
        return None

