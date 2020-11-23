# Copyright (c) 2019 Curtis Penner

import unittest
import os

import ps.syms as syms


class TestSyms(unittest.TestCase):
    filename = 'test_syms.ps'

    def setUp(self) -> None:
        if os.path.exists(self.filename):
            os.remove(self.filename)

    def tearDown(self) -> None:
        if os.path.exists(self.filename):
            os.remove(self.filename)

    def test__add_cv(self):
        f1 = 0.5
        f2 = 0.5
        p =[[-10, -2], [0, 15], [1, -11], [10, 2], [0, -15],
            [-1, 11], [-10, -2]]
        with open(self.filename, 'w') as fp:
            syms._add_cv(fp, f1, f2, p, 1, 2)
        with open(self.filename) as fp:
            lines = fp.readlines()
        self.assertEqual("  5.00 8.50 5.50 -4.50 10.00 2.00 rcurveto",
            lines[0].rstrip())
        self.assertEqual('  -5.00 -8.50 -5.50 4.50 -10.00 -2.00 rcurveto',
            lines[1].rstrip())

    def test__add_sg(self):
        f1 = 0.5
        f2 = 0.5
        p = [[-15, 0], [-15, 23], [15, 23], [15, 0], [14.5, 0],
             [12, 18], [-12, 18], [-14.5, 0]]
        with open(self.filename, 'w') as fp:
            syms._add_sg(fp, f1, f2, p, 4, 1)
        with open(self.filename) as fp:
            lines = fp.readlines()
        self.assertEqual('  -0.25 0.00 rlineto', lines[0].rstrip())

    def test__add_mv(self):
        f1 = 0.5
        f2 = 0.5
        p =[[-10, -2], [0, 15], [1, -11], [10, 2], [0, -15], [-1, 11], [-10, -2]]
        with open(self.filename, 'w') as fp:
            syms._add_mv(fp, f1, f2, p, 0)
        with open(self.filename) as fp:
            lines = fp.readlines()
        self.assertEqual('  -5.00 -1.00 rmoveto', lines[0].rstrip())
