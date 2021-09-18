# Copyright 2019 Curtis Penner

import unittest

import tab


class TestTab(unittest.TestCase):
    tab = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.tab = tab.Tabformat()

    @classmethod
    def tearDownClass(cls) -> None:
        del cls.tab

    def test_constructor(self):
        self.assertEqual(self.tab.addflags, 2)
        self.assertEqual(self.tab.rhstyle, tab.RHSIMPLE)
        self.assertEqual(self.tab.allflags, 0)
        self.assertEqual(self.tab.firstflag, 0)
        self.assertEqual(self.tab.ledgeabove, 0)
        self.assertEqual(self.tab.flagspace, 0.0)
        self.assertEqual(self.tab.gchordspace, 10)
        self.assertEqual(self.tab.brummer, tab.BRUMMER_ABC)
        self.assertEqual(self.tab.germansepline, 1)
        self.assertEqual(self.tab.size, 14)
        self.assertEqual(self.tab.scale, 1.0)
        self.assertEqual(self.tab.frfont, "frFrancisque")
        self.assertEqual(self.tab.itfont, "itTimes")
        self.assertEqual(self.tab.defont, "deCourier")

    # def test_read_tab_format(self):
    #     line = 'tabfontsize 12'
    #     self.tab.read_tab_format(line)
    #     self.assertEqual(self.tab.size, 12)
    #     line = 'tabfontsize 10.5'
    #     self.tab.read_tab_format(line)
    #     self.assertEqual(self.tab.size, 10.5)
