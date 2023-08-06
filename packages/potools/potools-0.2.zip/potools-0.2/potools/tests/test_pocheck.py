from potools import pocheck
import os
import unittest


class TestPoCheck(unittest.TestCase):

    def setUp(self):
        self.pocheck = pocheck.PoCheck()
        self.pofile = os.getcwd()+'/../../potools/tests/locales/test.po'
        self.potfile = os.getcwd()+'/../../potools/tests/locales/test.pot'

    def test_defaults(self):
        entries = self.pocheck._get_duplicate_defaults(self.pofile)
        self.assertEquals(len(entries), 0)

        entries = self.pocheck._get_duplicate_defaults(self.potfile)
        self.assertEquals(len(entries), 4)
        msgids = [e.msgid for e in entries]
        self.assertTrue('label_comment' in msgids)
        self.assertTrue('navigation_surveys' in msgids)
        self.assertTrue('title_updated' in msgids)
        self.assertTrue('expl_update' in msgids)
