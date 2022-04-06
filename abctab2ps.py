# Copyright 2022 Curtis Penner

import os.path
import sys
import signal

import cmdline
import common
import format
import info
import parse
import voice
import pssubs
import buffer
import music
import subs
import tab
from format import Format
from constants import (VERSION, REVISION, INDEXFILE)
from constants import (HISTORY, MWORDS, DEFVOICE)
from constants import (OBEYLINES, OBEYRIGHT, OBEYCENTER, ALIGN, SKIP, RAGGED)

from log import log

args = cmdline.options()
cfmt = Format()
voice = voice.Voice()


def signal_handler():
    """ signal handler for premature termination """
    subs.close_output_file(args.outfile)
    log.critical('could not install signal handler for SIGTERM and SIGINT')
    exit(130)


def process_textblock(fpin, fp, job: bool) -> None:
    add_final_nl = False
    if job == OBEYLINES:
        add_final_nl = True
    music.output_music(fp)
    buffer.buffer_eob(fp)
    common.cfmt.textfont.set_font(fp, False)
    common.words_of_text = ""
    for i in range(100):
        ln = fpin.read()
        if ln == '':
            log.error("EOF reached scanning text block")
        common.linenum += 1
        if common.verbose >= 5 or common.vb >= 10:
            print(f"{common.linenum:3d}  {ln} \n")
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


def process_pscomment(fpin, fp, line):
    # char w[81], fstr[81], unum1[41], unum2[41], unum3[41];
    # float h1, h2, len, lwidth;
    # int i, nch, job;
    global cfmt

    from constants import CM

    dfmt = Format()

    lwidth = cfmt.staffwidth

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
        process_textblock(fpin, fp, job)
        return

    if w == "text" or w == "center" or w == "right":
        if common.epsf and not common.within_block:
            return

        if common.within_block and not common.do_this_tune:
            return
        music.output_music(fp)
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
        music.output_music(fp)

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
        common.bskip(h1)
        fp.write(f"{lwidth / 2 - s_len / 2:.1f} {lwidth / 2 + s_len / 2:.1f} sep0\n")
        common.bskip(h2)
        buffer.buffer_eob(fp)
    elif w == "vskip":
        if common.within_block and not common.do_this_tune:
            return
        music.output_music(fp)
        unum1 = line

        h1 = format.g_unum(unum1)
        if h1 * h1 < 0.00001:
            h1 = 0.5 * CM
        common.bskip(h1)
        buffer.buffer_eob(fp)
    elif w == "newpage":
        if common.within_block and not common.do_this_tune:
            return
        music.output_music(fp)
        buffer.write_buffer(fp)
        common.use_buffer = False
        pssubs.write_pagebreak(fp)
    else:
        if common.within_block:
            cfmt.interpret_format_line(line)
        else:
            dfmt.interpret_format_line(line)
            cfmt = dfmt


def process_file(fp_in, fp_out, xref_str, pat, sel_all, search_field, info=None):
    # int type;
    common.within_tune = False
    common.within_block = False
    common.do_this_tune = False

    # This is where there is the statements of verbose.
    # Just need to understand what the verbose number means to
    #  debug, warning, info, error, critical

    with open(fp_in) as f:
        lines = f.readlines()
    if parse.is_cmdline(lines[0].strip()):
        subs.process_cmdline(lines[0])
        del lines[0]
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if parse.is_pseudocomment(line):
            process_pscomment(fp_in, fp_out, line)
            continue
        if parse.is_comment(line):
            continue

        parse.decomment_line(line)

        # reset_info(default_info)
        field = info.Field()
        if field.is_field(line):
            # skip after history field. Nightmarish syntax, that.
            k, v = line.split(':', 1)
            if k != 'H':
                pass
            else:
                field.history(v)

        if not common.do_music:
            return
        if voice.parse_vocals(line):
            return MWORDS

        # now parse a real line of music
        if not common.voices:
            common.ivc = voice.switch_voice(DEFVOICE)

        nsym0 = len(common.voices[common.ivc].syms)

        # music or tablature?
        if tab.is_tab_line(line):
            tab.parse_tab_line(line)
        else:
            parse.parse_music_line(line)

        log.debug(f"  parsed music symbols {nsym0} to"
                  f" {len(common.voices[common.ivc].syms)-1} for voice {common.ivc}")
        field.process_line(fp_out, xref_str, pat, sel_all, search_field)

    if not common.epsf:
        buffer.buffer_eob(fp_out)
        buffer.write_buffer(fp_out)


def main():
    import index

    # cleanup on premature termination
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # help printout
    if args.help_me == 1:
        cmdline.write_help()
        exit(0)

    log.info(f"do_output: {common.do_output}")
    if common.do_output:
        print(f"This is abctab2ps, version {VERSION}.{REVISION}")

    if args.filename:
        args.filenames.append(args.filename)
    log.info(args.filenames)
    # set the page format
    cfmt.set_page_format()

    common.search_field0 = args.select_field0   # default for interactive mode
    # if args.epsf:
    #     for filename in args.filename.split():
    #         name, extension = os.path.splitext(filename)

    if not args.filenames:
        # no input file specified: open stdin
        log.error("++++ No input files, read from stdin")
        sys.exit(2)

    if common.do_output and args.make_index:
        log.info(f"make_index: {args.make_index}")
        index = index.Index()
        index.open_index_file(INDEXFILE)

    # loop over files in list
    pat, xref_str = parse.rehash_selectors(args.filenames)
    global fout
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

        log.info(f"{filename}:")
        if args.output:
            fout = open(args.output)
        else:
            fout = open(name + '.ps', 'a')
        fin = open(filename, 'r')
        if not common.do_output:
            log.info(f"{filename}:")
            parse.do_index(fin, xref_str, pat, common.select_all, args.search_field0)

        # this is the start of the process
        process_file(fin, fout, xref_str, pat, common.select_all, args.search_field0)

    # The rest just closes everything up
    if not common.do_output:
        print(f"Selected {common.tnum1} title {common.tnum1} of {common.tnum2}")

    if common.do_output and common.make_index:
        subs.close_index_file()
    subs.close_output_file(fout)


if __name__ == '__main__':
    main()
