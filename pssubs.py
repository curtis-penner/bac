# Copyright 2018 Curtis Penner

import datetime
import getpass

import common
import constants
import log
import cmdline
import syms
from format import Format, Font

log = log.log
args = cmdline.options()

cfmt = Format()

PS_LEVEL = 2


def level1_fix(fp):
    """
    Special defs for level 1 Postscript. The fix to define
    ISOLatin1Encoding for ps level 1 (David Weisman)
    """
    msg =("/selectfont { exch findfont exch dup     %% emulate level 2 op\n"
          "    type /arraytype eq {makefont}{scalefont} ifelse setfont\n"
          "} bind def\n")
    #
    msg_changes = """
/ISOLatin1Encoding
[ /.notdef        /.notdef        /.notdef        /.notdef
  /.notdef        /.notdef        /.notdef        /.notdef
  /.notdef        /.notdef        /.notdef        /.notdef
  /.notdef        /.notdef        /.notdef        /.notdef
  /.notdef        /.notdef        /.notdef        /.notdef
  /.notdef        /.notdef        /.notdef        /.notdef
  /.notdef        /.notdef        /.notdef        /.notdef
  /.notdef        /.notdef        /.notdef        /.notdef
  /space          /exclam         /quotedbl       /numbersign
  /dollar         /percent        /ampersand      /quoteright
  /parenleft      /parenright     /asterisk       /plus
  /comma          /hyphen         /period         /slash
  /zero           /one            /two            /three
  /four           /five           /six            /seven
  /eight          /nine           /colon          /semicolon
  /less           /equal          /greater        /question
  /at             /A/B/C/D/E/F/G/H/I/J/K/L/M/N/O/P/Q/R/S/T/U/V/W/X/Y/Z /bracketleft
  /backslash      /bracketright/asciicircum/underscore
  /quoteleft      /a/b/c/d/e/f/g/h/i/j/j/l/m/n/o/p/q/r/s/t/u/v/w/x/y/z /braceleft
  /bar            /braceright/asciitilde          /.notdef
  /.notdef        /.notdef        /.notdef        /.notdef
  /.notdef        /.notdef        /.notdef        /.notdef
  /.notdef        /.notdef        /.notdef        /.notdef
  /.notdef        /.notdef        /.notdef        /.notdef
  /dotlessi       /grave          /acute          /circumflex
  /tilde          /macron         /breve          /dotaccent
  /dieresis       /.notdef        /ring           /cedilla
  /.notdef        /hungarumlaut/ogonek            /caron
  /space          /exclamdown /cent               /sterling
  /currency       /yen            /brokenbar      /section
  /dieresis       /copyright      /ordfeminine/guillemotleft
  /logicalnot     /hyphen         /registered /macron
  /degree         /plusminus      /twosuperior/threesuperior
  /acute          /mu             /paragraph      /periodcentered
  /cedilla        /onesuperior/ordmasculine/guillemotright
  /onequarter     /onehalf        /threequarters/questiondown
  /Agrave         /Aacute         /Acircumflex/Atilde
  /Adieresis      /Aring          /AE             /Ccedilla
  /Egrave         /Eacute         /Ecircumflex/Edieresis
  /Igrave         /Iacute         /Icircumflex/Idieresis
  /Eth            /Ntilde         /Ograve         /Oacute
  /Ocircumflex/Otilde             /Odieresis      /multiply
  /Oslash         /Ugrave         /Uacute         /Ucircumflex
  /Udieresis      /Yacute         /Thorn          /germandbls
  /agrave         /aacute         /acircumflex/atilde
  /adieresis      /aring          /ae             /ccedilla
  /egrave         /eacute         /ecircumflex/edieresis
  /igrave         /iacute         /icircumflex/idieresis
  /eth            /ntilde         /ograve         /oacute
  /ocircumflex/otilde             /odieresis      /divide
  /oslash         /ugrave         /uacute         /ucircumflex
  /udieresis      /yacute         /thorn          /ydieresis
] def\n\n"""

    fp.write(msg)
    fp.write(msg_changes)
    # end of fix to define ISOLatin1Encoding for ps level 1


