# Copyright(c) Curtis Penner
import math
import os

from constants import GSTEM_XOFF, STAFFHEIGHT, TABFONTDIRS
from common import cfmt
import cmdline
from log import log

args = cmdline.options()
temp_switch = False

STEM_XOFF = 3.5
STEM_YOFF = 1.0


def def_misc(fp):
    fp.write("\n/cshow [ % string cshow - center at current pt\n"
             "   dup stringwidth pop 2 div neg 0 rmoveto\n"
             "   bx [box] if show\n"
             "] bind def\n"
             "\n/lshow [ % string lshow - show left-aligned\n"
             "   dup stringwidth pop neg 0 rmoveto bx [box] if show\n"
             "] bind def\n"
             "\n/rshow [ % string rshow - show right-aligned\n"
             "   bx [box] if show\n"
             "] bind def\n")

    fp.write(
        "\n/box [ % str box - draw box around string\n"
        "  gsave 0.5 setlinewidth dup stringwidth pop\n"
        "  -2 -2 rmoveto 4 add fh 4 add 2 copy\n"
        "  0 exch rlineto 0 rlineto neg 0 exch rlineto neg 0 rlineto\n"
        "  stroke grestore\n"
        "] bind def\n")

    fp.write(
        "\n/wd [ moveto bx [box] if show ] bind def\n"
        "/wln [\n"
        "dup 3 1 roll moveto gsave 0.6 setlinewidth lineto stroke grestore\n"
        "] bind def\n")

    fp.write(
        "/whf [moveto gsave 0.5 1.2 scale(-) show grestore] bind def\n")


def def_typeset(fp):
    fp.write(
        "\n/WS [ % w nspaces str WS\n"
        "   dup stringwidth pop 4 -1 roll\n"
        "   sub neg 3 -1 roll div 0 8#040 4 -1 roll\n"
        "   widthshow\n"
        "] bind def\n")

    fp.write(
        "\n/W1 [ show pop pop ] bind def\n")

    fp.write(
        "\n/str 50 string def\n"
        "/W0 [\n"
        "   dup stringwidth pop str cvs exch show(  ) show show pop pop\n"
        "] bind def\n")

    fp.write(
        "\n/WC [ counttomark 1 sub dup 0 eq [ 0 ]\n"
        "  [ ( ) stringwidth pop neg 0 3 -1 roll\n"
        "  [  dup 3 add index stringwidth pop( ) stringwidth pop add\n"
        "  dup 3 index add 4 index lt 2 index 1 lt or\n"
        "  [3 -1 roll add exch 1 add] [pop exit] ifelse\n"
        "  ] repeat ] ifelse\n"
        "] bind def\n")

    fp.write(
        "\n/P1 [\n"
        "  [  WC dup 0 le [exit] if\n"
        "      exch pop gsave [ exch show( ) show ] repeat grestore LF\n"
        "   ] loop pop pop pop pop\n"
        "] bind def\n")

    fp.write(
        "\n/P2 [\n"
        "   [  WC dup 0 le [exit] if\n"
        "      dup 1 sub dup 0 eq\n"
        "      [ pop exch pop 0.0 ]\n"
        "      [ 3 2 roll 3 index exch sub exch div ] ifelse\n"
        "      counttomark 3 sub 2 index eq [ pop 0 ] if exch gsave\n"
        "      [  3 2 roll show( ) show dup 0 rmoveto ] repeat\n"
        "      grestore LF pop\n"
        "   ] loop pop pop pop pop\n"
        "] bind def\n")


def define_font(fp, name, num):
    """

    :param file fp:
    :param str name:
    :param int num:
    """

    if name != "Symbol":
        fp.write(
            f'/F{num} [ 1 eq [/bx true def] [ /bx false def] ifelse\n'
            '  dup 0.72 mul  /fh exch def\n'
            f'  /{name} exch selectfont ] bind def\n')
        return

    fp.write(
        "\n/%s findfont\n"
        "dup length dict begin\n"
        "   [1 index /FID ne [def] [pop pop] ifelse] forall\n"
        "   /Encoding ISOLatin1Encoding def\n"
        "   currentdict\n"
        "end\n"
        "/%s-ISO exch definefont pop\n"
        % (name, name))

    fp.write(
        "/F%d [ 1 eq [/bx true def] [ /bx false def] ifelse\n"
        "  dup 0.72 mul  /fh exch def\n"
        "  /%s-ISO exch selectfont ] bind def\n"
        % (num, name))


def def_tsig(fp):
    fp.write(
        "\n/tsig [ % x(top) (bot) tsig -- draw time signature\n"
        "   3 -1 roll 0 moveto /bx false def\n"
        "   gsave /NewCenturySchlbk-Bold 16 selectfont\n"
        "   0 0.8 rmoveto currentpoint 3 -1 roll cshow\n"
        "   moveto 0 12 rmoveto cshow grestore\n"
        "] bind def\n"
        )
    fp.write(
        "\n/t1sig [ % x(top) t1sig - timesig without denominator\n"
        "   exch 4.5 moveto /bx false def\n"
        "   /NewCenturySchlbk-Bold 19 selectfont cshow\n"
        "] bind def\n"
        )


def _add_cv(fp, f1, f2, p, i0, ncv):
    """

    :param file fp:
    :param float f1:
    :param float f2:
    :param list p:
    :param int i0:
    :param int ncv:
    :return:
    """
    i1 = i0
    for m in range(ncv):
        fp.write(" ")
        for i in range(3):
            fp.write(" %.2f %.2f"
                     % (f1*(p[i1+i][0]-p[i1-1][0]),
                        f2*(p[i1+i][1]-p[i1-1][1])))
        fp.write(" rcurveto\n")
        i1 = i1+3


def _add_sg(fp, f1, f2, p, i0, nseg):
    """

    :param file fp:
    :param float f1:
    :param float f2:
    :param list p:
    :param int i0:
    :param int nseg:
    """
    for i in range(nseg):
        fp.write("  %.2f %.2f rlineto\n"
                 % (f1*(p[i0+i][0]-p[i0+i-1][0]),
                    f2*(p[i0+i][1]-p[i0+i-1][1])))


def _add_mv(fp, f1, f2, p, i0):
    """

    :param file fp:
    :param float f1:
    :param float f2:
    :param list p:
    :param int i0:
    """
    if i0 == 0:
        fp.write("  %.2f %.2f rmoveto\n"
                 % (f1*p[i0][0], f2*p[i0][1]))
    else:
        fp.write("  %.2f %.2f rmoveto\n"
                 % (f1*(p[i0][0]-p[i0-1][0]),
                    f2*(p[i0][1]-p[i0-1][1])))


# ----- def_stems -------
def def_stems(fp):
    fp.write(
        ("\n/su [ % len su - up stem\n"
         "  x y moveto %.1f %.1f rmoveto %.1f sub 0 exch rlineto stroke\n"
         "] bind def\n") % (STEM_XOFF,
                            STEM_YOFF,
                            STEM_YOFF))

    fp.write(
        ("\n/sd [ % len td - down stem\n"
         "  x y moveto %.1f %.1f rmoveto neg %.1f add 0 exch rlineto stroke\n"
         "] bind def\n") % (-STEM_XOFF,
                            -STEM_YOFF,
                            STEM_YOFF))


def def_dot(fp):
    fp.write(
        "\n/dt [ % dx dy dt - dot shifted by dx,dy\n"
        "  y add exch x add exch 1.2 0 360 arc fill\n"
        "] bind def\n")


def def_deco(fp):
    p = [[-10, -2], [0, 15], [1, -11], [10, 2], [0, -15], [-1, 11], [-10, -2]]

    # Walsh suggestion, scale 1.8 in y
    q = [[-13, 0], [-12, 9], [12, 9], [13, 0], [10, 7.4],
         [-10, 7.4], [-13, -0]]
    s = [[-8, -4.8], [-6, -5.5], [-3, -4.6], [0, 0], [-2.3, -5],
         [-6, -6.8], [-8.5, -6]]

    f1 = 0.5
    f2 = 0.5

    fp.write("\n/grm [ % x y grm - gracing mark\n"
             "  moveto\n")
    _add_mv(fp, f1, f2, p, 0)
    _add_cv(fp, f1, f2, p, 1, 2)
    fp.write("   fill\n] bind def\n")
    fp.write("\n/stc [ % x y stc - staccato mark\n"
             "  1.2 0 360 arc fill ] bind def\n")

    fp.write(
        "\n/hat [ % x y hat\n"
        "  moveto\n"
        "  -4 -2 rmoveto 4 6 rlineto currentpoint stroke moveto\n"
        "  4 -6 rlineto -2 0 rlineto -3 4.5 rlineto fill\n"
        " ] bind def\n")

    fp.write(
        "\n/att [ % x y att\n"
        "  moveto\n"
        "  -4 -3 rmoveto 8 3 rlineto -8 3 rlineto stroke\n"
        " ] bind def\n")

    f2 = f2*1.8

    # todo remove the true part of the if statement
    if temp_switch == 3:
        f1 = 0.8*f1
        f2 = 0.8*f2
    else:
        f1 = 0.9*f1
        f2 = 0.9*f2

    fp.write("\n/cpu [ % x y cpu - roll sign above head\n"
             "  moveto\n")
    _add_mv(fp, f1, f2, q, 0)
    _add_cv(fp, f1, f2, q, 1, 2)
    fp.write("   fill\n] bind def\n")

    for i in range(7):
        q[i][1] = -q[i][1]

    fp.write("\n/cpd [ % x y cpd - roll sign below head\n"
             "  moveto\n")
    _add_mv(fp, f1, f2, q, 0)
    _add_cv(fp, f1, f2, q, 1, 2)
    fp.write("   fill\n] bind def\n")

    f1 = 0.9
    f2 = 1.0
    fp.write(
        "\n/sld [ % y dx sld - slide\n"
        "  x exch sub exch moveto\n")
    _add_mv(fp, f1, f2, s, 0)
    _add_cv(fp, f1, f2, s, 1, 2)
    fp.write("   fill\n] bind def\n")

    fp.write(
        "\n/emb [ % x y emb - tenuto sign\n"
        "  gsave 1.4 setlinewidth 1 setlinecap\n"
        "  moveto -3.5 0 rmoveto 7 0 rlineto stroke grestore\n"
        "] bind def\n")

    fp.write(
        "\n/trl [ % x y trl - trill sign\n"
        "  gsave /Times-BoldItalic 14 selectfont\n"
        "  moveto(tr) cshow grestore\n"
        "] bind def\n")

    fp.write(
        "\n/sgno [ % x y sgno - segno\n"
        "  moveto gsave\n"
        "  0 3 rmoveto currentpoint currentpoint currentpoint\n"
        "  2.8 -0.54 2.89 1.18 1.39 1.63 rcurveto\n"
        "  -2.2 -0.9 -1.4 -3.15 2.76 -2.48 rcurveto\n"
        "  3.1 2.4 2.54 6.26 -7.71 13.5 rcurveto\n"
        "  0.5 3.6 3.6 3.24 5.4 2.5 rcurveto\n"
        "  -2.8 0.54 -2.89 -1.18 -1.39 -1.63 rcurveto\n"
        "  2.2 0.9 1.4 3.15 -2.76 2.48 rcurveto\n"
        "  -3.1 -2.4 -2.54 -6.26 7.71 -13.5 rcurveto\n"
        "  -0.5 -3.6 -3.6 -3.24 -5.4 -2.5 rcurveto\n"
        "  fill\n"
        "  moveto 0.6 setlinewidth -5.6 1.6 rmoveto 12.5 12.5 rlineto stroke\n"
        "  7.2 add exch -5.6 add exch 1 0 360 arc fill\n"
        "  8.4 add exch 7 add exch 1 0 360 arc fill grestore\n"
        "] bind def\n")

    fp.write(
        "\n/coda [ % x y coda - coda \n"
        "  gsave 1.2 setlinewidth 2 copy moveto 0 20 rlineto\n"
        "  2 copy 10 add exch -10 add exch moveto 20 0 rlineto stroke\n"
        "  10 add 6 0 360 arc 1.8 setlinewidth stroke grestore\n"
        "] bind def\n")

    fp.write(
        "\n/umrd [ % x y umrd - upper mordent\n"
        "  4 add moveto\n"
        "  2.2 2.2 rlineto 2.1 -2.9 rlineto 0.7 0.7 rlineto\n"
        "  -2.2 -2.2 rlineto -2.1 2.9 rlineto -0.7 -0.7 rlineto\n"
        "  -2.2 -2.2 rlineto -2.1 2.9 rlineto -0.7 -0.7 rlineto\n"
        "  2.2 2.2 rlineto 2.1 -2.9 rlineto 0.7 0.7 rlineto fill\n"
        "] bind def\n")

    fp.write(
        "\n/lmrd [ % x y lmrd - lower mordent\n"
        "  2 copy umrd 8 add moveto\n"
        "  0.6 setlinewidth 0 -8 rlineto stroke\n"
        "] bind def\n")

    fp.write(
        "\n/turn [ % x y turn - doppelschlag\n"
        "  moveto 5.2 8 rmoveto\n"
        "  1.4 -0.5 0.9 -4.8 -2.2 -2.8 rcurveto\n"
        "  -4.8 3.5 rlineto\n"
        "  -3.0 2.0 -5.8 -1.8 -3.6 -4.4 rcurveto\n"
        "  1.0 -1.1 2.0 -0.8 2.1 0.1 rcurveto\n"
        "  0.1 0.9 -0.7 1.2 -1.9 0.6 rcurveto\n"
        "  -1.4 0.5 -0.9 4.8 2.2 2.8 rcurveto\n"
        "  4.8 -3.5 rlineto\n"
        "  3.0 -2.0 5.8 1.8 3.6 4.4 rcurveto\n"
        "  -1.0 1.1 -2 0.8 -2.1 -0.1 rcurveto\n"
        "  -0.1 -0.9 0.7 -1.2 1.9 -0.6 rcurveto\n"
        "  fill\n"
        "] bind def\n")

    fp.write(
        "\n/wedge [ % x y wedge \n"
        "  moveto 1.4 7 rlineto\n"
        "  -0.8 2 -1.2 2 -2.8 0 rcurveto\n"
        "  1.4 -7 rlineto fill\n"
        "] bind def\n")

    fp.write(
        "\n/plus [ % x y plus - plus sign\n"
        "  1 add moveto gsave 1 setlinewidth\n"
        "  0 10 rlineto currentpoint stroke moveto\n"
        "  -5 -5 rmoveto 10 0 rlineto stroke grestore\n"
        "] bind def\n")

    fp.write(
        "\n/cross [ % x y cross - x shaped cross\n"
        "  gsave 1.2 setlinewidth 1 setlinecap\n"
        "  moveto -3 1 rmoveto 6 8 rlineto currentpoint stroke moveto\n"
        "  0 -8 rmoveto -6 8 rlineto stroke grestore\n"
        "] bind def\n")

    fp.write(
        "\n/dyn [ %(s) x y cross - dynamic mark s\n"
        "  /Times-BoldItalic 16 selectfont 5 add moveto cshow\n"
        "] bind def\n")


