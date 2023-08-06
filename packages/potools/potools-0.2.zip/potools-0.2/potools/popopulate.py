import logging
import sys
import polib
from optparse import OptionParser
from potools.utils import get_default
from potools.utils import append_entry

log = logging.getLogger(__name__)

def parse_options(self):
    usage = "%prog [options] FILE"
    parser = OptionParser(usage)
    parser.add_option("-v", "--verbose",
                        action="store_true", dest="verbose", default=False,
                        help="Verbose mode")
    (options, args) = parser.parse_args()
    return (options, args)


def PoPopulate():
    """ For every untranslated or fuzzy entry, copy its "Default" 
        string for its msgstr value. If no default value exists, copy its 
        msgid.
    """
    def __init__(self, options={}, args=()):
        self.options = options
        self.args = args

    def run(self):
        pofile = polib.pofile(self.args[1])
        outpo = polib.POFile()

        # Copy header and metadata
        outpo.header = pofile.header
        [outpo.metadata.update({key: val}) for (key, val) in pofile.metadata.items()]

        entries = pofile.untranslated_entries() + pofile.fuzzy_entries()
        for entry in entries:
            default = get_default(entry)
            outpo = append_entry(outpo, entry, default)

        print outpo
        log.debug("--------------------------------------------------------")
        log.debug("SOME STATS TO HELP WITH DOUBLE-CHECKING:")
        log.debug("Untranslated entries in old.po: %d" % len(pofile.untranslated_entries()))
        log.debug("Fuzzy entries in old.po: %d" % len(pofile.fuzzy_entries()))
        log.debug("Found %d entries that need to be updated" % len(outpo))
        log.debug("--------------------------------------------------------")
        sys.exit(0)


def main():
    options, args = parse_options()
    logging.basicConfig(
            level=options.verbose and logging.DEBUG or logging.INFO,
            format="%(levelname)s: %(message)s")
    popopulate = PoPopulate(options, args)
    popopulate.run()

