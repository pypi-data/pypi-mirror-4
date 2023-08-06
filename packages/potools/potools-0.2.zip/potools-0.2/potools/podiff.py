# -*- coding: UTF-8 -*-
from mr.developer.common import which
from optparse import OptionParser
import logging
import os
import polib
import re
import subprocess
import tempfile
import urllib

log = logging.getLogger(__name__)


def parse_options():
    usage = """\n%prog [options] FILE1 FILE2\n%prog \
        "--vcs $vcstype $vcsurl [options] FILE"""
    parser = OptionParser(usage)
    parser.add_option("-v", "--verbose",
                      action="store_true", dest="verbose", default=False,
                      help="Verbose mode")
    parser.add_option("--vcs", nargs=2, dest="vcs",
                      help=u"Compare the file to one in a version "
                           u"control repository. Specify the version "
                           u"control type and its URL (e.g --vcs git "
                           u"git@github.com:syslabcom/potools.git).")

    (options, args) = parser.parse_args()
    if not options.vcs and len(args) != 2:
        parser.error(u"If you aren't using the --vcs option, then you'll "
                     u"need to specify exactly two files.")
    return (options, args)


class Podiff(object):
    """ Shows the difference between two po files. Only cares about msgid and
        msgstr, not about position in the file, comments etc.
    """
    def __init__(self, options={}, args=()):
        self.options = options
        self.args = args

    def run(self):
        if not self.options.vcs:
            self.diff(self.args[0], self.args[1])
        else:
            self.vcsdiff(self.args[0],
                         self.options.vcs[0],
                         self.options.vcs[1])

    def get_package_root(self, dir):
        while 'setup.py' not in os.listdir(dir):
            newdir = os.path.dirname(dir)
            if newdir == dir:
                log.critical("Couldn't find python package root.")
                return
            dir = newdir
        return dir

    def vcsdiff(self, pofile, vcstype, vcsurl):
        """ Internal helper function.

            Diffs a file with it's counterpart in a VCS repository, of
            type $vcstype at $vcsurl.
        """
        pofile = os.path.abspath(pofile)
        basepath = self.get_package_root(os.getcwd())

        proto, string = urllib.splittype(vcsurl)
        host, path = urllib.splithost(string)

        relpath = os.path.relpath(pofile, basepath)
        pofileurl = os.path.join(vcsurl, relpath)
        tmp, tmppath = tempfile.mkstemp(text=True)
        if vcstype == 'svn':
            urllib.urlretrieve(pofileurl, tmppath)
        elif vcstype == 'git':
            cmd = which('git')
            branchmatch = re.search('branch=(\S*)', vcsurl)
            if branchmatch:
                branch = branchmatch.group(1)
            else:
                branch = 'master'
            cmdline = '%s show %s:%s' % (cmd, branch, relpath)
            err, errtmppath = tempfile.mkstemp(text=True)
            out = subprocess.Popen(cmdline.split(' '),
                                   stdout=subprocess.PIPE,
                                   stderr=err,
                                   cwd=basepath).stdout.read()
            err = open(errtmppath).read()
            if err:
                log.critical(err)
                return
            outfile = open(tmppath, 'w')
            outfile.write(out)
            outfile.close()
        else:
            log.critical('Sorry, %s is not supported yet.')
            return
        log.debug("Comparing %s and %s:%s" % (pofile, branch, relpath))
        self.diff(tmppath, pofile)
        os.remove(tmppath)

    def _diff(self, filepath1, filepath2):
        """ Internal helper function
        """
        file1 = polib.pofile(filepath1)
        file2 = polib.pofile(filepath2)
        diff = []
        for removed_entry in filter(
                lambda e: not file2.find(e.msgid,
                                         include_obsolete_entries=True),
                file1):
            diff += [u'-msgid "%s"' % removed_entry.msgid]
            diff += [u'-msgstr "%s"\n' % removed_entry.msgstr]

        for entry_file2 in file2:
            entry_file1 = file1.find(entry_file2.msgid,
                                     include_obsolete_entries=True)
            if not entry_file1:
                diff += [u'+msgid "%s"' % entry_file2.msgid]
                diff += [u'+msgstr "%s"\n' % entry_file2.msgstr]
            else:
                changed = {}
                changed['comment'] = entry_file2.comment != entry_file1.comment
                changed['msgstr'] = entry_file2.msgstr != entry_file1.msgstr
                if not changed['comment'] and not changed['msgstr']:
                    continue

                if changed['comment']:
                    diff += [u'-#. "%s"' % line
                             for line in entry_file1.comment.split('\n')]
                    diff += [u'+#. "%s"' % line
                             for line in entry_file2.comment.split('\n')]
                else:
                    diff += [u'#. "%s"' % line
                             for line in entry_file2.comment.split('\n')]

                diff += [u'msgid "%s"' % line
                         for line in entry_file2.msgid.split('\n')]

                if changed['msgstr']:
                    diff += [u'-msgstr "%s"' % line
                             for line in entry_file1.msgstr.split('\n')]
                    diff += [u'+msgstr "%s"' % line
                             for line in entry_file2.msgstr.split('\n')]
                else:
                    diff += [u'msgstr "%s"' % line
                             for line in entry_file2.msgstr.split('\n')]
        return diff

    def diff(self, filepath1, filepath2):
        """ Diffs two po files. Only cares about msgid and msgstr, not about
            position in the file, comments etc.
        """
        po_path = u'Index: %s' % filepath2
        diff = ['\n'+po_path+'\n'+'='*len(po_path) +
                '\n--- repository\n+++ working copy\n']
        diff += self._diff(filepath1, filepath2)
        diff = "\n".join([o.encode('utf-8') for o in diff])
        print(diff)
        return diff


def main():
    options, args = parse_options()
    logging.basicConfig(
        level=options.verbose and logging.DEBUG or logging.INFO,
        format="%(levelname)s: %(message)s")
    podiff = Podiff(options, args)
    podiff.run()
