import unittest
import kforge.soleInstance

def run(suiteName, verbosity=1):
    suite = __import__(suiteName,'','','*').suite()
    return unittest.TextTestRunner(verbosity=verbosity).run(suite)

