import os.path
import sys
import cmdline
import common
import music_seg
from format import Format
from constants import INDEXFILE



def main():
    psel = list()
    # set default options and parse arguments
    maxSyms = allocSyms = 800
    maxVc = allocVc = 3
    cfmt = Format()

    # init_ops(true)   # do_output = false
    args = cmdline.options()
    if common.do_output:
        print(f"This is abctab2ps, version {cmdline.version}.{cmdline.revision}")


    # alloc_structs()

    # set the page format
    nfontnames = 0
    if not cfmt.set_page_format():
        exit(3)
    if args.help_me == 2:
        print(cfmt)
        exit (0)

    # help printout
    if args.help_me == 1:
        cmdline.write_help()
        exit (0)

    if args.number_input_files > 0:
        isel = psel[args.number_input_files-1]
    else:
        isel=psel[0]

    search_field0 = cmdline.s_field[isel]   # default for interactive mode
    if args.epsf:
        for filename in cmdline.file
        name, extension = os.path.splitext(filename)
        cutext(outf);

    # initialize
    symbol = music_seg.Symbol()
    common.pagenum = 0
    common.tunenum = 0
    common.tnum1 = 0
    common.tnum2 = 0
    # verbose = 0;
    common.file_open = False
    common.file_initialized = False
    nepsf = 0
    bposy = 0
    common.posx = cfmt.leftmargin
    common.posy = cfmt.pageheight - cfmt.topmargin

    page_init = ""

    print(f"do_output: {common.do_output}")
    print(f"make_index: {args.make_index}")
    if common.do_output and args.make_index:
        open_index_file(INDEXFILE)

    # loop over files in list
    if args.number_input_files == 0:
        print("++++ No input files, read from stdin\n")
    for j in range(args.number_input_files): {
        if args.number_input_files == 0:
            # no input file specified: open stdin
            fin = sys.stdin
            in_file[0] = "stdin"
        else:
            # process list of input files
            if j == args.number_input_files):
                break
            else {
                getext(in_file[j], ext);
                / *skip.ps and.eps
                files * /
                if ((!strcmp(ext, "ps")) | | (!strcmp(ext, "eps"))) continue;

                if ((fin = fopen (in_file[j], "r")) == NULL) {
                if (!strcmp(ext, "")) strext (in_file[j], in_file[j], "abc", 1);
                if ((fin = fopen (in_file[j], "r")) == NULL) {
                printf ("++++ Cannot open input file: %s\n", in_file[j]);
                continue;
                }
                }
            }
        }
        isel=psel[j];
        search_field=s_field[isel];
        npat=rehash_selectors (sel_str[isel], xref_str, pat);
        dfmt=sfmt;
        strcpy(infostr, in_file[j]);

        // The code in broken here as do_output is forever true.
        if (not do_output) {
          printf ("%s:\n", in_file[j]);
          do_index (fin,xref_str,npat,pat,select_all,search_field);
        } else {
          if (!epsf) {
            strext (outf, outf, "ps", 1);
            if (choose_outname) strext (outf, in_file[j], "ps", 1);
            open_output_file(outf,in_file[j]);
          }
          printf ("%s: ", in_file[j]);
          if (vb>=3) printf ("\n");
          process_file (fin,fout,xref_str,npat,pat,select_all,search_field);
          printf ("\n");
        }
  }

  if (not do_output)
    printf ("Selected %d title%s of %d\n", tnum1, tnum1==1?"":"s", tnum2);

  if (do_output && make_index) close_index_file ();
  rc = close_output_file ();

  if (do_output && rc)
    return 1;
  else
    return 0;
}

if __name__ == '__main__':
    main()

                                                                              334,0-1       Bot

