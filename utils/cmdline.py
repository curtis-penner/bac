# Copyright 2019 Curtis

import argparse

version = '0.1'
revision = 'a'
format_dir = ''


def options():
    """
    Parse the cli

    :return: raw (not parse_args) of all the options
    """
    parser = argparse.ArgumentParser(description='typeset music using abc'
                                     ' format directly in postscript',
                                     prog='bac',
                                     prefix_chars='-+')
    parser.add_argument('--version',
                        action='version',
                        version=f'%(prog)s {version} {revision}')
    parser.add_argument('-1',
                        dest='one_per_page',
                        action='store_true',
                        help='write one tune per page.')
    parser.add_argument('+1',
                        dest='one_per_page',
                        action='store_const',
                        const=False,
                        help='write multiple tunes per page.')
    parser.add_argument('-a',
                        dest='maxshrink',
                        type=float,
                        default=0.0,
                        help=('set the maximal amount of permitted '
                              'shrinking to alfa, where 0 <= alfa <= 1. '
                              'A value of 0.0 means that no shrinking is '
                              'allowed, and a value of 1.0 allows '
                              'shrinking until the music are almost '
                              'touching. In conjunction with -c, by '
                              'default alfa is set to an intermediate '
                              'value (displayed with "abctab2ps -c -h"). '
                              'When -c is not used, maximal shrinking and '
                              'stretching are allowed.'))
    parser.add_argument('-b',
                        dest='break_all',
                        default=False,
                        action='store_true',
                        help=('break at all line ends, even if they end '
                              'with the continuation symbol "\\".'))
    parser.add_argument('+b',
                        dest='break_all',
                        action='store_false',
                        help='break at all line ends, following '
                             'normal convention')
    parser.add_argument('-B',
                        dest='bars_per_line',
                        default=0,
                        type=int,
                        help='try to typeset with bars per staff bars '
                             'on each line.')
    parser.add_argument('+B',
                        dest='bars_per_line',
                        default=0,
                        type=int,
                        help='try to typeset with bars per staff bars '
                             'on each line.')
    parser.add_argument('-C',
                        dest='select_composer',
                        default=False,
                        action='store_true',
                        help='Select composer')
    parser.add_argument('-c',
                        dest='continue_all',
                        default=False,
                        action='store_true',
                        help=('consider the input as one long line, ie., '
                              'implicitly append the continuation symbol '
                              '"\\" to every line of music. When doing '
                              'automatic line breaking with -c, the user '
                              'can control the spacing of the music '
                              'along the staff by specifying the '
                              '"compression parameter" alfa with '
                              'the -a flag.'))
    parser.add_argument('+c',
                        # This needs to be choose_outname = False
                        # outf = OUTPUTFILE
                        action='store_false',
                        dest='continue_all',
                        help='Do not consider input as one long line.')
    # This needs to have a special option -- see util.scan_U
    parser.add_argument('-d',
                        dest='dstaffsep',
                        type=str,
                        default='0.0cm',
                        help='set staff distance to distance (cm/in/pt).')
    parser.add_argument('-D',
                        dest='fmtdir',
                        default='',
                        type=str,
                        help='look for format files in directory fmtdir.')
    parser.add_argument('-e',
                        dest='sel_arg',
                        default=0,
                        type=int,
                        nargs='+',
                        help=('typesets only the tunes matching the '
                              'xref numbers selector1 [selector2 ...]. '
                              'Optionally, the search can be done on other '
                              'fields using in place of -e the flags -R '
                              '(seaches the rhythm field), -C (searches '
                              'the composer field), -S (searches the '
                              'source field), -T (seaches the title field '
                              '(default)).'))
    parser.add_argument('-E',
                        dest='epsf',
                        default=False,
                        action='store_true',
                        help='make EPSF (encapsulated postscript) output. '
                             'Each tune is then put into a separate file '
                             'with a correct bounding box and '
                             'no page breaks.')
    parser.add_argument('+E',
                        dest='epsf',
                        action='store_false',
                        help=('turn off EPSF (encapsulated postscript) '
                              'output.'))
    parser.add_argument('-args',
                        dest='filename',
                        default='',
                        type=str,
                        help='sets the input file. Has the same effect as '
                             'omitting this flag.')
    parser.add_argument('-F',
                        dest='styf',
                        default='fonts.fmt',
                        type=str,
                        help='read format from file formatfile[.fmt]. The '
                             'directory can be set with flag -D.')
    parser.add_argument('+F',
                        action='store_const',
                        const='',
                        dest='styf',
                        help='Do not read the format file.')
    parser.add_argument('-g',
                        dest='glue',
                        default='fill',
                        choices=['shrink', 'space', 'stretch', 'fill'],
                        help=('sets the "glue mode". The default mode is '
                              'fill, which fills the staff. This flag is '
                              'useful when changing the layout parameters, '
                              'to see what effect the changes have for '
                              'each mode separately.'))
    parser.add_argument('-Help',
                        dest='help_me',
                        default=False,
                        action='store_true',
                        help='show the default format parameters.')
    parser.add_argument('-I',
                        dest='make_index',
                        default=False,
                        action='store_true',
                        help='create index file, output: "Ind.ps".')
    parser.add_argument('-k',
                        dest='nbars',
                        type=int,
                        default=None,
                        help=('number every nbars. To number every first '
                              'bar per staff, set nbars to 0.'))
    parser.add_argument('-l',
                        dest='landscape',
                        action='store_true',
                        default=False,
                        help='print in landscape mode.')
    parser.add_argument('+l',
                        dest='landscape',
                        action='store_false',
                        help='print in portrait mode.')
    parser.add_argument('-m',
                        dest='leftmargin',
                        default='0.0cm',
                        type=str,
                        help='sets the left margin to margin (cm/in/pt).')
    parser.add_argument('-noauthor',
                        dest='noauthor',
                        default=False,
                        action='store_true',
                        help=('suppresses the postscript DSC comment for '
                              'the author (%%For). Useful when abctab2ps '
                              'is run automatically on a webserver or '
                              'when you do not want your name listed in '
                              'the ouput file.'))
    parser.add_argument('-notab',
                        dest='notab',
                        default=False,
                        action='store_true',
                        help=('suppresses all tablature specific '
                              'postscript routines and fonts in the '
                              'output file; use: passul for music only '
                              'input, because the resulting output file is '
                              'smaller. Basically, abctab2ps should behave '
                              'like abc2ps with this option.'))
    parser.add_argument('-nofrenchtab',
                        dest='frfont',
                        default='frFrancisque',
                        action='store_const',
                        const='',
                        help=('does not include the font for french tab '
                              'into the output file; useful if you only '
                              'use a different tab, because the resulting '
                              'output file is smaller.'))
    parser.add_argument('-noitaliantab',
                        dest='itfont',
                        default='itTimes',
                        action='store_const',
                        const='',
                        help=('does not include the font for italian tab '
                              '(and other number based tabs) into the '
                              'output file; useful if you only use a '
                              'different tab, because the resulting '
                              'output file is smaller.'))
    parser.add_argument('-nogermantab',
                        dest='defont',
                        default='deCourier',
                        action='store_const',
                        const='',
                        help=('does not include the font for german tab '
                              'into the output file; useful if you only '
                              'use a different tab, because the resulting '
                              'output file is smaller.'))
    parser.add_argument('-n',
                        dest='write_historical',
                        default=False,
                        action='store_true',
                        help='includes historical notes and other stuff at '
                             'the bottom of each tune.')
    parser.add_argument('+n',
                        dest='write_historical',
                        action='store_false',
                        help='turn off historical notes and other stuff.')
    parser.add_argument('-N',
                        dest='pagenumbers',
                        default=False,
                        action='store_true',
                        help='write page numbers')
    parser.add_argument('+N',
                        dest='pagenumbers',
                        default=False,
                        action='store_true',
                        help='write page numbers')
    parser.add_argument(
        '-o',
        dest='outfile',
        default='out.ps',
        help='output filename')
    parser.add_argument(
        '-O',
        dest='outf',  # change this to choose_output
        default=False,
        action='store_true',
        help=('in PS (EPS) mode, the output is written to outfile.ps '
              '(outfile001.eps). If the parameter to -O is "=", output '
              'for "foo.abc" is written to "foo.ps" ("foo001.eps").'))
    parser.add_argument('+O',
                        dest='outf',
                        action='store_false',
                        help='make out.ps the default')
    parser.add_argument('-p',
                        dest='pretty',
                        action='store_const',
                        const=1,
                        help=('generates pretty output, with more '
                              'whitespace between tunes, larger fonts for '
                              'titles, and larger music music. By '
                              'default, the layout squeezes the tunes to '
                              'reduce the number of pages.'))
    parser.add_argument('+p',
                        dest='pretty',
                        action='store_const',
                        const=0,
                        help='turn off pretty output.')
    parser.add_argument('-P',
                        dest='pretty',
                        action='store_const',
                        const=2,
                        help='another pretty output format.')
    parser.add_argument('-paper',
                        dest='paper_format',
                        default='letter',
                        type=str,
                        help=('sets paper format. Typical values for '
                              'format are "a4" or "letter". This command '
                              'line option overrides the system-wide '
                              'default papersize given in /etc/papersize. '
                              'For a list of all possible values try an '
                              'invalid value for format; this will also '
                              'print the default papersize on '
                              'your system.'))
    parser.add_argument('-R',
                        dest='select_rhythm',
                        default=False,
                        action='store_true',
                        help='Select rhythm')
    parser.add_argument('-S',
                        dest='select_source',
                        default=False,
                        action='store_true',
                        help='Select source')
    parser.add_argument('-s',
                        dest='scale',
                        default=0.7,
                        type=float,
                        help='scales the music output by factor scale.')
    parser.add_argument('-T',
                        dest='select_title',
                        default=False,
                        action='store_true',
                        help='Select title')
    parser.add_argument('-t',
                        dest='transposition',
                        default='',
                        help='transpose all music. If transposition is a '
                             'number, the music is transposed up as many '
                             'halftones; for downward transposition start '
                             'the number with an underscore "_". If '
                             'transposition is a note name, this note '
                             'becomes the root.')
    '''
    -tab or -nofrenchtab or -noitaliantab or -nogermantab: 
        parse_tab_args(-- --)
    '''
    parser.add_argument('-tabsize',
                        dest='tabsize',
                        default=14,
                        type=int,
                        help='sets the size of the tablature font '
                             'TabFont to fontsize.')
    parser.add_argument('-transposegchords',
                        dest='transposegchords',
                        default=False,
                        action='store_true',
                        help='transpose guitar chords too (in combination '
                             'with option -t), in case you use guitar '
                             'chords actually for chord letters')
    parser.add_argument('-V',
                        dest='voices',
                        nargs='?',
                        type=str,
                        default='',
                        help='select specified voices, eg. "-V 1,4-5"')
    parser.add_argument('-w',
                        dest='staffwidth',
                        default='',
                        type=str,
                        help='sets the width of the staff '
                             'to width (cm/in/pt).')
    parser.add_argument(
        '-x',
        dest='include_xrefs',
        action='store_true',
        default=False,
        help='includes the xref numbers in the tune title.')

    parser.add_argument(
        '+x',
        dest='include_xrefs',
        default=False,
        action='store_false',
        help='')
    parser.add_argument(
        '-X',
        dest='strictness',
        default=0.0,
        type=float,
        help='set strictness for note spacing; 0 < strictness < 1.')
    parser.add_argument(
        'filenames',
        type=str,
        nargs='*',
        default='',
        help='abc files to be processed. There must be one')

    return parser.parse_args()


