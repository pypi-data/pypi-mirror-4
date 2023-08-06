from optparse import OptionParser
import logging
import polib
import re
import sys

log = logging.getLogger(__name__)


def parse_options(args=None, values=None):
    usage = "%prog [options] FILE"
    parser = OptionParser(usage)
    parser.add_option("-v", "--verbose",
                      action="store_true", dest="verbose", default=False,
                      help="Verbose mode")
    parser.add_option("--defaults", action="store_true",
                      dest="defaults", default=False,
                      help=u"Check for duplicate default entries.")

    (options, args) = parser.parse_args(args, values)
    if len(args) != 1:
        parser.error(u"Invalid number of arguments.")
    return (options, args)


class PoCheck(object):
    """ Check a po file for various smells.
    """

    def __init__(self, args=(), options={}):
        self.options = options
        self.args = args

    def run(self):
        """ """
        out = '\n'
        if self.options.defaults:
            entries = self.check_duplicate_defaults(self.args[0])
            if entries:
                msg = "Duplicate defaults found for the following msgids:\n"
                out += msg
                out += "-"*(len(msg)-1)+'\n'
                for entry in entries:
                    out += '%s\n' % entry.msgid
        print out
        sys.exit(0)

    def _get_duplicate_defaults(self, filename):
        patt = re.compile("""Default:.?["\' ](.*?)(["\']$|$)""", re.S)
        po = polib.pofile(filename)
        counter = 0
        entries = []
        for entry in po:
            counter += 1
            match = patt.match(entry.comment)
            if match:
                if "Default:" in match.group(1).replace('\n', ' '):
                    entries.append(entry)
        return entries


def main():
    """ """
    options, args = parse_options()
    logging.basicConfig(
        level=options.verbose and logging.DEBUG or logging.INFO,
        format="%(levelname)s: %(message)s")
    PoCheck(args, options).run()