def init_ps(fp, filename, bx1=0.0, by1=0.0, bx2=0.0, by2=0.0):
    """
    :param file fp:
    :param str filename:
    :param float bx1:
    :param float by1:
    :param float bx2:
    :param float by2:
    """
    if common.is_epsf:
        log.info(f'Open EPS file with title "{filename}"')
        fp.write('%!PS-Adobe-3.0 EPSF-3.0\n')
        fp.write(f'%%BoundingBox: {bx1:.0f} {by1:.0f} {bx2:.0f} {by2:.0f}\n')
    else:
        log.info(f'Open PS file with title "{filename}"')
        fp.write(f'%!PS-Adobe-3.0\n')

    # Title
    fp.write(f'%%Title: {fp}\n')

    # CreationDate
    now = datetime.datetime.now()
    fp.write('%%Creator: abctab2ps '
             f'{constants.VERSION}.{constants.REVISION}\n')
    fp.write(f'%%CreationDate: {now}\n')

    # Author
    if not args.noauthor:
        fp.write(f'%%For: {getpass.getuser()}\n')

    if PS_LEVEL == 2:
        fp.write('%%LanguageLevel: 2\n')
    if not common.is_epsf:
        fp.write('%%Pages: (atend)\n')
    fp.write('%%EndComments\n\n')

    if common.is_epsf:
        fp.write('gsave /origstate save def mark\n100 dict begin\n\n')

    fp.write('%%BeginSetup\n')
    if PS_LEVEL < 2:
        level1_fix(fp)
    log.debug('\nDefining ISO fonts in file header:\n')
    for i, font in enumerate(Font.names):
        syms.define_font(fp, font, i)
        log.debug(f'     F{i}     {font}')

    syms.define_symbols(fp)
    fp.write('\n/T {translate} bind def\n/M {moveto} bind def\n')
    fp.write('\n0 setlinecap 0 setlinejoin 0.8 setlinewidth\n')
    fp.write('%%EndSetup\n')
    common.file_initialized = True


def close_ps(fp):
    log.info("closing PS file\n")
    fp.write("\n%%%%Trailer\n"
             f"%%%%Pages: {common.page_number}\n"
             "\n%%EOF\n\n")


def init_page(fp):
    """
    initialize postscript page

    :param fp:
    """
    log.info(f"init_page called, in_page is {common.in_page}")
    if common.in_page:
        return

    if not common.file_initialized:
        log.info("file not yet initialized, do it now")
        init_ps(fp, common.filename)

    common.in_page = True
    common.page_number += 1
    log.info(f"[{common.page_number}] ")

    fp.write(f"\n%% --- page {common.page_number}\n"
             f"%%Page: {common.page_number} {common.page_number}\n"
             "%%BeginPageSetup\n")

    if cfmt.landscape:
        fp.write("%%PageOrientation: Landscape\n")
    fp.write("gsave ")
    if cfmt.landscape:
        fp.write(f"90 rotate 0 {-cfmt.page_height:.1f} translate ")
    fp.write(f"{cfmt.left_margin:.2f} "
             f"{cfmt.page_height - cfmt.top_margin:.2f} translate\n")
    fp.write( "%%EndPageSetup\n")

    # write page number
    if common.page_number:
        fp.write( "/Times-Roman 12 selectfont ")

        # page numbers always at right
        fp.write(f"{cfmt.staff_width:.1f} {cfmt.top_margin - 30.0:.1f} "
                 f"moveto ({common.page_number:d}) /bx false def lshow\n")


def close_page(fp):
    log.debug(f"close_page called; in_page is {common.in_page}")
    if not common.in_page:
        return
    common.in_page = False
    fp.write("\n%%PageTrailer\ngrestore\nshowpage\n")


def init_epsf(fp):
    px = cfmt.left_margin
    py = cfmt.page_height - cfmt.top_margin
    fp.write(f"{px:.2f} {py:.2f} translate\n")


def close_epsf(fp):
    fp.write("\nshowpage\nend\n"
             "cleartomark origstate restore grestore\n\n")


def write_pagebreak(fp):
    close_page(fp)
    init_page(fp)
    if len(common.page_init) > 0:
        fp.print(f"{common.page_init}\n")
    common.posy = common.cfmt.page_height - common.cfmt.top_margin