def def_deco1(fp):
    # for hold sign
    p = [[-15, 0], [-15, 23], [15, 23], [15, 0],
         [14.5, 0], [12, 18], [-12, 18], [-14.5, 0]]
    # for down bow sign
    q = [[-4, 0], [-4, 9], [4, 9], [4, 0],
         [-4, 6], [-4, 9], [4, 9], [4, 6]]
    # for up bow sign
    r = [[-3.2, 11], [0, 0], [3.2, 11]]

    f1 = 0.5
    f2 = 0.5
    fp.write("\n/hld [ % x y hld - hold sign\n"
             "  2 copy moveto 2 copy 1.5 add 1.3 0 360 arc moveto\n")
    _add_mv(fp, f1, f2, p, 0)
    _add_cv(fp, f1, f2, p, 1, 1)
    _add_sg(fp, f1, f2, p, 4, 1)
    _add_cv(fp, f1, f2, p, 5, 1)
    fp.write("   fill\n] bind def\n")

    f1 = 0.8
    f2 = 0.8
    fp.write("\n/dnb [ % x y dnb - down bow\n"
             "  moveto\n")
    _add_mv(fp, f1, f2, q, 0)
    _add_sg(fp, f1, f2, q, 1, 3)
    fp.write("   currentpoint stroke moveto\n")
    _add_mv(fp, f1, f2, q, 4)
    _add_sg(fp, f1, f2, q, 5, 3)
    fp.write("   fill\n] bind def\n")

    fp.write(
        "\n/upb [ % x y upb - up bow\n"
        "  moveto\n")
    _add_mv(fp, f1, f2, r, 0)
    _add_sg(fp, f1, f2, r, 1, 2)
    fp.write("   stroke\n] bind def\n")

    fp.write(
        "\n/brth [ % x y brth - breath mark\n"
        "  gsave 0.8 setlinewidth\n"
        "  moveto -1 -3 rmoveto 2 7 rlineto stroke grestore\n"
        "] bind def\n")


def def_hl(fp):
    fp.write(
        "\n/hl [ % y hl - ledger line at height y\n"
        "   gsave 1 setlinewidth x exch moveto \n"
        "   -5.5 0 rmoveto 11 0 rlineto stroke grestore\n"
        "] bind def\n")

    fp.write(
        "\n/hl1 [ % y hl1 - longer ledger line for whole notes\n"
        "   gsave 1 setlinewidth x exch moveto \n"
        "   -7 0 rmoveto 14 0 rlineto stroke grestore\n"
        "] bind def\n")

    fp.write(
        "\n/hl2 [ % y hl2 - longer ledger line for brevis\n"
        "   gsave 1 setlinewidth x exch moveto \n"
        "   -8 0 rmoveto 16 0 rlineto stroke grestore\n"
        "] bind def\n")


def def_beam(fp):
    fp.write(
        "\n/bm [ % x1 y1 x2 y2 t bm - beam, depth t\n"
        "  3 1 roll moveto dup 0 exch neg rlineto\n"
        "  dup 4 1 roll sub lineto 0 exch rlineto fill\n"
        "] bind def\n")

    fp.write(
        "\n/bnum [ % x y(str) bnum - number on beam\n"
        "  3 1 roll moveto gsave /Times-Italic 12 selectfont\n"
        "  /bx false def cshow grestore\n"
        "] bind def\n")

    fp.write(
        "\n/hbr [ % x1 y1 x2 y2 hbr - half bracket\n"
        "  moveto lineto 0 -3 rlineto stroke\n"
        "] bind def\n")

    fp.write(
        "\n/fbr [ % x1 y1 x2 y2 fbr - full bracket\n"
        "  moveto currentpoint 4 2 roll lineto 0 -3 rlineto\n"
        "  moveto 0 -3 rlineto stroke\n"
        "] bind def\n")


def def_flags1(fp):
    p = [[0.0, 0.0], [1.5, -3.0], [1.0, -2.5], [4.0, -6.0], [9.0, -10.0],
         [9.0, -16.0], [8.0, -20.0], [7.0, -24.0], [4.0, -26.0],
         [6.5, -21.5], [9.0, -15.0], [4.0, -9.0], [0.0, -8.0]]

    f1 = 6.0/9.0
    f2 = 6.0/9.0
    fp.write(
        "\n/f1u [ % len f1u - single flag up\n"
        f"  y add x {STEM_XOFF:.1f} add exch moveto\n")
    _add_mv(fp, f1, f2, p, 0)
    _add_cv(fp, f1, f2, p, 1, 4)
    fp.write("   fill\n] bind def\n")

    f1 *= 1.2
    for i in range(13):
        p[i][1] = -p[i][1]
    fp.write("\n/f1d [ % len f1d - single flag down\n"
             f"  neg y add x {STEM_XOFF:.1f} sub exch moveto\n")
    _add_mv(fp, f1, f2, p, 0)
    _add_cv(fp, f1, f2, p, 1, 4)
    fp.write("   fill\n] bind def\n")


def def_flags2(fp):
    p = [[0.0, 0.0],
         [2.0, -5.0], [9.0, -6.0], [7.5, -18.0],
         [7.5, -9.0], [1.5, -6.5], [0.0, -6.5],
         [2.0, -14.0], [9.0, -14.0], [7.5, -26.0],
         [7.5, -17.0], [1.5, -14.5], [0.0, -14.0]]

    # up flags
    f1 = 6.0 / 9.0
    f2 = 6.0 / 9.0
    fp.write("\n/f2u [ % len f2u - double flag up\n"
             f"  y add x {STEM_XOFF:.1f} add exch moveto\n")
    _add_mv(fp, f1, f2, p, 0)
    _add_cv(fp, f1, f2, p, 1, 4)
    fp.write("   fill\n] bind def\n")

    # down flags
    f1 = 1.2*f1
    for i in range(13):
        p[i][1] = -p[i][1]
    fp.write("\n/f2d [ % len f2d - double flag down\n"
             f"  neg y add x  {STEM_XOFF:.1f} sub exch moveto\n")
    _add_mv(fp, f1, f2, p, 0)
    _add_cv(fp, f1, f2, p, 1, 4)
    fp.write("   fill\n] bind def\n")


def def_xflags(fp):

    p = [[0.0, 0.0],
         [2.0, -7.5], [9.0, -7.5], [7.5, -19.5],
         [7.5, -10.5], [1.5, -8.0], [0.0, -7.5]]
    # extra up flag
    f1 = 6.0 / 9.0
    f2 = 6.0 / 9.0
    fp.write(
        "\n/xfu [ % len xfu - extra flag up\n"
        f"  y add x {STEM_XOFF:.1f} add exch moveto\n")
    _add_mv(fp, f1, f2, p, 0)
    _add_cv(fp, f1, f2, p, 1, 2)
    fp.write("   fill\n] bind def\n")

    # extra down flag
    f1 = 1.2*f1
    for i in range(7):
        p[i][1] = -p[i][1]
    fp.write("\n/xfd [ % len xfd - extra flag down\n"
             f"  neg y add x {STEM_XOFF:.1f} sub exch moveto\n")
    _add_mv(fp, f1, f2, p, 0)
    _add_cv(fp, f1, f2, p, 1, 2)
    fp.write("   fill\n] bind def\n")

    fp.write("\n/f3d [dup f2d 9.5 sub xfd] bind def\n")

    fp.write("\n/f4d [dup dup f2d 9.5 sub xfd 14.7 sub xfd] bind def\n")

    fp.write("\n/f3u [dup f2u 9.5 sub xfu] bind def\n")

    fp.write("\n/f4u [dup dup f2u 9.5 sub xfu 14.7 sub xfu] bind def\n")


