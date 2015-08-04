from optparse import OptionParser
import os
import sys
import unittest

from util import ConfigLogging
from util import ProcessUtil
from util import TestConfig

LOGGER = ConfigLogging.config_root(__name__)

# Run an individual test case
def run_test(options):
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    suite.addTests(loader.discover(start_dir = os.path.join(os.path.dirname(__file__), "tests"),
                                   pattern= "" +  options.test + "*"))
    return  unittest.TextTestRunner().run(suite)

# Run the whole test suite
def run_suite(options):
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    suite.addTests(loader.discover(os.path.join(os.path.dirname(__file__),"tests"),
                                   pattern='*Test.py'))
    return  unittest.TextTestRunner().run(suite)

def main():
    # setup arguments
    parser = OptionParser()
    parser.add_option("-o", "--output", dest="logfile",
                      help="write log to FILE", default="/tmp/testlog.txt", metavar="FILE")
    parser.add_option("-t", "--test", dest="test", default=None)
    parser.add_option("-q", "--quiet",
                      action="store_false", dest="verbose", default=True,
                      help="don't print status messages to stdout")

    # Read command line options
    (options, args) = parser.parse_args()

    # Get default configuration
    config = TestConfig.MapsEditorConfig()

    LOGGER.info("Starting tests..")

    if options.test is None:
        result = run_suite(options)
    else:
        result = run_test(options)

    if result.wasSuccessful():
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == '__main__':
  sys.exit(main())