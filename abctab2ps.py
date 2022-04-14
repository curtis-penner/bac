# Copyright 2022 Curtis Penner

import os.path
import sys
import signal

import cmdline
import common
import util
from common import cfmt
import format
import parse
import voice
import pssubs
import buffer
import music
import subs
import tab
import index
from constants import (VERSION, REVISION, INDEXFILE)
from constants import (MWORDS, DEFVOICE)
from constants import OBEYLINES, OBEYRIGHT, OBEYCENTER, ALIGN, SKIP, RAGGED
from log import log


def signal_handler():
    """ signal handler for premature termination """
    log.critical('Bad shutdown with signal handler: SIGTERM and SIGINT')
    exit(130)


def process_blankline():
    common.within_tune = False
    common.do_this_tune = False
    common.within_block = False


def process_text_block(fp_in, fp, job: bool) -> None:
    # This is needs rework.
    add_final_nl = False
    if job == OBEYLINES:
        add_final_nl = True
    music.output_music(fp)
    buffer.buffer_eob(fp)
    cfmt.textfont.set_font(fp, False)
    common.words_of_text = ""
    for i in range(100):
        ln = fp_in.read()
        if not ln:
            log.error("EOF reached scanning text block")
        common.linenum += 1
        log.warning(f"{common.linenum:3d}  {ln} \n")
        if ln.startswith('%%'):
            del ln[0:1]

        if ln == "endtext":
            break

        if job != SKIP:
            if not ln:
                subs.write_text_block(fp, job)
                common.words_of_text = ''
            else:
                subs.add_to_text_block(ln, add_final_nl)
    if job != SKIP:
        subs.write_text_block(fp, job)


def is_pseudo_comment(ps: str) -> bool:
    return len(str) > 2 and ps.startswith('%%')


def process_ps_comment(fp_in, fp, line: str) -> None:
    from constants import CM

    l_width = cfmt.staff_width

    line = line.replace('%', ' ').strip()
    if ' ' in line:
        w = line
        fstr = ''
    else:
        w, fstr = line.split(maxsplit=1)

    if w == "begintext":
        if common.epsf and not common.within_block:
            return
        fstr = fstr.strip()
        if not fstr:
            fstr = "obeylines"

        if fstr == "obeylines":
            job = OBEYLINES
        elif fstr == "align":
            job = ALIGN
        elif fstr == "skip":
            job = SKIP
        elif fstr == "ragged":
            job = RAGGED
        else:
            job = SKIP
            log.error(f"bad argument for begintext: {fstr}")

        if common.within_block and not common.do_this_tune:
            job = SKIP
        process_text_block(fp_in, fp, job)
        return

    if w == "text" or w == "center" or w == "right":
        if common.epsf and not common.within_block:
            return

        if common.within_block and not common.do_this_tune:
            return
        music.output_music(fp)   # todo why go here?
        cfmt.textfont.set_font(fp, False)
        common.words_of_text = ''
        if fstr:
            subs.add_to_text_block(fstr, True)
        else:
            subs.add_to_text_block("", True)
        if w == "text":
            subs.write_text_block(fp, OBEYLINES, fstr)
        elif w == "right":
            subs.write_text_block(fp, OBEYRIGHT, fstr)
        else:
            subs.write_text_block(fp, OBEYCENTER, fstr)
            buffer.buffer_eob(fp)

    elif w == "sep":
        if common.within_block and not common.do_this_tune:
            return
        music.output_music(fp)   # todo why go here?

        unum1, unum2, unum3 = line.split(maxsplit=3)
        h1 = format.g_unum(unum1)
        h2 = format.g_unum(unum2)
        s_len = format.g_unum(unum3)
        if h1 * h1 < 0.00001:
            h1 = 0.5 * CM
        if h2 * h2 < 0.00001:
            h2 = h1
        if s_len * s_len < 0.0001:
            s_len = 3.0 * CM
        common.bskip(fp, h1)
        fp.write(f"{l_width / 2 - s_len / 2:.1f} {l_width / 2 + s_len / 2:.1f} sep0\n")
        common.bskip(fp, h2)
        buffer.buffer_eob(fp)
    elif w == "vskip":
        if common.within_block and not common.do_this_tune:
            return
        music.output_music(fp)   # todo Why go here?
        unum1 = line

        h1 = format.g_unum(unum1)
        if h1 * h1 < 0.00001:
            h1 = 0.5 * CM
        common.bskip(fp, h1)
        buffer.buffer_eob(fp)
    elif w == "newpage":
        if common.within_block and not common.do_this_tune:
            return
        music.output_music(fp)   # todo Why go here?
        buffer.write_buffer(fp)
        common.use_buffer = False
        pssubs.write_pagebreak(fp)
    else:
        if common.within_block:
            cfmt.interpret_format_line(line)
        else:
            dfmt = format.Format()
            dfmt.interpret_format_line(line)
            common.cfmt = dfmt


