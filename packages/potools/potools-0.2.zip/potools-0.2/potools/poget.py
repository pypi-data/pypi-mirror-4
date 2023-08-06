from optparse import OptionParser
from potools import utils
import logging
import polib
import sys

log = logging.getLogger(__name__)


def parse_options(args=None, values=None):
    usage = "%prog [options] FILE1 FILE2"
    parser = OptionParser(usage)
    parser.add_option("-v", "--verbose",
                      action="store_true", dest="verbose", default=False,
                      help="Verbose mode")
    parser.add_option("--untranslated", action="store_true",
                      dest="untranslated", default=False,
                      help=u"Include non-new but untranslated entries.")
    parser.add_option("--ignore-translated", action="store_true",
                      dest="ignore_translated", default=False,
                      help=u"Ignore new but translated entries.")
    parser.add_option("--prefill", action="store_true",
                      dest="prefill", default=False,
                      help=u"Set the msgstr of each returned entry equal "
                           u"to the default translation.")
    parser.add_option("--fuzzy", action="store_true", default=False,
                      help=u"Include non-new but fuzzy entries"),
    parser.add_option("--dirty", action="store_true", default=False,
                      help=u"Include non-new but dirty entries. These are "
                           u"entries whose default values have changed."),

    (options, args) = parser.parse_args(args, values)
    if len(args) != 2:
        parser.error(u"Invalid number of arguments.")
    return (options, args)


class PoGetNew(object):
    """ Compare two po files and return all new entries that need to be
        translated.

        Output is printed to stdout, in the format as a valid po file, so that
        it can be sent to translator.
    """

    def __init__(self, args=(), options={}):
        self.options = options
        self.args = args

    def run(self):
        """ """
        entries = self._get_new(self.args[0], self.args[1])
        outpo = self._generate_pofile(entries)
        print outpo
        log.debug('Found %d entries in %s that are not in %s' \
                  % (len(outpo), self.args[0], self.args[1]))
        sys.exit(0)

    def is_dirty(self, old_entry, new_entry):
        default_old = utils.get_default(old_entry)
        default_new = utils.get_default(new_entry)
        if default_old != default_new:
            return True
        return False

    def _get_new(self, filepath1, filepath2):
        """ Compare two .po or .pot files and find all the entries in the
            second file that are not in the first one.

            Optionally:
                - include fuzzy and dirty non-new entries.
                - ignore new but translated entries.
                - prefill msgstr of all entries with their default values
        """
        firstpo = polib.pofile(filepath1)
        secondpo = polib.pofile(filepath2)
        entries = []
        for new_entry in secondpo:
            if new_entry.obsolete:
                # Ignore outcommented entries
                continue
            old_entry = firstpo.find(new_entry.msgid)
            if not old_entry:
                # We have a new entry
                if self.options.ignore_translated and new_entry.translated():
                    continue
                entries.append(new_entry)
            elif self.options.untranslated and not new_entry.translated() or \
                    self.options.fuzzy and 'fuzzy' in new_entry.flags or \
                    self.options.dirty and self.is_dirty(old_entry, new_entry):
                entries.append(new_entry)
        return entries

    def _generate_pofile(self, entries):
        outpo = polib.POFile()
        secondpo = polib.pofile(self.args[1])
        # Copy header and metadata
        outpo.header = secondpo.header
        for (key, val) in secondpo.metadata.items():
            outpo.metadata.update({key: val})
        for e in entries:
            default_msgstr = self.options.prefill and utils.get_default(e) \
                or None
            outpo = utils.append_entry(outpo, e, default_msgstr)
        return outpo


def main():
    """ """
    options, args = parse_options()
    logging.basicConfig(
        level=options.verbose and logging.DEBUG or logging.INFO,
        format="%(levelname)s: %(message)s")
    pogetnew = PoGetNew(args, options)
    pogetnew.run()
