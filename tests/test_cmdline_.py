# Copyright 2020 Curtis Penner
import unittest
import sys
import cmdline


class TestOptionsDefaults(unittest.TestCase):
    def test_no_args(self):
        arg = cmdline.options()
        # Boolean
        self.assertFalse(arg['one_per_page'])
        self.assertEqual(arg['maxshrink'], 0.0)
        self.assertFalse(arg['break_all'])
        self.assertEqual(arg['bars_per_line'], 0)
        self.assertFalse(arg['select_composer'])
        self.assertFalse(arg['epsf'])
        self.assertFalse(arg['help_me'])
        self.assertFalse(arg['make_index'])
        self.assertFalse(arg['landscape'])
        self.assertFalse(arg['notab'])
        self.assertFalse(arg['noauthor'])
        self.assertFalse(arg['write_historical'])
        self.assertFalse(arg['pagenumbers'])
        # self.assertFalse(arg['do_outfile'])
        # self.assertTrue(arg['outf'])
        self.assertFalse(arg['select_rhythm'])
        self.assertFalse(arg['select_source'])
        self.assertFalse(arg['select_title'])
        self.assertFalse(arg['transposegchords'])
        self.assertFalse(arg['include_xrefs'])
        # Float
        self.assertEqual(arg['scale'], 0.70)
        self.assertEqual(arg['strictness'], 0.0)
        # Int
        self.assertEqual(arg['sel_arg'], 0)
        self.assertEqual(arg['tabsize'], 14)
        # String
        self.assertEqual(arg['dstaffsep'], '0.0cm')
        self.assertEqual(arg['leftmargin'], '0.0cm')
        self.assertEqual(arg['styf'], 'fonts.fmt')
        self.assertEqual(arg['glue'], 'fill')
        self.assertEqual(arg['frfont'], 'frFrancisque')
        self.assertEqual(arg['itfont'], 'itTimes')
        self.assertEqual(arg['defont'], 'deCourier')
        self.assertEqual(arg['transposition'], '')
        self.assertEqual(arg['voices'], '')
        self.assertEqual(arg['staffwidth'], '')
        self.assertEqual(arg['filename'], '')
        self.assertEqual(arg['filenames'], '')
        # Special
        self.assertIsNone(arg['nbars'])
        self.assertIsNone(arg['withxrefs'])
        # Count Check
        self.assertEqual(len(arg), 41)


class TestOptionsArguments(unittest.TestCase):
    def tearDown(self) -> None:
        # Reset the args after each test
        sys.argv = [sys.argv[0]]

    def test_one_per_line_0(self):
        sys.argv.append('+1')
        args = cmdline.options()
        self.assertFalse(args['one_per_page'])

    def test_one_per_line_1(self):
        sys.argv.append('-1')
        args = cmdline.options()
        self.assertTrue(args['one_per_page'])

    def test_maxshrink(self):
        sys.argv.append('-a')
        sys.argv.append('0.12')
        args = cmdline.options()
        self.assertEqual(args['maxshrink'], 0.12)

    def test_maxshrink_low(self):
        sys.argv.append('-a -0.12')
        args = cmdline.options()
        self.assertEqual(args['maxshrink'], 0.0)

    def test_maxshrink_high(self):
        sys.argv.append('-a')
        sys.argv.append('1.12')
        args = cmdline.options()
        self.assertEqual(args['maxshrink'], 1.0)

    def test_break_all_0(self):
        sys.argv.append('+b')
        args = cmdline.options()
        self.assertFalse(args['break_all'])

    def test_break_all_1(self):
        sys.argv.append('-b')
        args = cmdline.options()
        self.assertTrue(args['break_all'])

    def test_bars_per_line_0(self):
        sys.argv.append('+B')
        args = cmdline.options()
        self.assertEqual(args['bars_per_line'], 0)

    def test_bars_per_iine_1(self):
        sys.argv.append('-B 4')
        args = cmdline.options()
        self.assertEqual(args['bars_per_line'], 4)

    def test_select_composer(self):
        sys.argv.append('-C')
        args = cmdline.options()
        self.assertTrue(args['select_composer'])

    def test_continue_all_0(self):
        sys.argv.append('-c')
        args = cmdline.options()
        self.assertTrue(args['continue_all'])

    def test_continue_all_1(self):
        sys.argv.append('+c')
        args = cmdline.options()
        self.assertFalse(args['continue_all'])

    def test_dstaffsep(self):
        sys.argv.append('-d 2.3cm')
        args = cmdline.options()
        self.assertTrue(args['dstaffsep'], '2.3cm')

        sys.argv = [sys.argv[0]]
        sys.argv.append('-d hello')
        args = cmdline.options()
        self.assertTrue(args['dstaffsep'], 'hello')

    def test_sel_arg(self):
        sys.argv.append('-e 4')
        args = cmdline.options()
        self.assertFalse(args['sel_arg'], 4)


class TestExtFunctions(unittest.TestCase):
    pass
