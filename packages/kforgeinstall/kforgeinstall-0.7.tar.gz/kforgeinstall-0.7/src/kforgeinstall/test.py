import unittest        
from optparse import OptionParser
import sys
import os
         
def suite():
    import kforgeinstall.clitest
    suites = [
        kforgeinstall.clitest.suite(),
    ]
    return unittest.TestSuite(suites)


class KForgeInstallTestCase(unittest.TestCase):

    isVerbose = False

    def join(self, *args):
        return os.path.join(*args)

    def assertPathExists(self, path):
        assert os.path.exists(path)

    def assertPathMissing(self, path):
        assert not os.path.exists(path)


class TestRunner(object):

    usage  = 'usage: %prog [options] [module_name]'

    def __init__(self):
        self.parseInput()
        self.runTestSuite()

    def parseInput(self):
        self.parser = OptionParser(self.usage)
        self.parser.add_option('-v', '--verbose', dest='isVerbose', action='store_true')
        (self.options, self.args) = self.parser.parse_args()
        self.testSuiteName = 'kforgeinstall.test'
        if len(self.args) == 1:
            self.testSuiteName = self.args[0]
        elif len(self.args) >= 1:
            self.parser.print_help()
            sys.exit(1)
        if self.options.isVerbose:
            KForgeInstallTestCase.isVerbose = True
            self.verbosity = 2
        else:
            self.verbosity = 1
        
    def runTestSuite(self):
        suite = __import__(self.testSuiteName,'','','*').suite()
        return unittest.TextTestRunner(verbosity=self.verbosity).run(suite)

