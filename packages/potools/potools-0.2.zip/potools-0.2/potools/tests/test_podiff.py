from potools import podiff
import os
import polib
import tempfile
import unittest
import shutil


class TestPodiff(unittest.TestCase):
    """ """

    def setUp(self):
        self.podiff = podiff.Podiff()
        self.pf = os.getcwd()+'/../../potools/tests/locales/test.po'
        # We create a temporary copy of the po file for testing
        tmp, self.tmppath = tempfile.mkstemp(text=True)
        shutil.copyfile(self.pf, self.tmppath)

    def tearDown(self):
        os.remove(self.tmppath)

    def test_no_changes(self):
        diff = self.podiff._diff(self.pf, self.tmppath)
        self.assertEquals(len(diff), 0)

    def test_comment_edited(self):
        """ If the only change is in the comments, the diff should be
            empty.

            XXX: Is this really wanted? The default value is shown in
            comment.
        """
        po = polib.pofile(self.tmppath)
        po[0].comment = po[0].comment+' edited'
        po.save()
        diff = self.podiff._diff(self.pf, self.tmppath)
        self.assertEquals(len(diff), 4)
        self.assertEquals(diff[0].strip(), u'-#. "Default: Foo"')
        self.assertEquals(diff[1].strip(), u'+#. "Default: Foo edited"')
        self.assertEquals(diff[2].strip(), u'msgid "label_foo"')
        self.assertEquals(diff[3].strip(), u'msgstr "Foo"')

    def test_order_changed(self):
        """ If the only change is the order of the entries, the diff should be
            empty.
        """
        po = polib.pofile(self.tmppath)
        po.reverse()
        po.save()
        diff = self.podiff._diff(self.pf, self.tmppath)
        self.assertEquals(len(diff), 0)

    def test_msgstr_changed(self):
        """ Test that changest to an entry's msgstr are reflected
        """
        # Edit the first entry's msgstr
        po = polib.pofile(self.tmppath)
        po[0].msgstr = po[0].msgstr + ' edited'
        po.save()
        diff = self.podiff._diff(self.pf, self.tmppath)
        self.assertEquals(len(diff), 4)
        self.assertEquals(diff[0].strip(), u'#. "Default: Foo"')
        self.assertEquals(diff[1].strip(), u'msgid "label_foo"')
        self.assertEquals(diff[2].strip(), u'-msgstr "Foo"')
        self.assertEquals(diff[3].strip(), u'+msgstr "Foo edited"')

        # Edit the last entry's msgstr
        po[-1].msgstr = po[-1].msgstr + ' edited'
        po.save()
        diff = self.podiff._diff(self.pf, self.tmppath)
        self.assertEquals(len(diff), 8)
        self.assertEquals(diff[4].strip(), u'#. "Default: Bar"')
        self.assertEquals(diff[5].strip(), u'msgid "Hello World"')
        self.assertEquals(diff[6].strip(), u'-msgstr "Hello World"')
        self.assertEquals(diff[7].strip(), u'+msgstr "Hello World edited"')

    def test_msgid_changed(self):
        """ Test that changest to an entry's msgstr are reflected
        """
        # Edit the first entry's msgid
        po = polib.pofile(self.tmppath)
        po[0].msgid = po[0].msgid + ' edited'
        po.save()
        diff = self.podiff._diff(self.pf, self.tmppath)
        self.assertEquals(len(diff), 4)
        self.assertEquals(diff[0].strip(), u'-msgid "label_foo"')
        self.assertEquals(diff[1].strip(), u'-msgstr "Foo"')
        self.assertEquals(diff[2].strip(), u'+msgid "label_foo edited"')
        self.assertEquals(diff[3].strip(), u'+msgstr "Foo"')

        # Edit the last entry's msgid
        po[-1].msgid = po[-1].msgid + ' edited'
        po.save()
        diff = self.podiff._diff(self.pf, self.tmppath)
        self.assertEquals(len(diff), 8)
        self.assertEquals(diff[0].strip(), u'-msgid "label_foo"')
        self.assertEquals(diff[1].strip(), u'-msgstr "Foo"')
        self.assertEquals(diff[2].strip(), u'-msgid "Hello World"')
        self.assertEquals(diff[3].strip(), u'-msgstr "Hello World"')
        self.assertEquals(diff[4].strip(), u'+msgid "label_foo edited"')
        self.assertEquals(diff[5].strip(), u'+msgstr "Foo"')
        self.assertEquals(diff[6].strip(), u'+msgid "Hello World edited"')
        self.assertEquals(diff[7].strip(), u'+msgstr "Hello World"')