def curve(fp, f1, f2, r):
    _add_mv(fp, f1, f2, r, 0)
    _add_sg(fp, f1, f2, r, 1, 4)
    _add_mv(fp, f1, f2, r, 5)
    _add_sg(fp, f1, f2, r, 6, 4)
    fp.write("  currentpoint fill moveto\n")
    _add_mv(fp, f1, f2, r, 10)
    _add_sg(fp, f1, f2, r, 11, 1)
    fp.write("  currentpoint stroke moveto\n")
    _add_mv(fp, f1, f2, r, 12)
    _add_sg(fp, f1, f2, r, 13, 1)
    fp.write("  stroke\n ] bind def\n")


def def_acc(fp):
    p = [[-2, 3], [6, 6.5], [6, -1], [-2, -4.5], [4, 0],
         [4, 4], [-2, 2], [-2, 10], [-2, -4]]
    q = [[4, 4], [4, 7], [-4, 5], [-4, 2], [4, 4], [4, -5],
         [4, -2], [-4, -4], [-4, -7], [4, -5],
         [2, -10], [2, 11.5], [-2, -11.5], [-2, 10]]
    r = [[-2.5, -6], [2.5, -5], [2.5, -2], [-2.5, -3], [-2.5, 6],
         [-2.5, 2], [2.5, 3], [2.5, 6], [-2.5, 5], [-2.5, 2],
         [-2.5, 11], [-2.5, -5.5],
         [2.5, 5.5], [2.5, -11]]
    s = [[0.7, 0], [3.9, 3], [6, 3], [6.2, 6.2], [3, 6], [3, 3.9],
         [0, 0.7], [-3, 3.9], [-3, 6], [-6.2, 6.2], [-6, 3], [-3.9, 3],
         [0, -0.7], [3, -3.9], [3, -6], [6.2, -6.2], [6, -3], [3.9, -3],
         [0.7, 0]]

    f2 = 8.0/9.0
    f1 = f2*0.9
    fp.write(
        '\n/ft0 [ % x y ft0 - flat sign\n'
        '  moveto\n')
    _add_mv(fp, f1, f2, p, 0)
    _add_cv(fp, f1, f2, p, 1, 2)
    fp.write("  currentpoint fill moveto\n")
    _add_mv(fp, f1, f2, p, 7)
    _add_sg(fp, f1, f2, p, 8, 1)
    fp.write("  stroke\n ] bind def\n")
    fp.write(
        "/ft [ % dx ft - flat relative to head\n"
        " neg x add y ft0 ] bind def\n")

    f2 = 8.0/9.0   # more narrow flat sign for double flat
    f1 = f2*0.8
    fp.write("\n/ftx [ % x y ftx - narrow flat sign\n"
             "  moveto\n")
    _add_mv(fp, f1, f2, p, 0)
    _add_cv(fp, f1, f2, p, 1, 2)
    fp.write("  currentpoint fill moveto\n")
    _add_mv(fp, f1, f2, p, 7)
    _add_sg(fp, f1, f2, p, 8, 1)
    fp.write("  stroke\n ] bind def\n")

    fp.write("/dft0 [ % x y dft0 ft - double flat sign\n"
             "  2 copy exch 2.5 sub exch ftx exch 1.5 "
             "add exch ftx ] bind def\n"
             "/dft [ % dx dft - double flat relative to head\n"
             "  neg x add y dft0 ] bind def\n")

    f2 = 6.5/9.0
    f1 = f2*0.9
    fp.write("\n/sh0 [ % x y sh0 - sharp sign\n"
             "  moveto\n")

    curve(fp, f1, f2, q)

    fp.write("/sh [ % dx sh - sharp relative to head\n"
             " neg x add y sh0 ] bind def\n")
    fp.write("/sh1 [ % sh1 - sharp inline at currentpos\n"
             "  currentpoint\n"
             "  currentpoint moveto 3.5 4.6 rmoveto gsave 0.75 0.75 "
             "scale currentpoint sh0 grestore\n"
             "  moveto 7 0 rmoveto\n"
             "] bind def\n"
             "/ft1 [ % ft1 - flat inline at currentpos\n"
             "  currentpoint\n"
             "  currentpoint moveto 3.7 3.1 rmoveto gsave 0.75 0.75 "
             "scale currentpoint ft0 grestore\n"
             "  moveto 7 0 rmoveto\n"
             "] bind def\n"
             "/nt1 [ % nt1 - natural inline at currentpos\n"
             "  currentpoint\n"
             "  currentpoint moveto 4 4 rmoveto gsave 0.75 0.75 scale "
             "currentpoint nt0 grestore\n"
             "  moveto 7 0 rmoveto\n"
             "] bind def\n")

    f2 = 6.5/9.0
    f1 = f2*0.9
    fp.write(
        "\n/nt0 [ % x y nt0 - neutral sign\n"
        "  moveto\n")

    curve(fp, f1, f2, r)

    fp.write("  stroke\n ] bind def\n")
    fp.write("/nt [ % dx nt - neutral relative to head\n"
             " neg x add y nt0 ] bind def\n")

    f1 = 5.0/9.0
    f2 = f1
    fp.write("\n/dsh0 [ % x y dsh0 - double sharp \n"
             "  moveto\n")
    _add_mv(fp, f1, f2, s, 0)
    _add_sg(fp, f1, f2, s, 1, 24)
    fp.write("  fill\n ] bind def\n")
    fp.write("/dsh [ % dx dsh - double sharp relative to head\n"
             " neg x add y dsh0 ] bind def\n")


def def_rests(fp):
    p = [[-1, 17], [15, 4], [-6, 8], [6.5, -5], [-2, -2], [-5, -11], [1, -15],
         [-9, -11], [-6, 0], [1, -1], [-9, 7], [7, 5], [-1, 17]]
    q = [[8, 14], [5, 9], [3, 5], [-1.5, 4],
         [4, 11], [-9, 14], [-9, 7],
         [-9, 4], [-6, 2], [-3, 2],
         [4, 2], [5, 7], [7, 11],
         [-1.8, -20], [-0.5, -20], [8.5, 14]]
    r = [[8, 14], [5, 9], [3, 5], [-1.5, 4],
         [4, 11], [-9, 14], [-9, 7],
         [-9, 4], [-6, 2], [-3, 2],
         [4, 2], [5, 7], [7, 11],
         [8, 14], [5, 9], [3, 5], [-1.5, 4],
         [4, 11], [-9, 14], [-9, 7],
         [-9, 4], [-6, 2], [-3, 2],
         [4, 2], [5, 7], [7.3, 11],
         [-1.8, -21], [-0.5, -21], [8.5, 14]]

    fp.write(
        "\n/r4 [ % x y r4 - quarter rest\n"
        "   dup /y exch def exch dup /x exch def exch moveto\n")
    f1 = f2 = 6.0/11.5
    _add_mv(fp, f1, f2, p, 0)
    _add_cv(fp, f1, f2, p, 1, 4)
    fp.write("  fill\n ] bind def\n")

    fp.write("\n/r8 [ % x y r8 - eighth rest\n"
             "   dup /y exch def exch dup /x exch def exch moveto\n")
    f1 = f2 = 7/18.0
    _add_mv(fp, f1, f2, q, 0)
    _add_cv(fp, f1, f2, q, 1, 4)
    _add_sg(fp, f1, f2, q, 13, 3)
    fp.write("  fill\n ] bind def\n")

    for i in range(13, 26):
        r[i][0] -= 4.2
        r[i][1] -= 14
    fp.write("\n/r16 [ % x y r16 - 16th rest\n"
             "   dup /y exch def exch dup /x exch def exch moveto\n")
    f1 = f2 = 7/18.0
    _add_mv(fp, f1, f2, r, 0)
    _add_cv(fp, f1, f2, r, 1, 4)
    _add_sg(fp, f1, f2, r, 13, 1)
    _add_cv(fp, f1, f2, r, 14, 4)
    _add_sg(fp, f1, f2, r, 26, 3)
    fp.write("  fill\n ] bind def\n")

    fp.write(
        "\n/r00 [ % x y r00 - longa rest\n"
        "  2 copy /y exch def /x exch def moveto\n"
        "  -1 6 rmoveto 0 -12 rlineto 3 0 rlineto 0 12 rlineto fill\n"
        "] bind def\n")

    fp.write(
        "\n/r0 [ %	x y r0	-  brevis rest\n"
        "  6 add dup /y exch def exch dup /x exch def exch moveto\n"
        "  -1 0 rmoveto 0 -6 rlineto 3 0 rlineto 0 6 rlineto fill\n"
        "] bind def\n")

    fp.write(
        "\n/r1 [ % x y r1 - whole rest\n"
        "  dup /y exch def exch dup /x exch def exch moveto\n"
        "  -3 6 rmoveto 0 -3 rlineto 6 0 rlineto 0 3 rlineto fill\n"
        "] bind def\n")

    fp.write(
        "\n/r2 [ % x y r2 - half rest\n"
        "  dup /y exch def exch dup /x exch def exch moveto\n"
        "  -3 0 rmoveto 0 3 rlineto 6 0 rlineto 0 -3 rlineto fill\n"
        "] bind def\n")

    # get 32nd, 64th rest by overwriting 8th and 16th rests
    fp.write(
        "\n/r32 [\n"
        "2 copy r16 5.5 add exch 1.6 add exch r8\n"
        "] bind def\n")
    fp.write(
        "\n/r64 [\n"
        "2 copy 5.5 add exch 1.6 add exch r16\n"
        "5.5 sub exch 1.5 sub exch r16\n"
        "] bind def\n")

    fp.write(
        "\n/brest [ % nb_measures x y brest\n"
        "   gsave T 0.8 setlinewidth\n"
        "   0 -6 moveto 0 12 rlineto 40 -6 moveto 0 12 rlineto stroke\n"
        "   3 setlinewidth 0 0 moveto 40 0 rlineto stroke\n"
        "   /Times-Bold 13 selectfont 20 16 moveto cshow grestore\n"
        "] bind def \n")


def def_bars(fp):
    fp.write(
        "\n/bar [ % x bar - single bar\n"
        "  0 moveto  0 24 rlineto stroke\n"
        "] bind def\n"

        "\n/dbar [ % x dbar - thin double bar\n"
        "   0 moveto 0 24 rlineto -3 -24 rmoveto\n"
        "   0 24 rlineto stroke\n"
        "] bind def\n"

        "\n/fbar1 [ % x fbar1 - fat double bar at start\n"
        "  0 moveto  0 24 rlineto 3 0 rlineto 0 -24 rlineto \n"
        "  currentpoint fill moveto\n"
        "  3 0 rmoveto 0 24 rlineto stroke\n"
        "] bind def\n"

        "\n/fbar2 [ % x fbar2 - fat double bar at end\n"
        "  0 moveto  0 24 rlineto -3 0 rlineto 0 -24 rlineto \n"
        "  currentpoint fill moveto\n"
        "  -3 0 rmoveto 0 24 rlineto stroke\n"
        "] bind def\n"

        "\n/rdots [ % x rdots - repeat dots \n"
        "  0 moveto 0 9 rmoveto currentpoint 2 copy 1.2 0 360 arc \n"
        "  moveto 0 6 rmoveto  currentpoint 1.2 0 360 arc fill\n"
        "] bind def\n")


