# Copyright 2022 Curtis Penner

import os.path
import sys
import signal

import cmdline
import common
import format
import parse
import pssubs
import buffer
import music
import field
import util
import tab
import index
from constants import (VERSION, REVISION, INDEXFILE)
from constants import DEFVOICE
from constants import OBEYLINES, OBEYRIGHT, OBEYCENTER, ALIGN, SKIP, RAGGED
from log import log

cfmt = common.cfmt


def signal_handler():
    """ signal handler for premature termination """
    log.critical('could not install signal handler for SIGTERM and SIGINT')
    exit(130)


def is_pseudo_comment(line: str) -> bool:
    line = line.strip()
    return line.startswith("%%")


def write_text_block(fp, job: int, words_of_text='') -> None:
    if not words_of_text:
        return

    baseskip = cfmt.textfont.size * cfmt.lineskipfac
    parskip = cfmt.textfont.size * cfmt.parskipfac
    cfmt.textfont.set_font_str(common.page_init)

    swfac = music.set_swfac(cfmt.textfont.name)

    # Now this is stupid. All that work to just set it to 1.0

    spw = util.cwid(' ')
    fp.write("/LF \\{0 "
             f"{-baseskip:.1f}"
             " rmoveto} bind def\n")

    # output by pieces, separate at newline token
    ntxt = len(words_of_text)
    i1: int = 0
    while i1 < ntxt:
        i2 = -1
        for i in range(i1, ntxt):
            if words_of_text[i] == '$$NL$$':
                i2 = i
                break
        if i2 == -1:
            i2 = ntxt
        common.bskip(fp, baseskip)

        if job == OBEYLINES:
            fp.write("0 0 M(")
            for i in range(i1, i2):
                line, w_width = music.tex_str(words_of_text[i])
                fp.write(f"{line} ")
            fp.write(") rshow\n")

        elif job == OBEYCENTER:
            fp.write(f"{cfmt.staff_width / 2:.1f} 0 M(")
            for i in range(i1, i2):
                line, w_width = music.tex_str(words_of_text[i])
                fp.write(f"{line}")
                if i < i2-1:
                    fp.write(" ")
            fp.write(") cshow\n")

        elif job == OBEYRIGHT:
            fp.write(f"{cfmt.staff_width:.1f} 0 M(")
            for i in range(i1, i2):
                line, w_width = music.tex_str(words_of_text[i])
                fp.write(f"{line}")
                if i < i2-1:
                    fp.write(" ")
            fp.write(") lshow\n")

        else:
            fp.write("0 0 M mark\n")
            nc = 0
            mc = -1
            wtot = -spw
            text_width = cfmt.textfont.size
            for i in range(i2-1, i1, -1):
                line, w_width = music.tex_str(words_of_text[i])
                mc += len(words_of_text)
                wtot += w_width+spw
                nc += len(line)+2
                if nc >= 72:
                    fp.write("\n")
                fp.write(f"({line})")
                if job == RAGGED:
                    fp.write(" %.1f P1\n", cfmt.staff_width)
                else:
                    fp.write(" %.1f P2\n", cfmt.staff_width)
                    # first estimate:(total textwidth)/(available width)
                    text_width = wtot*swfac*cfmt.textfont.size
            if "Courier" in cfmt.textfont.name:
                text_width = 0.60 * mc * cfmt.textfont.size
            ftline0 = text_width / cfmt.staff_width
            # revised estimate: assume some chars lost at each line end
            nbreak = int(ftline0)
            text_width = text_width + 5 * nbreak * util.cwid('a') * swfac * cfmt.textfont.size
            ftline = text_width/cfmt.staff_width
            ntline = int(ftline + 1.0)
            log.info(f"first estimate {ftline0:.2f}, revised {ftline:.2f}")
            log.info(f"Output {i2-i1} words, about {ftline:.2f} lines(fac {swfac:.2f})")
            common.bskip(fp, (ntline-1)*baseskip)

        buffer.buffer_eob(fp)
        # next line to allow pagebreak after each text "line"
        # if(!epsf && !within_tune) write_buffer(fp);
        i1 = i2+1
    common.bskip(fp, parskip)
    buffer.buffer_eob(fp)
    # next line to allow pagebreak after each paragraph
    if not common.epsf and not common.within_tune:
        buffer.write_buffer(fp)
    common.page_init = ""


