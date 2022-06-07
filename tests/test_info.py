
import field
import pytest


class TestXRef:
    def test_is_info_field(self):
        s = 'X: 1'
        assert field.is_info_field(s)
        s = 'X:'
        assert field.is_info_field(s)
        s = "X 1"
        assert field.is_info_field(s)
        s = "|: A"
        assert field.is_info_field(s)

#     def test_00(self):
#         self.assertEqual(self.field.X.xref_str, '1')
#         self.assertEqual(self.field.X.xref, 1)
#         self.assertTrue(self.field.X.do_tune)
#
#     def test_01(self):
#         s = 'X: 1a'
#         self.assertTrue(field.is_field_line(s))
#         self.assertEqual(self.field.X.xref, 0)
#         self.assertIsNone(self.field.X.xref_str)
#         self.assertFalse(self.field.X.do_tune)
#
#     def test_02(self):
#         s = 'X: jh'
#         self.assertTrue(field.is_field_line(s))
#         self.assertEqual(self.field.X.xref, 0)
#         self.assertIsNone(self.field.X.xref_str)
#         self.assertFalse(self.field.X.do_tune)
#
#     def test_03(self):
#         s = 'X: 1.0'
#         self.assertTrue(field.is_field_line(s))
#         self.assertEqual(self.field.X.xref, 0)
#         self.assertIsNone(self.field.X.xref_str)
#         self.assertFalse(self.field.X.do_tune)
#
#     def test_04(self):
#         s = 'X: 0'
#         self.assertTrue(field.is_field_line(s))
#         self.assertEqual(self.field.X.xref, 0)
#         self.assertIsNone(self.field.X.xref_str)
#         self.assertFalse(self.field.X.do_tune)
#
#     def test_05(self):
#         s = 'X: -2'
#         self.assertTrue(field.is_field_line(s))
#         self.assertEqual(self.field.X.xref, 0)
#         self.assertIsNone(self.field.X.xref_str)
#         self.assertFalse(self.field.X.do_tune)
#
#     def test_06(self):
#         s = 'X:14'
#         self.assertTrue(field.is_field_line(s))
#         self.field.process(s)
#         self.assertEqual(self.field.X.xref_str, '14')
#         self.assertEqual(self.field.X.xref, 14)
#         self.assertTrue(self.field.X.do_tune)
#
#     def test_07(self):
#         s = 'X:1234567890'
#         self.assertTrue(field.is_field_line(s))
#         self.field.process(s)
#         self.assertEqual(self.field.X.xref_str, '1234567890')
#         self.assertEqual(self.field.X.xref, 1234567890)
#         self.assertTrue(self.field.X.do_tune)
#
#
# class TestSingleField(unittest.TestCase):
#     field = None
#
#     @classmethod
#     def setUpClass(cls):
#         cls.field = field.Info()
#
#     @classmethod
#     def tearDownClass(cls):
#         del cls.field
#
#     def test_00(self):
#         area = field.SingleField()
#         lines = ['X: 1', 'A: England']
#         self.assertTrue(field.is_field_line(lines[0]))
#         self.assertTrue(field.is_field_line(lines[1]))
#         area('England')
#         self.assertEqual('England', area.field)
#
#     def test_01(self):
#         book = field.SingleField()
#         book('Russia')
#         self.assertEqual('Russia', book.field)
#         book('France')
#         self.assertEqual('France', book.field)
#
#
# class TestTitle(unittest.TestCase):
#     title = None
#     field = None
#
#     def setUp(self):
#         self.field = field.Info()
#
#     def tearDown(self):
#         del self.field
#
#     def test_00(self):
#         self.assertEqual(0, len(self.title.titles))
#
#     def test_01(self):
#         s = 'X:1'
#         self.assertTrue(field.is_field_line(s))
#         s = 'T: title first'
#         self.assertTrue(field.is_field_line(s))
#
#
# class TestMeter(unittest.TestCase):
#     m = None
#     field = None
#
#     def setUp(self):
#         self.m = field.Meter()
#
#     def tearDown(self):
#         del self.m
#
#     def test_00(self):
#         self.m('6/8')
#         self.assertEqual(self.m.meter1, 6)
#         self.assertEqual(self.m.meter2, 8)
#         self.assertEqual(self.m.meter_str, '6/8')
#
#     def test_01(self):
#         self.m('C')
#         self.assertEqual(self.m.meter1, 4)
#         self.assertEqual(self.m.meter2, 4)
#         self.assertEqual(self.m.meter_str, 'C')
#
#
# class TestVoice(unittest.TestCase):
#     v = None
#
#     def setUp(self):
#         self.v = field.Voice()
#
#     def tearDown(self):
#         del self.v
#
#     def test_00(self):
#         self.assertTrue(True)