def def_ends(fp):
    # use dy=6 for smaller boxes
    dy = 12

    fp.write(
        '\n/end1 [ % x1 x2 h(str) end1 - mark first ending\n'
        f'  4 1 roll -{dy} add dup 3 1 roll moveto 0 {dy} rlineto 2 copy {dy} '
        f'add lineto 0 -{dy} rlineto stroke\n'
        f'  moveto 4 {dy-10} rmoveto gsave /Times-Roman 13 selectfont '
        f'1.2 0.95 scale\n'
        '  show grestore\n'
        '] bind def\n')

    fp.write(
        '\n/end2 [ % x1 x2 h(str) end2 - mark second ending\n'
        f'  4 1 roll dup 3 1 roll moveto 2 copy lineto '
        f'0 -{dy} rlineto stroke\n'
        '  moveto 4 -10 rmoveto gsave /Times-Roman 13 selectfont '
        '1.2 0.95 scale\n'
        '  show grestore\n'
        '] bind def\n' % dy)


def def_gchord(fp):
    fp.write('\n')


def def_sl(fp):
    fp.write(
        "\n/SL [ % pp2x pp1x p1 pp1 pp2 p2 p1 sl\n"
        "  moveto curveto rlineto curveto fill\n"
        "] bind def\n")


def def_hd1(fp):
    p = [[8.0, 0.0], [8.0, 8.0], [-8.0, 8.0], [-8.0, 0.0], [-8.0, -8.0],
         [8.0, -8.0], [8.0, 0.0]]

    c = 0.825
    s = 0.565

    for i in range(7):
        xx = c*p[i][0] - s*p[i][1]
        yy = s*p[i][0] + c*p[i][1]
        p[i][0] = xx
        p[i][1] = yy

    f1 = f2 = 6.0/12.0
    fp.write("\n/hd [ % x y hd - full head\n"
             "  dup /y exch def exch dup /x exch def exch moveto\n")
    _add_mv(fp, f1, f2, p, 0)
    _add_cv(fp, f1, f2, p, 1, 2)
    fp.write("   fill\n] bind def\n")


def def_hd2(fp):
    p = [[8.0, 0.0], [8.0, 8.5], [-8.0, 8.5], [-8.0, 0.0], [-8.0, -8.5],
         [8.0, -8.5], [8.0, 0.0], [7.0, 0.0], [7.0, -4.0], [-7.0, -4.0],
         [-7.0, 0.0], [-7.0, 4.0], [7.0, 4.0], [7.0, 0.0]]

    c = 0.878
    s = 0.479

    for i in range(14):
        xx = c*p[i][0] - s*p[i][1]
        yy = s*p[i][0] + c*p[i][1]
        p[i][0] = xx
        p[i][1] = yy

    f1 = f2 = 6.0/12.0
    fp.write("\n/Hd [ % x y Hd - open head for half\n"
             "  dup /y exch def exch dup /x exch def exch moveto\n")
    _add_mv(fp, f1, f2, p, 0)
    _add_cv(fp, f1, f2, p, 1, 2)
    _add_mv(fp, f1, f2, p, 7)
    _add_cv(fp, f1, f2, p, 8, 2)
    fp.write("   fill\n] bind def\n")


def def_hd3(fp):
    p = [[11.0, 0.0], [11.0, 2.0], [6.0, 6.5], [0.0, 6.5], [-6.0, 6.5],
         [-11.0, 2.0], [-11.0, 0.0], [-11.0, -2.0], [-6.0, -6.5],
         [0.0, -6.5], [6.0, -6.5], [11.0, -2.0], [11.0, 0.0]]

    q = [[11.0, 0.0], [5.0, 0.0], [5.0, -5.0], [-5.0, -5.0], [-5.0, 0.0],
         [-5.0, 5.0], [5.0, 5.0], [5.0, 0.0]]

    c = -0.801
    s = 0.598

    for i in range(1, 8):
        xx = c*q[i][0] - s*q[i][1]
        yy = s*q[i][0] + c*q[i][1]
        q[i][0] = xx
        q[i][1] = yy

    f1 = f2 = 6.5/12.0
    fp.write("\n/HD [ % x y HD - open head for whole\n"
             "  dup /y exch def exch dup /x exch def exch moveto\n")
    _add_mv(fp, f1, f2, p, 0)
    _add_cv(fp, f1, f2, p, 1, 4)
    _add_mv(fp, f1, f2, q, 1)
    _add_cv(fp, f1, f2, q, 2, 2)
    fp.write("   fill\n] bind def\n")

    # brevis(round and square) and longa
    fp.write(
        "\n/HDD [ % x y HDD - double note\n"
        "  HD\n"
        "  x y moveto -6 -4 rmoveto 0 8 rlineto stroke\n"
        "  x y moveto 6 -4 rmoveto 0 8 rlineto stroke\n"
        "] bind def\n")
    fp.write(
        "\n/brevis [ % x y brevis - square brevis\n"
        "  2 copy /y exch def /x exch def moveto\n"
        "  2.5 setlinewidth -6 -2.7 rmoveto 12 0 rlineto\n"
        "  0 5.4 rmoveto -12 0 rlineto stroke\n"
        "  0.8 setlinewidth x y moveto -6 -5 rmoveto 0 10 rlineto\n"
        "  x y moveto 6 -5 rmoveto 0 10 rlineto stroke\n"
        "] bind def\n")
    fp.write(
        "\n/longa [ % x y longa\n"
        "  brevis x y moveto 6 -10 rmoveto 0 15 rlineto stroke\n"
        "] bind def\n")


def def_historic(fp):
    # diamond shaped heads
    fp.write(
        "\n/hdh [ % x y hdh - full head(historic)\n"
        "  dup /y exch def exch dup /x exch def exch\n"
        "  moveto 0 -3.5 rmoveto\n"
        "  3.5 3.5 rlineto -3.5 3.5 rlineto -3.5 -3.5 rlineto "
        "3.5 -3.5 rlineto fill\n"
        "] bind def\n")

    fp.write(
        "\n/Hdh [ % x y Hdh - open head(historic)\n"
        "  dup /y exch def exch dup /x exch def exch\n"
        "  gsave 1 setlinewidth\n"
        "  moveto 0 -4.0 rmoveto\n"
        "  4.0 4.0 rlineto currentpoint\n"
        "  -0.4 0.4 rlineto -4.0 -4.0 rlineto 0.4 -0.4 rlineto fill moveto\n"
        "  -4.0 4.0 rlineto currentpoint\n"
        "  -1.1 -1.1 rlineto 4.0 -4.0 rlineto 1.1 1.1 rlineto fill moveto\n"
        "  -4.0 -4.0 rlineto currentpoint\n"
        "  0.4 -0.4 rlineto 4.0 4.0 rlineto -0.4 0.4 rlineto fill moveto\n"
        "  4.0 -4.0 rlineto currentpoint\n"
        "  1.1 1.1 rlineto -4.0 4.0 rlineto -1.1 -1.1 rlineto fill moveto\n"
        "  grestore\n"
        "] bind def\n")

    # stems and flags
    fp.write(
        "\n/suh [ % len su - up stem(historic)\n"
        "  gsave 1 setlinewidth\n"
        "  x y moveto 0 3.5 rmoveto 1.0 sub 0 exch rlineto stroke\n"
        "  grestore\n"
        "] bind def\n"
        "\n"
        "/sdh [ % len sd - down stem(historic)\n"
        "  gsave 1 setlinewidth\n"
        "  x y moveto 0 -3.5 rmoveto neg 1.0 add 0 exch rlineto stroke\n"
        "  grestore\n"
        "] bind def\n")

    fp.write(
        "\n/f1uh [ % len f1uh - single flag up(historic)\n"
        "  2.5 add y add x exch moveto\n"
        "  7.0 1.0 4.5 -5.0 0.0 -9.0 rcurveto 0 1 rlineto\n"
        "  3.0 3.5 5.0 6.0 0.0 6.0 rcurveto closepath\n"
        "  fill\n"
        "] bind def\n"
        "\n"
        "/f1dh [ % len f1dh - single flag down(historic)\n"
        "  2.5 add neg y add x exch moveto\n"
        "  -7.0 -1.0 -4.5 5.0 0.0 9.0 rcurveto 0 -1 rlineto\n"
        "  -3.0 -3.5 -5.0 -6.0 0.0 -6.0 rcurveto closepath\n"
        "  fill\n"
        "] bind def\n")

    fp.write(
        "\n/f2uh [ % len f2uh - double flag up(historic)\n"
        "  2.5 add y add x exch moveto\n"
        "  7.0 1.0 4.5 -5.0 0.0 -9.0 rcurveto 0 1 rlineto\n"
        "  3.0 3.5 5.0 6.0 0.0 6.0 rcurveto closepath\n"
        "  currentpoint fill gsave moveto\n"
        "  1 setlinewidth 0 -7 rmoveto 5.0 -6.5 rlineto stroke grestore\n"
        "] bind def\n"
        "\n"
        "/f2dh [ % len f2d - double flag down(historic)\n"
        "  2.5 add neg y add x exch moveto\n"
        "  -7.0 -1.0 -4.5 5.0 0.0 9.0 rcurveto 0 -1 rlineto\n"
        "  -3.0 -3.5 -5.0 -6.0 0.0 -6.0 rcurveto closepath\n"
        "  currentpoint fill gsave moveto\n"
        "  1 setlinewidth 0 7 rmoveto -5.0 6.5 rlineto stroke grestore\n"
        "] bind def\n")

    fp.write("\n/f4dh [f3dh] bind def % unsupported\n")

    # brevis and longa
    fp.write(
        "\n/brevish [ % x y brevish - brevis(historic)\n"
        "  2 copy /y exch def /x exch def moveto\n"
        "  1.8 setlinewidth -4 -2.5 rmoveto 8 0 rlineto\n"
        "  0 5.0 rmoveto -8 0 rlineto stroke\n"
        "  0.8 setlinewidth x y moveto -4 -4.8 rmoveto 0 9.6 rlineto\n"
        "  x y moveto 4 -4.8 rmoveto 0 9.6 rlineto stroke\n"
        "] bind def\n")

    fp.write(
        "\n/longah [ % x y longah - longa(historic)\n"
        "  brevish x y moveto 4 -2.5 rmoveto 0 -10 rlineto stroke\n"
        "] bind def\n")

    # time signatures
    r2 = 5.0   # outer radius*/
    arc1 = 35.0   # inner border angle*/
    thick = 1.2   # line thickness*/
    r1 = r2 - thick   # inner radius*/
    arc2 = math.pi * 180.0 * math.acos(math.cos(math.pi/180.0) * r1 / r2)
    fp.write(
        '\n/csigh [ % x csigh - C timesig(historic)\n'
        f'  newpath dup 12 {r2:.1f} {arc2:.1f} -{arc2:.1f} arc 12 '
        f'{r1:.1f} -{arc1:.1f} {arc1:.1f} arcn closepath fill\n'
        '] bind def\n')

    fp.write(
        "\n/ctsigh [ % x ctsigh - C| timesig historic\n"
        "  dup csigh 3 moveto 0 18 rlineto stroke\n"
        "] bind def\n")


