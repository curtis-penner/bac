# Copyright (c) 2019 Curtis Penner

import unittest
import sys

import cmdline


class TestCmdline(unittest.TestCase):
    def test_cmdline_defaults(self):
        args = cmdline.options()
        self.assertFalse(args.one_per_page)
        self.assertEqual(args.maxshrink, 0.0)
        self.assertFalse(args.break_all)
        self.assertEqual(args.bars_per_line, 0)
        self.assertFalse(args.select_composer)
        self.assertFalse(args.continue_all)
        self.assertEqual(args.dstaffsep, '0.0cm')
        self.assertEqual(args.styd, '')
        self.assertEqual(args.sel_arg, 0)
        self.assertFalse(args.epsf)
        self.assertEqual(args.filename, '')
        self.assertEqual(args.styf, 'fonts.fmt')
        self.assertEqual(args.gmode, 'fill')
        self.assertFalse(args.help_me)
        self.assertFalse(args.make_index)
        self.assertIsNone(args.nbars)
        self.assertFalse(args.landscape)
        self.assertEqual(args.left_margin, '0.0cm')
        self.assertFalse(args.noauthor)
        self.assertFalse(args.notab)
        self.assertEqual(args.frfont, 'frFrancisque')
        self.assertEqual(args.itfont, 'itTimes')
        self.assertEqual(args.defont, 'deCourier')
        self.assertFalse(args.write_historical)
        self.assertFalse(args.pagenumbers)
        self.assertEqual(args.outfile, 'out.ps')
        self.assertIsNone(args.pretty)
        self.assertEqual(args.paper_format, 'letter')
        self.assertFalse(args.select_rhythm)
        self.assertFalse(args.select_source)
        self.assertEqual(args.select_field0, 1)
        self.assertEqual(args.transpose, '')
        self.assertEqual(args.tabsize, 14)
        self.assertFalse(args.transposegchords)
        self.assertEqual(args.voices, '')
        self.assertEqual(args.staff_width, '')
        self.assertFalse(args.include_xrefs)
        self.assertEqual(args.strictness, 0.0)
        self.assertEqual(args.filenames, list())


class TestCmdlineUsed(unittest.TestCase):
    def setUp(self) -> None:
        sys.argv = [sys.argv[0]]

    def test_o(self):
        sys.argv.append('-o')
        sys.argv.append('oh.ps')
        args = cmdline.options()
        self.assertEqual(args.outfile, 'oh.ps')

    def test_f(self):
        sys.argv.append('-f')
        sys.argv.append('file0')
        args = cmdline.options()
        self.assertEqual('file0', args.filename)

    def test_fn(self):
        sys.argv.append('file1')
        sys.argv.append('file2')
        sys.argv.append('file3')
        args = cmdline.options()
        self.assertIsInstance(args.filenames, list)
        self.assertTrue('file2' in args.filenames[0])
        self.assertTrue('file0' not in args.filenames[0])
        args.filenames = args.filenames[0]
        print(args.filenames)
        args.filenames.append('file0')
        self.assertTrue('file0' in args.filenames)

    def test_b(self):
        sys.argv.append('-b')
        args = cmdline.options()
        self.assertTrue(args.break_all)
        sys.argv = [sys.argv[0]]
        sys.argv.append('+b')
        args = cmdline.options()
        self.assertFalse(args.break_all)



# def test_is_cmdline(self):
#     cmd = utils.cmdline.Process()
#     line = 'This'
#     self.assertFalse(cmd.is_cmdline(line))
#
#     line = '%This'
#     self.assertFalse(cmd.is_cmdline(line))
#
#     line = '%!This'
#     self.assertTrue(cmd.is_cmdline(line))
#
#     line = '  %!  '
#     self.assertTrue(cmd.is_cmdline(line))
#
# def test_parse_cmdline(self):
#     self.assertTrue(True)
