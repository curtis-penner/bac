# Copyright (c) 2019. Curtis Penner

import unittest

from music.symbol import Gchord


class TestGchord(unittest.TestCase):
    def test_00(self):
        gch = Gchord()
        line = '"This is it", so go.'
        new_line = gch.parse_gchord(line)
        self.assertEqual(new_line, ', so go.')
        self.assertEqual(gch.text, 'This is it')
        del gch