def def_gnote(fp):
    # parameter for filled head
    p = [[0, 10], [16, 10], [16, -10], [0, -10],
         [-16, -10], [-16, 10], [0, 10]]

    # parameter for half note head
    ph = [[8.0, 0.0], [8.0, 8.5], [-8.0, 8.5], [-8.0, 0.0], [-8.0, -8.5],
          [8.0, -8.5], [8.0, 0.0], [7.0, 0.0], [7.0, -4.0], [-7.0, -4.0],
          [-7.0, 0.0], [-7.0, 4.0], [7.0, 4.0], [7.0, 0.0]]

    # parameter for whole note head
    pw = [[11.0, 0.0], [11.0, 2.0], [6.0, 6.5], [0.0, 6.5], [-6.0, 6.5],
          [-11.0, 2.0], [-11.0, 0.0], [-11.0, -2.0], [-6.0, -6.5],
          [0.0, -6.5], [6.0, -6.5], [11.0, -2.0], [11.0, 0.0]]

    qw = [[11.0, 0.0], [5.0, 0.0], [5.0, -5.0], [-5.0, -5.0], [-5.0, 0.0],
          [-5.0, 5.0], [5.0, 5.0], [5.0, 0.0]]

    c = 0.765
    s = 0.644
    for i in range(7):
        xx = c*p[i][0] - s*p[i][1]
        yy = s*p[i][0] + c*p[i][1]
        p[i][0] = xx
        p[i][1] = yy

    for i in range(14):
        xx = c*ph[i][0] - s*ph[i][1]
        yy = s*ph[i][0] + c*ph[i][1]
        ph[i][0] = xx
        ph[i][1] = yy

    c = -0.801
    s = 0.598
    for i in range(1, 8):
        xx = c*qw[i][0] - s*qw[i][1]
        yy = s*qw[i][0] + c*qw[i][1]
        qw[i][0] = xx
        qw[i][1] = yy

    f1 = f2 = 2./10.0

    fp.write(
        "\n/gn16 [ % x y l gn16 - single sixteenth grace note\n"
        "  3 1 roll 2 copy moveto\n")
    _add_mv(fp, f1, f2, p, 0)
    _add_cv(fp, f1, f2, p, 1, 2)
    fp.write(
        f'  fill moveto {GSTEM_XOFF:.2f} 0 rmoveto 0 exch rlineto '
        f'currentpoint\n'
        '  3 -4 4 -5 3 -8 rcurveto -5 2 rmoveto stroke\n'
        '  3.4 sub moveto\n'
        '  3 -4 4 -5 2 -8 rcurveto -5 2 rmoveto stroke\n')
    fp.write("] bind def\n")

    fp.write(
        "\n/gn8 [ % x y l gn8 - single eighth grace note\n"
        "  3 1 roll 2 copy moveto\n")
    _add_mv(fp, f1, f2, p, 0)
    _add_cv(fp, f1, f2, p, 1, 2)
    fp.write(
        f'  fill moveto {GSTEM_XOFF:.2f} 0 rmoveto 0 exch rlineto\n'
        '3 -4 4 -5 2 -8 rcurveto -5 2 rmoveto\n'
        'stroke\n')
    fp.write("] bind def\n")

    fp.write(
        "\n/gn8s [ % x y l gn8s - single eighth grace note with stroke\n"
        "  3 1 roll 2 copy moveto\n")
    _add_mv(fp, f1, f2, p, 0)
    _add_cv(fp, f1, f2, p, 1, 2)
    fp.write(
        f'  fill moveto {GSTEM_XOFF:.2f} 0 rmoveto 0 exch rlineto\n'
        '3 -4 4 -5 2 -8 rcurveto -5 2 rmoveto 7 4 rlineto\n'
        'stroke\n')
    fp.write('] bind def\n')

    fp.write(
        '\n/gnt [ % x y l gnt - grace note without flag\n'
        '  3 1 roll 2 copy moveto\n')
    _add_mv(fp, f1, f2, p, 0)
    _add_cv(fp, f1, f2, p, 1, 2)
    fp.write(
        f'  fill moveto {GSTEM_XOFF:.2f} 0 rmoveto 0 exch '
        f'rlineto stroke\n')
    fp.write("] bind def\n")

    fp.write(
        "\n/gn2 [ % x y l gn2 - grace half note\n"
        "  3 1 roll 2 copy moveto\n")
    fh = 8.0/25.0
    _add_mv(fp, fh, fh, ph, 0)
    _add_cv(fp, fh, fh, ph, 1, 2)
    _add_mv(fp, fh, fh, ph, 7)
    _add_cv(fp, fh, fh, ph, 8, 2)
    fp.write(f"  fill moveto {GSTEM_XOFF:.2f} 0 rmoveto 0 "
             f"exch rlineto stroke\n")
    fp.write("] bind def\n")

    fp.write(
        "\n/gn1 [ % x y gn1 - whole grace note\n"
        "  2 copy moveto\n")
    fw = 9.0/25.0
    _add_mv(fp, fw, fw, pw, 0)
    _add_cv(fp, fw, fw, pw, 1, 4)
    _add_mv(fp, fw, fw, qw, 1)
    _add_cv(fp, fw, fw, qw, 2, 2)
    fp.write("  fill\n")
    fp.write("] bind def\n")

    fp.write(
        "\n/gbm1 [ % x1 y1 x2 y2 gbm1 - single note beam\n"
        "  gsave 1.4 setlinewidth\n"
        "  0.5 sub moveto 0.5 sub lineto stroke grestore\n"
        "] bind def\n")

    fp.write(
        "\n/gbm2 [ % x1 y1 x2 y2 gbm2 - double note beam\n"
        "  gsave 1.4 setlinewidth\n"
        "  4 copy 0.5 sub moveto 0.5 sub lineto stroke\n"
        "  3.4 sub moveto 3.4 sub lineto stroke grestore\n"
        "] bind def\n")

    fp.write(
        "\n/gbm3 [ % x1 y1 x2 y2 gbm3 - triple gnote beam\n"
        "  gsave 1.2 setlinewidth\n"
        "  4 copy 0.3 sub moveto 0.3 sub lineto stroke\n"
        "  4 copy 2.5 sub moveto 2.5 sub lineto stroke\n"
        "  4.7 sub moveto 4.7 sub lineto stroke grestore\n"
        "] bind def\n")

    fp.write(
        "\n/ghl [ % x y ghl - grace note ledger line\n"
        "   gsave 0.7 setlinewidth moveto \n"
        "   -3 0 rmoveto 6 0 rlineto stroke grestore\n"
        "] bind def\n")

    fp.write(
        "\n/gsl [ % x1 y2 x2 y2 x3 y3 x0 y0 gsl\n"
        "  moveto curveto stroke\n"
        "] bind def\n")

    fp.write(
        "\n/gsh0 [ % x y gsh0\n"
        "gsave translate 0.7 0.7 scale 0 0 sh0 grestore\n"
        "] bind def\n")

    fp.write(
        "\n/gft0 [ % x y gft0\n"
        "gsave translate 0.7 0.7 scale 0 0 ft0 grestore\n"
        "] bind def\n")

    fp.write(
        "\n/gnt0 [ % x y gnt0\n"
        "gsave translate 0.7 0.7 scale 0 0 nt0 grestore\n"
        "] bind def\n")

    fp.write(
        "\n/gdf0 [ % x y gdf0\n"
        "gsave translate 0.7 0.6 scale 0 0 dft0 grestore\n"
        "] bind def\n")

    fp.write(
        "\n/gds0 [ % x y gds0\n"
        "gsave translate 0.7 0.7 scale 0 0 dsh0 grestore\n"
        "] bind def\n")


def def_csg(fp):
    p = [[0, 26],
         [4, 26], [11, 23], [11, 14],
         [11, 20], [5, 19], [5, 14],
         [5, 9], [12, 9], [12, 15],
         [12, 25], [6, 28], [0, 28],
         [-15, 28], [-25, 17], [-25, 2],
         [-25, -10], [-10, -28], [11, -8],
         [-6, -20], [-18, -11], [-18, 2],
         [-18, 14], [-14, 26], [0, 26]]

    for i in range(25):
        p[i][0] = p[i][0]+4
        p[i][1] = p[i][1]+43
    f1 = f2 = 0.25
    fp.write(
        "\n/csig [ % x csig - C timesig \n"
        "  0 moveto\n")
    _add_mv(fp, f1, f2, p, 0)
    _add_cv(fp, f1, f2, p, 1, 8)
    fp.write("   fill\n] bind def\n")

    fp.write(
        "\n/ctsig [ % x ctsig - C| timesig \n"
        "  dup csig 4 moveto 0 16 rlineto stroke\n"
        "] bind def\n")


def def_gclef(fp):
    p = [[-6, 16], [-8, 13], [-14, 19], [-10, 35], [2, 35], [8, 37],
         [21, 30], [21, 17], [21, 5], [10, -1], [0, -1], [-12, -1],
         [-23, 5], [-23, 22], [-23, 29], [-22, 37], [-7, 49], [10, 61],
         [10, 68], [10, 73], [10, 78], [9, 82], [7, 82], [2, 78],
         [-2, 68], [-2, 62], [-2, 25], [10, 18], [11, -8], [11, -18],
         [5, -23], [-4, -23], [-10, -23], [-15, -18], [-15, -13],
         [-15, -8], [-12, -4], [-7, -4], [3, -4], [3, -20], [-6, -17],
         [-5, -23], [9, -20], [9, -9], [7, 24], [-5, 30], [-5, 67],
         [-5, 78], [-2, 87], [7, 91], [13, 87], [18, 80], [17, 73],
         [17, 62], [10, 54], [1, 45], [-5, 38], [-15, 33], [-15, 19],
         [-15, 7], [-8, 1], [0, 1], [8, 1], [15, 6], [15, 14], [15, 23],
         [7, 26], [2, 26], [-5, 26], [-9, 21], [-6, 16]]

    f1 = f2 = 24.0/65.0
    fp.write(
        "\n/gclef [ % x n gclef - G clef on line n\n"
        "  2 sub 6 mul moveto\n")   # shift to line n*/
    _add_mv(fp, f1, f2, p, 0)
    _add_sg(fp, f1, f2, p, 1, 1)
    _add_cv(fp, f1, f2, p, 2, 23)
    fp.write("   fill\n] bind def\n")
    fp.write(
        "\n/sgclef [\n"
        "  0.85 div exch 0.85 div exch"   # compensate scale*/
        " gsave 0.85 0.85 scale gclef grestore\n"
        "] bind def\n")


def def_t8clef(fp):
    fp.write(
        "\n/t8clef [ % x t8clef - treble 8va clef\n"
        "  dup 2 gclef -20 moveto\n"
        "  gsave /Times-Roman 12 selectfont\n"
        "  /bx false def(8) cshow grestore\n"
        "] bind def\n"
        "\n/st8clef [\n"
        "  0.85 div gsave 0.85 0.85 scale t8clef grestore\n"
        "] bind def\n")
    fp.write(
        "\n/t8upclef [ % x t8upclef - treble 8va clef\n"
        "  dup 2 gclef 33 moveto\n"
        "  gsave /Times-Italic 12 selectfont\n"
        "  /bx false def(8) cshow grestore\n"
        "] bind def\n"
        "\n/st8upclef [\n"
        "  0.85 div gsave 0.85 0.85 scale t8upclef grestore\n"
        "] bind def\n")


