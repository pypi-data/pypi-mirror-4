import sys
import os
import polib
from ptools import utils


def poupdate():
    """%(program)s: For an existing po file ORIG and a second po file UPDATE that
        contains new translations for a subset of ORIG, the new translations are
        merged to ORIG.
        Msgids present in UPDATE that are not present in ORIG will be a ignored
        (warning) given

        usage:    %(program)s orig.po update.po
        orig.po   A po file that should be updated with new translations
        update.po The po file that contains new translations to go into orig.po
    """
    if len(sys.argv) < 3:
        utils.usage(sys.stderr, poupdate, "\nERROR: Not enough arguments")
    origfile = sys.argv[1]
    updatefile = sys.argv[2]

    if not os.path.isfile(origfile):
        utils.usage(sys.stderr, poupdate, "\nERROR: path to ORIG file is not valid")

    if not os.path.isfile(updatefile):
        utils.usage(sys.stderr, poupdate, "\nERROR: path to UPDATE file is not valid")

    orig = polib.pofile(origfile)
    update = polib.pofile(updatefile)

    for entry in update:
        msgid = entry.msgid
        if msgid.strip() == '':
            continue
        target = orig.find(msgid)
        if not target:
            print "WARNING! msgid '%s' not present in %s." % (msgid, origfile)
            continue
        target.msgstr = entry.msgstr

    orig.save()
    sys.exit('Ok')

