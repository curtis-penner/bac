# Copyright (c) 2019 Curtis Penner

import unittest
import sys

import utils.cmdline


class TestCmdline(unittest.TestCase):
    def test_cmdline_defaults(self):
        args = utils.cmdline.options()
        self.assertFalse(args.one_per_page)
        self.assertEqual(args.maxshrink, 0.0)
        self.assertFalse(args.break_all)
        self.assertEqual(args.bars_per_line, 0)
        self.assertFalse(args.select_composer)
        self.assertFalse(args.continue_all)
        self.assertEqual(args.dstaffsep, '0.0cm')
        self.assertEqual(args.fmtdir, '')
        self.assertEqual(args.sel_arg, 0)
        self.assertFalse(args.epsf)
        self.assertEqual(args.filename, '')
        self.assertEqual(args.styf, 'fonts.fmt')
        self.assertEqual(args.glue, 'fill')
        self.assertFalse(args.help_me)
        self.assertFalse(args.make_index)
        self.assertIsNone(args.nbars)
        self.assertFalse(args.landscape)
        self.assertEqual(args.leftmargin, '0.0cm')
        self.assertFalse(args.noauthor)
        self.assertFalse(args.notab)
        self.assertEqual(args.frfont, 'frFrancisque')
        self.assertEqual(args.itfont, 'itTimes')
        self.assertEqual(args.defont, 'deCourier')
        self.assertFalse(args.write_historical)
        self.assertFalse(args.pagenumbers)
        self.assertEqual(args.outfile, 'out.ps')
        self.assertFalse(args.outf)
        self.assertIsNone(args.pretty)
        self.assertEqual(args.paper_format, 'letter')
        self.assertFalse(args.select_rhythm)
        self.assertFalse(args.select_source)
        self.assertEqual(args.scale, 0.7)
        self.assertFalse(args.select_title)
        self.assertEqual(args.transposition, '')
        self.assertEqual(args.tabsize, 14)
        self.assertFalse(args.transposegchords)
        self.assertEqual(args.voices, '')
        self.assertEqual(args.staffwidth, '')
        self.assertFalse(args.include_xrefs)
        self.assertEqual(args.strictness, 0.0)
        # self.assertEqual(args.filenames, list())


class TestCmdlineUsed(unittest.TestCase):
    def setUp(self) -> None:
        sys.argv = [sys.argv[0]]

    def test_o(self):
        sys.argv.append('-o')
        sys.argv.append('oh.ps')
        args = utils.cmdline.options()
        self.assertEqual(args.outfile, 'oh.ps')

    def test_f1(self):
        sys.argv.append('file0')
        args = utils.cmdline.options()
        self.assertIsInstance(args.filenames, list)
        self.assertTrue('file0' in args.filenames)
        self.assertEqual(args.filenames[0], 'file0')


    def test_fn(self):
        sys.argv.append('file1')
        sys.argv.append('file2')
        sys.argv.append('file3')
        args = utils.cmdline.options()
        self.assertIsInstance(args.filenames, list)
        self.assertTrue('file2' in args.filenames)
        self.assertTrue('file0' not in args.filenames)
        self.assertEqual(len(args.filenames), 3)

    def test_b(self):
        sys.argv.append('-b')
        args = utils.cmdline.options()
        self.assertTrue(args.break_all)
        sys.argv = [sys.argv[0]]
        sys.argv.append('+b')
        args = utils.cmdline.options()
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