def def_fclef(fp):
    p = [[-2.3, 3], [6, 7], [10.5, 12], [10.5, 16],
         [10.5, 20.5], [8.5, 23.5], [6.2, 23.3],
         [5.2, 23.5], [2, 23.5], [0.5, 19.5],
         [2, 20], [4, 19.5], [4, 18],
         [4, 17], [3.5, 16], [2, 16],
         [1, 16], [0, 16.9], [0, 18.5],
         [0, 21], [2.1, 24], [6, 24],
         [10, 24], [13.5, 21.5], [13.5, 16.5],
         [13.5, 11], [7, 5.5], [-2.0, 2.8],
         [14.9, 21],
         [14.9, 22.5], [16.9, 22.5], [16.9, 21],
         [16.9, 19.5], [14.9, 19.5], [14.9, 21],
         [14.9, 15],
         [14.9, 16.5], [16.9, 16.5], [16.9, 15],
         [16.9, 13.5], [14.9, 13.5], [14.9, 15]]

    for i in range(42):
        p[i][0] -= 7.5
        p[i][1] -= 0.5
    f1 = f2 = 1.0
    fp.write(
        "\n/fclef [ % x n fclef - F clef on line n\n"
        "  4 sub 6 mul moveto\n")
    _add_mv(fp, f1, f2, p, 0)
    _add_cv(fp, f1, f2, p, 1, 9)
    _add_cv(fp, f1, f2, p, 1, 9)

    _add_mv(fp, f1, f2, p, 28)
    _add_cv(fp, f1, f2, p, 29, 2)

    _add_mv(fp, f1, f2, p, 25)
    _add_cv(fp, f1, f2, p, 36, 2)

    fp.write("fill\n] bind def\n")

    fp.write(
        "\n/sfclef [\n"
        "  0.85 div exch 0.85 div exch"   # compensate scale*/
        " gsave 0.85 0.85 scale fclef grestore\n"
        "] bind def\n")


def def_cclef(fp):
    p = [[0, 0], [2, 5.5],
         [9, 4.5], [12, 10], [12, 15.5],
         [12, 19.5], [11, 23.3], [6.5, 23.5],
         [5.2, 23.5], [2, 23.5], [0.5, 19.5],
         [2, 20], [4, 19.5], [4, 18],
         [4, 17], [3.5, 16], [2, 16],
         [1, 16], [0, 16.9], [0, 18.5],
         [0, 21], [2.1, 24], [6, 24],
         [12, 24], [15, 21.5], [15, 16.5],
         [15, 10], [10, 4.5], [4, 5],
         [3, 0]]

    for i in range(30):
        p[i][1] += 24

    f1 = 0.6
    f2 = 0.5
    fp.write(
        "\n/cchalf [\n"
        "  0 moveto\n")
    _add_mv(fp, f1, f2, p, 0)
    _add_sg(fp, f1, f2, p, 1, 1)
    _add_cv(fp, f1, f2, p, 2, 9)
    _add_sg(fp, f1, f2, p, 29, 1)
    fp.write("fill\n] bind def\n")

    fp.write(
        "\n/cclef [   % x n cclef - C clef on line n\n"
        "   gsave 0 exch 3 sub 6 mul translate\n"
        "   dup dup dup\n"
        "   cchalf 0 24 translate 1 -1 scale cchalf\n"
        "   6.5 sub 0 moveto 0 24 rlineto 3 0 rlineto 0 -24 rlineto fill\n"
        "   1.8 sub 0 moveto 0 24 rlineto 0.8 setlinewidth stroke grestore \n"
        "] bind def\n")

    fp.write("\n/scclef [ cclef ] bind def\n")


def def_brace(fp):
    p = [[7.2, 60], [-7, 39], [17, 17], [-1, 0],
         [-1.4, 0], [13, 13], [-11, 39], [7, 60]]

    q = [[-3, 0], [2, 0], [4, 1], [5.5, 5],
         [5.9, 4.7], [4.7, 1.2], [3.2, -.4], [-1, -1.2]]

    f1 = 0.9
    f2 = 1.0
    fp.write("\n/bracehalf [\n")
    _add_mv(fp, f1, f2, p, 0)
    _add_cv(fp, f1, f2, p, 1, 1)
    _add_sg(fp, f1, f2, p, 4, 1)
    _add_cv(fp, f1, f2, p, 5, 1)
    fp.write("  fill\n] bind def\n")

    fp.write(
        "\n/brace [   % scale x0 y0 brace\n"
        "   3 copy moveto gsave 1 exch scale bracehalf grestore\n"
        "   moveto gsave neg 1 exch scale bracehalf grestore\n"
        "] bind def\n")

    f1 = 1.0
    f2 = 1.0
    fp.write("\n/brackhead [\n")
    _add_mv(fp, f1, f2, q, 0)
    _add_cv(fp, f1, f2, q, 1, 1)
    _add_sg(fp, f1, f2, q, 4, 1)
    _add_cv(fp, f1, f2, q, 5, 1)
    fp.write("  fill\n] bind def\n")

    fp.write(
        "\n/bracket [   % h x0 y0 bracket\n"
        "   3 copy moveto 0 exch rmoveto brackhead\n"
        "   3 copy moveto pop gsave 1 -1 scale brackhead grestore \n"
        "   moveto -3 0 rlineto 0 exch rlineto 3 0 rlineto fill\n"
        "] bind def \n")


def def_staff(fp):
    fp.write(
        '\n/staff [ % l staff - draw staff\n'
        f'  gsave {cfmt.stafflinethickness:3.2f} setlinewidth 0 0 moveto\n'
        '  dup 0 rlineto dup neg 6 rmoveto\n'
        '  dup 0 rlineto dup neg 6 rmoveto\n'
        '  dup 0 rlineto dup neg 6 rmoveto\n'
        '  dup 0 rlineto dup neg 6 rmoveto\n'
        '  dup 0 rlineto dup neg 6 rmoveto\n'
        '  pop stroke grestore\n'
        '] bind def\n')


def def_sep(fp):
    fp.write(
        "\n/sep0 [ % x1 x2 sep0 - hline separator \n"
        "   0 moveto 0 lineto stroke\n"
        "] bind def\n")


def open_tabfontfile(basename):
    """
    find first font file in directory list $ABCTABFONTS
    and open it. If $ABCTABFONTS is unset, standard directories are
    searched. If the file cannot be found, NULL is returned.

    :param basename:
    :return:
    """
    # get font directory list
    font_dirs = os.environ.get('ABCTABFONT', None)
    if not font_dirs:
        font_dirs = TABFONTDIRS
    font_file = '.'.join([basename, 'ps'])

    for font_dir in font_dirs:
        t = [f for f in os.listdir(font_dir)
             if os.path.isfile(os.path.join(font_dir, font_file))]
        if t:
            return t
    return


def def_tabfonts(fp):
    """
    writes font definitions into outfile
    from fontfile is removed by getline() and rewritten,
    to achieve native line breaks on each platform

    It is not possible to decide automatically, whether tab
    is needed, because only one tune is accessible at a time

    - load french font (can be suppressed with %%tabfontfrench none)
    - load italian font (can be suppressed with %%tabfontitalian none)
    - load german font (can be suppressed with %%tabfontgerman none)

    :param fp:
    """
    if args.notab:    # when global flag set
        return
    if not args.frfont:
        frfont = "frFrancisque"  # font for frenchtab
    else:
        frfont = args.frfont
    if not args.itfont:
        itfont = "itTimes"  # font for italiantab
    else:
        itfont = args.itfont
    if not args.defont:
        defont = "deCourier"  # font for germantab
    else:
        defont = args.defont

    font_list = [frfont, itfont, defont]
    for tab_font in font_list:
        if tab_font == "none":
            fp.write('\n')
            with open_tabfontfile(tab_font) as fontfp:
                if not fontfp:
                    log.error('Please check the environment variable '
                              'ABCTABFONTS\n'
                              f'Cannot find tablature font file: {frfont}')
                lines = fontfp.readlines()
                for line in lines:
                    if line.startswith('%!'):
                        fp.write(line)


