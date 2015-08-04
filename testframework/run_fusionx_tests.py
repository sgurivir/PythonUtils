from optparse import OptionParser
import os
import sys

from util import ConfigLogging
from util import ProcessUtil
from util import TestConfig

LOGGER = ConfigLogging.config_root(__name__)

def main():
    # setup arguments
    parser = OptionParser()
    parser.add_option("-f", "--file", dest="filename",
                      help="write report to FILE", metavar="FILE")
    parser.add_option("-q", "--quiet",
                      action="store_false", dest="verbose", default=True,
                      help="don't print status messages to stdout")

    # Read command line options
    (options, args) = parser.parse_args()

    # Get default configuration
    config  = TestConfig.MapsEditorConfig()

    LOGGER.info("Starting tests..")

if __name__ == '__main__':
  sys.exit(main())