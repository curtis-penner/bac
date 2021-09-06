import unittest
import sys

import syms


class TestDef(unittest.TestCase):

    def test_def_misc(self):
        fp = sys.stdout
        s = syms.def_misc(fp)
        print(s)
        self.assertEqual('', '')