def def_tabsyms(fp, cfmt):
    """
    writes PS macros for tablature into outfile
    """
    # these are from tab.read_tab_format. That module was never called
    size = 14
    scale = 1.0
    # when global flag set
    if args.notab:
        return

    # It is not possible to decide automatically, whether tab is needed,
    # because only one tune is accessible at a time

    # tablature system
    fp.write("\n/tabN { %% l n tabN - n line tab\n"
             "    gsave %3.2f setlinewidth 0 0 moveto\n"
             "    {dup 0 rlineto dup neg %d rmoveto} repeat\n"
             "    pop stroke grestore\n"
             "} bind def\n" % (cfmt.stafflinethickness, size))

    fp.write("\n/tab1 { %% l y tab1 - tab separator line\n"
             "    gsave %3.2f setlinewidth 0 exch moveto 0 rlineto\n"
             "    stroke grestore\n"
             "} bind def\n" % cfmt.stafflinethickness)

    # time signatures
    fp.write("\n/tabcsig { %% x n tabcsig - C time sig\n"
             "    gsave 1.2 setlinewidth\n"
             "    6 sub %.1f mul %.1f add moveto currentpoint\n"
             "    -10 0 -10 %d 0 %d rcurveto\n"
             "    -15 0 -15 -%d 0 -%d rcurveto\n"
             "    fill moveto 7 3.5 rmoveto\n"
             "    -3.5 -3.5 -3.5 -3.5 -7 -3.5 rcurveto\n"
             "    -15 0 -15 %d 0 %d rcurveto\n"
             "    3.5 0 3.5 0 7 -3.5 rcurveto\n"
             "    currentpoint stroke moveto 0.5 0 rmoveto\n"
             "    currentpoint exch -2 add exch -2 add 2 0 360 arc\n"
             "    fill grestore\n"
             "} bind def\n" % (size * 0.5, size * 1.5,
                               size * 2, size * 2,
                               size * 2, size * 2,
                               size * 2, size * 2))

    fp.write("\n/tabctsig { %% x n tabctsig - C| timesig\n"
             "    2 copy tabcsig\n"
             "    6 sub %.1f mul %.1f add moveto 0 %d rlineto stroke\n"
             "} bind def\n" % (size * 0.5,
                               size * 0.5,
                               size * 4))
    # beware that tab is higher than music
    fp.write("\n/tabtsig { %% x n (top) (bot) tabtsig - time signature\n"
             "    4 -2 roll -5 add %d mul moveto /bx false def\n"
             "    gsave /NewCenturySchlbk-Bold 16 selectfont %.1f %.1f scale\n"
             "    0 1.0 rmoveto currentpoint 3 -1 roll cshow\n"
             "    moveto 0 %d %.1f div rmoveto cshow grestore\n"
             "} bind def\n" % (size,
                               3 * size / STAFFHEIGHT,
                               3 * size / STAFFHEIGHT,
                               2 * size,
                               3 * size / STAFFHEIGHT))
    fp.write(
        "\n/tabt1sig { %% x n (top) tabt1sig - timesig without denominator\n"
        "    3 1 roll 6 sub %.1f mul %.1f add moveto /bx false def\n"
        "    gsave /NewCenturySchlbk-Bold 16 selectfont %.1f %.1f scale\n"
        "    cshow grestore\n"
        "} bind def\n" % (size * 0.5,
                          size * 1.8,
                          3 * size / STAFFHEIGHT,
                          3 * size / STAFFHEIGHT))

    # tablature letter
    fp.write(
        "\n/tabfshow { %% x n (c) tabfshow - french tabletter c on course n\n"
        "    3 1 roll\n"
        # raise one point so that line is not touched
        "    -6 add -%d mul 1 add moveto\n"
        #                                ^^^^^
        "    gsave /FrenchTabfont %.1f selectfont\n"
        "    /bx false def cshow grestore\n"
        "} bind def\n" % (size, size * scale))
    fp.write(
        "\n/tabsshow { %% x n (c) tabsshow - spanish tabletter c on course n\n"
        "    3 1 roll\n"
        "    -5.5 add -%d mul moveto\n"
        "    gsave /ItalianTabfont %.1f selectfont\n"
        "    /bx false def cshow grestore\n"
        "} bind def\n" % (size, size * scale))
    fp.write("\n/tabgshow { %% x n (c) tabgshow - german tabletter c at pos n\n"
             "    3 1 roll\n"
             "    -4.25 add -%d mul moveto\n"
             "    gsave /GermanTabfont %.1f selectfont\n"
             "    /bx false def cshow grestore\n"
             "} bind def\n" % (size, size * scale))

    # rhythm flags
    fp.write("\n/tabbrevis { %% x y tabbrevis - brevis\n"
             "    gsave 0.8 setlinewidth\n"
             "    2 copy moveto -4 1.5 rmoveto\n"
             "    8 0 rlineto 0 1.5 rlineto -8 0 rlineto 0 -1.5 rlineto fill\n"
             "    2 copy moveto -4 5.5 rmoveto\n"
             "    8 0 rlineto 0 1.5 rlineto -8 0 rlineto 0 -1.5 rlineto fill\n"
             "    2 copy moveto -4 0 rmoveto 0 9 rlineto stroke\n"
             "    moveto 4 0 rmoveto 0 9 rlineto stroke\n"
             "    grestore\n"
             "} bind def\n")
    fp.write("\n/tablonga { %% x y tablonga - longa\n"
             "    gsave 0.8 setlinewidth\n"
             "    2 copy 4 add tabbrevis\n"
             "    moveto 4 0 rmoveto 0 5 rlineto stroke\n"
             "    grestore\n"
             "} bind def\n")
    fp.write(
        "\n/tabsflag { %% x y n tabsflag - stem with n flags (simple style)\n"
        "    gsave 1 setlinewidth\n"
        "    3 1 roll moveto 0 20 rlineto\n"
        "    currentpoint stroke moveto\n"
        "    dup 0 lt {\n"
        "        dup neg {\n"
        "            -4 -2 rlineto 1 -1 rlineto 3 2 rlineto 0 1 rlineto\n"
        "            currentpoint fill moveto 0 -5 rmoveto\n"
        "        } repeat\n"
        "    } if\n"
        "    dup 0 gt {\n"
        "        {\n"
        "            1.2 -1 rlineto \n"
        "            2 -1 6 -1 6 -3 rcurveto\n"
        "            -1.2 -1.2 rlineto\n"
        "            0 2 -4 2 -6 3 rcurveto\n"
        "            0 2.2 rlineto\n"
        "            currentpoint fill moveto\n"
        "            0 -5 rmoveto\n"
        "        } repeat\n"
        "    } {pop} ifelse    grestore\n"
        "} bind def\n")
    fp.write(
        "\n/tabdflag { %% x y n tabdflag - stem with n flags (diamond style)\n"
        "    gsave 1 setlinewidth\n"
        "    3 1 roll moveto\n"
        "    dup 0 lt {\n"
        "        4 4 rlineto currentpoint\n"
        "        -0.4 0.4 rlineto -4 -4 rlineto 0.4 -0.4 rlineto fill moveto\n"
        "        -4 4 rlineto currentpoint\n"
        "        -1.1 -1.1 rlineto 4 -4 rlineto 1.1 1.1 rlineto fill moveto\n"
        "        -4 -4 rlineto currentpoint\n"
        "        0.4 -0.4 rlineto 4 4 rlineto -0.4 0.4 rlineto fill moveto\n"
        "        4 -4 rlineto currentpoint\n"
        "        1.1 1.1 rlineto -4 4 rlineto -1.1 -1.1 rlineto fill moveto\n"
        "        0 8 rmoveto\n"
        "    } {\n"
        "        4 4 rlineto -4 4 rlineto -4 -4 rlineto 4 -4 rlineto\n"
        "        currentpoint fill moveto 0 8 rmoveto\n"
        "    } ifelse\n"
        "    dup -2 gt {\n"
        "        0 setlinejoin 0 setlinecap\n"
        "        0 20 8 sub rlineto \n"
        "    } if\n"
        "    dup 0 gt {\n"
        "        {\n"
        "            6 -3 rlineto\n"
        "            -6 0 rmoveto\n"
        "        } repeat\n"
        "    } {pop} ifelse\n"
        "    stroke grestore\n"
        "} bind def\n")
    fp.write(
        "\n/tabmflag { %% x y n tabmflag - stem with n flags (modern style)\n"
        "    gsave 1 setlinewidth\n"
        "    3 1 roll moveto\n"
        "    dup 0 lt {\n"
        "        2.5 7 rmoveto\n"
        "        0 -1 0 -7 -5 -7 rcurveto -2 0 0 7 5 7 rcurveto\n"
        "        currentpoint stroke moveto\n"
        "    } {\n"
        "        3 7 rmoveto\n"
        "        0 -1 0 -7 -5 -7 rcurveto -2 0 0 7 5 7 rcurveto\n"
        "        currentpoint fill moveto -0.5 0 rmoveto\n"
        "    } ifelse\n"
        "    dup -2 gt {\n"
        "        0 20 7 sub rlineto\n"
        "        currentpoint stroke moveto\n"
        "    } if \n"
        "    dup 0 gt {\n"
        "        1.2 -0.2 rlineto currentpoint\n"
        "        -1.2 -1.2 rlineto closepath fill moveto\n"
        "        {\n"
        "            2.4 -0.4 7 0 3.5 -5 rcurveto\n"
        "            -1.2 -1.2 rlineto currentpoint\n"
        "            3.5 5 -1.1 4.6 -3.5 5 rcurveto 1.2 1.2 rlineto\n"
        "            fill moveto\n"
        "        } repeat\n"
        "    } {pop} ifelse grestore\n"
        "} bind def\n")

    # rests (only modern style has own implemetation)
    fp.write(
        "\n/tabsrest { %% usage x y n tabsrest - rest with n flags (simple style)\n"
        "    tabsflag\n"
        "} bind def\n")
    fp.write(
        "\n/tabdrest { %% usage x y n tabdrest - rest with n flags (diamond style)\n"
        "    tabdflag\n"
        "} bind def\n")
    fp.write(
        "\n/tabmrest { %% usage x y n tabmrest - rest with n flags (modern style)\n"
        "    gsave 1 setlinewidth\n"
        "    3 1 roll moveto\n"
        "    dup -4 le { %% longa rest\n"
        "        gsave 0.8 setlinewidth\n"
        "        currentpoint -5 5 rmoveto\n"
        "        10 0 rlineto 0 3 rlineto -10 0 rlineto 0 -3 rlineto fill\n"
        "        moveto currentpoint -5 4 rmoveto 0 5 rlineto stroke\n"
        "        moveto 5 0 rmoveto 0 9 rlineto stroke grestore\n"
        "    } if\n"
        "    dup -3 eq { %% brevis rest\n"
        "        gsave 0.8 setlinewidth\n"
        "        currentpoint -5 1 rmoveto\n"
        "        10 0 rlineto 0 3 rlineto -10 0 rlineto 0 -3 rlineto fill\n"
        "        moveto currentpoint -5 0 rmoveto 0 5 rlineto stroke\n"
        "        moveto 5 0 rmoveto 0 5 rlineto stroke grestore\n"
        "    } if\n"
        "    dup -2 eq { %% whole note rest\n"
        "        -5 3 rmoveto 10 0 rlineto\n"
        "        currentpoint stroke moveto -2 -3 rmoveto\n"
        "        0 3 rlineto -6 0 rlineto 0 -3 rlineto 6 0 rlineto fill\n"
        "    } if\n"
        "    dup -1 eq { %% half note rest\n"
        "        -5 0 rmoveto 10 0 rlineto\n"
        "        currentpoint stroke moveto -2 0 rmoveto\n"
        "        0 3 rlineto -6 0 rlineto 0 -3 rlineto 6 0 rlineto fill\n"
        "} if\n"
        "    dup 0 eq { %% crotchet rest\n"
        "        -2 4 1 4 3 3 rcurveto currentpoint -1.5 1.5 rlineto\n"
        "        -2 1 -5 1 -3 -3 rcurveto 1.5 -1.5 rlineto fill moveto\n"
        "        -1 1 rmoveto\n"
        "        -5 5 3 4 -2 9 rcurveto -1.5 1.5 rlineto\n"
        "        5 -5 -3 -4 2 -9 rcurveto 1.5 -1.5 rlineto fill\n"
        "    } if\n"
        "    dup 1 ge { %% (semi)quaver rests\n"
        "        2 8 rlineto dup dup 0.5 mul exch 2 mul rlineto\n"
        "        currentpoint stroke moveto\n"
        "        {\n"
        "            -2 -2 -3 -2 -5 -2 rcurveto \n"
        "            currentpoint 1.5 add 1.5 -90 0 arcn \n"
        "            0 -1 2.5 0 3.5 0.5 rcurveto\n"
        "            currentpoint fill moveto\n"
        "            -1 -4 rmoveto\n"
        "        } repeat\n"
        "    } {pop} ifelse grestore\n"
        "} bind def\n")

    # multibar rests
    fp.write("\n/tabbrest { %% usage (n) x yn x y tabbrest - multibar rest\n"
             "     gsave moveto currentpoint 0.8 setlinewidth\n"
             "     0 -6 rmoveto 0 12 rlineto 40 0 rmoveto 0 -12 rlineto stroke\n"
             "     3 setlinewidth moveto 40 0 rlineto stroke\n"
             "     moveto 20 0 rmoveto /Times-Bold 13 selectfont cshow grestore\n"
             "} bind def\n")

    # dots after flag
    fp.write("\n/tabdt { %% x y n tabdt - n dots after flag\n"
             "    3 1 roll moveto 1 1 rmoveto currentpoint 3 2 roll\n"
             "    {\n"
             "        exch 3 add exch newpath\n"
             "        1 0 360 arc\n"
             "        currentpoint fill closepath\n"
             "    } repeat\n"
             "    pop pop\n"
             "} bind def\n")

    # Bourdon string
    # version with ledger lines BEFORE letter
    fp.write(
        "\n/tabfbourdon { %% x m n (c) - n-th bourdon stopped at c drawn at course 7+m in frenchtab\n"
        "    gsave .75 setlinewidth\n"
        "    4 1 roll 2 index\n"
        "    -%.1f add 2 index -%d mul -2 add moveto\n"
        "    { -%.1f -%d rlineto %.1f %d rmoveto} repeat stroke\n"
        "    1 add -%d mul 1 add moveto\n"
        "    /FrenchTabfont %.1f selectfont\n"
        "    /bx false def cshow grestore\n"
        "} bind def\n" % (scale, size,
                          0.5 * size, size - 2,
                          0.5 * size - 2.5, size - 2,
                          size, size * scale))
    # alternative version with ledger lines ABOVE letter
    fp.write(
        "\n/tabf1bourdon { %% x m n (c) - n-th bourdon stopped at c drawn at course 7+m in frenchtab\n"
        "    gsave .75 setlinewidth\n"
        "    4 1 roll 3 1 roll 2 index exch 2 index 2 index\n"
        "    .5 mul neg -%.1f add add 1 index -%d mul -7 add moveto\n"
        "    4 -1 roll 3 -1 roll\n"
        "    {%d 4 rlineto -%.1f -7 rmoveto} repeat stroke\n"
        "    -3 mul -%d add 1 add exch -%d mul add moveto\n"
        "    /FrenchTabfont %.1f selectfont\n"
        "    /bx false def cshow grestore\n"
        "} bind def\n" % (0.5 * size, size,
                          size, -0.5 + size,
                          size, size,
                          size * scale))
    # italian tablature seventh course
    fp.write(
        "\n/tabibourdon { %% x (c) tabibourdon - (c) on 7th course in italiantab\n"
        "    gsave .75 setlinewidth\n"
        "    exch dup %d moveto -%d 0 rmoveto %d 0 rlineto stroke\n"
        "    0 3 -1 roll tabsshow grestore\n"
        "} bind def\n" % (
            6 * size, size // 2, size + 1
        ))
    # italian tablature eighth course
    fp.write(
        "\n/tabi8bourdon { %% x (c) tabi8bourdon - (c) on 8th course in italiantab\n"
        "    gsave .75 setlinewidth\n"
        "    exch dup %d moveto -%d 0 rmoveto %d 0 rlineto currentpoint stroke\n"
        "    moveto 0 %d rmoveto -14 0 rlineto stroke\n"
        "    -1 3 -1 roll tabsshow grestore\n"
        "} bind def\n" % (
            6 * size, size // 2, size + 1,
            size
        ))

    # different bar lines
    fp.write(
        "\n/tabbar { %% x h tabbar - single bar in tab\n"
        "    exch 0 moveto 0 exch rlineto stroke\n"
        "} bind def\n"
    )
    fp.write(
        "\n/tabdbar { %% x h tabdbar - thin double bar in tab\n"
        "    exch 0 moveto dup 0 exch rlineto dup -3 exch neg rmoveto\n"
        "    0 exch rlineto stroke\n"
        "} bind def\n"
    )
    fp.write(
        "\n/tabfbar1 { %% x h tabfbar1 - fat double bar at start\n"
        "    exch 0 moveto dup 0 exch rlineto 3 0 rlineto \n"
        "    dup 0 exch neg rlineto currentpoint fill moveto\n"
        "    3 0 rmoveto dup 0 exch rlineto stroke\n"
        "} bind def\n"
    )
    fp.write(
        "\n/tabfbar2 { %% x tabfbar2 - fat double bar at end\n"
        "    exch 0 moveto dup 0 exch rlineto -3 0 rlineto \n"
        "    dup 0 exch neg rlineto currentpoint fill moveto\n"
        "    -3 0 rmoveto dup 0 exch rlineto stroke\n"
        "} bind def\n"
    )

    # repeat dots
    fp.write(
        "\n/tabrdots { %% x n rdots - n repeat dots\n"
        "    exch 0 moveto 0 %.1f rmoveto currentpoint 2 copy 1.2 0 360 arc\n"
        "    3 -1 roll 2 sub {moveto 0 %d rmoveto    currentpoint 2 copy 1.2 0 360 arc} repeat\n"
        "    moveto 0 %d rmoveto    currentpoint 1.2 0 360 arc fill\n"
        "} bind def\n" % (
            0.5 * size, size, size
        ))

    # first/second endings
    dy = 15  # use dy=6 for small boxes
    fp.write("\n/tabend1 { %% x1 x2 h (str) tabend1 - mark first ending\n"
             "    4 1 roll -%d add dup 3 1 roll moveto 0 %d rlineto 2 copy %d add lineto 0 -%d rlineto stroke\n"
             "    moveto 4 %d rmoveto gsave /Times-Roman 13 selectfont 1.2 0.95 scale\n"
             "    show grestore\n"
             "} bind def\n" % (dy, dy, dy, dy, dy - 10))
    fp.write("\n/tabend2 { %% x1 x2 h (str) tabend2 - mark second ending\n"
             "    4 1 roll dup 3 1 roll moveto 2 copy lineto 0 -%d rlineto stroke\n"
             "    moveto 4 -10 rmoveto gsave /Times-Roman 13 selectfont 1.2 0.95 scale\n"
             "    show grestore\n"
             "} bind def\n" % dy)

    # grace signs
    fp.write(
        "\n/tabtrl { %% x y tabtrl - trill\n"
        "    gsave /Times-BoldItalic 14 selectfont\n"
        "    moveto -4 0 rmoveto (tr.) show grestore\n"
        "} bind def\n"
    )
    fp.write(
        "\n/tabacc { %% usage x n tabacc - accent from above\n"
        "    -6 add -%d mul -2.5 add moveto\n"
        "    1 1 2 1 2 4 rcurveto\n"
        "    currentpoint 1.5 add 1.5 -90 0 arcn\n"
        "    0 -3 -3 -3.5 -3.5 -5.5 rcurveto fill\n"
        "} bind def\n" % size)
    fp.write(
        "\n/tabx { %% usage x n tabx - mordent\n"
        "    -6 add -%d mul -3.5 add moveto\n"
        "    gsave 0.7 setlinewidth\n"
        "    5 7 rlineto -5 0 rmoveto 5 -7 rlineto\n"
        "    stroke grestore\n"
        "} bind def\n" % size)
    fp.write(
        "\n/tabu { %% usage x n tabu - arc starting at x\n"
        "    -6 add -%d mul -2 add moveto\n"
        "    gsave 1.0 setlinewidth\n"
        "    2 -4 5 -4 7 0 rcurveto\n"
        "    stroke grestore\n"
        "} bind def\n" % size)
    fp.write(
        "\n/tabv { %% usage x n tabu - arc centered at x\n"
        "    -6 add -%d mul -2 add exch -3.5 add exch moveto\n"
        "    gsave 1.0 setlinewidth\n"
        "    2 -4 5 -4 7 0 rcurveto\n"
        "    stroke grestore\n"
        "} bind def\n" % size)
    fp.write(
        "\n/tabstar { %% usage x n tabstar - asterisque\n"
        "    -6 add -%d mul -%.1f add moveto\n"
        "    /Helvetica 21 selectfont (*) show\n"
        "} bind def\n" % (
            size, 0.5 * size
        ))
    fp.write(
        "\n/tabcross { %% usage x n tabcross - double cross\n"
        "    -6 add -%d mul -1 add moveto\n"
        "    /Helvetica 14 selectfont (#) show\n"
        "} bind def\n" % size)
    fp.write(
        "\n/taboline { %% usage x n taboline - oblique line\n"
        "    -5.5 add -%d mul moveto\n"
        "    gsave 1.2 setlinewidth\n"
        "    -5 -1.5 rmoveto 12 3 rlineto stroke grestore\n"
        "} bind def\n" % size)
    fp.write(
        "\n/tabstrup { %% x y tabstrup - strum up arrow\n"
        "    -12 add moveto gsave 1 setlinewidth\n"
        "    0 12 rlineto -3 -4 rmoveto 3 4 rlineto 3 -4 rlineto\n"
        "    stroke grestore\n"
        "} bind def\n"
    )
    fp.write(
        "\n/tabstrdn { %% x y tabstrdn - strum down arrow\n"
        "    moveto gsave 1 setlinewidth\n"
        "    0 -12 rlineto -3 4 rmoveto 3 -4 rlineto 3 4 rlineto\n"
        "    stroke grestore\n"
        "} bind def\n"
    )

    # right hand indications
    fp.write(
        "\n/tabi { %% x n tabi - index finger\n"
        "    -5.5 add -%d mul moveto\n"
        "    currentpoint 2 copy 1.2 0 360 arc fill\n"
        "} bind def\n" % size)
    fp.write(
        "\n/tabm { %% x n tabm - middle finger\n"
        "    -5.5 add -%d mul moveto -1.3 0 rmoveto\n"
        "    currentpoint 2 copy 1.2 0 360 arc\n"
        "    currentpoint fill moveto 2.6 0 rmoveto\n"
        "    currentpoint 2 copy 1.2 0 360 arc fill\n"
        "} bind def\n" % size)
    fp.write(
        "\n/taba { %% x n taba - ring finger\n"
        "    -5.5 add -%d mul moveto -2.5 0 rmoveto\n"
        "    currentpoint 2 copy 1.2 0 360 arc\n"
        "    currentpoint fill moveto 2.5 0 rmoveto\n"
        "    currentpoint 2 copy 1.2 0 360 arc\n"
        "    currentpoint fill moveto 2.5 0 rmoveto\n"
        "    currentpoint 2 copy 1.2 0 360 arc fill\n"
        "} bind def\n" % size)

    fp.write(
        "\n/tabp { %% x n tabp - thumb\n"
        "    -5.5 add -%d mul moveto\n"
        "    gsave 1 setlinewidth\n"
        "    0 2.5 rmoveto 0 -5 rlineto\n"
        "    stroke grestore\n"
        "} bind def\n" % size)

    fp.write(
        "\n/tabpguitar { %% x n tabpguitar - thumb (guitar style)\n"
        "    -5.5 add -%d mul moveto\n"
        "    gsave 1 setlinewidth\n"
        "    0 2.5 rmoveto 0 -5 rlineto\n"
        "    -2.5 2.5 rmoveto 5 0 rlineto\n"
        "    stroke grestore\n"
        "} bind def\n" % size)

    fp.write("\n/tabten { %% x1 y1 x2 y2 tenuto stroke\n"
             "    gsave 0.4 setlinewidth 4 2 roll moveto lineto stroke grestore\n"
             "} bind def\n")