def process_file(f_in, f_out, xref_str: str, pat: list, sel_all: bool,
                 search_field: str, info=None):
    common.within_tune = False
    common.within_block = False
    common.do_this_tune = False

    lines = f_in.readlines()

    if parse.is_cmdline(lines[0].strip()):
        cmdline.process_cmdline(lines[0])
        del lines[0]
    for line in lines:
        line = line.strip()
        if util.isblankstr(line):
            process_blankline()
            continue
        if is_pseudo_comment(line):
            process_ps_comment(f_in, f_out, line)
            continue
        if parse.is_comment(line):
            continue

        line = parse.decomment_line(line)

        # # reset_info(default_info)
        # field = info.Field()
        # if field.is_field(line):
        #     # skip after history field. Nightmarish syntax, that.
        #     k, v = line.split(':', 1)
        #     if k == 'H':
        #         field.history(v)

        if not common.do_music:
            return

        # now parse a real line of music
        if not common.voices:
            v = voice.Voice()
            common.ivc = v.switch_voice(DEFVOICE)

        # Before
        n_sym_0 = len(common.voices[common.ivc].syms)

        # music or tablature?
        if tab.is_tab_line(line):
            tab.parse_tab_line(line)
        else:
            parse.parse_music_line(line)

        # After
        log.debug(f"  parsed music symbols {n_sym_0} to"
                  f" {len(common.voices[common.ivc].syms)-1} for voice {common.ivc}")
        field.process_line(f_out, xref_str, pat, sel_all, search_field)

    if not common.epsf:
        buffer.buffer_eob(f_out)
        buffer.write_buffer(f_out)


def main():
    args = cmdline.options()

    # cleanup on premature termination
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # help printout
    if args.help_me == 1:
        cmdline.write_help()
        exit(0)

    log.debug(f"do_output: {common.do_output}")
    if common.do_output:
        log.info(f"This is abctab2ps, version {VERSION}.{REVISION}")
    # consolidate the filenames
    if args.filename:
        args.filenames.append(args.filename)
    log.debug(f'Files to be processed: {args.filenames}')
    # set the page format
    cfmt.set_page_format()

    # if args.epsf:
    #     for filename in args.filenames:
    #         name, extension = os.path.splitext(filename)

    if not args.filenames:
        # no input file specified: open stdin
        log.error("++++ No input files, read from stdin")
        sys.exit(2)

    ind = index.Index()
    if common.do_output and args.make_index:
        log.info(f"make_index: {args.make_index}")
        ind.open_index_file(INDEXFILE)

    # loop over files in list
    pat, xref_str = parse.rehash_selectors(args.filenames)
    for filename in args.filenames:
        # process list of input files and skip.ps and.eps files
        name, ext = os.path.splitext(filename)
        if ext != ".ps" or ext != ".eps":
            continue
        elif not ext and not os.path.exists(name):
            filename = name + '.abc'
            if not os.path.exists(filename):
                log.error(f'{filename} not found')
                continue

        # Create file pointers
        if args.output:
            fout = open(args.output)
        else:
            fout = open(name + '.ps', 'a')
        fin = open(filename, 'r')

        if not common.do_output:
            log.info(f"{filename}:")
            ind.do_index(fin, xref_str, pat, common.select_all, args.search_field0)
        if common.do_output and common.make_index:
            subs.close_index_file()

        # this is the start of the process
        process_file(fin, fout, xref_str, pat, common.select_all, args.search_field0)

        subs.close_output_file(fout)  # Clean up; close the files gracefully

    if not common.do_output:
        print(f"Selected {common.tnum1} title {common.tnum1} of {common.tnum2}")


if __name__ == '__main__':
    main()
