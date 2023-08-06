import dm.testunit
import kforge.builder
import kforge.soleInstance
from kforge.dictionarywords import SYSTEM_MODE
assert kforge.soleInstance.application.dictionary[SYSTEM_MODE] == 'development', "Can't run tests unless system mode is 'development'."

class TestCase(dm.testunit.TestCase):
    pass

class ApplicationTestSuite(dm.testunit.ApplicationTestSuite):
    appBuilderClass = kforge.builder.ApplicationBuilder