def write_help():
    print(f'abctab2ps v{version}.{revision}')

    print("""
Usage: abctab2ps files..    [-e nums-or-pats] [other flags]
    - typeset abc files in Postscript.
where: files     input files in abc format
             nums        tune xref numbers, i.e. 1 3 6-7,20-
             pats        patterns for title search
Tunes are selected if they match a number or a pattern.
Flags: 
    -o            write output for selected tunes(obsolete)
    -E            produce EPSF output, one tune per file
    -O aa     set outfile name to aaa
    -O =        make outfile name from infile/title 
    -v nn     set verbosity level to nn
    -h            show this command summary

Selection:
    -e            following arguments are selectors
    -f            following arguments are file names
    -T            search    Title     field(default)
    -C            search Composer field instead of title
    -R            search    Rhythm    field instead of title
    -S            search    Source    field instead of title
    -V str    select voices, eg. -V 1,4-5

Formatting:
    -H            show the format parameters
    -p            pretty output(looks better, needs more space)
    -P            select second predefined pretty output style
    -s xx     set scale factor for symbol size to xx 
    -w xx     set staff width(cm/in/pt)
    -m xx     set left margin(cm/in/pt)
    -d xx     set staff separation(cm/in/pt)
    -x            include xref numbers in output
    -k nn     number every nn bars; 0 for first in staff
    -n            include notes and history in output
    -N            write page numbers
    -I            write index to Ind.ps
    -1            write one tune per page
    -l            landscape mode
    -g xx     set glue mode to shrink|space|stretch|fill
    -F foo    read format from \"foo.fmt\"
    -D bar    look for format files in directory "bar"
    -X x        set strictness for note spacing, 0<x<1 Transposing:
    -t n        transpose by n halftones(_n for negative number)
    -t XX     transpose root up/down to note XX(eg. C A# ^Bb _Bb)
    -transposegchords        transpose guitar chords too Line breaks:
    -a xx     set max shrinkage to xx(between 0 and 1)
    -b            break at all line ends(ignore continuations)
    -c            continue all line ends(append '\\')
    -B bb     put line break every bb bars

Tablature:
    -notab         music only input
    -nofrenchtab   no french tab in input
    -noitaliantab  no italian tab in input
    -nogermantab   no german tab in input
    -tabsize n     set tablature font size to n
""")


def write_version():
    print(f"bac {version}.{revision}")

    if len(format_dir) > 0:
        print(f'Default format directory {format_dir}', )
