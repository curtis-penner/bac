# Copyright 2022 Curtis Penner

import os.path
import sys
import signal

import cmdline
import common
import constants
import field
import music
import parse
import tab
from log import log


args = cmdline.options()


def signal_handler():
    """ signal handler for premature termination """
    log.critical('could not install signal handler for SIGTERM and SIGINT')
    exit(130)


def is_comment(comment: str) -> bool:
    return len(comment) and comment[0] == '%'


def is_pseudo_comment(line: str) -> bool:
    return line.startswith("%%")


def is_cmdline(cmd: str) -> bool:
    """ command line """
    return len(cmd) > 2 and cmd.startswith('%!')


def process_file(fin):    # , fp_out, xref_str, pat, sel_all, search_field):
    # int type;
    common.within_tune = False
    common.within_block = False
    common.do_this_tune = False

    info = field.Field()
    # This is where there is the statements of verbose.
    # Just need to understand what the verbose number means to
    #  debug, warning, info, error, critical

    with open(fin) as f:
        lines = f.readlines()

    with open(args.output, 'w') as fp:
        if is_cmdline(lines[0].strip()):
            cmdline.process_cmdline(lines[0])
            del lines[0]

        for line in lines:
            line = line.strip()
            if not line:   # Todo: if within_block end it, otherwise do nothing
                # if common.within_tune
                continue
            if is_pseudo_comment(line):
                music.process_ps_comment(fp, line)
                continue
            if is_comment(line):
                continue

            line = parse.decomment_line(line)

            # reset_info(default_info)
            if field.is_field(line):
                info(line)

            if info.voice.parse_vocals(line):
                return

            # now parse a real line of music
            if not common.voices:
                common.voices.append(info.voice.switch_voice(constants.DEFVOICE))

            # music or tablature?
            if tab.is_tab_line(line):
                tab.parse_tab_line(line)
            else:
                parse.parse_music_line(line)

            # log.debug(f"  parsed music symbols {n_sym_0} to"
            #           f" {len(common.voices[common.ivc].syms)-1} for voice {common.ivc}")
            info.process_line(fp, line)    # field.XRef, line, xref_str, pat, sel_all)

        # if not common.epsf:
        #     buffer.buffer_eob(fp_out)
        #     buffer.write_buffer(fp_out)


def main():
    # cleanup on premature termination
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    log.debug(f"do_output: {common.do_output}")
    if common.do_output:
        log.info(f"This is abctab2ps, version {constants.VERSION}.{constants.REVISION}")

    # consolidate the filenames
    if args.filename:
        args.filenames.append(args.filename)
        log.debug(args.filenames)
    # set the page format
    common.cfmt.set_page_format()

    # common.search_field0 = args.select_field0   # default for interactive mode
    # if args.epsf:
    #     for filename in args.filename.split():
    #         name, extension = os.path.splitext(filename)

    if not args.filenames:
        # no input file specified: open stdin
        log.error("++++ No input files, read from stdin")
        sys.exit(2)

    # if common.do_output and args.make_index:
    #     log.info(f"make_index: {args.make_index}")
    #     ind = index.Index()
    #     index_file = 'index.ps'
    #     ind.open_index_file(index_file)

    # loop over files in list
    # pat, xref_str = parse.rehash_selectors(args.filenames)
    # fout = None

    # process list of input files and skip.ps and.eps files
    for filename in args.filenames:
        name, ext = os.path.splitext(filename)
        if ext == ".ps" or ext == ".eps":
            continue
        elif not ext and not os.path.exists(name):
            filename = name + '.abc'
            if not os.path.exists(filename):
                log.error(f'{filename} not found')
                continue

        log.info(f"{filename}:")
        if args.output:
            common.output = args.output
        else:
            common.output = name + '.ps'

        if not common.do_output:
            log.info(f"{filename=}: not no output")
        # parse.do_index(fin, xref_str, pat, common.select_all, args.search_field0)

        # this is the start of the process
        process_file(filename)  # fp, xref_str, pat, common.select_all, args.search_field0)

    # The rest just closes everything up
    # if not common.do_output:
    #     print(f"Selected {common.tune_num1} title {common.tune_num1} of {common.tune_num2}")

    # if common.do_output and common.make_index:
    #     index.close_index_file()
    # field.Field().close_output_file(fout)


if __name__ == '__main__':
    main()
