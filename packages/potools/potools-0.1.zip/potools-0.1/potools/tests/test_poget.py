from potools import poget
import os
import polib
import tempfile
import unittest
import shutil
import optparse

class TestPoGetNew(unittest.TestCase):
    """ """

    def setUp(self):
        self.pogetnew = poget.PoGetNew()
        self.pf = os.getcwd()+'/../../potools/tests/locales/test.po'
        # We create a temporary copy of the po file for testing
        tmp, self.tmppath = tempfile.mkstemp(text=True)
        shutil.copyfile(self.pf, self.tmppath)
        self.prep_instance()

    def tearDown(self):
        os.remove(self.tmppath)

    def prep_instance(self, values={}):
        options = {'prefill': False, 
                   'verbose': False, 
                   'untranslated': False, 
                   'ignore_translated': False, 
                   'dirty': False, 
                   'fuzzy': False 
                    }
        options.update(values)
        options = optparse.Values(options)
        options, args = poget.parse_options([self.pf, self.tmppath], options)
        self.pogetnew.options = options
        self.pogetnew.args = args 

    def test_no_changes(self):
        entries = self.pogetnew._get_new(self.pf, self.tmppath)
        self.assertEquals(len(entries), 0)

        self.prep_instance({
                        'untranslated': True, 
                        'ignore_translated': True, 
                        'dirty': True, 
                        'fuzzy': True 
                        })
        entries = self.pogetnew._get_new(self.pf, self.tmppath)
        self.assertEquals(len(entries), 0)

    def test_comment_edited(self):
        po = polib.pofile(self.tmppath)
        po[0].comment = po[0].comment+' edited'
        po.save()
        entries = self.pogetnew._get_new(self.pf, self.tmppath)
        self.assertEquals(len(entries), 0)

        self.prep_instance({
                        'dirty': True, 
                        })
        entries = self.pogetnew._get_new(self.pf, self.tmppath)
        self.assertEquals(len(entries), 1)
        self.assertEquals(entries[0].msgid, po[0].msgid)
        self.assertEquals(entries[0].comment, po[0].comment)

    def test_order_changed(self):
        po = polib.pofile(self.tmppath)
        po.reverse()
        po.save()
        entries = self.pogetnew._get_new(self.pf, self.tmppath)
        self.assertEquals(len(entries), 0)

    def test_msgstr_changed(self):
        po = polib.pofile(self.tmppath)
        po[0].msgstr = po[0].msgstr + ' edited'
        po.save()
        entries = self.pogetnew._get_new(self.pf, self.tmppath)
        self.assertEquals(len(entries), 0)

        self.prep_instance({
                        'untranslated': True, 
                        'ignore_translated': True, 
                        'dirty': True, 
                        'fuzzy': True 
                        })
        entries = self.pogetnew._get_new(self.pf, self.tmppath)
        self.assertEquals(len(entries), 0)

    def test_msgid_changed(self):
        """ Test that changest to an entry's msgstr are reflected
        """
        # Edit the first entry's msgid
        po = polib.pofile(self.tmppath)
        po[0].msgid = po[0].msgid + ' edited'
        po.save()
        entries = self.pogetnew._get_new(self.pf, self.tmppath)
        self.assertEquals(len(entries), 1)
        self.assertEquals(entries[0].msgid, po[0].msgid)

        # Edit the last entry's msgid
        po[-1].msgid = po[-1].msgid + ' edited'
        po.save()
        entries = self.pogetnew._get_new(self.pf, self.tmppath)
        self.assertEquals(len(entries), 2)
        self.assertEquals(entries[-1].msgid, po[-1].msgid)
