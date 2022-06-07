# Copyright 2019 Curtis Penner

import unittest

from field import Key
import constants


class TestKey(unittest.TestCase):
    def test_set_key(self):
        k = Key()
        k('C')
        self.assertEqual(2, k.root, 2)
        self.assertEqual(0, k.sf, 0)
        self.assertEqual(k.A_NT, k.root_acc)
        k('A#')
        self.assertEqual(0, k.root)
        self.assertEqual(3, k.sf)
        self.assertEqual(k.A_SH, k.root_acc)
        k('Gdor')
        self.assertEqual(6, k.root)
        self.assertEqual(1, k.sf)
        self.assertEqual(k.A_SH, k.root_acc)

    def test_constructor(self):
        k = Key()
        self.assertEqual(k.sf, 0)
        self.assertEqual(k.key_type, constants.TREBLE)
        self.assertEqual(k.add_pitch, 0)
        self.assertEqual(k.root, 2)
        self.assertEqual(k.root_acc, constants.A_NT)

    def test_set_keysig(self):
        k = Key()
        value = 'A'
        self.assertEqual(k.set_keysig(value), None)

    def test_get_halftones(self):
        k = Key()
        value = '#'
        m = k
        k.get_halftones(value)
        self.assertEqual(m, 0)
        self.assertEqual(k.root_acc, constants.A_SH)

        value = '_'
        m = k.get_halftones(value)
        self.assertEqual(m, 0)
        self.assertEqual(k.root_acc, constants.A_FT)


if __name__ == '__main__':
    unittest.main()
