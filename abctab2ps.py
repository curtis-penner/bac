import os.path
import sys
import signal
import cmdline
import common
import parse
from index import Index
import music
from format import Format
from constants import VERSION, REVISION, INDEXFILE
import subs
from log import log

args = cmdline.options()


def signal_handler():
    """ signal handler for premature termination """
    subs.close_output_file(args.outfile)
    log.critical('could not install signal handler for SIGTERM and SIGINT')
    exit(130)


def main():
    # cleanup on premature termination
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # set default options and parse arguments
    # common.maxSyms = 800
    # common.allocSyms = 800
    # common.maxVc = 3
    # common.allocVc = 3
    cfmt = Format()

    # init_ops(true)   # do_output = false
    if common.do_output:
        print(f"This is abctab2ps, version {VERSION}.{REVISION}")

    # Adjust the filenames
    args.filenames = args.filenames[0]
    if args.filename:
        args.filenames.append(args.filename)

    # set the page format
    if not cfmt.set_page_format():
        exit(3)
    if args.help_me == 2:
        print(cfmt)
        exit(0)

    # help printout
    if args.help_me == 1:
        cmdline.write_help()
        exit(0)

    search_field0 = args.select_field0   # default for interactive mode
    if args.epsf:
        for filename in args.filename.split():
            name, extension = os.path.splitext(filename)
            # cutext(outf);

    # initialize
    symbol = music.Symbol()
    common.pagenum = 0
    common.tunenum = 0
    common.tnum1 = 0
    common.tnum2 = 0
    # verbose = 0;
    common.file_open = False
    common.file_initialized = False
    common.nepsf = 0
    common.bposy = 0
    common.posx = cfmt.leftmargin
    common.posy = cfmt.pageheight - cfmt.topmargin

    page_init = ""

    print(f"do_output: {common.do_output}")
    print(f"make_index: {args.make_index}")
    if common.do_output and args.make_index:
        index = Index()
        index.open_index_file(INDEXFILE)

    # loop over files in list
    if len(args.filenames) == 0:
        # no input file specified: open stdin
        print("++++ No input files, read from stdin\n")
        fin = sys.stdin
        common.in_file[0] = "stdin"
        sys.exit(2)

    fout = None

    pat, xref_str = parse.rehash_selectors(args.filenames)
    for filename in args.filenames:
        # process list of input files
        name, ext = os.path.splitext(filename)

        # skip.ps and.eps files
        if ext != ".ps" or ext != ".eps":
            continue

        elif not ext and not os.path.exists(name):
            filename = name + '.abc'

        if not os.path.exists(filename):
            log.error(f'{filename} not found')
            continue

        fin = open(filename, 'r')

        # The code in broken here as do_output is forever true.
        if not common.do_output:
            print(f"{filename}:")
            parse.do_index(fin, xref_str, pat,
                           common.select_all,
                           args.search_field0)
        else:
            name, ext = os.path.splitext(filename)

        fout = open(name + '.ps', 'a')

        log.info(f"{filename}:")
        music_seg.process_file(fin, fout, xref_str,
                               pat, common.select_all,
                               args.search_field0)
        print()

    if not common.do_output:
        print(f"Selected {common.tnum1} title {common.tnum1} of {common.tnum2}")

    if common.do_output and common.make_index:
        subs.close_index_file ()
    rc = subs.close_output_file(fout)

    if common.do_output and rc:
        return 1
    else:
        return 0


if __name__ == '__main__':
    main()