def process_text_block(fp_in, fp, job: bool) -> None:
    add_final_nl = False
    if job == OBEYLINES:
        add_final_nl = True
    music.output_music(fp)
    buffer.buffer_eob(fp)
    common.cfmt.textfont.set_font(fp, False)
    common.words_of_text = ""
    for i in range(100):
        ln = fp_in.read()
        if ln == '':
            log.error("EOF reached scanning text block")
        common.linenum += 1
        log.warning(f"{common.linenum:3d}  {ln} \n")
        if ln.startswith('%%'):
            del ln[0:1]

        if ln == "endtext":
            break

        if job != SKIP:
            if not ln:
                write_text_block(fp, job)
                common.words_of_text = ''
            else:
                field.add_to_text_block(ln, add_final_nl)
    if job != SKIP:
        write_text_block(fp, job)


def process_ps_comment(fp_in, fp, line):
    from constants import CM

    l_width = common.cfmt.staff_width

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
        music.output_music(fp)
        common.cfmt.textfont.set_font(fp, False)
        common.words_of_text = ''
        if fstr:
            field.add_to_text_block(fstr, True)
        else:
            field.add_to_text_block("", True)
        if w == "text":
            write_text_block(fp, OBEYLINES, fstr)
        elif w == "right":
            write_text_block(fp, OBEYRIGHT, fstr)
        else:
            write_text_block(fp, OBEYCENTER, fstr)
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
        common.bskip(fp, h1)
        fp.write(f"{l_width / 2 - s_len / 2:.1f} {l_width / 2 + s_len / 2:.1f} sep0\n")
        common.bskip(fp, h2)
        buffer.buffer_eob(fp)
    elif w == "vskip":
        if common.within_block and not common.do_this_tune:
            return
        music.output_music(fp)
        unum1 = line

        h1 = format.g_unum(unum1)
        if h1 * h1 < 0.00001:
            h1 = 0.5 * CM
        common.bskip(fp, h1)
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
            common.cfmt.interpret_format_line(line)
        else:
            dfmt = format.Format()
            dfmt.interpret_format_line(line)
            common.cfmt = dfmt


def process_file(fp_in, fp_out, xref_str, pat, sel_all, search_field):
    # int type;
    common.within_tune = False
    common.within_block = False
    common.do_this_tune = False

    # This is where there is the statements of verbose.
    # Just need to understand what the verbose number means to
    #  debug, warning, info, error, critical
    info = field.Field()
    with open(fp_in) as f:
        lines = f.readlines()
    fp = open(fp_out, 'w')
    if parse.is_cmdline(lines[0].strip()):
        info.process_line(fp, field.XRef, lines[0], pat, sel_all, search_field)
        del lines[0]
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if is_pseudo_comment(line):
            process_ps_comment(fp_in, fp_out, line)
            continue
        if parse.is_comment(line):
            continue

        parse.decomment_line(line)

        # reset_info(default_info)
        info = field.Field()
        if field.is_field(line):
            # skip after history info. Nightmarish syntax, that.
            k, v = line.split(':', 1)
            if k != 'H':
                pass
            else:
                info.history(v)

        if not common.do_music:
            return
        if info.voice.parse_vocals(line):
            return

        # now parse a real line of music
        if not common.voices:
            common.ivc = info.voice.switch_voice(DEFVOICE)

        n_sym_0 = len(common.voices[common.ivc].syms)

        # music or tablature?
        if tab.is_tab_line(line):
            tab.parse_tab_line(line)
        else:
            parse.parse_music_line(line)

        log.debug(f"  parsed music symbols {n_sym_0} to"
                  f" {len(common.voices[common.ivc].syms)-1} for voice {common.ivc}")
        info.process_line(fp, field.XRef, line, xref_str, pat, sel_all)

    if not common.epsf:
        buffer.buffer_eob(fp_out)
        buffer.write_buffer(fp_out)


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
    log.debug(args.filenames)
    # set the page format
    common.cfmt.set_page_format()

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
        ind = index.Index()
        ind.open_index_file(INDEXFILE)

    # loop over files in list
    pat, xref_str = parse.rehash_selectors(args.filenames)
    fout = None
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
        index.Index().close_index_file()
    field.Field().close_output_file(fout)


if __name__ == '__main__':
    main()