def define_symbols(fp):
    """
    write postscript macros to file

    :param fp:
    :return:
    """
    # load tablature fonts
    def_tabfonts(fp)

    # general music stuff
    def_misc(fp)
    def_gclef(fp)
    def_t8clef(fp)
    def_fclef(fp)
    def_cclef(fp)
    def_hd1(fp)
    def_hd2(fp)
    def_hd3(fp)
    def_historic(fp)
    def_stems(fp)
    def_beam(fp)
    def_sl(fp)
    def_dot(fp)
    def_deco(fp)
    def_deco1(fp)
    def_hl(fp)
    def_flags1(fp)
    def_flags2(fp)
    def_xflags(fp)
    def_acc(fp)
    def_gchord(fp)
    def_rests(fp)
    def_bars(fp)
    def_ends(fp)
    def_gnote(fp)
    def_csg(fp)
    def_sep(fp)
    def_tsig(fp)
    def_staff(fp)
    def_brace(fp)
    def_typeset(fp)
    def_tabsyms(fp, cfmt)


if __name__ == '__main__':
    with open('hello', 'w') as fp:
        # def_misc(fp)
        # def_gclef(fp)
        # def_t8clef(fp)
        def_fclef(fp)
        # def_cclef(fp)
        # def_hd1(fp)
        # def_hd2(fp)
        # def_hd3(fp)
        # def_historic(fp)
        # def_stems(fp)
        # def_beam(fp)
        # def_sl(fp)
        # def_dot(fp)
        # def_deco(fp)
        # def_deco1(fp)
        # def_hl(fp)
        # def_flags1(fp)
        # def_flags2(fp)
        # def_xflags(fp)
        # def_acc(fp)
        # def_gchord(fp)
        # def_rests(fp)
        # def_bars(fp)
        # def_ends(fp)
        # def_gnote(fp)
        # def_csg(fp)
        # def_sep(fp)
        # def_tsig(fp)
        # def_staff(fp)
        # def_brace(fp)
        # def_typeset(fp)