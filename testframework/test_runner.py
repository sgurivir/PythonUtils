import logging
from optparse import OptionParser
import util.logger
import util.ProcessUtil

parser = OptionParser()
parser.add_option("-f", "--file", dest="filename",
                  help="write report to FILE", metavar="FILE")
parser.add_option("-q", "--quiet",
                  action="store_false", dest="verbose", default=True,
                  help="don't print status messages to stdout")

(options, args) = parser.parse_args()

util.logger.prepare_logging("/tmp/log.txt")
logging.warn("Sridhar")

util.ProcessUtil.kill_process(222222)