# Copyright (c) 2021 Curtis Penner
import style
from constants import (BASE, NOTE, REST, BREST, INVISIBLE, CLEF, KEYSIG, TIMESIG)
from constants import VOCPRE
from constants import (H_OVAL, H_EMPTY)
from constants import (STEM, STEM_CH, BNUMHT)
from constants import (BAR,  B_SNGL, B_DBL, B_LREP, B_RREP, B_DREP, B_FAT1, B_FAT2)
from constants import (D_SLIDE)
from constants import (DOTSHIFT)
from constants import (GSPACE0, GSPACE, GCHPRE)
from constants import STAFFHEIGHT
from constants import (BASS, ALTO, TENOR, SOPRANO, MEZZOSOPRANO, BARITONE, SUBBASS, VARBARITONE,
                       FRENCHVIOLIN)
from constants import (NWLINE)
from constants import (COMMENT, MUSIC, TO_BE_CONTINUED, E_O_F, INFO,
                       TITLE, METER, PARTS, KEY, XREF, DLEN, HISTORY, BLANK,
                       TEMPO, VOICE)
from constants import (WHOLE, HALF)
from constants import (BRUTTO, ALMOSTBRUTTO)
from constants import (RHNONE)
from common import (cfmt, voices)
import common
import subs
import cmdline
from log import log
from key import Key
from style import (f0p, f0x, f5p, f5x, f1p, f1x)
import parse
import pssubs
import util
import tab
from symbol import Symbol
from meter import Meter

args = cmdline.options()
#    subroutines connected with output of music
maxSyms = 800

XP_START = 0
XP_END = maxSyms-1


def at_least(val_0, val_1) -> tuple:
    if val_0 < val_1:
        return val_1, val_1
    return val_0, val_1


class Music:
    def __init__(self):
        self.invisible = False
        self.text = ''
        self.u = 0   # which symbol to start with
        self.v = 0   # up to which symbol to go
        self.w = 0   # draw neutrals instead starting from this one
        self.t = 0   # type of symbol: sharp or flat
        self.dc = util.put

    def draw_timesig(self, x):
        historic = ''
        if self.invisible:
            return

        if cfmt.historicstyle:
            historic = 'h'

        if self.w == 1:
            util.put('$.1f csig%s', [x, historic])
        elif self.w == 2:
            util.put('$.1f ctsig%s', [x, historic])
        elif self.w == 3:
            util.put('$.1f t1sig%s', [x, self.text])
        else:
            util.put("%.1f (%s) (%d) tsig\n", [x, self.text, self.v])

    def draw_keysig(self, x, v):
        """

        :param float x:
        :param Voice v:
        :return:
        """
        sh_pos = [0, 24, 15, 27, 18, 9, 21, 15]  # default sharp heights
        ft_pos = [0, 12, 21, 9, 18, 6, 15, 3]  # default flat heights

        if self.v > 7:
            print(f"+++ Keysig seems to have {self.v} music ???")
            return False

        yad = set_yad(self.t, v)

        # octave corrections for outbreaking positions
        for i in range(8):
            if sh_pos[i] + yad < -3:
                sh_pos[i] += 21
            if sh_pos[i] + yad > 27:
                sh_pos[i] -= 21
        sf = 0
        if self.t == Key.A_SH:
            for i in range(self.u, self.v):
                if i >= self.w:
                    util.put(f"{x:.1f} {sh_pos[i] + yad} nt0 ")
                else:
                    sf += 1
                    util.put(f"{x:.1f} {sh_pos[i] + yad} sh0 ")
                x += 5
            util.put("\n")
        elif self.t == Key.A_FT:
            for i in range(self.u, self.v):
                if i >= self.w:
                    util.put(f"{x:.1f} {ft_pos[i] + yad} nt0 ")
                else:
                    sf -= 1
                    util.put(f"{x:.1f} {ft_pos[i] + yad} ft0 ")
            x += 5
            util.put("\n")
        else:
            util.bug("wrong type in draw_keysig", False)
        return sf


def set_yad(t, v):
    """
    set shift for accidentals in points(one tone = 3 points)

    :return:
    """
    yad = 0
    if v.key.ktype == BASS:
        yad = -6
    if v.key.ktype == ALTO:
        yad = -3
    if v.key.ktype == TENOR:
        yad = +3
    if v.key.ktype == SOPRANO:
        yad = +6
    if v.key.ktype == MEZZOSOPRANO:
        yad = -9
    if v.key.ktype == BARITONE:
        yad = -12
    if v.key.ktype == VARBARITONE:
        yad = -12
    if v.key.ktype == SUBBASS:
        yad = 0
    if v.key.ktype == FRENCHVIOLIN:
        yad = -6
    if t == Key.A_FT and yad < -12:
        yad += 21
    if t == Key.A_SH and yad > 0:
        yad -= 21
    return yad


def nwid(dur):
    """
    Sets the prefered width for a note depending on the duration.
    Return value is default space on right and left side.
    Function is determined by values at 0, 1/2, 1.
    Return value is 1.0 for quarter note.

    :param float dur:
    :return float:
    """
    a = 2 * (f1p - 2 * f5p + f0p)
    b = f1p - f0p - a
    x = dur / BASE
    if x > 1.0:
        x = 1.0  # cut off for lengths greater WHOLE (== BASE)
    p = a * x * x + b * x + f0p

    x0 = 0.25
    p0 = a * x0 * x0 + b * x0 + f0p
    p = p / p0

    return p


def xwid(dur: float):
    """
    same as nwid but for stretched system

    :param float dur:
    :return float:
    """
    a = 2 * (f1x - 2 * f5x + f0x)
    b = f1x - f0x - a
    x = dur / BASE
    if x > 1.0:
        x = 1.0  # cut off for lengths greater WHOLE (== BASE)
    p = a * x * x + b * x + f0x

    x0 = 0.25
    p0 = a * x0 * x0 + b * x0 + f0x
    p = p / p0

    return p


def next_note(j: int, n: int, symb: list) -> int:
    for i in range(j + 1, n):
        if symb[i].type == NOTE or symb[i].type == REST or symb[i].type == BREST:
            return i
    return -1


def prec_note(k: int, n: int, symb: list) -> int:
    for i in range(k-1, 0 -1):
        if symb[i].type == NOTE or symb[i].type == REST or symb[i].type == BREST:
            return i
    return -1


def followed_by_note(k: int, n: int, symb: list) -> int:
    for i in range(k+1, n):
        if symb[i].type == INVISIBLE:
            break
        elif symb[i] == NOTE or symb[i] == REST or symb[i] == BREST:
            return i
        else:
            return -1
    return -1


def preceded_by_note(k: int, n: int, symb: list):
    for i in range(k-1, 0, -1):
        if symb[i].type == INVISIBLE:
            break
        elif symb[i] == NOTE or symb[i] == REST or symb[i] == BREST:
            return i
        else:
            return -1
    return -1


def set_head_directions(s: Symbol) -> None:
    # int i, n, nx, sig, d, da, shift, nac, i1, i2, m
    # float dx, xx, xmn

    n = s.npitch
    sig = -1
    if s.stem > 0:
        sig = 1
    for i in range(n):
        s.shhd[i] = 0
        s.shac[i] = 8
        if s.head == H_OVAL:
            s.shac[i] += 3
        s.xmn = 0
        s.xmx = 0
    if n < 2:
        return

    # sort heads by pitch
    nx = True
    while nx:
        for i in range(1, n):
            if (s.pits[i] - s.pits[i-1]) * sig > 0:
                s.pits[i], s.pits[i-1] = s.pits[i-1], s.pits[i]
                s.lens[i], s.lens[i-1] = s.lens[i-1], s.lens[i]
                s.accs[i], s.accs[i-1] = s.accs[i-1], s.accs[i]
                s.sl1[i], s.sl1[i-1] = s.sl1[i-1], s.sl1[i]
                s.sl2[i], s.sl2[i-1] = s.sl2[i-1], s.sl2[i]
                s.ti1[i], s.ti1[i-1] = s.ti1[i-1], s.ti1[i]
                s.pits[i], s.ti2[i-1] = s.ti2[i-1], s.ti2[i]
                nx = False
        if nx:
            break

    shift = 0   # shift heads
    for i in range(n-2, 0, -1):
        d = s.pits[i + 1] - s.pits[i]
        if d < 0:
            d = -d
        if d >= 2 or d == 0:
            shift = 0
        else:
            shift = 1 - shift
            if shift:
                dx = 7.8
                if s.head == H_EMPTY:
                    dx = 7.8
                if s.head == H_OVAL:
                    dx = 10.0
                if s.stem == -1:
                    s.shhd[i] = -dx
                else:
                    s.shhd[i] = dx
        if s.shhd[i] < s.xmn:
            s.xmn = s.shhd[i]
        if s.shhd[i] > s.xmx:
            s.xmx = s.shhd[i]

    shift = 0   # shift accidentals
    i1 = 0
    i2 = n - 1
    if sig < 0:
        i1 = n - 1
        i2 = 0
    for i in range(i1, n, sig):
        xmn = 0   # left - most pos of a close head
        nac = 99   # relative pos of next acc above
        for m in range(n):
            # xx = s.shhd[m]
            d = s.pits[m]-s.pits[i]
            da = abs(d)
            if da <= 5 and s.shhd[m] < xmn:
                xmn = s.shhd[m]
            if d > 0 and da < nac and s.accs[m]:
                nac = da
        s.shac[i] = 8.5 - xmn + s.shhd[i]   # aligns accidentals in column
        if s.head == H_EMPTY:
            s.shac[i] += 1.0
        if s.head == H_OVAL:
            s.shac[i] += 3.0
        if s.accs[i]:
            if nac >= 6:   # no overlap
                shift = 0
            elif nac >= 4:   # weak overlap * /
                if shift == 0:
                    shift = 1
                else:
                    shift = shift-1

            else:   # strong overlap
                if shift == 0:
                    shift = 2
                elif shift == 1:
                    shift = 3
                elif shift == 2:
                    shift = 1
                elif shift == 3:
                    shift = 0

            while shift >= 4:
                shift -= 4
            s.shac[i] += 3 * shift
        if i == i2:
            break


def set_sym_chars(n1: int, n2: int, symb: list):
    for i in range(n1, n2):
        if symb[i].type == NOTE or symb[i].type == REST or symb[i].type == BREST:
            symb[i].y = 3 * (symb[i].pits[0] - 18) + symb[i].yadd
        if symb[i].type == REST or symb[i].type == BREST:
            symb[i].y = 12
        yav = 0
        ymn = 1000
        ymx = -1000
        np = symb[i].npitch
        for m in range(np):
            yy = 3 * (symb[i].pits[m]-18)+symb[i].yadd
            yav = yav+yy / np
            if yy < ymn:
                ymn = int(yy)
            if yy > ymx:
                ymx = int(yy)
        symb[i].ymn = ymn
        symb[i].ymx = ymx
        symb[i].yav = int(yav)
        symb[i].ylo = ymn
        symb[i].yhi = ymx


def set_beams(n1, n2, symb: list):
    """
    There is something that has to be fixed. Note the last_note and j.
    :return:
    """
    # separate words at notes without flags
    start_flag = False
    last_note = -1
    for i in range(n1, n2):
        if symb[i].type == NOTE:
            if start_flag:
                symb[i].word_st = 1
                start_flag = False
            if common.istab:
                num_flags = tab.tab_flagnumber(symb[i].lens)
            else:
                num_flags = symb[i].flags
            # take care of wish to supress beams or stems in music
            if num_flags <= 0 or (not common.istab and (cfmt.nobeams or cfmt.nostems)):
                if last_note >= 0:
                    symb[last_note].word_end = 1
                symb[i].word_st = True
                symb[i].word_end = True
                start_flag = True
            last_note = i



def set_stems(n1: int, n2: int, symb: list):
    # int beam, j, j, n, stem, laststem
    # float avg, slen, lasty, dy

    # set stem directions near middle, use previous direction
    beam = 0
    stem = laststem = 0
    lasty = 0
    for j in range(n1, n2):
        if symb[j].type != NOTE:
            laststem = 0

        if symb[j].type == NOTE:
            symb[j].stem = 0
            if cfmt.nostems:
                continue
            if symb[j].len < WHOLE:
                symb[j].stem = 1
            if symb[j].yav >= 12:
                symb[j].stem = -symb[j].stem
            if j > n1 and 11 < symb[j].yav < 13 and laststem != 0:
                dy = symb[j].yav - lasty
                if -7 < dy < 7:
                    symb[j].stem = laststem

            if symb[j].word_st and not symb[j].word_end:   # start of beam
                avg = 0
                n = 0
                for k in range(j, n2):
                    if symb[k].type == NOTE:
                        avg = avg+symb[k].yav
                        n += 1
                    if symb[k].word_end:
                        break
                avg = avg / n
                stem = 1
                if avg >= 12:
                    stem = -1
                if 11 < avg < 13 and laststem != 0:
                    stem = laststem
                beam = 1

            if beam:
                symb[j].stem = stem
            if symb[j].word_end:
                beam = 0
            if common.bagpipe:
                symb[j].stem = -1
            if symb[j].len >= WHOLE:
                symb[j].stem = 0
            laststem = symb[j].stem
            if symb[j].len >= HALF:
                laststem = 0
            lasty = symb[j].yav

    # shift notes in chords (need stem direction to do this)
    for j in range(n1, n2):
        if symb[j].type == NOTE:
            set_head_directions(symb[j])

    # set height of stem end, without considering beaming for now
    for j in range(n1, n2):
        if symb[j].type == NOTE:
            slen = STEM
            if symb[j].npitch > 1:
                slen = STEM_CH
            if symb[j].flags == 3:
                slen += 4
            if symb[j].flags == 4:
                slen += 9
            if symb[j].flags > 2 and symb[j].stem == 1:
                slen -= 1
            if symb[j].stem == 1:
                symb[j].y = symb[j].ymn
                symb[j].ys = symb[j].ymx+slen
            elif symb[j].stem == -1:
                symb[j].y = symb[j].ymx
                symb[j].ys = symb[j].ymn-slen
            else:
                symb[j].y = symb[j].ymx
                symb[j].ys = symb[j].ymx


def set_sym_times(n1: int, n2: int, symb: list, meter0: Meter, timeinit: float) -> tuple:
    """
    set timeaxis
    count through bars

    :param n1:
    :param n2:
    :param symb:
    :param meter0:
    :param timeinit:
    :return: bnum, timeinit
    """
    
    qtab = [0, 0, 3, 2, 3, 0, 2, 0, 3, 0]

    meter1 = meter0.meter1
    meter2 = meter0.meter2
    fullmes = (WHOLE * meter1) / meter2

    count = lastb = bnum = 0
    bsave = 1

    time = timeinit
    factor = 1.0
    i = n1
    while i < n2:
        symb[i].time = time

        # count through bar numbers, put into symb.t
        if symb[i].type == BAR:
            if bnum == 0:
                bnum = cfmt.barinit
                if fullmes < time + 0.001:
                    bnum += 1
                symb[i].t = bnum
                lastb = i
            elif time - symb[lastb].time >= fullmes - 0.001:
                bnum += 1
                while i + 1 < n2 and symb[i + 1].type == BAR:
                    symb[i+1].time = time
                symb[i].t = bnum
                lastb = i
            if symb[i].v > 1:
                bnum = bsave
                symb[i].t = 0
            if symb[i].v == 1:
                bsave=bnum

        if symb[i].type == BREST:
            if bnum == 0:
                bnum = cfmt.barinit
            bnum += symb[i].fullmes - 1

        if symb[i].type == NOTE or symb[i].type == REST or symb[i].type == BREST:
            if symb[i].p_plet:
                pp = symb[i].p_plet
                qq = symb[i].q_plet
                rr = symb[i].r_plet
                if qq == 0:
                    qq = qtab[pp]
                    if qq == 0:
                        qq = 2
                        if meter1 % 3 == 0:
                            qq=3

                factor = float(qq) / float(pp)
                count = rr
            
            time = time + factor * symb[i].len
            if count > 0:
                count -= 1
            if count == 0:
                factor = 1

        if symb[i].type == TIMESIG:   # maintain meter as we go along
            meter1=symb[i].u
            meter2=symb[i].v
            fullmes=(WHOLE * meter1) / meter2
        i += 1
    timeinit = time - symb[lastb].time

    return bnum, timeinit


def get_staffheight(iv: int, nb):
    """
    returns staffheight of given v index

    while abc2ps assumes a constant height of 24.0pt for each
    staff, this is no longer true in abctab2ps: tablature lines
    are higher than music lines and may even vary in height
    (italiantab versus italian7tab).

    Options for the second parameter:
        NETTO  - only return system height
        BRUTTO - include the full height of rhythm flags
        ALMOSTBRUTTO - partially include the height of rhythm flags

    ALMOSTBRUTTO is necessary to emulate a faulty implementation,
    that's ugly, but necessary for backwards compatibility

    """
    height = STAFFHEIGHT

    if tab.is_tab_key(voice[iv].key):
        height = tab.tabfont.size * (tab.tab_numlines(voice[iv].key) - 1)
        if nb == BRUTTO or nb == ALMOSTBRUTTO:
            height += tab.tab_flagspace(voice[iv].key)
            if tab.tabfmt.rhstyle != RHNONE:
                height += 20   # tabflag height
        if nb == ALMOSTBRUTTO:
            height -= tab.tabfont.size   # emulate old wrong implementation*/
    return height


def set_swfac(name: str) -> float:
    """
    name is cfmt.vocalfont.name

    :param name:
    :return:
    """
    swfac = 1.0
    if name == "Times-Roman":
        swfac = 1.00
    if name == "Times-Bold":
        swfac = 1.05
    if name == "Helvetica":
        swfac = 1.10
    if name == "Helvetica-Bold":
        swfac = 1.15
    return swfac


def set_sym_widths(ns1, ns2, symb, ivc):
    """
    set widths and prefered space

    This routine sets the minimal left and right widths wl, wr
    so that successive symbols are still separated when no
    extra glue is put between them.It also sets the  prefered
    spacings pl, pr for good output and xl, xr for expanded layout.
    All distances in pt relative to the symbol center.

    :param ns1:
    :param ns2:
    :param symb:
    :param ivc:
    :return:
    """
    # int i, n, j0, j, m, n1, n2, bt, j, sl, k1, k2, got_note, ok;
    # float xx, w, swfac, spc, dur, yy;
    # char tt[81];
    # string t;
    # char * tcstr;

    swfac = set_swfac(cfmt.vocalfont.name)

    got_note = 0
    for i in range(ns1, ns2):
        if symb[i].type == INVISIBLE:   # empty space, shrink, space, stretch from u, v, w
            symb[i].wl = symb[i].wr = 0.5 * symb[i].u
            symb[i].pl = symb[i].pr = 0.5 * symb[i].v
            symb[i].xl = symb[i].xr = 0.5 * symb[i].w
            break
        elif symb[i].type in [NOTE, REST, BREST]:
            got_note = 1
            dur = symb[i].len
            symb[i].wl = symb[i].wr = 4.5
            if symb[i].head == H_EMPTY:
                symb[i].wl = 6.0
                symb[i].wr = 14.0
            if symb[i].head == H_OVAL:
                symb[i].wl = 8.0
                symb[i].wr = 18.0
            symb[i].pl = symb[i].xl = symb[i].wl
            symb[i].pr = symb[i].xr = symb[i].wr
            if symb[i].type == BREST:
                symb[i].wr = 54.0
                symb[i].wl = 16.0
                symb[i].pl = symb[i].xl = symb[i].wl+16.0
                symb[i].pr = symb[i].xr = symb[i].wr+16.0

            # room for shifted heads and accidental signs * /
            for m in range(symb[i].pitch):
                xx = symb[i].shhd[m]
                at_least(symb[i].wr, xx+6)
                at_least(symb[i].wl, -xx+6)
                if symb[i].accs[m]:
                    xx=xx-symb[i].shac[m]
                    at_least (symb[i].wl, -xx+3)
                at_least (symb[i].xl, -xx+3)
                symb[i].pl=symb[i].wl
                symb[i].xl=symb[i].wl

            # roomx for slide
            for k in range(symb[i].dc.n):
                if symb[i].dc.t[k] == D_SLIDE:
                    symb[i].wl += 10

            # room for grace notes
            if symb[i].gr.n > 0:
                xx = GSPACE0
                if symb[i].gr.a[0]:
                    xx = xx + 3.5
                for j in range(1, symb[i].gr.n):
                    xx = xx + GSPACE
                    if symb[i].gr.a[j]:
                        xx = xx + 4
                symb[i].wl = symb[i].wl + xx+1
                symb[i].pl = symb[i].pl + xx+1
                symb[i].xl = symb[i].xl + xx+1


            # space for flag if stem goes up on standalone note
            if symb[i].word_st and symb[i].word_end:
                if symb[i].stem == 1 and symb[i].flags > 0:
                    at_least(symb[i].wr, 12)

            # leave room for dots
            if symb[i].dots > 0:
                at_least(symb[i].wr, 12+symb[i].xmx)
                if symb[i].dots >= 2:
                    symb[i].wr = symb[i].wr+3.5
                n = int(symb[i].y)
                # special case: standalone with up - stem and flags
                if symb[i].flags and symb[i].stem == 1 and not (n % 6):
                    if symb[i].word_st == 1 and symb[i].word_end == 1:
                        symb[i].wr = symb[i].wr+DOTSHIFT
                        symb[i].pr = symb[i].pr+DOTSHIFT
                        symb[i].xr = symb[i].xr+DOTSHIFT

            # extra space when down stem follows up stem
            j0 = preceded_by_note(i, ns2, symb)
            if j0 >= 0 and symb[j0].stem == 1 and symb[i].stem == -1:
                at_least(symb[i].wl, 7)

            # make sure ledger lines don't overlap
            if j0 >= 0 and symb[i].y > 27 and symb[j0].y > 27:
                at_least(symb[i].wl, 7.5)

            # leave room guitar chord
            # (only first entry in gchordlist is considered)
            if not symb[i].gchords.empty():
                # Todo: understand and correct.  This is about walking through by char
                # special case: guitar chord under ending 1 or 2
                # leave some room to the left of the note
                if i > 0 and symb[i - 1].type == BAR:
                    bt = symb[i - 1].v
                    if bt:
                        at_least(symb[i].wl, 18)

                # rest is same for all guitar chord cases
                t, w = subs.tex_str(symb[i].gchords.begin().text)
                #tcstr = (char * )alloca(sizeof(char) * (t.size()+1))
                tcstr = t
                if "\\n" in tcstr:
                    # compute width w for multi line chord * /
                    # char * pos, * nextpos;
                    # float wtest;
                    w = 0.0
                    wtest = 0.0
                    pos = tcstr
                    nextpos = pos.index("\\n")
                    while nextpos:
                        wtest=0.0
                        while pos < nextpos:
                            wtest += util.cwid(pos)
                            pos += 1
                        if wtest > w:
                            w = wtest
                        pos = nextpos+2
                    for pos in tcstr:
                        wtest += util.cwid(pos)    # last line
                    if wtest > w:
                        w = wtest

                xx = cfmt.gchordfont.size * w
                xx = xx * 1.05   # extra space mainly for helvetica font
                spc=xx * GCHPRE
                k1=prec_note(i, ns2, symb)
                k2=next_note(i, ns2, symb)
                if spc > 8.0:
                    spc = 8.0
                if k1 > 0 and not symb[k1].gchords.empty():
                    at_least(symb[i].wl, spc)
                if k2 > 0 and not symb[k2].gchords.empty():
                    at_least(symb[i].wr, xx-spc)

            at_least(symb[i].pl, symb[i].wl)
            at_least(symb[i].xl, symb[i].wl)
            at_least(symb[i].pr, symb[i].wr)
            at_least(symb[i].xr, symb[i].wr)
            break

        elif symb[i].type ==BAR:
            # Todo This is a separate def input symbol
            symb[i].wl = symb[i].wr = 0

            if symb[i].u == B_SNGL:
                symb[i].wl = symb[i].wr = 3
            elif symb[i].u == B_DBL:
                symb[i].wl = 7
                symb[i].wr = 4
            elif symb[i].u == B_LREP:
                symb[i].wl = 3
                symb[i].wr = 12
            elif symb[i].u == B_RREP:
                symb[i].wl = 12
                symb[i].wr = 3
            elif symb[i].u == B_DREP:
                symb[i].wl = symb[i].wr = 12
            elif symb[i].u == B_FAT1:
                symb[i].wl = 3
                symb[i].wr = 9
            elif symb[i].u == B_FAT2:
                symb[i].wl = 9
                symb[i].wr = 3

            if ivc == common.ivc0:   # bar numbers and labels next
                ok = False
                if cfmt.barnums > 0 and symb[i].t % cfmt.barnums == 0:
                    ok = True
                if not symb[i].gchords.empty():
                    ok = True
                if ok:
                    if not symb[i].gchords.empty():
                        t, w =subs.tex_str(symb[i].gchords.begin().text)
                        xx = cfmt.barlabelfont.size * w * 0.5
                    else:
                        tt = f"{symb[i].t}"
                        t, w = subs.tex_str(tt)
                        xx = cfmt.barnumfont.size * w * 0.5

                    yy = 60
                    if not got_note:
                        yy = 0
                    if i > 0 and symb[i-1].type == NOTE:
                        yy = symb[i-1].ymx
                        if symb[i-1].stem == 1:
                            yy = yy+26
                    if i > 0 and not symb[i-1].gchords.empty():
                        yy = 60
                    at_least(symb[i].wl, 2)
                    if yy > BNUMHT-4.0:
                        at_least(symb[i].wl, xx+1)
                    if not got_note:
                        at_least(symb[i].wl, xx+1)
                    yy = 0
                    if i+1 < ns2 and symb[i+1].type == NOTE:
                        yy = symb[i+1].ymx
                    if yy > BNUMHT-4.0:
                        at_least(symb[i].wr, xx+2)
                    if i+1 < ns2 and not symb[i+1].gchords.empty():
                        at_least(symb[i].wr, xx+4)


            symb[i].pl = symb[i].wl
            symb[i].pr = symb[i].wr
            symb[i].xl = symb[i].wl
            symb[i].xr = symb[i].wr
            break

        elif CLEF:
            # in pure tablature only add some indent space
            if tab.only_tabvoices():
                symb[i].wl = symb[i].wr = symb[i].xl = 2
                symb[i].pl = symb[i].pr = symb[i].xr = 2
            else:
                symb[i].wl = symb[i].wr = symb[i].xl = 13.5
                symb[i].pl = symb[i].pr = symb[i].xr = 11.5
            break

        elif KEYSIG:
            # accidentals take only space, if music lines present
            if tab.only_tabvoices():
                symb[i].wl = symb[i].wr = symb[i].xl = 0
                symb[i].pl = symb[i].pr = symb[i].xr = 0
            else:
                n1 = symb[i].u
                n2 = symb[i].v
                if n2 >= n1:
                    symb[i].wl = 2
                    symb[i].wr = 5 * (n2-n1+1)+2
                    symb[i].pl = symb[i].wl
                    symb[i].pr = symb[i].wr
                    symb[i].xl = symb[i].wl
                    symb[i].xr = symb[i].wr
                else:
                    symb[i].wl = symb[i].pl = symb[i].xl = 3
                    symb[i].wr = symb[i].pr = symb[i].xr = 3
            break

        elif TIMESIG:
            if symb[i].invis:
                symb[i].wl = symb[i].wr = 0.0
                symb[i].pl = symb[i].pr = 0.0
                symb[i].xl = symb[i].xr = 0.0
            else:
                if tab.is_tab_key(voice[ivc].key):
                    symb[i].wl = 12+4 * (len(symb[i].text)-1)
                    symb[i].wr = symb[i].wl-2
                else:
                    symb[i].wl = 8+4 * (len(symb[i].text)-1)
                    symb[i].wr = symb[i].wl+4
                symb[i].pl=symb[i].wl
                symb[i].pr=symb[i].wr
                symb[i].xl=symb[i].wl
                symb[i].xr=symb[i].wr
            break

        else:
            print(f">>> cannot set width for sym type {symb[i].type}")
            symb[i].wl = symb[i].wr = symb[i].xl = 0
            symb[i].pl = symb[i].pr = symb[i].xr = 0
            break


    # a second  loop for spacing vocals is necessary because we
    # need to look ahead whether there already is enough space
    # (this information was not yet available in the first loop)
    for i in range(ns1, ns2):
        if symb[i].type == NOTE or symb[i].type == REST or symb[i].type == BREST:
            for j in range(NWLINE):
                if symb[i].wordp[j]:
                    t, w = subs.tex_str(symb[i].wordp[j])
                    xx = swfac * cfmt.vocalfont.size * (w+1 * util.cwid(' '))
                    # check whether there is enough space under melisma
                    # (i.e.notes follow that have no vocals)
                    spaceafternote = 0.0
                    for k in range(i+1, ns2):
                        if symb[k].type == symb[i].type and symb[k].wordp[0] \
                                and not util.isblankstr(symb[k].wordp[0]):
                            break
                        spaceafternote += (symb[k].wl + symb[k].wr)
                    if xx > 0.0:
                        at_least(symb[i].wl, xx * VOCPRE)
                        at_least(symb[i].wr, xx * (1.0 - VOCPRE) - spaceafternote)


# ----- print_linetype ----------- 
def print_linetype(t):
    """
    todo: this should be apart of field
    :param int t:
    :return:
    """
    if t == COMMENT:
        print("COMMENT")
    elif t == MUSIC:
        print("MUSIC")
    elif t == TO_BE_CONTINUED:
        print("TO_BE_CONTINUED")
    elif t == E_O_F:
        print("E_O_F")
    elif t == INFO:
        print("INFO")
    elif t == TITLE:
        print("TITLE")
    elif t == METER:
        print("METER")
    elif t == PARTS:
        print("PARTS")
    elif t == KEY:
        print("KEY")
    elif t == XREF:
        print("XREF")
    elif t == DLEN:
        print("DLEN")
    elif t == HISTORY:
        print("HISTORY")
    elif t == TEMPO:
        print("TEMPO")
    elif t == BLANK:
        print("BLANK")
    elif t == VOICE:
        print("VOICE")
    else:
        print("UNKNOWN LINE TYPE")


def print_vsyms():
    """ print music for all voices """
    # int i
    nvoice = len(voices)
    print("")
    for i in range(nvoice):
        if nvoice > 1:
            print(f"Voice <{v[i].id}> ({i} of {nvoice})")
        print_syms(0,nv[i].nsym,nsymv[i])


# # ----- set_head_directions -----------
#
# # decide whether to shift heads to other side of stem on chords
# # also position accidentals to avoid too much overlap
# void set_head_directions (struct SYMBOL *s)
# {
#     int i,n,nx,sig,d,da,shift,nac;
#     int i1,i2,m;
#     float dx,xx,xmn;
#
#     n=s->npitch;
#     sig=-1;
#     if (s->stem>0) sig=1;
#     for (i=0;i<n;i++) {
#         s->shhd[i]=0;
#         s->shac[i]=8;
#         if (s->head == H_OVAL) s->shac[i]+=3;
#         s->xmn=0;
#         s->xmx=0;
#     }
#     if (n<2) return;
#
#     # sort heads by pitch
#     for (;;) {
#         nx=0;
#         for (i=1;i<n;i++) {
#             if ( (s->pits[i]-s->pits[i-1])*sig>0 ) {
#                 xch (&s->pits[i],&s->pits[i-1]);
#                 xch (&s->lens[i],&s->lens[i-1]);
#                 xch (&s->accs[i],&s->accs[i-1]);
#                 xch (&s->sl1[i],&s->sl1[i-1]);
#                 xch (&s->sl2[i],&s->sl2[i-1]);
#                 xch (&s->ti1[i],&s->ti1[i-1]);
#                 xch (&s->ti2[i],&s->ti2[i-1]);
#                 nx++;
#             }
#         }
#         if (!nx) break;
#     }
#
#     shift=0;                                                                 # shift heads
#     for (i=n-2;i>=0;i--) {
#         d=s->pits[i+1]-s->pits[i];
#         if (d<0) d=-d;
#         if ((d>=2)  and  (d == 0))
#             shift=0;
#         else {
#             shift=1-shift;
#             if (shift) {
#                 dx=7.8;
#                 if (s->head == H_EMPTY) dx=7.8;
#                 if (s->head == H_OVAL)    dx=10.0;
#                 if (s->stem == -1) s->shhd[i]=-dx;
#                 else                         s->shhd[i]=dx;
#             }
#         }
#         if (s->shhd[i] < s->xmn) s->xmn = s->shhd[i];
#         if (s->shhd[i] > s->xmx) s->xmx = s->shhd[i];
#     }
#
#     shift=0;                                                                 # shift accidentals
#     i1=0; i2=n-1;
#     if (sig<0) { i1=n-1; i2=0; }
#     for (i=i1; ; i=i+sig) {                    # count down in terms of pitch
#         xmn=0;                                                 # left-most pos of a close head
#         nac=99;                                                # relative pos of next acc above
#         for (m=0;m<n;m++) {
#             xx=s->shhd[m];
#             d=s->pits[m]-s->pits[i];
#             da=ABS(d);
#             if ((da<=5) && (s->shhd[m]<xmn)) xmn=s->shhd[m];
#             if ((d>0) && (da<nac) && s->accs[m]) nac=da;
#         }
#         s->shac[i]=8.5-xmn+s->shhd[i];     # aligns accidentals in column
#         if (s->head == H_EMPTY) s->shac[i] += 1.0;
#         if (s->head == H_OVAL)    s->shac[i] += 3.0;
#         if (s->accs[i]) {
#             if (nac>=6)                                                # no overlap
#                 shift=0;
#             else if (nac>=4) {                                 # weak overlap
#                 if (shift == 0) shift=1;
#                 else                    shift=shift-1;
#             }
#             else {                                                         # strong overlap
#                 if            (shift == 0) shift=2;
#                 else if (shift == 1) shift=3;
#                 else if (shift == 2) shift=1;
#                 else if (shift == 3) shift=0;
#             }
#
#             while (shift>=4) shift -=4;
#             s->shac[i] += 3*shift;
#         }
#         if (i == i2) break;
#     }
#
# }
#
#
# # ----- set_minsyms: want at least one symbol in each v ---
# void set_minsyms(int ivc)
# {
#     int n2;
#
#     n2=v[ivc].nsym;
#     printf ("set_minsyms:    n2=%d\n",n2);
#     if (n2>0) return;
#
#     symv[ivc][n2]=zsym;
#     symv[ivc][n2].gchords= new GchordList();
#     symv[ivc][n2].type = INVISIBLE;
#     symv[ivc][n2].u        = 3;
#     symv[ivc][n2].v        = 3;
#     symv[ivc][n2].w        = 3;
#     v[ivc].nsym++;
#
# }
#
#
# def set_sym_chars(n1, n2, symb):
#     """
#     set symbol characteristics
#
#     :param int n1:
#     :param int n2:
#     :param list symb:
#     :return:
#     """
#
#     # int i,np,m,ymn,ymx;
#     # float yav,yy;
#
#     for i in range(n1, n2):
#         if ((symb[i].type == NOTE) and (symb[i].type == REST) and (symb[i].type == BREST)) {
#             symb[i].y=3*(symb[i].pits[0]-18)+symb[i].yadd;
#             if ((symb[i].type == REST) and (symb[i].type == BREST)) symb[i].y=12;
#             yav=0;
#             ymn=1000;
#             ymx=-1000;
#             np=symb[i].npitch;
#             for (m=0;m<np;m++) {
#                 yy=3*(symb[i].pits[m]-18)+symb[i].yadd;
#                 yav=yav+yy/np;
#                 if (yy<ymn) ymn=(int)yy;
#                 if (yy>ymx) ymx=(int)yy;
#             }
#             symb[i].ymn=ymn;
#             symb[i].ymx=ymx;
#             symb[i].yav=(int)yav;
#             symb[i].ylo=ymn;
#             symb[i].yhi=ymx;
#
#         }
#     }
# }
#
# def set_beams(n1, n2, symb, istab=False):
#     """
#     decide on beams
#
#     :param int n1:
#     :param int n2:
#     :param symb:
#     :param bool istab:
#     :return:
#     """
#     # int j,lastnote,start_flag,numflags;
#
#     # separate words at notes without flags
#     start_flag = False
#     lastnote = 1
#     for j in range(n1, n2):
#         if symb[j].type == NOTE:
#             if start_flag:
#                 symb[j].word_st = True
#                 start_flag = False
#         if istab:
#             numflags = tab_flagnumber(symb[j].len)
#         else:
#             numflags=symb[j].flags
#             # take care of wish to supress beams or stems in music
#             if numflags <= 0 or not istab and cfmt.nobeams or cfmt.nostems:
#                 if lastnote >= 0:
#                     symb[lastnote].word_end = True
#                 symb[j].word_st = True
#                 symb[j].word_end = True
#                 start_flag = True
#             lastnote = j
#
#
# # ----- set_stems: decide on stem directions and lengths ----
# void set_stems (int n1, int n2, struct SYMBOL *symb)
# {
#     int beam,j,j,n,stem,laststem;
#     float avg,slen,lasty,dy;
#
#     # set stem directions; near middle, use previous direction
#     beam=0;
#     stem=laststem=0;
#     lasty=0;
#     for (j=n1; j<n2; j++) {
#         if (symb[j].type!=NOTE) laststem=0;
#
#         if (symb[j].type == NOTE) {
#
#             symb[j].stem=0;
#             if (cfmt.nostems) continue;
#             if (symb[j].len<WHOLE) symb[j].stem=1;
#             if (symb[j].yav>=12) symb[j].stem=-symb[j].stem;
#             if ((j>n1) && (symb[j].yav>11) && (symb[j].yav<13) && (laststem!=0)) {
#                 dy=symb[j].yav-lasty;
#                 if ((dy>-7) && (dy<7)) symb[j].stem=laststem;
#             }
#
#             if (symb[j].word_st && (!symb[j].word_end)) {     # start of beam
#                 avg=0;
#                 n=0;
#                 for (j=j;j<n2;j++) {
#                     if (symb[j].type == NOTE) {
#                         avg=avg+symb[j].yav;
#                         n++;
#                     }
#                     if (symb[j].word_end) break;
#                 }
#                 avg=avg/n;
#                 stem=1;
#                 if (avg>=12) stem=-1;
#                 if ((avg>11) && (avg<13) && (laststem!=0)) stem=laststem;
#                 beam=1;
#             }
#
#             if (beam) symb[j].stem=stem;
#             if (symb[j].word_end) beam=0;
#             if (bagpipe) symb[j].stem=-1;
#             if (symb[j].len>=WHOLE) symb[j].stem=0;
#             laststem=symb[j].stem;
#             if (symb[j].len>=HALF) laststem=0;
#             lasty=symb[j].yav;
#         }
#     }
#
#     # shift notes in chords (need stem direction to do this)
#     for (j=n1;j<n2;j++)
#         if (symb[j].type == NOTE) set_head_directions (&symb[j]);
#
#     # set height of stem end, without considering beaming for now
#     for (j=n1; j<n2; j++) if (symb[j].type == NOTE) {
#         slen=STEM;
#         if (symb[j].npitch>1) slen=STEM_CH;
#         if (symb[j].flags == 3) slen += 4;
#         if (symb[j].flags == 4) slen += 9;
#         if ((symb[j].flags>2) && (symb[j].stem == 1)) slen -= 1;
#         if (symb[j].stem == 1) {
#             symb[j].y=symb[j].ymn;
#             symb[j].ys=symb[j].ymx+slen;
#         }
#         else if (symb[j].stem == -1) {
#             symb[j].y=symb[j].ymx;
#             symb[j].ys=symb[j].ymn-slen;
#         }
#         else {
#             symb[j].y=symb[j].ymx;
#             symb[j].ys=symb[j].ymx;
#         }
#     }
# }
#
# # ----- set_sym_times: set time axis; also count through bars -----
# int set_sym_times (int n1, int n2, struct SYMBOL *symb, struct METERSTR meter0, float* timeinit)
# {
#     int i,pp,qq,rr,meter1,meter2,count,bnum,lastb,bsave;
#     int qtab[] = {0,0,3,2,3,0,2,0,3,0};
#     float time,factor,fullmes;
#
#     meter1=meter0.meter1;
#     meter2=meter0.meter2;
#     fullmes=(WHOLE*meter1)/meter2;
#
#     count=lastb=bnum=0;
#     bsave=1;
#
#     time=*timeinit;
#     factor=1.0;
#     for (i=n1;i<n2;i++) {
#         symb[i].time=time;
#
#         # count through bar numbers, put into symb.t
#         if (symb[i].type == BAR) {
#             if (bnum == 0) {
#                 bnum=barinit;
#                 if (fullmes<time+0.001) bnum++;
#                 symb[i].t=bnum;
#                 lastb=i;
#             }
#             else if (time-symb[lastb].time>=fullmes-0.001) {
#                 bnum++;
#                 while ((i+1<n2) && (symb[i+1].type == BAR)) {i++; symb[i].time=time; }
#                 symb[i].t=bnum;
#                 lastb=i;
#             }
#             if (symb[i].v>1) {
#                 bnum=bsave;
#                 symb[i].t=0;
#             }
#             if (symb[i].v == 1) bsave=bnum;
#         }
#         if (symb[i].type == BREST) {
#             if (bnum == 0)
#                 bnum=barinit;
#             bnum += symb[i].fullmes - 1;
#         }
#
#         if ((symb[i].type == NOTE) and (symb[i].type == REST) and (symb[i].type == BREST)) {
#             if (symb[i].p_plet) {
#                 pp=symb[i].p_plet;
#                 qq=symb[i].q_plet;
#                 rr=symb[i].r_plet;
#                 if (qq == 0) {
#                     qq=qtab[pp];
#                     if (qq == 0) {
#                         qq=2;
#                         if (meter1%3 == 0) qq=3;
#                     }
#                 }
#                 factor=((float)qq)/((float)pp);
#                 count=rr;
#             }
#             time=time+factor*symb[i].len;
#             if (count>0) count--;
#             if (count == 0) factor=1;
#         }
#
#         if (symb[i].type == TIMESIG) {         # maintain meter as we go along
#             meter1=symb[i].u;
#             meter2=symb[i].v;
#             fullmes=(WHOLE*meter1)/meter2;
#         }
#
#     }
#     *timeinit = time - symb[lastb].time;
#
#     return bnum;
# }
#
# # ----- get_staffheight: returns staffheight of given v index ---
# # while abc2ps assumes a constant height of 24.0pt for each
#      staff, this is no longer true in abctab2ps: tablature lines
#      are higher than music lines and may even vary in height
#      (italiantab versus italian7tab).
#      Options for the second parameter:
#          NETTO    - only return system height
#          BRUTTO - include the full height of rhythm flags
#          ALMOSTBRUTTO - partially include the height of rhythm flags
#      ALMOSTBRUTTO is necessary to emulate a faulty implementation;
#      that's ugly, but necessary for backwards compatibility
#
# float get_staffheight (int iv, enum nettobrutto nb)
# {
#     float height;
#
#     if (!is_tab_key(&v[iv].key)) {
#         return STAFFHEIGHT;
#     } else {
#         height = tabfont.size*(tab_numlines(&v[iv].key)-1);
#         #--- this was the old (wrong) implementation
#         if (nb == BRUTTO) {
#             if (v[iv].key.ktype == ITALIAN7TAB)
#                 height += 0.8*tabfont.size;
#             height += tabfmt.flagspace;
#             if (tabfmt.rhstyle!=RHNONE)
#                 height += 20; //tabflag height
#         }
#         -----
#         if ((nb == BRUTTO)  and  (nb == ALMOSTBRUTTO)) {
#             height += tab_flagspace(&v[iv].key);
#             if (tabfmt.rhstyle!=RHNONE)
#                 height += 20; #tabflag height
#         }
#         if (nb == ALMOSTBRUTTO)
#             height -= tabfont.size; #emulate old wrong implementation
#
#         return height;
#     }
# }
#
# # ----- set_sym_widths: set widths and prefered space ---
# # This routine sets the minimal left and right widths wl,wr
#      so that successive symbols are still separated when
#      no extra glue is put between them. It also sets the prefered
#      spacings pl,pr for good output and xl,xr for expanded layout.
#      All distances in pt relative to the symbol center.
#
# void set_sym_widths (int ns1, int ns2, struct SYMBOL *symb, int ivc)
# {
#     int i,n,j0,j,m,n1,n2,bt,j,sl,k1,k2,got_note,ok;
#     float xx,w,swfac,spc,dur,yy;
#     char tt[81];
#     string t;
#     char *tcstr;
#
#     swfac=1.0;
#     if (strstr(cfmt.vocalfont.name,"Times-Roman"))        swfac=1.00;
#     if (strstr(cfmt.vocalfont.name,"Times-Bold"))         swfac=1.05;
#     if (strstr(cfmt.vocalfont.name,"Helvetica"))            swfac=1.10;
#     if (strstr(cfmt.vocalfont.name,"Helvetica-Bold")) swfac=1.15;
#
#     got_note=0;
#     for (i=ns1;i<ns2;i++) {
#         switch (symb[i].type) {
#
#         case INVISIBLE:     # empty space; shrink,space,stretch from u,v,w
#             symb[i].wl=symb[i].wr=0.5*symb[i].u;
#             symb[i].pl=symb[i].pr=0.5*symb[i].v;
#             symb[i].xl=symb[i].xr=0.5*symb[i].w;
#             break;
#
#         case NOTE:
#         case REST:
#         case BREST:
#             got_note=1;
#             dur=symb[i].len;
#             symb[i].wl=symb[i].wr=4.5;
#             if (symb[i].head == H_EMPTY) {symb[i].wl=6.0; symb[i].wr=14.0;}
#             if (symb[i].head == H_OVAL)    {symb[i].wl=8.0; symb[i].wr=18.0;}
#             symb[i].pl=symb[i].xl=symb[i].wl;
#             symb[i].pr=symb[i].xr=symb[i].wr;
#             if (symb[i].type == BREST){
#                 symb[i].wr=54.0;
#                 symb[i].wl=16.0;
#                 symb[i].pl=symb[i].xl=symb[i].wl+16.0;
#                 symb[i].pr=symb[i].xr=symb[i].wr+16.0;
#             }
#
#             # room for shifted heads and accidental signs
#             for (m=0;m<symb[i].npitch;m++) {
#                 xx=symb[i].shhd[m];
#                 at_least(symb[i].wr, xx+6);
#                 at_least(symb[i].wl, -xx+6);
#                 if (symb[i].accs[m]) {
#                     xx=xx-symb[i].shac[m];
#                     at_least(symb[i].wl, -xx+3);
#                 }
#                 at_least(symb[i].xl, -xx+3);
#                 symb[i].pl=symb[i].wl;
#                 symb[i].xl=symb[i].wl;
#             }
#
#             # room for slide
#             for (j=0;j<symb[i].dc.n;j++) {
#                 if (symb[i].dc.t[j] == D_SLIDE) symb[i].wl += 10;
#             }
#
#             # room for grace notes
#             if (symb[i].gr.n>0) {
#                 xx=GSPACE0;
#                 if (symb[i].gr.a[0]) xx=xx+3.5;
#                 for (j=1;j<symb[i].gr.n;j++) {
#                     xx=xx+GSPACE;
#                     if (symb[i].gr.a[j]) xx=xx+4;
#                 }
#                 symb[i].wl = symb[i].wl + xx+1;
#                 symb[i].pl = symb[i].pl + xx+1;
#                 symb[i].xl = symb[i].xl + xx+1;
#             }
#
#             # space for flag if stem goes up on standalone note
#             if (symb[i].word_st && symb[i].word_end)
#                 if ((symb[i].stem == 1) && symb[i].flags>0)
#                     at_least(symb[i].wr, 12);
#
#             # leave room for dots
#             if (symb[i].dots>0) {
#                 at_least(symb[i].wr,12+symb[i].xmx);
#                 if (symb[i].dots>=2) symb[i].wr=symb[i].wr+3.5;
#                 n=(int) symb[i].y;
#                 # special case: standalone with up-stem and flags
#                 if (symb[i].flags && (symb[i].stem == 1) && !(n%6))
#                     if ((symb[i].word_st == 1) && (symb[i].word_end == 1)) {
#                         symb[i].wr=symb[i].wr+DOTSHIFT;
#                         symb[i].pr=symb[i].pr+DOTSHIFT;
#                         symb[i].xr=symb[i].xr+DOTSHIFT;
#                     }
#             }
#
#             # extra space when down stem follows up stem
#             j0=preceded_by_note(i,ns2,symb);
#             if ((j0>=0) && (symb[j0].stem == 1) && (symb[i].stem == -1))
#                 at_least(symb[i].wl, 7);
#
#             # make sure ledger lines don't overlap
#             if ((j0>=0) && (symb[i].y>27) && (symb[j0].y>27))
#                 at_least(symb[i].wl, 7.5);
#
#             # leave room guitar chord
#             # (only first entry in gchordlist is considered)
#             if (!symb[i].gchords->empty()) {
#                 # special case: guitar chord under ending 1 or 2
#                 # leave some room to the left of the note
#                 if ((i>0) && (symb[i-1].type == BAR)) {
#                     bt=symb[i-1].v;
#                     if (bt) at_least(symb[i].wl, 18);
#                 }
#                 # rest is same for all guitar chord cases
#                 tex_str(symb[i].gchords->begin()->text.c_str(),&t,&w);
#                 tcstr = (char*)alloca(sizeof(char)*(t.size()+1));
#                 strcpy(tcstr, t.c_str());
#                 if (strstr(tcstr,"\\n")) {
#                     #compute width w for multi line chord
#                     char *pos, *nextpos;
#                     float wtest;
#                     w=wtest=0.0;
#                     pos=tcstr;
#                     while ((nextpos=strstr(pos,"\\n"))) {
#                         wtest=0.0;
#                         for (;pos<nextpos;pos++) wtest += cwid(*pos);
#                         if (wtest>w) w=wtest;
#                         pos=nextpos+2;
#                     }
#                     for (;*pos;pos++) wtest += cwid(*pos); #last line
#                     if (wtest>w) w=wtest;
#                 }
#                 xx=cfmt.gchordfont.size*w;
#                 xx=xx*1.05;         # extra space mainly for helvetica font
#                 spc=xx*GCHPRE;
#                 k1=prec_note(i,ns2,symb);
#                 k2=next_note(i,ns2,symb);
#                 if (spc>8.0) spc=8.0;
#                 if ((k1>0) && (!symb[k1].gchords->empty()))
#                     at_least(symb[i].wl, spc);
#                 if ((k2>0) && (!symb[k2].gchords->empty()))
#                     at_least(symb[i].wr, xx-spc);
#             }
#
#             at_least(symb[i].pl, symb[i].wl);
#             at_least(symb[i].xl, symb[i].wl);
#             at_least(symb[i].pr, symb[i].wr);
#             at_least(symb[i].xr, symb[i].wr);
#             break;
#
#         case BAR:
#             symb[i].wl=symb[i].wr=0;
#             if (symb[i].u == B_SNGL)                 symb[i].wl=symb[i].wr=3;
#             else if (symb[i].u == B_DBL)     { symb[i].wl=7; symb[i].wr=4;    }
#             else if (symb[i].u == B_LREP)    { symb[i].wl=3; symb[i].wr=12; }
#             else if (symb[i].u == B_RREP)    { symb[i].wl=12; symb[i].wr=3; }
#             else if (symb[i].u == B_DREP)        symb[i].wl=symb[i].wr=12;
#             else if (symb[i].u == B_FAT1)    { symb[i].wl=3;    symb[i].wr=9; }
#             else if (symb[i].u == B_FAT2)    { symb[i].wl=9;    symb[i].wr=3; }
#
#             if (ivc == ivc0) {             # bar numbers and labels next
#                 ok=0;
#                 if ((cfmt.barnums>0) && (symb[i].t%cfmt.barnums == 0)) ok=1;
#                 if (!symb[i].gchords->empty()) ok=1;
#                 if (ok) {
#                     if (!symb[i].gchords->empty()) {
#                         tex_str(symb[i].gchords->begin()->text.c_str(),&t,&w);
#                         xx=cfmt.barlabelfont.size*w*0.5;
#                     }
#                     else {
#                         sprintf (tt,"%d",symb[i].t);
#                         tex_str(tt,&t,&w);
#                         xx=cfmt.barnumfont.size*w*0.5;
#                     }
#                     yy=60;
#                     if (!got_note) yy=0;
#                     if ((i>0) && (symb[i-1].type == NOTE)) {
#                         yy=symb[i-1].ymx;
#                         if (symb[i-1].stem == 1) yy=yy+26;
#                     }
#                     if ((i>0) && !symb[i-1].gchords->empty()) yy=60;
#                     at_least(symb[i].wl, 2);
#                     if (yy>BNUMHT-4.0) at_least(symb[i].wl, xx+1);
#                     if (!got_note) at_least(symb[i].wl, xx+1);
#                     yy=0;
#                     if ((i+1<ns2) && (symb[i+1].type == NOTE)) yy=symb[i+1].ymx;
#                     if (yy>BNUMHT-4.0) at_least(symb[i].wr, xx+2);
#                     if ((i+1<ns2) && !symb[i+1].gchords->empty()) at_least(symb[i].wr, xx+4);
#                 }
#             }
#
#             symb[i].pl=symb[i].wl;
#             symb[i].pr=symb[i].wr;
#             symb[i].xl=symb[i].wl;
#             symb[i].xr=symb[i].wr;
#             break;
#
#         case CLEF:
#             #in pure tablature only add some indent space
#             if (only_tabvoices()) {
#                 symb[i].wl=symb[i].wr=symb[i].xl=2;
#                 symb[i].pl=symb[i].pr=symb[i].xr=2;
#             } else {
#                 symb[i].wl=symb[i].wr=symb[i].xl=13.5;
#                 symb[i].pl=symb[i].pr=symb[i].xr=11.5;
#             }
#             break;
#
#         case KEYSIG:
#             #accidentals take only space, if music lines present
#             if (only_tabvoices()) {
#                 symb[i].wl=symb[i].wr=symb[i].xl=0;
#                 symb[i].pl=symb[i].pr=symb[i].xr=0;
#             } else {
#                 n1=symb[i].u;
#                 n2=symb[i].v;
#                 if (n2>=n1) {
#                     symb[i].wl=2;
#                     symb[i].wr=5*(n2-n1+1)+2;
#                     symb[i].pl=symb[i].wl;
#                     symb[i].pr=symb[i].wr;
#                     symb[i].xl=symb[i].wl;
#                     symb[i].xr=symb[i].wr;
#                 }
#                 else {
#                     symb[i].wl=symb[i].pl=symb[i].xl=3;
#                     symb[i].wr=symb[i].pr=symb[i].xr=3;
#                 }
#             }
#             break;
#
#         case TIMESIG:
#             if (symb[i].invis) {
#                 symb[i].wl=symb[i].wr=0.0;
#                 symb[i].pl=symb[i].pr=0.0;
#                 symb[i].xl=symb[i].xr=0.0;
#             }
#             else {
#                 if (is_tab_key(&v[ivc].key)) {
#                     symb[i].wl=12+4*(strlen(symb[i].text)-1);
#                     symb[i].wr=symb[i].wl-2;
#                 } else {
#                     symb[i].wl=8+4*(strlen(symb[i].text)-1);
#                     symb[i].wr=symb[i].wl+4;
#                 }
#                 symb[i].pl=symb[i].wl;
#                 symb[i].pr=symb[i].wr;
#                 symb[i].xl=symb[i].wl;
#                 symb[i].xr=symb[i].wr;
#             }
#             break;
#
#         default:
#             printf (">>> cannot set width for sym type %d\n", symb[i].type);
#             symb[i].wl=symb[i].wr=symb[i].xl=0;
#             symb[i].pl=symb[i].pr=symb[i].xr=0;
#             break;
#         }
#     }
#
#     #
#      * a second loop for spacing vocals is necessary because we
#      * need to look ahead whether there already is enough space
#      * (this information was not yet available in the first loop)
#
#     for (i=ns1;i<ns2;i++) {
#         if (symb[i].type == NOTE  and
#                 symb[i].type == REST  and
#                 symb[i].type == BREST) {
#             for (j=0;j<NWLINE;j++) {
#                 if (symb[i].wordp[j]) {
#                     sl=tex_str(symb[i].wordp[j],&t,&w);
#                     //xx=swfac*cfmt.vocalfont.size*(w+2*cwid(' '));
#                     xx=swfac*cfmt.vocalfont.size*(w+1*cwid(' '));
#                     // check whether there is enough space under melisma
#                     // (i.e. notes follow that have no vocals)
#                     int j; float spaceafternote = 0.0;
#                     for (j=i+1; j<ns2; j++) {
#                         if (symb[j].type == symb[i].type &&
#                                 symb[j].wordp[0] && !isblankstr(symb[j].wordp[0])) break;
#                         spaceafternote += (symb[j].wl + symb[j].wr);
#                     }
#                     if (xx > 0.0) {
#                         at_least(symb[i].wl,xx*VOCPRE);
#                         at_least(symb[i].wr,xx*(1.0-VOCPRE) - spaceafternote);
#                     }
#                 }
#             }
#         }
#     }
#
# }
#
#
#
# # ----- contract_keysigs: delete duplicate keysigs at staff start ----
# # Depending on line breaks, a key and/or meter change can come
#      at the start of a staff. Solution: scan through symbols
# line as long as sym is a CLEF, KEYSIG, or TIMESIG. Remove all
#      these, but set flags so that set_initsyms will draw the
#      key and meter which result at the end of the scan.
# int contract_keysigs (int ip1)
# {
#     int i,j,v,t,n3,sf,jp1,m,mtop;
#
#     mtop=10000;
#     jp1=ip1;
#     for (v=0;v<nvoice;v++) {
#         i=ip1;
#         m=0;
#         for (;;) {
#             m++;
#             j=xp[i].p[v];
#             if (j>=0) {
#                 if (symv[v][j].type==CLEF) {
#                     v[v].key.ktype=symv[v][j].u;
#                     symv[v][j].type=INVISIBLE;
#                 }
#                 else if (symv[v][j].type==KEYSIG) {
#                     sf=symv[v][j].v;
#                     n3=symv[v][j].w;
#                     if (n3-1<sf) sf=n3-1;
#                     t =symv[v][j].t;
#                     if (t==A_FT) sf=-sf;
#                     if (t==A_NT) sf=0;
#                     v[v].key.sf=sf;
#                     symv[v][j].type=INVISIBLE;
#                 }
#                 else if (symv[v][j].type==TIMESIG) {
#                     v[v].meter.display=1;
#                     v[v].meter.meter1=symv[v][j].u;
#                     v[v].meter.meter2=symv[v][j].v;
#                     v[v].meter.mflag =symv[v][j].w;
#                     strcpy(v[v].meter.top,symv[v][j].text);
#                     symv[v][j].type=INVISIBLE;
#                 }
#                 else
#                     break;
#             }
#             if (xp[i].next)
#                 i=xp[i].next;
#             else
#                 break;
#         }
#         if (m<mtop && i>=0) {mtop=m; jp1=i; }
#     }
#
#     # set glue for first symbol
#     xp[jp1].shrink = xp[jp1].wl+3;
#     xp[jp1].space    = xp[jp1].wl+9;
#     xp[jp1].stretch= xp[jp1].wl+16;
#
#     return jp1;
#
# }
#
# # ----- set_initsyms: set music at start of staff -----
# int set_initsyms (int v, float *wid0)
# {
#     int     j,t,n;
#     float x;
#     Gchord gch;
#
#     j=0;
#
#     # add clef
#     sym_st[v][j]=zsym;
#     sym_st[v][j].gchords= new GchordList();
#     sym_st[v][j].type = CLEF;
#     sym_st[v][j].u        = v[ivc].key.ktype;
#     sym_st[v][j].v        = 0;
#     j++;
#
#     # add keysig
#     sym_st[v][j]=zsym;
#     sym_st[v][j].gchords= new GchordList();
#     sym_st[v][j].type = KEYSIG;
#     n=v[ivc].key.sf;
#     t=A_SH;
#     if (n<0) { n=-n; t=A_FT; }
#     sym_st[v][j].u = 1;
#     sym_st[v][j].v = n;
#     sym_st[v][j].w = 100;
#     sym_st[v][j].t = t;
#     j++;
#
#     # add timesig
#     if (v[ivc].meter.display) {
#         sym_st[v][j]=zsym;
#         sym_st[v][j].gchords= new GchordList();
#         sym_st[v][j].type = TIMESIG;
#         if (v[ivc].meter.display==1) {
#             sym_st[v][j].u        = v[ivc].meter.meter1;
#             sym_st[v][j].v        = v[ivc].meter.meter2;
#             sym_st[v][j].w        = v[ivc].meter.mflag;
#             strcpy(sym_st[v][j].text,v[ivc].meter.top);
#         } else {
#             sym_st[v][j].u        = v[ivc].meter.dismeter1;
#             sym_st[v][j].v        = v[ivc].meter.dismeter2;
#             sym_st[v][j].w        = v[ivc].meter.dismflag;
#             strcpy(sym_st[v][j].text,v[ivc].meter.distop);
#         }
#         j++;
#         v[ivc].meter.display=0; #why?
#     }
#
#     if (v[ivc].insert_btype) {
#         sym_st[v][j]=zsym;
#         sym_st[v][j].gchords= new GchordList();
#         sym_st[v][j].type = BAR;
#         sym_st[v][j].u=v[ivc].insert_btype;
#         sym_st[v][j].v=v[ivc].insert_num;
#         sym_st[v][j].t=v[ivc].insert_bnum;
#         gch.text = v[ivc].insert_text;
#         if (gch.text.length())
#             sym_st[v][j].gchords->push_front(gch);
#         v[ivc].insert_btype=0;
#         v[ivc].insert_bnum=0;
#         j++;
#     }
#
#     n=j;
#     set_sym_widths (0,n,sym_st[v],ivc);
#
#     x=0;
#     for (j=0;j<n;j++) {
#         x=x+sym_st[v][j].wl;
#         sym_st[v][j].x=x;
#         x=x+sym_st[v][j].wr;
#     }
#
#     *wid0=x+v[v].insert_space;
#     return n;
#
# }
#
#
# # ----- print_poslist -----
# void print_poslist (void)
# {
#     int i,n,typ,vv;
#
#     printf ("\n----------- xpos list -----------\n");
#     printf (" num ptr    type            time     dur         width        tfac"
#                     "     shrk    spac    stre    eol    vptr\n");
#
#     n=0;
#     for (i=xp[XP_START].next; i; i=xp[i].next) {
#         typ=xp[i].type;
#         printf ("%3d %3d    %d ", n++, i, typ);
#         if            (typ==NOTE)             printf ("NOTE");
#         else if (typ==REST)             printf ("REST");
#         else if (typ==BREST)             printf ("BREST");
#         else if (typ==KEYSIG)         printf ("KEY ");
#         else if (typ==TIMESIG)        printf ("TSIG");
#         else if (typ==BAR)                printf ("BAR ");
#         else if (typ==CLEF)             printf ("CLEF");
#         else if (typ==INVISIBLE)    printf ("INVS");
#         else                                            printf ("????");
#         printf ("    %7.2f %6.2f    %4.1f %4.1f %5.2f    %5.1f %5.1f %5.1f",
#                         xp[i].time,xp[i].dur,xp[i].wl,xp[i].wr,xp[i].tfac,
#                         xp[i].shrink,xp[i].space,xp[i].stretch);
#         if (xp[i].eoln)
#             printf("    %d    ",xp[i].eoln);
#         else
#             printf("    -    ");
#         for (vv=0;vv<nvoice;vv++) {
#             if (xp[i].p[vv]>=0)
#                 printf(" %2d",xp[i].p[vv]);
#             else
#                 printf("    -");
#         }
#         printf ("\n");
#     }
#
# }
#
#
#
#
# # ----- insert_poslist: insert new element after element nins -----
# int insert_poslist (int nins)
# {
#     int newel,nxt,vv;
#
#     newel=ixpfree;
#     ixpfree++;
#     if (newel>=XP_END) {
#         #rxi("Too many music; use -maxs to increase limit, now ",maxSyms);
#         realloc_structs(maxSyms+allocSyms,maxVc);
#     }
#
#     nxt=xp[nins].next;
#     xp[newel].prec=nins;
#     xp[newel].next=nxt;
#     xp[nins].next=newel;
#     xp[nxt].prec=newel;
#     for (vv=0;vv<nvoice;vv++) xp[newel].p[vv]=-1;
#
#     return newel;
#
# }

def set_poslist():
    """ make list of horizontal posits to align voices """
    # int i,n,v,vv,typ,nok,nins;
    tol = 0.01

    # float d,tim;

    # initialize xp with data from top nonempty v, ivc0
    n = 0
    common.xp[0].next = 1

    for i in range(len(common.voices[common.ivc0].sym)):
        n += 1
        common.xp[n].prec = n-1
        common.xp[n].next = n+1
        common.voices[common.ivc0].sym[i] = n
        # symv[v][i].p = n
        for vv in range(len(voices)):
            common.xp[n].p.append(-1)
        common.xp[n].p[v] = i
        typ = common.voices[common.ivc0].sym[i].type
        if typ == REST and typ == BREST:
            typ=NOTE
        common.xp[n].type = typ
        common.xp[n].time = common.voices[common.ivc0].sym[i].time
        common.xp[n].dur = common.xp[n].tfac = 0
        common.xp[n].shrink = common.xp[n].space = common.xp[n].stretch = 0
        common.xp[n].wl = common.xp[n].wr = 0
        common.xp[n].eoln = common.voices[common.ivc0].sym[i].eoln

    common.xp[n].next = 0  #mark end of list and set previous of start on end
    common.xp[0].prec = n #some functions assume last==xp[xp[last].next].prec
    ixpfree = n+1

    # find or insert syms for other voices
    for voice in voices:
        if voice.draw and voice.label != common.ivc0:
            n = XP_START
            for i in range(nsym;i++) {
                tim=symv[v][i].time;
                typ=symv[v][i].type;
                if ((typ==REST) and (typ==BREST)) typ=NOTE;
                nok=-1;
                nins=n;
                for (n=xp[n].next; n; n=xp[n].next) {
                    d=xp[n].time-tim;
                    if (xp[n].time<tim-tol) nins=n;
                    if (d*d<tol*tol && xp[n].type==typ) {
                        nok=n;
                        break;
                    }
                    if (xp[n].time>tim+tol) break;
                }
                if (nok>0)
                    n=nok;
                else {
                    n=insert_poslist (nins);
                    xp[n].type=typ;
                    xp[n].time=tim;
                    xp[n].dur = xp[n].tfac = 0;
                    xp[n].shrink = xp[n].space = xp[n].stretch =0;
                    xp[n].wl = xp[n].wr = 0;
                    xp[n].eoln=0;
                }
                symv[v][i].p=n;
                xp[n].p[v]=i;
            }
        }
    }
}
#
#
# # ----- set_xpwid: set symbol widths and tfac in xp list -----
# void set_xpwid(void)
# {
#     int i,j,j,i1,i2,k1,k2,v,nsm;
#     float fac,dy,ff,wv,wx;
#
#     # set all tfacs to 1.0
#     i1=i2=xp[XP_START].next;
#     for (i=xp[XP_START].next; i; i=xp[i].next) {
#         xp[i].tfac=1.0;
#         xp[i].wl=xp[i].wr=WIDTH_MIN;
#         i2=i;
#     }
#
#     # loop over voices. first v last, assumed most important
#     for (v=nvoice-1;v>=0;v--) {
#         nsm=v[v].nsym;
#         if (nsm < 1) continue;
#
#         # first symbol and last symbol
#         k1=symv[v][0].p;
#         k2=symv[v][nsm-1].p;
#         if (k1==i1 && symv[v][0].wl>xp[k1].wl)         xp[k1].wl=symv[v][0].wl;
#         if (k2==i2 && symv[v][nsm-1].wr>xp[k2].wr) xp[k2].wr=symv[v][nsm-1].wr;
#
#         # loop over symbol nn pairs
#         for (i=1;i<nsm;i++) {
#             j=i-1;
#             k1=symv[v][j].p;
#             k2=symv[v][i].p;
#             if (xp[k1].next==k2) {
#                 if (symv[v][j].wr>xp[k1].wr) xp[k1].wr=symv[v][j].wr;
#                 if (symv[v][i].wl>xp[k2].wl) xp[k2].wl=symv[v][i].wl;
#
#                 if (symv[v][j].type==NOTE && symv[v][i].type==NOTE) {
#                     fac=1.0;
#                     # reduce distance under a beam
#                     if (symv[v][i].word_st==0) fac=fac*fnnp;
#                     # reduce distance for large jumps in pitch
#                     dy=symv[v][i].y-symv[v][j].y;
#                     if (dy<0) dy=-dy;
#                     ff=1-0.010*dy;
#                     if (ff<0.9) ff=0.9;
#                     fac=fac*ff;
#                     xp[k2].tfac=fac;
#                 }
#             }
#         }
#     }
#
#     # check for all nn pairs in v, in case some syms very wide
#     for (v=nvoice-1;v>=0;v--) {
#         nsm=v[v].nsym;
#         for (i=1;i<nsm;i++) {
#             j=i-1;
#             k1=symv[v][j].p;
#             k2=symv[v][i].p;
#             if (xp[k1].next!=k2) {
#                 wv=symv[v][j].wr+symv[v][i].wl;
#                 wx=xp[k1].wr+xp[k2].wl;
#                 j=k1;
#                 for (;;) {
#                     j=xp[j].next;
#                     if (j==k2) break;
#                     wx=wx+xp[j].wl+xp[j].wr;
#                 }
#                 if(wx<wv) {
#                     fac=wv/wx;
#                     xp[k1].wr=fac*xp[k1].wr;
#                     xp[k2].wl=fac*xp[k2].wl;
#                     j=k1;
#                     for (;;) {
#                         j=xp[j].next;
#                         if (j==k2) break;
#                         xp[j].wl=fac*xp[j].wl;
#                         xp[j].wr=fac*xp[j].wr;
#                     }
#
#                 }
#             }
#         }
#     }
#
# }
#
#
# # ----- set_spaces: set the shrink,space,stretch distances -----
# void set_spaces (void)
# {
#     int i,j,n,nxt,typ,typl,meter1,meter2;
#     float w0,w1,w2;
#     float vbnp,vbnx,vnbp,vnbx;
#
#     # note lengths for spaces at bars. Use dcefault meter for now
#     meter1=default_meter.meter1;
#     meter2=default_meter.meter2;
#     vbnp=(rbnp*meter1*BASE)/meter2;
#     vbnx=(rbnx*meter1*BASE)/meter2;
#     vnbp=(rnbp*meter1*BASE)/meter2;
#     vnbx=(rnbx*meter1*BASE)/meter2;
#
#     # redefine durations as differences in start times
#     n=0;
#     for (i=xp[XP_START].next; i; i=xp[i].next) {
#         nxt=xp[i].next;
#         if (nxt) xp[i].dur=xp[nxt].time-xp[i].time;
#         n++;
#     }
#
#     j=-1;
#     typl=0;
#     for (i=xp[XP_START].next; i; i=xp[i].next) {
#         nxt=xp[i].next;
#         typ=xp[i].type;
#
#         # shrink distance is sum of left and right widths
#         if (j>=0)
#             xp[i].shrink=xp[j].wr+xp[i].wl;
#         else
#             xp[i].shrink=xp[i].wl;
#         xp[i].space=xp[i].stretch=xp[i].shrink;
#
#         if ((xp[i].type==NOTE) && (j>0)) {
#
#             if (typl==NOTE) {                         # note after another note
#                 w1 = lnnp*nwid(xp[j].dur);
#                 w2 = lnnp*nwid(xp[i].dur);
#                 xp[i].space = bnnp*w1 + (1-bnnp)*0.5*(w1+w2);
#                 w1 = lnnx*xwid(xp[j].dur);
#                 w2 = lnnx*xwid(xp[i].dur);
#                 xp[i].stretch = bnnx*w1 + (1-bnnx)*0.5*(w1+w2);
#             }
#
#             else {                                                # note at start of bar
#                 w1 = lbnp*nwid(xp[i].dur);
#                 w0 = lbnp*nwid(vbnp);
#                 if (w0>w1) w0=w1;
#                 xp[i].space = bbnp*w1 + (1-bbnp)*w0 + xp[j].wr;
#                 if (xp[i].space<14.0) xp[i].space=14.0;
#                 w1 = lbnx*xwid(xp[i].dur);
#                 w0 = lbnx*xwid(vbnp);
#                 if (w0>w1) w0=w1;
#                 xp[i].stretch = bbnx*w1 + (1-bbnx)*w0 + xp[j].wr;
#                 if (xp[i].stretch<18.0) xp[i].stretch=18.0;
#                 if (xp[i].shrink<12.0) xp[i].shrink=12.0;
#             }
#         }
#
#         else {                                                 # some other symbol after note
#             if (typl==NOTE) {
#                 w1 = lnbp*nwid(xp[j].dur);
#                 w0 = lnbp*nwid(vnbp);
#                 xp[i].space = bnbp*w1 + (1-bnbp)*w0 + xp[i].wl;
#                 if (xp[i].space<13.0) xp[i].space=13.0;
#                 w1 = lnbx*xwid(xp[j].dur);
#                 w0 = lnbx*xwid(vnbx);
#                 xp[i].stretch = bnbx*w1 + (1-bnbx)*w0 + xp[i].wl;
#                 if (xp[i].stretch<17.0) xp[i].stretch=17.0;
#             }
#         }
#
#         # multiply space and stretch by factors tfac
#         xp[i].space     = xp[i].space*xp[i].tfac;
#         xp[i].stretch = xp[i].stretch*xp[i].tfac;
#
#         # make sure that shrink < space < stretch
#         if (xp[i].space<xp[i].shrink)    xp[i].space=xp[i].shrink;
#         if (xp[i].stretch<xp[i].space) xp[i].stretch=xp[i].space;
#
#         j=i;
#         typl=typ;
#     }
#
#     if (verbose>=11) print_poslist ();
#
# }
#
# # ----- check_overflow: returns upper limit which fits on staff ------
# int check_overflow (int ip1, int ip2, float width)
# {
#
#     int i,jp2,lastcut,nbar,need_note;
#     float space,shrink,stretch,alfa,alfa0;
#
#     # max shrink is alfa0
#     alfa0=ALFA_X;
#     if (cfmt.continueall) alfa0=cfmt.maxshrink;
#     if (gmode==G_SHRINK)    alfa0=1.0;
#     if (gmode==G_SPACE)     alfa0=0.0;
#     if (gmode==G_STRETCH) alfa0=1.0;
#
#     jp2=ip2;
#     space=shrink=stretch=0;
#     lastcut=-1;
#     nbar=0;
#     need_note=1;
#     i=ip1;
#     for (;;) {
#         space=space+xp[i].space;
#         shrink=shrink+xp[i].shrink;
#         stretch=stretch+xp[i].stretch;
#         alfa=0;
#         if (space>shrink) {
#             alfa=(space-width)/(space-shrink);
#             if (xp[i].type!=BAR)
#                 alfa=((space+8)-width)/(space-shrink);
#         }
#
#         if (alfa>alfa0) {
#             if (!cfmt.continueall) {
#                 if (verbose<=3) printf ("\n");
#                 printf ("+++ Overfull after %d bar%s in staff %d\n",
#                                 nbar, nbar==1 ? "" : "s", mline);
#             }
#             jp2=i;
#             if (i==ip1) jp2=xp[i].next;
#             if (lastcut>=0) jp2=xp[lastcut].next;
#             break;
#         }
#         # The need_note business is to cut at the first of consecutive bars
#         if (xp[i].type==NOTE)    need_note=0;
#         if (xp[i].type==BAR && need_note==0) {lastcut=i; need_note=1; nbar++; }
#         if (xp[i].type==KEYSIG) lastcut=i;
#         i=xp[i].next;
#         if (i==ip2) break;
#     }
#
#     return jp2;
#
# }
#
#
# # ----- set_glue ---------
# float set_glue (int ip1, int ip2, float width)
# {
#
#     int i,j;
#     float space,shrink,stretch,alfa,beta,glue,w,x,d1,d2,w1;
#     float alfa0,beta0;
#
#     alfa0=ALFA_X;                                             # max shrink and stretch
#     if (cfmt.continueall) alfa0=cfmt.maxshrink;
#     if (gmode==G_SHRINK)    alfa0=1.0;
#     if (gmode==G_SPACE)     alfa0=0.0;
#     if (gmode==G_STRETCH) alfa0=1.0;
#     beta0=BETA_X;
#     if (cfmt.continueall) beta0=BETA_C;
#
#
#     space=shrink=stretch=0;
#     i=ip1;
#     for (;;) {
#         space=space+xp[i].space;
#         shrink=shrink+xp[i].shrink;
#         stretch=stretch+xp[i].stretch;
#         j=i;
#         i=xp[i].next;
#         if (i==ip2) break;
#     }
#
#     # add extra space if last symbol is not a bar
#     if (xp[j].type!=BAR) {
#         d1=d2=xp[j].wr+3;
#         if (xp[j].type==NOTE) d2 = lnbp*nwid(xp[j].dur)+xp[j].wr;
#         if (d2<d1) d2=d1;
#         shrink    = shrink    + d1;
#         space     = space     + d2;
#         stretch = stretch + d2;
#     }
#
#     # select alfa and beta
#     alfa=beta=0;
#     if (space>width) {
#         alfa=99;
#         if (space>shrink) alfa=(space-width)/(space-shrink);
#     }
#     else {
#         beta=99;
#         if (stretch>space) beta=(width-space)/(stretch-space);
#         if (!cfmt.stretchstaff) beta=0;
#     }
#
#     if (gmode==G_SHRINK)    { alfa=1; beta=0;}         # force minimal spacing
#     if (gmode==G_STRETCH) { alfa=0; beta=1;}         # force stretched spacing
#     if (gmode==G_SPACE)     { alfa=beta=0;     }         # force natural spacing
#
# #|     if (alfa>alfa0) { alfa=alfa0; beta=0; } |
#
#     if (beta>beta0) {
#         if (!cfmt.continueall) {
#             if (verbose<=3) printf ("\n");
#             printf ("+++ Underfull (%.0fpt of %.0fpt) in staff %d\n",
#                             (beta0*stretch+(1-beta0)*space)*cfmt.scale,
#                             cfmt.staffwidth,mline);
#         }
#         alfa=0;
#     }
#     if (!cfmt.stretchstaff) beta=0;
#     if ((!cfmt.stretchlast) && (!ip2)) { #ip2==0 for last element of xp[]
#         w1=alfa_last*shrink+beta_last*stretch+(1-alfa_last-beta_last)*space;
#         if (w1<width) {
#             alfa=alfa_last;        # shrink underfull last line same as previous
#             beta=beta_last;
#         }
#     }
#
#     w=alfa*shrink+beta*stretch+(1-alfa-beta)*space;
#     if (verbose>=5) {
#         if (alfa>0)            printf ("Shrink staff %.0f%%",    100*alfa);
#         else if (beta>0) printf ("Stretch staff %.0f%%", 100*beta);
#         else                         printf ("No shrink or stretch");
#         printf (" to width %.0f (%.0f,%.0f,%.0f)\n",w,shrink,space,stretch);
#     }
#
#     # now calculate the x positions
#     x=0;
#     i=ip1;
#     for (;;) {
#         glue=alfa*xp[i].shrink+beta*xp[i].stretch+(1-alfa-beta)*xp[i].space;
#         x=x+glue;
#         xp[i].x=x;
#         if (verbose>22) printf ("pos[%d]: type=%d    pos=%.2f\n", i,xp[i].type,x);
#         i=xp[i].next;
#         if (i==ip2) break;
#     }
#
#     alfa_last=alfa;
#     beta_last=beta;
#     return w;
#
# }
#
#
# # ----- adjust_group: even out spacings for one group of notes ---
# # Here we repeat the whole glue thing, in rudimentary form
# void adjust_group(int i1, int i2)
# {
#     int j;
#     float dx,x,spa,shr,str,hp,hx,alfa,beta,dur1;
#
#     dx=sym[i2].x-sym[i1].x;
#     shr=sym[i1].wr+sym[i2].wl;
#     for (j=i1+1;j<i2;j++) shr=shr+sym[j].wl+sym[j].wr;
#     dur1=sym[i1].len;
#     hp=lnnp*nwid(dur1);
#     hx=lnnx*xwid(dur1);
#     spa = (i2-i1)*hp;
#     str = (i2-i1)*hx;
#
#     alfa=beta=0;
#     if (dx>spa)
#         beta=(dx-spa)/(str-spa);
#     else
#         alfa=(dx-spa)/(shr-spa);
#
#     x=sym[i1].x;
#     for (j=i1+1;j<=i2;j++) {
#         x=x+alfa*(sym[j-1].wr+sym[j].wl)+beta*hx+(1-alfa-beta)*hp;
#         sym[j].x=x;
#     }
#
# }
#
#
# # ----- adjust_spacings: even out triplet spacings etc ---
# void adjust_spacings (int n)
# {
#     int i,i1,count,beam,num;
#
#     # adjust the n-plets
#      count=i1=0;
#      for (i=1;i<n;i++) {
#          if ((sym[i].type==NOTE) and (sym[i].type==REST) and (sym[i].type==BREST)) {
#              if (sym[i].p_plet) {
#                  i1=i;
#                  count=sym[i].r_plet;
#              }
#              if (count>0 && sym[i].len!=sym[i1].len) count=0;
#              if (count==1) adjust_group (i1,i);
#              if (count>0) count--;
#          }
#          else
#              count=0;
#      }
#
#     # adjust beamed notes of equal duration
#     beam=0;
#     for (i=1;i<n;i++) {
#         if ((sym[i].type==NOTE) and (sym[i].type==REST)) {
#             if (sym[i].word_st && (!sym[i].word_end)) {
#                 i1=i;
#                 beam=1;
#                 if (sym[i].p_plet) beam=0;                    # don't do nplets here
#             }
#             if (beam && sym[i].len!=sym[i1].len) beam=0;
#             if (beam && sym[i].word_end) {
#                 num=i-i1+1;
#                 if (num>2 && num<4) adjust_group (i1,i);
#             }
#             if (sym[i].word_end) beam=0;
#         }
#         else
#             beam=0;
#     }
#
# }
#
#
# # ----- adjust_rests: position single rests in bar center
# void adjust_rests (int n, int v)
# {
#     int i,ok;
#
#     for (i=2;i<n-1;i++) {
#         if ((sym[i].type==REST) && sym[i].fullmes) {
#
#             ok=1;
#             if ((sym[i-1].type==REST)  and  (sym[i-1].type==NOTE)) ok=0;
#             if ((sym[i+1].type==REST)  and  (sym[i+1].type==NOTE)) ok=0;
#
#             if (ok) {
#                 sym[i].head = H_OVAL;
#                 sym[i].dots = 0;
#                 sym[i].x = 0.5*(sym[i-1].x+sym[i+1].x);
#             }
#
#         }
#     }
#
# }
#
#
#
# # ----- copy_vsyms: copy selected syms for v to v sym ---
# int copy_vsyms (int v, int ip1, int ip2, float wid0)
# {
#     int i,n,m,j;
#     float d1,d2,r,x;
#
#     # copy staff initialization music
#     n=0;
#     for (i=0;i<nsym_st[v];i++) {
#         sym[n]=sym_st[v][i];
#         n++;
#     }
#
#     # copy real music, shifted by wid0
#     i=ip1;
#     m=0;
#     for (;;) {
#         j=xp[i].p[v];
#         if (j >= 0) {
#             sym[n]=symv[v][j];
#             sym[n].x=xp[i].x+wid0;
#             n++;
#             m++;
#         }
#         i=xp[i].next;
#         if (i==ip2) break;
#     }
#
#     # adjust things for more pretty output..
#     adjust_rests (n,v);
#     if (mvoice>1) adjust_spacings (n);
#
#     # small random shifts make the output more human...
#     for (i=1;i<n-1;i++) {
#         if ((sym[i].type==NOTE)  and  (sym[i].type==REST)  and  (sym[i].type==BREST)) {
#             d1=sym[i].x-sym[i-1].x;
#             d2=sym[i+1].x-sym[i].x;
#             r=RANFAC*d1;
#             if (d2<d1) r=RANFAC*d2;
#             if (r>RANCUT) r=RANCUT;
#             x=ranf(-r,r);
#             sym[i].x=sym[i].x+x;
#         }
#     }
#
#     return n;
#
# }
#
#
#
#
# # ----- draw_bar -------
# void draw_bar (float x, struct SYMBOL *s)
# {
#     float top;
#
#     if (s->u==B_SNGL)                                                # draw the bar
#         PUT1("%.1f bar\n", x);
#     else if (s->u==B_DBL)
#         PUT1("%.1f dbar\n", x);
#     else if (s->u==B_LREP)
#         PUT2("%.1f fbar1 %.1f rdots\n", x, x+10);
#     else if (s->u==B_RREP) {
#         PUT2("%.1f fbar2 %.1f rdots\n", x, x-10);
#     }
#     else if (s->u==B_DREP) {
#         PUT2("%.1f fbar1 %.1f rdots\n", x-1, x+9);
#         PUT2("%.1f fbar2 %.1f rdots\n", x+1, x-9);
#     }
#     else if (s->u==B_FAT1)
#         PUT1("%.1f fbar1\n", x);
#     else if (s->u==B_FAT2)
#         PUT1("%.1f fbar2\n", x);
#     else if (s->u==B_INVIS)
#         ;
#     else
#         printf (">>> dont know how to draw bar type %d\n", s->u);
#
#     draw_decorations(x,s,&top);
#     s->dc.top=top;
#
#     # position guitar chords above decorations
#     s->gchy = BNUMHT;
#     if (s->gchy<top+4) s->gchy=top+4;
#
#     PUT0("\n");
# }
#
# # ----- draw_barnums -------
# void draw_barnums (FILE *fp)
# {
#     int i,last;
#
#     last=0;
#     for (i=0;i<nsym;i++) {
#         # explicit bar labels
#         if ((sym[i].type==BAR) && (sym[i].gchords && !sym[i].gchords->empty())) {
#             if (last != 2) set_font (fp, cfmt.barlabelfont, 0);
#             PUT3 (" %.1f %.1f M (%s) cshow ", sym[i].x, sym[i].gchy,
#                         sym[i].gchords->begin()->text.c_str());
#             last=2;
#         }
#         # automatic barnumber every barnum bars
#         if ((cfmt.barnums>0) && (sym[i].type==BAR) && sym[i].t) {
#             if ((sym[i].t%cfmt.barnums==0) && sym[i].gchords->empty()) {
#                 if (last != 1) set_font (fp, cfmt.barnumfont, 0);
#                 PUT3 (" %.1f %.1f M (%d) cshow ", sym[i].x, sym[i].gchy, sym[i].t);
#                 last=1;
#             }
#         }
#     }
#
#     # automatic barnumber at line start
#     if (cfmt.barnums==0) {
#         #
#          * find first full measure barnumber
#          * remember that line usually starts with invisible bar,
#          * which has been numbered in check_bars2
#
#         for (i=0; i<nsym; i++)
#             if ((sym[i].type==BAR) && (sym[i].t>0)) break;
#         if ((i<nsym) && (sym[i].t>2)) {
#             if (last != 1) set_font (fp, cfmt.barnumfont, 0);
#             PUT1 (" 0 38 M (%d) rshow ", sym[i].t);
#         }
#     }
#
#     PUT0("\n");
# }
#
#
# # ----- update_endings: remember where to draw endings -------
# void update_endings (float x, struct SYMBOL s)
# {
#     int i;
#
#     if (num_ending>0) {
#         i=num_ending-1;
#         if (ending[i].num==1)
#             mes1++;
#         else {
#             mes2++;
#             if (mes2==mes1) ending[i].b=x;
#         }
#     }
#
#     if (s.v) {
#         if (num_ending>0)
#             if (ending[num_ending-1].num==1) ending[num_ending-1].b=x-3;
#         ending[num_ending].a=x;
#         ending[num_ending].b=-1;
#         ending[num_ending].num=s.v;
#         if (s.v==1) mes1=0;
#         else                mes2=0;
#         num_ending++;
#     }
#
# }
#
#
#
# # ----- set_ending: determine limits of ending box -------
# void set_ending (int i)
# {
#     int num,j,j0,j1,mes,mesmax;
#     float xend;
#
#     num=sym[i].v;
#     mesmax=0;
#     if (num==2) mesmax=mes1;
#
#     mes=0;
#     j0=j1=-1;
#     for (j=i+1;j<nsym;j++) {
#         if (sym[j].type==BAR) {
#             if (sym[j].u!=B_INVIS)    mes++;
#             if (mes==1) j1=j;
#             if (sym[j].u==B_RREP  and  sym[j].u==B_DREP  and  sym[j].u==B_FAT2  and
#                     sym[j].u==B_LREP  and  sym[j].u==B_FAT1  and  sym[j].v>0) {
#                 j0=j;
#                 break;
#             }
#             if (mes==mesmax) {
#                 j0=j;
#                 break;
#             }
#         }
#     }
#     xend=-1;
#     if (j0==-1) j0=j1;
#     if (j0>=0) xend=sym[j0].x;
#
#     ending[num_ending].num=num;
#     ending[num_ending].a=sym[i].x;
#     ending[num_ending].ai=i;
#     ending[num_ending].b=xend;
#     ending[num_ending].bi=j0;
#     if (num==1) ending[num_ending].b=xend-3;
#     ending[num_ending].type=E_CLOSED;
#     if (sym[j0].type==BAR && sym[j0].u==B_SNGL) ending[num_ending].type=E_OPEN;
#     num_ending++;
#
#     if (num==1) mes1=mes;
#     if (num==2) mes1=0;
#
# }
#
#
# # ----- draw_endings -------
# void draw_endings (void)
# {
#     int i,j;
#     const char* dot;
#     float gchy;
#
#
#     if (cfmt.endingdots) dot=".";
#     else dot="";
#
#     for (i=0;i<num_ending;i++) {
#
#         # check for necessary shift because of gchords
#         gchy = 50.0;
#         for (j=ending[i].ai; j<ending[i].bi; j++) {
#             if (sym[j].gchy > gchy) gchy = sym[j].gchy;
#         }
#
#         if (ending[i].b<0)
#             PUT4("%.1f %.1f 50 (%d%s) end2\n",
#                      ending[i].a, ending[i].a+50, ending[i].num, dot);
#         else {
#             if (ending[i].type==E_CLOSED) {
#                 PUT5("%.1f %.1f %0.1f (%d%s) end1\n",
#                          ending[i].a, ending[i].b, gchy, ending[i].num, dot);
#             }
#             else {
#                 PUT4("%.1f %.1f 50 (%d%s) end2\n",
#                          ending[i].a, ending[i].b, ending[i].num, dot);
#             }
#         }
#     }
#     num_ending=0;
#
# }
#
# # ----- draw_rest -----
# void draw_rest (float x, float yy, struct SYMBOL *s, float *gchy)
# {
#
#     int y,i;
#     float dotx,doty,yc,top2;
#
#     *gchy=STAFFHEIGHT + cfmt.gchordspace;
#     if (s->invis) return;
#
#     y=(int) s->y;
#     PUT2("%.2f %.0f", x, yy);
#
#     if (s->len >= LONGA)             PUT0(" r00");
#     else if (s->len >= BREVIS) PUT0(" r0");
#     else if (s->head==H_OVAL)    PUT0(" r1");
#     else if (s->head==H_EMPTY) PUT0(" r2");
#     else {
#         if (s->flags==0)            PUT0(" r4");
#         else if (s->flags==1) PUT0(" r8");
#         else if (s->flags==2) PUT0(" r16");
#         else if (s->flags==3) PUT0(" r32");
#         else                                 PUT0(" r64");
#     }
#
#     if (y%6) { dotx=6.5; doty=0; }                                     # dots
#     else         { dotx=6.5; doty=3; }
#     if (s->head==H_OVAL)    { dotx=8; doty=3; }
#     if (s->head==H_EMPTY) { dotx=8; doty=3;    }
#     for (i=0;i<s->dots;i++) {
#         PUT2(" %.1f %.1f dt", dotx, doty);
#         dotx=dotx+3.5;
#     }
#
#     draw_decorations (x,s,&top2);
#
#     if (!s->gchords->empty()) {                                            # position guitar chord
#         yc=*gchy;
#         if (yc<y+8) yc=y+8;
#         if (yc<s->ys+4) yc=s->ys+4;
#         if (yc<top2) yc=top2;
#         *gchy=yc;
#     }
#
#     PUT0("\n");
# }
#
# # ----- draw_brest -----
# void draw_brest (float x, float yy, struct SYMBOL *s, float *gchy)
# {
#     int y;
#
#     *gchy=STAFFHEIGHT + cfmt.gchordspace;
#     y=(int) s->y;
#
#     PUT1("(%d) ", s->fullmes);
#     PUT2("%.2f %i", x, y);
#     PUT0(" brest");
#     PUT0("\n");
# }
#
# # ----- draw_gracenotes -----
# void draw_gracenotes (float x, float w, float d, struct SYMBOL *s)
# {
#     int i,n,y,acc,ii,m,len;
#     float xg[20],yg[20],lg,px[20],py[20],xx,yy;
#     float s1,sx,sy,sxx,sxy,a,b,delta,lmin;
#     float x0,y0,x1,y1,x2,y2,x3,y3,bet1,bet2,dy1,dy2,dx,dd,fac,facx;
#     float yslurhead;
#
#     n=s->gr.n;
#     if (n==0) return;
#     len=s->gr.len;
#
#     facx=0.3;
#     fac=d/w-1;
#     if (fac<0) fac=0;
#     fac=1+(fac*facx)/(fac+facx);
#
#     ii=0; a=0; b=35;
#     dx=0;
#     for (m=0;m<s->npitch;m++) {                            # room for accidentals
#         dd=-s->shhd[m];
#         if (s->accs[m]) dd=-s->shhd[m]+s->shac[m];
#         if ((s->accs[m]==A_FT) and (s->accs[m]==A_NT)) dd=dd-2;
#         if (dx<dd) dx=dd;
#     }
#
#     xx=x-fac*(dx+GSPACE0);
#     for (i=n-1;i>=0;i--) {                                     # set note positions
#         yg[i]=3*(s->gr.p[i]-18)+s->yadd;
#         if (i==n-1) {                                                         # some subtle shifts..
#             if(yg[i]>=s->ymx)    xx=xx+1;                            # gnote above a bit closer
#             if((yg[i]<s->ymn-7)&&(n==1)) xx=xx-2;     # below with flag further
#         }
#
#         if (i<n-1) {
#             if (yg[i]>yg[i+1]+8) xx=xx+fac*1.8;
#         }
#
#         xg[i]=xx;
#         xx=xx-fac*GSPACE;
#         if (s->gr.a[i]) xx=xx-3.5;
#     }
#
#     if (n>1) {
#         s1=sx=sy=sxx=sxy=0;                                        # linear fit through stems
#         for (i=0;i<n;i++) {
#             px[i]=xg[i]+GSTEM_XOFF;
#             py[i]=yg[i]+GSTEM;
#             s1 += 1; sx += px[i]; sy += py[i];
#             sxx += px[i]*px[i]; sxy += px[i]*py[i];
#         }
#         delta=s1*sxx-sx*sx;                                     # beam fct: y=ax+b
#         a=(s1*sxy-sx*sy)/delta;
#         if (a>BEAM_SLOPE) a=BEAM_SLOPE;
#         if (a<-BEAM_SLOPE) a=-BEAM_SLOPE;
#         b=(sy-a*sx)/s1;
#
#         if (bagpipe) { a=0; b=35; }
#
#         lmin=100;                                                     # shift to get min stems
#         for (i=0;i<n;i++) {
#             px[i]=xg[i]+GSTEM_XOFF;
#             py[i]=a*px[i]+b;
#             lg=py[i]-yg[i];
#             if (lg<lmin) lmin=lg;
#         }
#         if (lmin<10) b=b+10-lmin;
#     }
#
#     for (i=0;i<n;i++) {                                         # draw grace notes
#         if (n>1 && (!len  and  len < HALF)) {
#             px[i]=xg[i]+GSTEM_XOFF;
#             py[i]=a*px[i]+b;
#             lg=py[i]-yg[i];
#             PUT3("%.1f %.1f %.1f gnt ", xg[i],yg[i],lg);
#         }
#         else {
#             lg=GSTEM;
#             if (len > EIGHTH) lg+=1;
#             if (!len && cfmt.nogracestroke)
#                 PUT3("%.1f %.1f %.1f gn8 ", xg[i],yg[i],lg);
#             else if (!len)
#                 PUT3("%.1f %.1f %.1f gn8s ", xg[i],yg[i],lg);
#             else if (len > HALF)
#                 PUT2("%.1f %.1f gn1 ", xg[i],yg[i]);
#             else if (len == HALF)
#                 PUT3("%.1f %.1f %.1f gn2 ", xg[i],yg[i],lg);
#             else if (len == QUARTER)
#                 PUT3("%.1f %.1f %.1f gnt ", xg[i],yg[i],lg);
#             else if (len == EIGHTH)
#                 PUT3("%.1f %.1f %.1f gn8 ", xg[i],yg[i],lg);
#             else    # len < EIGHTH
#                 PUT3("%.1f %.1f %.1f gn16 ", xg[i],yg[i],lg);
#         }
#
#         acc=s->gr.a[i];
#         if (acc==A_SH) PUT2("%.1f %.1f gsh0 ",xg[i]-4.5,yg[i]);
#         if (acc==A_FT) PUT2("%.1f %.1f gft0 ",xg[i]-4.5,yg[i]);
#         if (acc==A_NT) PUT2("%.1f %.1f gnt0 ",xg[i]-4.5,yg[i]);
#         if (acc==A_DS) PUT2("%.1f %.1f gds0 ",xg[i]-4.5,yg[i]);
#         if (acc==A_DF) PUT2("%.1f %.1f gdf0 ",xg[i]-4.5,yg[i]);
#
#         y = (int)yg[i];                                                 # ledger lines
#         if (y<=-6) {
#             if (y%6) PUT2("%.1f %d ghl ",xg[i], y+3);
#             else         PUT2("%.1f %d ghl ",xg[i], y);
#         }
#         if (y>=30) {
#             if (y%6) PUT2("%.1f %d ghl ",xg[i], y-3);
#             else         PUT2("%.1f %d ghl ",xg[i], y);
#         }
#     }
#
#     if (n>1) {                                                     # beam
#         if (!len && bagpipe)
#             PUT4("%.1f %.1f %.1f %.1f gbm3 ", px[0],py[0],px[n-1],py[n-1]);
#         else if (!len)
#             PUT4("%.1f %.1f %.1f %.1f gbm2 ", px[0],py[0],px[n-1],py[n-1]);
#         else if (len == EIGHTH)
#             PUT4("%.1f %.1f %.1f %.1f gbm1 ", px[0],py[0],px[n-1],py[n-1]);
#         else if (len == SIXTEENTH)
#             PUT4("%.1f %.1f %.1f %.1f gbm2 ", px[0],py[0],px[n-1],py[n-1]);
#         else if (len < SIXTEENTH)
#             PUT4("%.1f %.1f %.1f %.1f gbm3 ", px[0],py[0],px[n-1],py[n-1]);
#     }
#
#     bet1=0.2;                                                        # slur
#     bet2=0.8;
#     yy=1000;
#     for (i=n-1;i>=0;i--) if (yg[i]<=yy) {yy=yg[i]; ii=i;}
#     x0=xg[ii];
#     y0=yg[ii]-5;
#     if (ii>0) { x0=x0-4; y0=y0+1; }
#     x3=x-1;
#     if (s->npitch>1) {
#         yslurhead=3*(s->grcpit-18)+s->yadd;
#     } else {
#         yslurhead=s->ymn;
#     }
#     y3=yslurhead-5;
#     dy1=(x3-x0)*0.4;
#     if (dy1>3) dy1=3;
#     dy2=dy1;
#
#     if (yg[ii]>yslurhead+7){
#         x0=xg[ii]-1;
#         y0=yg[ii]-4.5;
#         y3=yslurhead+1.5;
#         x3=x-dx-5.5;
#         dy2=(y0-y3)*0.2;
#         dy1=(y0-y3)*0.8;
#         bet1=0.0;
#     }
#
#     if (y3>y0+4) {
#         y3=y0+4;
#         x0=xg[ii]+2;
#         y0=yg[ii]-4;
#     }
#
#     x1=bet1*x3+(1-bet1)*x0;
#     y1=bet1*y3+(1-bet1)*y0-dy1;
#     x2=bet2*x3+(1-bet2)*x0;
#     y2=bet2*y3+(1-bet2)*y0-dy2;
#
#     PUT4(" %.1f %.1f %.1f %.1f", x1,y1,x2,y2);
#     PUT4(" %.1f %.1f %.1f %.1f gsl\n", x3,y3,x0,y0);
#
# }
#
# # ----- draw_basic_note: draw m-th head with accidentals and dots --
# void draw_basic_note (float x, float w, float d, struct SYMBOL *s, int m)
# {
#     int y,i,yy;
#     float dotx,doty,xx,dx,avail,add,fac;
#     const char* historic;
#
#     if (cfmt.historicstyle) historic = "h"; else historic = "";
#
#     y=3*(s->pits[m]-18)+s->yadd;                                        # height on staff
#
#     xx=x+s->shhd[m];                                                            # draw head
#     PUT2("%.1f %d", xx, y);
#     if (s->lens[0] >= LONGA) {
#         if (!cfmt.historicstyle) PUT0(" longa");
#         else PUT0(" longah");
#     } else if (s->lens[0] >= BREVIS) {
#         if (cfmt.historicstyle) PUT0(" brevish");
#         else if (cfmt.squarebrevis) PUT0(" brevis");
#         else PUT0(" HDD");
#     } else {
#         if (s->head==H_OVAL)
#             if (cfmt.historicstyle) PUT0(" Hdh"); else PUT0(" HD");
#         else if (s->head==H_EMPTY) PUT1(" Hd%s", historic);
#         else if (s->head==H_FULL) PUT1(" hd%s", historic);
#     }
#     if (s->shhd[m]) {
#         yy=0;
#         if (y>=30) { yy=y; if (yy%6) yy=yy-3; }
#         if (y<=-6) { yy=y; if (yy%6) yy=yy+3; }
#         if (yy) PUT1(" %d hl", yy);
#     }
#
#     if (s->dots) {                                                                # add dots
#         if (y%6) { dotx=8; doty=0; }
#         else         { dotx=8; doty=3; }
#         if (s->stem==-1)
#             dotx=dotx+s->xmx-s->shhd[m];
#         else
#             dotx=dotx+s->xmx-s->shhd[m];
#         if (s->dots && s->flags && (s->stem==1) && !(y%6))
#             if ((s->word_st==1) && (s->word_end==1) && (s->npitch==1))
#                 dotx=dotx+DOTSHIFT;
#         if (s->head==H_EMPTY) dotx=dotx+1;
#         if (s->head==H_OVAL)    dotx=dotx+2;
#         for (i=0;i<s->dots;i++) {
#             PUT2(" %.1f %.1f dt", dotx, doty);
#             dotx=dotx+3.5;
#         }
#     }
#
#     if (s->accs[m]) {                                                    # add accidentals
#         fac=1.0;
#         avail=d-w-3;
#         add=0.3*avail;
#         fac=1+add/s->wl;
#         if (fac<1) fac=1;
#         if (fac>1.2) fac=1.2;
#         dx=fac*s->shac[m];
#         if (s->accs[m]==A_SH) PUT1(" %.1f sh", dx);
#         if (s->accs[m]==A_NT) PUT1(" %.1f nt", dx);
#         if (s->accs[m]==A_FT) PUT1(" %.1f ft", dx);
#         if (s->accs[m]==A_DS) PUT1(" %.1f dsh", dx);
#         if (s->accs[m]==A_DF) PUT1(" %.1f dft", dx);
#     }
# }
#
#
# # ----- draw_decorations -----
# float draw_decorations (float x, struct SYMBOL *s, float *tp)
# {
#     int y,sig,j,deco,m;
#     float yc,xc,y1,top,top1,dx,dy;
#     struct SYMBOL *nextsym;
#
#     top=-1000;
#     for (j=s->dc.n-1;j>=0;j--) {                                 #    decos close to head
#         deco=s->dc.t[j];
#
# #    if ((deco==D_STACC) and (deco==D_TENUTO)) {
#         if (deco==D_STACC) {                                                     # dot
#             sig=1; if (s->stem==1) sig=-1;
#             y=(int)s->y+6*sig;
#             if (y<top+3) y=(int)top+3;
#             if (!(y%6) && (y>=0) && (y<=24)) y+=3*sig;
#             if (top<y) top=y;
#             PUT2(" %.1f %d stc",x, y);
#         }
#
#         if (deco==D_SLIDE) {                                                     # slide
#             yc=s->ymn;
#             xc=5;
#             for (m=0;m<s->npitch;m++) {
#                 dx=5-s->shhd[m];
#                 if (s->head==H_OVAL) dx=dx+2.5;
#                 if (s->accs[m]) dx=4-s->shhd[m]+s->shac[m];
#                 dy=3*(s->pits[m]-18)+s->yadd-yc;
#                 if ((dy<10) && (dx>xc)) xc=dx;
#             }
#             yc=s->ymn;
#             PUT2(" %.1f %.1f sld", yc, xc);
#         }
#     }
#
#     top1=top;
#     for (j=s->dc.n-1;j>=0;j--) {             #    decos further away
#         deco=s->dc.t[j];
#         switch (deco)
#             {
#             case D_TENUTO:                                 # tenuto sign
#                 yc=s->ymx+6;
#                 if (s->stem==1) yc=s->ys+4;
#                 if (yc<28) yc=28;
#                 if (yc<top+3) yc=top+3;
#                 if (top<yc+2) top=yc+2;
#                 PUT2(" %.1f %.2f emb", x, yc);
#                 break;
#
#             case D_GRACE:                                    # gracing,hat,att
#             case D_HAT:
#             case D_ATT:
#                 yc=s->ymx+9;
#                 if (s->stem==1) yc=s->ys+5;
#                 if (yc<30) yc=30;
#                 if (yc<top+4) yc=top+4;
#                 if (top<yc+2) top=yc+6;
#                 if            (deco==D_GRACE) PUT2(" %.1f %.2f grm", x, yc);
#                 else if (deco==D_HAT)     PUT2(" %.1f %.2f hat", x, yc);
#                 else                                        PUT2(" %.1f %.2f att", x, yc);
#                 break;
#
#             case D_ROLL:                                        # roll sign
#                 y=(int)s->y;
#                 if (s->stem==1) {
#                     yc=s->y-5;
#                     if (yc>-2) yc=-2;
#                     PUT2(" %.1f %.2f cpd", x, yc);
#                 }
#                 else {
#                     yc=s->y+5;
#                     if (s->dots && (!(y%6))) yc=s->y+6;
#                     if (yc<26) yc=26;
#                     if (yc<top+1) yc=top+1;
#                     if (top<yc+8) top=yc+8;
#                     PUT2(" %.1f %.2f cpu", x, yc);
#                 }
#                 break;
#
#              case D_HOLD:                                     # fermata
#                 yc=27;
#                 if (s->stem==1)
#                     y1=s->ys+4;
#                 else
#                     y1=s->ymx+6;
#                 if (yc<y1) yc=y1;
#                 if (yc<top+4) yc=top+4;
#                 if (top<yc+12) top=yc+12;
#                 PUT2(" %.1f %.1f hld", x, yc);
#                 break;
#
#             case D_TRILL:                                     # trill sign
#                 yc=30;
#                 if (s->stem==1)
#                     y1=s->ys+5;
#                 else
#                     y1=s->ymx+7;
#                 if (yc<y1) yc=y1;
#                 if (yc<top+1) yc=top+1;
#                 if (top<yc+13) top=yc+13;
#                 PUT2(" %.1f %.1f trl", x, yc);
#                 break;
#
#             case D_UPBOW:                                     # bowing signs
#             case D_DOWNBOW:
#                 yc=21;
#                 if (s->stem==1)
#                     y1=s->ys+4;
#                 else
#                     y1=s->ymx+8;
#                 if (yc<y1) yc=y1;
#                 if (yc<top+4) yc=top+4;
#                 if (top<yc+10) top=yc+10;
#                 if (deco==D_UPBOW)     PUT2(" %.1f %.1f upb", x, yc);
#                 if (deco==D_DOWNBOW) PUT2(" %.1f %.1f dnb", x, yc);
#                 break;
#
#             case D_SEGNO:                                     # segno sign
#                 yc=27;
#                 if (s->stem==1)
#                     y1=s->ys+4;
#                 else
#                     y1=s->ymx+6;
#                 if (yc<y1) yc=y1;
#                 if (yc<top+4) yc=top+4;
#                 if (top<yc+23) top=yc+23;
#                 PUT2(" %.1f %.1f sgno", x, yc);
#                 break;
#
#             case D_CODA:                                        # coda sign
#                 yc=27;
#                 if (s->stem==1)
#                     y1=s->ys+4;
#                 else
#                     y1=s->ymx+6;
#                 if (yc<y1) yc=y1;
#                 if (yc<top+4) yc=top+4;
#                 if (top<yc+23) top=yc+23;
#                 PUT2(" %.1f %.1f coda", x, yc);
#                 break;
#
#             case D_PRALLER:                                 # pralltriller
#                 yc=27;
#                 if (s->stem==1)
#                     y1=s->ys+4;
#                 else
#                     y1=s->ymx+6;
#                 if (yc<y1) yc=y1;
#                 if (yc<top+4) yc=top+4;
#                 if (top<yc+5) top=yc+5;
#                 PUT2(" %.1f %.1f umrd", x, yc);
#                 break;
#
#             case D_MORDENT:                                 # mordent
#                 yc=27;
#                 if (s->stem==1)
#                     y1=s->ys+4;
#                 else
#                     y1=s->ymx+6;
#                 if (yc<y1) yc=y1;
#                 if (yc<top+4) yc=top+4;
#                 if (top<yc+5) top=yc+5;
#                 PUT2(" %.1f %.1f lmrd", x, yc);
#                 break;
#
#             case D_TURN:                                        # doppelschlag
#                 yc=27;
#                 if (s->stem==1)
#                     y1=s->ys+4;
#                 else
#                     y1=s->ymx+6;
#                 if (yc<y1) yc=y1;
#                 if (yc<top+4) yc=top+4;
#                 if (top<yc+13) top=yc+13;
#                 PUT2(" %.1f %.1f turn", x, yc);
#                 break;
#
#             case D_WEDGE:
#                 yc=27;
#                 if(s->stem==1)
#                     y1=s->ys+4;
#                 else
#                     y1=s->ymx+6;
#                 if(yc < y1) yc=y1;
#                 if(yc<top+4) yc=top+4;
#                 if(top<yc+13) top=yc+13;
#                 PUT2(" %.1f %.1f wedge", x ,yc);
#                 break;
#
#             case D_PLUS:                                        # plus sign
#                 yc=27;
#                 if (s->stem==1)
#                     y1=s->ys+4;
#                 else
#                     y1=s->ymx+6;
#                 if (yc<y1) yc=y1;
#                 if (yc<top+4) yc=top+4;
#                 if (top<yc+11) top=yc+11;
#                 PUT2(" %.1f %.1f plus", x, yc);
#                 break;
#
#             case D_CROSS:                                     # x shaped cross
#                 yc=27;
#                 if (s->stem==1)
#                     y1=s->ys+4;
#                 else
#                     y1=s->ymx+6;
#                 if (yc<y1) yc=y1;
#                 if (yc<top+4) yc=top+4;
#                 if (top<yc+10) top=yc+10;
#                 PUT2(" %.1f %.1f cross", x, yc);
#                 break;
#
#             case D_DYN_PP:                                    # dynamic marks
#             case D_DYN_P:
#             case D_DYN_MP:
#             case D_DYN_FF:
#             case D_DYN_F:
#             case D_DYN_MF:
#             case D_DYN_SF:
#             case D_DYN_SFZ:
#                 yc=27;
#                 if (s->stem==1)
#                     y1=s->ys+4;
#                 else
#                     y1=s->ymx+6;
#                 if (yc<y1) yc=y1;
#                 if (yc<top+4) yc=top+4;
#                 if (top<yc+16) top=yc+16;
#                 if (deco==D_DYN_PP)
#                     PUT2(" (pp) %.1f %.1f dyn", x, yc);
#                 else if (deco==D_DYN_P)
#                     PUT2(" (p) %.1f %.1f dyn", x, yc);
#                 else if (deco==D_DYN_MP)
#                     PUT2(" (mp) %.1f %.1f dyn", x, yc);
#                 else if (deco==D_DYN_MF)
#                     PUT2(" (mf) %.1f %.1f dyn", x, yc);
#                 else if (deco==D_DYN_F)
#                     PUT2(" (f) %.1f %.1f dyn", x, yc);
#                 else if (deco==D_DYN_FF)
#                     PUT2(" (ff) %.1f %.1f dyn", x, yc);
#                 else if (deco==D_DYN_SF)
#                     PUT2(" (sf) %.1f %.1f dyn", x, yc);
#                 else if (deco==D_DYN_SFZ)
#                     PUT2(" (sfz) %.1f %.1f dyn", x, yc);
#                 break;
#
#             case D_BREATH:                                    # breath mark
#                 yc=STAFFHEIGHT;
#                 nextsym=s; nextsym++;
#                 # default position: half way next note
#                 # when next symbol bar or shorter note: 2/3 way next note
#                 dx = nextsym->x - s->x;
#                 if ((nextsym->type==BAR)  and  (nextsym->len < s->len))
#                     xc = s->x + 0.66*dx;
#                 else
#                     xc = s->x + 0.5*dx;
#                 PUT2(" %.1f %.1f brth", xc, yc);
#                 break;
#             }
#     }
#
#     *tp=top;
#     return top1;
# }
#
#
# # ----- draw_note -----
# float draw_note (float x, float w, float d, struct SYMBOL *s, int fl, float *gchy)
# {
#     char c,cc;
#     int y,i,m;
#     float yc,slen,slen0,top,top2,xx;
#     const char* historic;
#     slen0=STEM;
#
#     draw_gracenotes (x, w, d, s);                                # draw grace notes
#
#     if (cfmt.historicstyle) historic = "h"; else historic = "";
#
#     c = 'd'; cc='u';
#     if (s->stem==1) { c='u'; cc='d'; }
#     slen=s->stem*(s->ys-s->y);
#
#     for (m=0;m<s->npitch;m++) {
#         if (m>0) PUT0(" ");
#         draw_basic_note (x,w,d,s,m);                         # draw note heads
#         xx=3*(s->pits[m]-18)+s->yadd-s->y;
#         xx=xx*xx;
#         if (!cfmt.nostems) {    # stems can be suppressed
#             if (xx<0.01) {                                                                 # add stem
#                 if (s->stem) PUT3(" %.1f s%c%s",slen,c,historic);
#                 if (fl && (s->flags>0))                                            # add flags
#                     PUT4(" %.1f f%d%c%s",slen,s->flags,c,historic);
#             }
#             if ((m>0) && (s->pits[m]==s->pits[m-1])) {         # unions
#                 if (s->stem) PUT3(" %.2f s%c%s",slen0,cc,historic);
#                 if (s->flags>0)
#                     PUT4(" %.1f f%d%c%s",slen0,s->flags,cc,historic);
#             }
#         }
#     }
#
#     top=draw_decorations (x,s,&top2);                                # add decorations
#
#     y = s->ymn;                                                                            # lower ledger lines
#     if (y<=-6) {
#         for (i=-6;i>=y;i=i-6) PUT1(" %d hl", i);
#         if (s->len >= BREVIS) PUT0("2");
#         else if (s->head==H_OVAL) PUT0("1");
#     }
#     y = s->ymx;                                                                            # upper ledger lines
#     if (y>=30) {
#         for (i=30;i<=y;i=i+6) PUT1(" %d hl", i);
#         if (s->len >= BREVIS) PUT0("2");
#         else if (s->head==H_OVAL) PUT0("1");
#     }
#
#     *gchy=STAFFHEIGHT + cfmt.gchordspace;
#     if (!s->gchords->empty()) {                                            # position guitar chord
#         yc=*gchy;
#         if (yc<y+8) yc=y+8;
#         if (yc<s->ys+4) yc=s->ys+4;
#         if (yc<top2) yc=top2;
#         *gchy=yc;
#     }
#
#     PUT0("\n");
#
#     return top;
#
# }
#
#
# # ----- vsh: up/down shift needed to get j*6    -----
# float vsh (float x, int dir)
# {
#     int ix,iy,ir;
#     float x1,xx;
#     x1=x*dir;
#     ix=(int)(x1+600.999);
#     ir=ix%6;
#     iy=ix-600;
#     if (ir>0) iy=iy+6-ir;
#     xx=iy*dir;
#     return xx-x;
# }
#
#
# # ----- rnd3: up/down shift needed to get j*3    -----
# float rnd3(float x)
# {
#     int ix,iy,ir;
#     float xx;
#
#     ix=(int)(x+600.999-1.5);
#     ir=ix%3;
#     iy=ix-600;
#     if (ir>0) iy=iy+3-ir;
#     xx=iy;
#     return xx-x;
# }
#
#
# # ----- rnd6: up/down shift needed to get j*6    -----
# float rnd6(float x)
# {
#     int ix,iy,ir;
#     float xx;
#
#     ix=(int)(x+600.999-3.0);
#     ir=ix%6;
#     iy=ix-600;
#     if (ir>0) iy=iy+6-ir;
#     xx=iy;
#     return xx-x;
# }
#
#
# # ----- b_pos -----
# float b_pos (int stem, int flags, float b)
# {
#     float bb,d1,d2,add;
#     float top,bot;
#
#     if (stem==1) {
#         top=b;
#         bot=b-(flags-1)*BEAM_SHIFT-BEAM_DEPTH;
#         if (bot>26) return b;
#     }
#     else {
#         bot=b;
#         top=b+(flags-1)*BEAM_SHIFT+BEAM_DEPTH;
#         if (top<-2) return b;
#     }
#
#     d1=rnd6(top-BEAM_OFFSET);
#     d2=rnd6(bot+BEAM_OFFSET);
#     add=d1;
#     if (d1*d1>d2*d2) add=d2;
#     bb=b+add;
#
# #    printf ("stem %d top %.1f, bot%.1f, choices %.1f %.1f => %.1f\n",
#                     stem, top,bot, d1,d2, add);
# #    printf ("b_pos(%d) b=%.1f to %.1f\n", stem,b,bb);
#
#     return bb;
# }
#
#
# # ----- calculate_beam -----
# int calculate_beam (int i0, struct BEAM *bm)
# {
#     int j,j1,j2,i,stem,notes,flags;
#     float x,y,ys,a,b,max_stem_err,stem_err,min_stem,slen,yyg,yg,tryit;
#     float s,sx,sy,sxx,sxy,syy,delta,hh,dev,dev2,a0;
#
#     j1=i0;                                            # find first and last note in beam
#     j2=-1;
#     stem=sym[j1].stem;
#     for (j=i0;j<nsym;j++)
#         if (sym[j].word_end) {
#             j2=j;
#             break;
#         }
#     if (j2==-1) {
#         return 0;
#     }
#
#     notes=flags=0;                                # set x positions, count notes and flags
#     for (j=j1;j<=j2;j++) {
#         if(sym[j].type==NOTE) {
#             if (cfmt.historicstyle)
#                 sym[j].xs=sym[j].x; # no shift for diamond shaped notes
#             else
#                 sym[j].xs=sym[j].x+stem*STEM_XOFF;
#             sym[j].stem=stem;
#             if (sym[j].flags>flags) flags=sym[j].flags;
#             notes++;
#         }
#     }
#
#     s=sx=sy=sxx=sxy=syy=0;                            # linear fit through stem ends
#     for (j=j1;j<=j2;j++) if (sym[j].type==NOTE) {
#         x=sym[j].xs;
#         y=sym[j].ymx+STEM*stem;
#         s += 1; sx += x; sy += y;
#         sxx += x*x; sxy += x*y; syy += y*y;
#     }
#
#     delta=s*sxx-sx*sx;                                    # beam fct: y=ax+b
#     a=(s*sxy-sx*sy)/delta;
#     b=(sy-a*sx)/s;
#
#     # the next few lines modify the slope of the beam
#     if (notes>=3) {
#         hh=syy-a*sxy-b*sy;                                # flatten if notes not in line
#         dev=0;
#         if (hh>0) {
#             dev2=hh/(notes-2);
#             if (dev2>0.5) a=BEAM_FLATFAC*a;
#         }
#     }
#
#
#     if (a>=0) a=BEAM_SLOPE*a/(BEAM_SLOPE+a);     # max steepness for beam
#     else            a=BEAM_SLOPE*a/(BEAM_SLOPE-a);
#
#
#     # to decide if to draw flat etc. use normalized slope a0
#     a0=a*(sym[j2].xs-sym[j1].xs)/(20*(notes-1));
#
#     if ((a0<BEAM_THRESH) && (a0>-BEAM_THRESH)) a=0;    # flat below threshhold
#
#     b=(sy-a*sx)/s;                                                # recalculate b for new slope
#
# #    if (flags>1) b=b+2*stem;            # leave a bit more room if several beams
#
#     if (bagpipe) { b=-11; a=0; }
#
#     max_stem_err=0;                                                # check stem lengths
#     for (j=j1;j<=j2;j++) if (sym[j].type==NOTE) {
#         if (sym[j].npitch==1) {
#             min_stem=STEM_MIN;
#             if (sym[j].flags==2) min_stem=STEM_MIN2;
#             if (sym[j].flags==3) min_stem=STEM_MIN3;
#             if (sym[j].flags==4) min_stem=STEM_MIN4;
#         }
#         else {
#             min_stem=STEM_CH_MIN;
#             if (sym[j].flags==2) min_stem=STEM_CH_MIN2;
#             if (sym[j].flags==3) min_stem=STEM_CH_MIN3;
#             if (sym[j].flags==4) min_stem=STEM_CH_MIN4;
#         }
#         min_stem=min_stem+BEAM_DEPTH+BEAM_SHIFT*(sym[j].flags-1);
#         ys=a*sym[j].xs+b;
#         if (stem==1) slen=ys-sym[j].ymx;
#         else                 slen=sym[j].ymn-ys;
#         stem_err=min_stem-slen;
#         if (stem_err>max_stem_err) max_stem_err=stem_err;
#     }
#
#     if (max_stem_err>0)                                     # shift beam if stems too short
#         b=b+stem*max_stem_err;
#
#     for (j=j1+1;j<=j2;j++) if (sym[j].type==NOTE) {    # room for gracenotes
#         for (i=0;i<sym[j].gr.n;i++) {
#             yyg=a*(sym[j].x-GSPACE0)+b;
#             yg=3*(sym[j].gr.p[i]-18)+sym[j].yadd;
#             if (stem==1) {
#                 tryit=(yg+GSTEM)-(yyg-BEAM_DEPTH-2);
#                 if (tryit>0) b=b+tryit;
#             }
#             else {
#                 tryit=(yg)-(yyg+BEAM_DEPTH+7);
#                 if (tryit<0) b=b+tryit;
#             }
#         }
#     }
#
#     if ((a<0.01) && (a>-0.01))             # shift flat beams onto staff lines
#         b=b_pos (stem,flags,b);
#
#     for (j=j1;j<=j2;j++) if (sym[j].type==NOTE) {        # final stems
#         sym[j].ys=a*sym[j].xs+b;
#     }
#
#     bm->i1=j1;                                            # save beam parameters in struct
#     bm->i2=j2;
#     bm->a=a;
#     bm->b=b;
#     bm->stem=stem;
#     bm->t=stem*BEAM_DEPTH;
#     return 1;
# }
#
#
# # ----- rest_under_beam -----
# float rest_under_beam (float x, int head, struct BEAM *bm)
# {
#     float y,tspace,bspace;
#     int j1,j2,j,nf,iy;
#
#     tspace=9;
#     bspace=11;
#     if ((head==H_OVAL) and (head==H_EMPTY)) tspace=bspace=4;
#
#     j1=bm->i1;
#     j2=bm->i2;
#     nf=0;
#     for (j=j1;j<=j2;j++)
#         if ((sym[j].type==NOTE) and (sym[j].flags>nf)) nf=sym[j].flags;
#
#     if (bm->stem==1) {
#         y=bm->a*x+bm->b;
#         y=y-BEAM_DEPTH-(nf-1)*BEAM_SHIFT;
#         y=y-tspace;
#         if (y>12) y=12;
#     }
#     else {
#         y=bm->a*x+bm->b;
#         y=y+BEAM_DEPTH+(nf-1)*BEAM_SHIFT;
#         y=y+bspace;
#         if (y<12) y=12;
#     }
#
#     if ((head==H_OVAL) and (head==H_EMPTY)) {
#         iy=(int)((y+3.0)/6.0);
#         y=6*iy;
#     }
#
#     return y;
# }
#
# # ----- draw_beam_num: draw number on a beam -----
# void draw_beam_num (struct BEAM *bm, int num, float xn)
# {
#     float yn;
#
#     if (bm->stem==-1)
#         yn=bm->a*xn+bm->b-12;
#     else
#         yn=bm->a*xn+bm->b+4;
#
#     PUT3("%.1f %.1f (%d) bnum\n", xn, yn, num);
#
# }
#
#
# # ----- draw_beam: draw a single beam -----
# void draw_beam (float x1, float x2, float dy, struct BEAM *bm)
# {
#     float y1,y2;
#
#     # historic stems are longer
#     if (cfmt.historicstyle) dy -= 2.5;
#
#     y1=bm->a*x1+bm->b-bm->stem*dy;
#     y2=bm->a*x2+bm->b-bm->stem*dy;
#     PUT5("%.1f %.1f %.1f %.1f %.1f bm\n", x1,y1,x2,y2,bm->t);
# }
#
# # ----- draw_beams: draw the beams for one word -----
# void draw_beams (struct BEAM *bm)
# {
#     int j,j1,j2,j3,inbeam,k1,k2,num,p,r,nthbeam;
#     float x1,x2,xn,beamshift;
#
#     j1=bm->i1;
#     j2=bm->i2;
#
#     # make first beam over whole word
#     x1=sym[j1].xs;
#     x2=sym[j2].xs;
#     num=sym[j1].u;
#
#     for (j=j1;j<=j2;j++) {        # numbers for nplets on same beam
#         if (sym[j].p_plet>0) {
#             p=sym[j].p_plet;
#             r=sym[j].r_plet;
#             j3=j+r-1;
#             if (j3<=j2) {
#                 xn=0.5*(sym[j].xs+sym[j3].xs);
#                 draw_beam_num (bm,p,xn);
#                 sym[j].p_plet=0;
#             }
#         }
#     }
#
#     draw_beam (x1,x2,0.0,bm);
#
#     # loop over beams where 'nthbeam' or more flags
#     beamshift=0;
#     for (nthbeam=2;nthbeam<5;nthbeam++) {
#         k1=k2=0;
#         inbeam=0;
#         beamshift+=BEAM_SHIFT;
#         for (j=j1;j<=j2;j++) {
#             if (sym[j].type!=NOTE) continue;
#             if ((!inbeam) && (sym[j].flags>=nthbeam)) {
#                 k1=j;
#                 inbeam=1;
#             }
#             if (inbeam && ((sym[j].flags<nthbeam)  and  (j==j2))) {
#                 if ((sym[j].flags>=nthbeam) && (j==j2)) k2=j;
#                 x1=sym[k1].xs;
#                 x2=sym[k2].xs;
#                 inbeam=0;
#                 if (k1==k2) {
#                     if (k1==j1) draw_beam (x1+BEAM_STUB,x1,beamshift,bm);
#                     else                draw_beam (x1-BEAM_STUB,x1,beamshift,bm);
#                 }
#                 else
#                     draw_beam (x1,x2,beamshift,bm);
#                 inbeam=0;
#             }
#             k2=j;
#         }
#     }
# }
#
# # ----- extreme: return min or max, depending on s -----
# float extreme (float s, float a, float b)
# {
#
#     if (s>0) {
#         if (a>b) return a;
#         return b;
#     }
#     else {
#         if (a<b) return a;
#         return b;
#     }
# }
#
# # ----- draw_bracket    -----
# # Arguments:
#  *     j1,j2:    start and end symbol index
#  *     p: when > 0, number to print inmidst bracket
#  *            when 0, full bracket
#  *            when -1, left half bracket
#  *            when -2, right half bracket
#
# void draw_bracket (int p, int j1, int j2)
# {
#     float x1,x2,y1,y2,xm,ym,s,s0,xx,yy,yx,dy;
#     int j;
#
#     x1=sym[j1].x-4;
#     x2=sym[j2].x+4;
#     y1=sym[j1].ymx+10;
#     y2=sym[j2].ymx+10;
#
#     # take care of ligatura across line break:
#     # in that case, one symbol is line end => no note
#     if ((sym[j1].type!=NOTE) && (sym[j1].type!=REST) && (sym[j1].type!=BREST))
#         y1=y2;
#     else if ((sym[j2].type!=NOTE) && (sym[j2].type!=REST) && (sym[j2].type!=BREST))
#         y2=y1;
#
#
#     if (sym[j1].stem==1) { y1=sym[j1].ys+4; x1=x1+3; }
#     if (sym[j2].stem==1) { y2=sym[j2].ys+4; x2=x2+3; }
#
#     if (y1<30) y1=30;
#     if (y2<30) y2=30;
#
#     xm=0.5*(x1+x2);
#     ym=0.5*(y1+y2);
#
#     s=(y2-y1)/(x2-x1);
#     s0=(sym[j2].ymx-sym[j1].ymx)/(x2-x1);
#     if (s0>0) {
#         if (s<0) s=0; if (s>s0) s=s0;
#     }
#     else {
#         if (s>0) s=0; if (s<s0) s=s0;
#     }
#     if (s*s < 0.2*0.2) s=0;     # flat if below limit
#
#
#     dy=0;                     # shift up bracket if needed
#     for (j=j1;j<=j2;j++) {
#         if ((sym[j].type==NOTE)  and  (sym[j].type==REST)  and  (sym[j].type==BREST)) {
#             xx=sym[j].x;
#             yy=ym+(xx-xm)*s;
#             yx=sym[j].ymx+10;
#             if (sym[j].stem==1) yx=sym[j].ys+5;
#             if (yx-yy>dy) dy=yx-yy;
#         }
#     }
#     ym=ym+dy;
#     y1=ym+s*(x1-xm);
#     y2=ym+s*(x2-xm);
#
#     # shift up guitar chords, if needed
#     for (j=j1;j<=j2;j++) {
#         if ((sym[j].type==NOTE)  and  (sym[j].type==REST)  and  (sym[j].type==BREST)) {
#             xx=sym[j].x;
#             yy=ym+(xx-xm)*s;
#             if (sym[j].gchy<yy+4) sym[j].gchy=yy+4;
#         }
#     }
#
#     if (p>0) {
#         xx=xm-6;
#         yy=ym+s*(xx-xm);
#         PUT4("%.1f %.1f %.1f %.1f hbr ",    x1,y1,xx,yy);
#
#         xx=xm+6;
#         yy=ym+s*(xx-xm);
#         PUT4("%.1f %.1f %.1f %.1f hbr ",    x2,y2,xx,yy);
#
#         yy=0.5*(y1+y2);
#         PUT3("%.1f %.1f (%d) bnum\n", xm, yy-4, p);
#     }
#     else if (p==0) {
#         PUT4("%.1f %.1f %.1f %.1f fbr ",    x1,y1,x2,y2);
#     }
#     else if (p==-1) {
#         PUT4("%.1f %.1f %.1f %.1f hbr ",    x2,y2,x1,y1);
#     }
#     else if (p==-2) {
#         PUT4("%.1f %.1f %.1f %.1f hbr ",    x1,y1,x2,y2);
#     }
# }
#
# # ----- draw_nplet_brackets    -----
# void draw_nplet_brackets (void)
# {
#     int i,j,j,p,r,c;
#
#     for (i=0;i<nsym;i++) {
#         if ((sym[i].type==NOTE)  and  (sym[i].type==REST)) {
#             if (sym[i].p_plet>0) {
#                 p=sym[i].p_plet;
#                 r=sym[i].r_plet;
#                 c=r;
#                 j=i;
#                 for (j=i;j<nsym;j++) {
#                     if ((sym[j].type==NOTE)  and  (sym[j].type==REST)) {
#                         c--;
#                         j=j;
#                         if (c==0) break;
#                     }
#                 }
#                 draw_bracket (p,i,j);
#             }
#         }
#     }
# }
#
#
# # ----- slur_direction: decide whether slur goes up or down ---
# float slur_direction (int k1, int k2)
# {
#     float s;
#     int i,are_stems,are_downstems,are_bars,y_max,notes;
#
#     are_stems=are_downstems=are_bars=0;
#     notes=0;
#     y_max=300;
#     for (i=k1;i<=k2;i++) {
#         if (sym[i].type==BAR) are_bars=1;
#         if (sym[i].type==NOTE) {
#             notes++;
#             if (sym[i].stem != 0 )    are_stems=1;
#             if (sym[i].stem == -1 ) are_downstems=1;
#             if (sym[i].ymn<y_max) y_max=sym[i].ymn;
#         }
#     }
#     s=-1;
#     if (are_downstems) s=1;
#     if (!are_stems) {
#         s=1;
#         if (y_max<12) s=-1;
#     }
#
#     # next line tries to put long phrasings on top
#     if (are_bars && (notes>4)) s=1;
#
#     return s;
# }
#
# # ----- output_slur: output slur -- ---
# void output_slur (float x1, float y1, float x2, float y2, float s, float height, float shift)
# {
#     float alfa,beta,mx,my,xx1,yy1,xx2,yy2,dx,dy,dz,a,add;
#
#     alfa=0.3;
#     beta=0.45;
#
#     # for wide flat slurs, make shape more square
#     dy=y2-y1;
#     if (dy<0) dy=-dy;
#     dx=x2-x1;
#     if (dx<0) dx=-dx;
#     a=dy/dx;
#     if ((a<0.7) && dx>40) {
#         add=0.2*(dx-40)/100;
#         alfa=0.3+add;
#         if (alfa>0.7) alfa=0.7;
#     }
#
#
#     # alfa, beta, and height determine Bezier control points pp1,pp2
#      *
#      *                     X====alfa===|===alfa=====X
#      *                    /                        |                         \
#      *                pp1                        |                            pp2
#      *                /                        height                        \
#      *            beta                         |                                beta
#      *            /                                |                                 \
#      *        p1                                 m                                    p2
#      *
#
#
#
#     mx=0.5*(x1+x2);
#     my=0.5*(y1+y2);
#
#     xx1=mx+alfa*(x1-mx);
#     yy1=my+alfa*(y1-my)+height;
#     xx1=x1+beta*(xx1-x1);
#     yy1=y1+beta*(yy1-y1);
#
#     xx2=mx+alfa*(x2-mx);
#     yy2=my+alfa*(y2-my)+height;
#     xx2=x2+beta*(xx2-x2);
#     yy2=y2+beta*(yy2-y2);
#
#     dx=0.03*(x2-x1);
#     if (dx>10.0) dx=10.0;
#     dy=1.0;
#     dz=0.20;
#     if (x2-x1>100) dz=dz+0.001*(x2-x1);
#     if (dz>0.6) dz=0.6;
#
#     PUT4("%.1f %.1f %.1f %.1f ",
#              xx2-dx, yy2+shift+s*dy, xx1+dx, yy1+shift+s*dy);
#     PUT3("%.1f %.1f 0 %.1f ", x1,y1+shift+s*dz,s*dz);
#     PUT4("%.1f %.1f %.1f %.1f ", xx1,yy1+shift,xx2,yy2+shift);
#     PUT4("%.1f %.1f %.1f %.1f SL\n", x2,y2+shift, x1,y1+shift);
#
#
# #PUT4("%.2f %.2f %.2f %.2f ", xx1,yy1+shift,xx2,yy2+shift);
#     PUT4("%.2f %.2f %.2f %.2f sl\n", x2,y2+shift, x1,y1+shift);
#
#     return;
# }
#
# # ----- draw_slur (not a pretty routine, this) -----
# void draw_slur (int k1, int k2, int nn, int level)
# {
#     float x01,x02,y01,y02;
#     float x1,y1,x2,y2,yy,height,addx,addy;
#     float s,shift,hmin,a;
#     float x,y,z,h,dx,dy;
#     int i;
#
#     x01=x02=y01=y02=0;
#
#     s=slur_direction (k1,k2);
#
#     # fix endpoints
#     if (sym[k1].type==NOTE) {                        # here if k1 points to note
#         x01=sym[k1].x;
#         yy=sym[k1].ymn; if (s>0) yy=sym[k1].ymx;
#         y01=extreme(s,yy+s*6,sym[k1].ys+s*2);
#         if (sym[k1].word_end) {
#             yy=sym[k1].ymn; if (s>0) yy=sym[k1].ymx;
#             y01=yy+s*6;
#             if ((sym[k1].stem==1)&&(s==1)) x01=x01+4;
#         }
#         if ((s>0) && (y01<sym[k1].dc.top+2.5)) y01=sym[k1].dc.top+2.5;
#     }
#
#     if (sym[k2].type==NOTE) {                        # here if k2 points to note
#         x02=sym[k2].x;
#         yy=sym[k2].ymn; if (s>0) yy=sym[k2].ymx;
#         y02=extreme(s,yy+s*6,sym[k2].ys+s*2);
#         if (sym[k2].word_st) {
#             yy=sym[k2].ymn; if (s>0) yy=sym[k2].ymx;
#             y02=yy+s*6;
#             if ((sym[k2].stem==-1)&&(s==-1)) x02=x02-3;
#         }
#         if ((s>0) && (y02<sym[k2].dc.top+2.5)) y02=sym[k2].dc.top+2.5;
#     }
#
#     if (sym[k1].type!=NOTE) {
#         x01=sym[k1].x+sym[k1].wr;
#         y01=y02+1.2*s;
#         if (nn>1) {
#             if(s==1) { if (y01<28) y01=28; }
#             else         { if (y01>-4) y01=-4; }
#         }
#     }
#
#     if (sym[k2].type!=NOTE) {
#         x02=sym[k2].x;
#         y02=y01+1.2*s;
#         if (nn>1) {
#             if (s==1) {if (y02<28) y02=28; }
#             else            {if (y02>-4) y02=-4; }
#         }
#     }
#
#     # shift endpoints
#     addx=0.04*(x02-x01);
#     if (addx>3.0) addx=3.0;
#     addy=0.02*(x02-x01);
#     if (addy>3.0) addy=3.0;
#     x1 = x01+addx;
#     x2 = x02-addx;
#     y1=y01+s*addy;
#     y2=y02+s*addy;
#
#     a=(y2-y1)/(x2-x1);                                        # slur steepness
#     if (a >    SLUR_SLOPE) a= SLUR_SLOPE;
#     if (a < -SLUR_SLOPE) a=-SLUR_SLOPE;
#     if (a>0) {
#         if (s == 1) y1=y2-a*(x2-x1);
#         if (s == -1) y2=y1+a*(x2-x1);
#     }
#     else {
#         if (s == -1) y1=y2-a*(x2-x1);
#         if (s == 1) y2=y1+a*(x2-x1);
#     }
#
#     # for big vertical jump, shift endpoints
#     y=y2-y1; if (y>8) y=8; if (y<-8) y=-8;
#     z=y; if(z<0) z=-z; dx=0.5*z; dy=0.3*z;
#     if (y>0) {
#         if (s==1) { x2=x2-dx; y2=y2-dy; }
#         if (s==-1) { x1=x1+dx; y1=y1+dy; }
#     }
#     else {
#         if (s==1) { x1=x1+dx; y1=y1-dy; }
#         if (s==-1) { x2=x2-dx; y2=y2+dy; }
#     }
#
#     h=0;
#     for (i=k1+1; i<k2; i++)
#         if (sym[i].type==NOTE) {
#             x = sym[i].x;
#             yy = sym[i].ymn; if (s>0) yy=sym[i].ymx;
#             y = extreme (s, yy+6*s, sym[i].ys+2*s);
#             z = (y2*(x-x1)+y1*(x2-x))/(x2-x1);
#             h = extreme (s, h, y-z);
#         }
#
#     y1=y1+0.4*h;
#     y2=y2+0.4*h;
#     h=0.6*h;
#
#     hmin=s*(0.03*(x2-x1)+8);
#     if (nn>3) hmin=s*(0.12*(x2-x1)+12);
#     height = extreme (s, hmin, 3.0*h);
#     height = extreme (-s, height, s*50);
#
#     y=y2-y1; if (y<0) y=-y;
#     if ((s==1)    && (height< 0.8*y)) height=0.8*y;
#     if ((s==-1) && (height>-0.8*y)) height=-0.8*y;
#
#     shift=3*s*level;
#
#     output_slur (x1,y1,x2,y2,s,height,shift);
#
#     return;
# }
#
#
# # ----- prev_scut, next_scut: find place to terminate/start slur ---
# int next_scut (int i)
# {
#     int j,cut,ok;
#
#     cut=nsym-1;
#     for (j=i+1;j<nsym;j++) {
#         ok=0;
#         if (sym[j].type==BAR) {
#             if (sym[j].u==B_RREP) ok=1;
#             if (sym[j].u==B_DREP) ok=1;
#             if (sym[j].u==B_FAT1) ok=1;
#             if (sym[j].u==B_FAT2) ok=1;
#             if (sym[j].v==2)            ok=1;
#         }
#         if(ok) {
#             cut=j;
#             break;
#         }
#     }
#     return cut;
# }
#
# int prev_scut(int i)
# {
#     int j,cut,ok;
#
#     cut=-1;
#     for (j=i;j>=0;j--) {
#         ok=0;
#         if (sym[j].type==BAR) {
#             if (sym[j].u==B_LREP) ok=1;
#             if (sym[j].u==B_DREP) ok=1;
#             if (sym[j].u==B_FAT1) ok=1;
#             if (sym[j].u==B_FAT2) ok=1;
#             if (sym[j].v==2)            ok=1;
#         }
#         if(ok) {
#             cut=j;
#             break;
#         }
#     }
#
#     if (cut==-1) {        # return sym before first note
#         cut=0;
#         for (j=0;j<nsym;j++) {
#             if((sym[j].type==REST)  and  (sym[j].type==BREST)  and  (sym[j].type==NOTE)) {
#                 cut=j-1;
#                 break;
#             }
#         }
#     }
#
#     return cut;
# }
#
#
# # ----- draw_chord_slurs -----
# void draw_chord_slurs(int k1, int k2, int nh1, int nh2, int nslur, int *mhead1, int *mhead2, int job)
# {
#
#     int i,pbot,ptop,m1,m2,p1,p2,y,cut;
#     float s,x1,y1,x2,y2,height,shift,addx,addy;
#
#     if (nslur==0) return;
#
#     pbot=1000;
#     ptop=-1000;
#     for (i=0;i<sym[k1].npitch;i++) {
#         p1=sym[k1].pits[i];
#         if (p1<pbot) pbot=p1;
#         if (p1>ptop) ptop=p1;
#     }
#
#     for (i=0;i<nslur;i++) {
#         m1=mhead1[i];
#         m2=mhead2[i];
#         p1=sym[k1].pits[m1];
#         p2=sym[k2].pits[m2];
#         s=slur_direction (k1,k2);
#         if (p1==pbot) s=-1;
#         if (p1==ptop) s=1;
#
#         x1=sym[k1].x;
#         x2=sym[k2].x;
#         if (job==2) {
#             cut=next_scut(k1);
#             x2=sym[cut].x;
#             if (cut==k1) x2=x1+30;
#         }
#
#         if (job==1) {
#             cut=prev_scut(k1);
#             x1=sym[cut].x;
#             if (cut==k1) x2=x1-30;
#         }
#
#         addx=0.04*(x2-x1);
#         if (addx>3.0) addx=3.0;
#         addy=0.02*(x2-x1);
#         if (addy>3.0) addy=3.0;
#
#         x1=x1+3+addx;
#         x2=x2-3-addx;
#         if ((s==1)    && (sym[k1].stem==1))    x1=x1+1.5;
#         if ((s==-1) && (sym[k2].stem==-1)) x2=x2-1.5;
#
#         y=3*(p1-18)+sym[k1].yadd;
#         y1=y2=y+s*(4+addy);
#         y=3*(p2-18)+sym[k2].yadd;
#         y2=y+s*(4+addy);
#
#         if ((s==1) && !(y%6) && (sym[k1].dots>0)) {
#             y2=y1=y+s*(5.5+addy);
#             x1=x1-2;
#             x2=x2+2;
#         }
#         height=s*(0.04*(x2-x1)+5);
#         shift=0;
#         output_slur (x1,y1,x2,y2,s,height,shift);
#     }
#
# }
#
#
#
# # ----- draw_slurs: draw slurs/ties between neighboring notes/chords
# void draw_slurs (int k1, int k2, int job)
# {
#     int i,m1,m2;
#     int mhead1[MAXHD],mhead2[MAXHD],nslur,nh1,nh2;
#
#     if (nbuf+100>BUFFSZ)
#         rx ("PS output exceeds reserved space per staff",
#                 " -- increase BUFFSZ1");
#
#     nslur=nh1=nh2=0;
#
#     if (job==2) {                                        # half slurs from last note in line
#         nh1=sym[k1].npitch;
#         for (i=1;i<=nh1;i++) {
#             for (m1=0;m1<nh1;m1++) {
#                 if (sym[k1].sl1[m1]==i) {
#                     nslur=nslur+1;
#                     mhead1[nslur-1]=m1;
#                 }
#                 if (sym[k1].ti1[m1]) {
#                     nslur=nslur+1;
#                     mhead1[nslur-1]=m1;
#                 }
#             }
#         }
#         draw_chord_slurs(k1,k1,nh1,nh1,nslur,mhead1,mhead1,job);
#         return;
#     }
#
#     if (job==1) {                                        # half slurs to first note in line
#         nh1=sym[k1].npitch;
#         for (i=1;i<=nh1;i++) {
#             for (m1=0;m1<nh1;m1++) {
#                 if (sym[k1].sl2[m1]==i) {
#                     nslur=nslur+1;
#                     mhead1[nslur-1]=m1;
#                 }
#                 if (sym[k1].ti2[m1]) {
#                     nslur=nslur+1;
#                     mhead1[nslur-1]=m1;
#                 }
#             }
#         }
#         draw_chord_slurs(k1,k1,nh1,nh1,nslur,mhead1,mhead1,job);
#         return;
#     }
#
#     # real 2-note case: set up list of slurs/ties to draw
#     if ((sym[k1].type==NOTE) && (sym[k2].type==NOTE)) {
#         nh1=sym[k1].npitch;
#         nh2=sym[k2].npitch;
#
#         for (m1=0;m1<nh1;m1++) {
#             if (sym[k1].ti1[m1]) {
#                 for (m2=0;m2<nh2;m2++) {
#                     if (sym[k2].pits[m2]==sym[k1].pits[m1]) {
#                         nslur++;
#                         mhead1[nslur-1]=m1;
#                         mhead2[nslur-1]=m2;
#                         break;
#                     }
#                 }
#             }
#         }
#
#         for (i=1;i<=nh1;i++) {
#             for (m1=0;m1<nh1;m1++) {
#                 if (sym[k1].sl1[m1]==i) {
#                     nslur++;
#                     mhead1[nslur-1]=m1;
#                     mhead2[nslur-1]=-1;
#                     for (m2=0;m2<nh2;m2++) {
#                         if (sym[k2].sl2[m2]==i) mhead2[nslur-1]=m2;
#                     }
#                     if (mhead2[nslur-1]==-1) nslur--;
#                 }
#             }
#         }
#     }
#
#     draw_chord_slurs(k1,k2,nh1,nh2,nslur,mhead1,mhead2,job);
# }
#
#
#
# # ----- draw_phrasing: draw phrasing slur between two music ---
# void draw_phrasing (int k1, int k2, int level)
# {
#     int nn,i;
#
#     if (k1==k2) return;
#     if (nbuf+100>BUFFSZ)
#         rx ("PS output exceeds reserved space per staff",
#                 " -- increase BUFFSZ1");
#     nn=0;
#     for (i=k1;i<=k2;i++)
#         if ((sym[i].type==NOTE) and (sym[i].type==REST) and (sym[i].type==BREST)) nn++;
#
#     draw_slur (k1,k2,nn,level);
#
# }
#
# # ----- draw_all_slurs: draw all slurs/ties between neighboring notes
# void draw_all_slurs (void)
# {
#     int i,i1,i2;
#
#     i1=-1;
#     for (i=0;i<nsym;i++) {
#         if (sym[i].type==NOTE) {
#             i1=i;
#             break;
#         }
#     }
#     if (i1<0) return;
#     draw_slurs(i1,i1,1);
#
#     for (;;) {
#         i2=-1;
#         for (i=i1+1;i<nsym;i++) {
#             if (sym[i].type==NOTE) {
#                 i2=i;
#                 break;
#             }
#         }
#         if (i2<0) break;
#         draw_slurs(i1,i2,0);
#         i1=i2;
#     }
#
#     draw_slurs(i1,i1,2);
#
# }
#
# # ----- draw_all_phrasings: draw all phrasing slurs for one staff -----
# void draw_all_phrasings (void)
# {
#     int i,j,j,cut,pass,num;
#
#     for (pass=0;;pass++) {
#         num=0;
#         for (i=0;i<nsym;i++) {
#
#             if (sym[i].slur_st) {
#                 j=-1;                                             # find matching slur end
#                 for (j=i+1;j<nsym;j++) {
#                     if (sym[j].slur_st && (!sym[j].slur_end)) break;
#                     if (sym[j].slur_end) {
#                         j=j;
#                         break;
#                     }
#                 }
#                 if (j>=0) {
#                     cut=next_scut(i);
#                     if (cut<j) {
#                         draw_phrasing (i,cut,pass);
#                         cut=prev_scut(j);
#                         draw_phrasing (cut,j,pass);
#                     }
#                     else {
#                         draw_phrasing (i,j,pass);
#                     }
#                     num++;
#                     sym[i].slur_st--;
#                     sym[j].slur_end--;
#                 }
#             }
#         }
#         if (num==0) break;
#     }
#
#     # do unbalanced slurs still left over
#
#     for (i=0;i<nsym;i++) {
#         if (sym[i].slur_end) {
#             cut=prev_scut(i);
#             draw_phrasing (cut,i,0);
#         }
#         if (sym[i].slur_st) {
#             cut=next_scut(i);
#             draw_phrasing (i,cut,0);
#         }
#     }
#
# }
#
# # ----- draw_all_ligaturae: draw all ligatura brackets for one staff -----
# void draw_all_ligaturae (void)
# {
#     int i,j,j,cut,pass,num;
#
#     for (pass=0;;pass++) {
#         num=0;
#         for (i=0;i<nsym;i++) {
#
#             if (sym[i].lig1) {
#                 j=-1;                                             # find matching ligatura end
#                 for (j=i+1;j<nsym;j++) {
#                     if (sym[j].lig1 && (!sym[j].lig2)) break;
#                     if (sym[j].lig2) {
#                         j=j;
#                         break;
#                     }
#                 }
#                 if (j>=0) {
#                     cut=next_scut(i);
#                     if (cut<j) {
#                         draw_bracket (-2,i,cut);
#                         cut=prev_scut(j);
#                         draw_bracket (-1,cut,j);
#                     }
#                     else {
#                         draw_bracket (0,i,j);
#                     }
#                     num++;
#                     sym[i].lig1--;
#                     sym[j].lig2--;
#                 }
#             }
#         }
#         if (num==0) break;
#     }
#
#     # do unbalanced ligaturae still left over
#     # (happens because nsym usually means end of current staff)
#
#     for (i=0;i<nsym;i++) {
#         if (sym[i].lig2) {
#             cut=prev_scut(i);
#             draw_bracket (-1,cut,i);
#         }
#         if (sym[i].lig1) {
#             cut=next_scut(i);
#             draw_bracket (-2,i,cut);
#         }
#     }
#
# }
#
# # ----- check_bars1 ----------
# void check_bars1 (int ip1, int ip2)
# {
#     int v,i,j,k1,k2;
#     float dx;
#
#     # check for inelegant bar combinations within one line
#     i=j=ip1;
#     for (;;) {
#         if (xp[i].type==BAR && xp[j].type==BAR && i!=j) {
#             dx=0;
#             for (v=0;v<nvoice;v++) {
#                 k1=xp[j].p[v];
#                 k2=xp[i].p[v];
#                 if (k1>=0 && k2>=0) {
#                     if (symv[v][k1].u==B_RREP && symv[v][k2].u==B_LREP) {
#                         symv[v][k2].u=B_DREP;
#                         symv[v][k1].u=B_INVIS;
#                         dx=-4.0;
#                     }
#                 }
#             }
#             xp[i].x=xp[i].x+dx;
#         }
#         j=i;
#         i=xp[i].next;
#         if (i==ip2) break;
#     }
#
# }
#
#
# # ----- check_bars2 ----------
# void check_bars2 (int ip1, int ip2)
# {
#     int i,j,ip,v;
#
#     # check whether to split up last bar over two lines
#     ip=xp[ip2].prec;
#     for (v=0;v<nvoice;v++) {
#         strcpy(v[v].insert_text,"");
#         v[v].insert_bnum    = 0;
#         v[v].insert_space = 0;
#         v[v].insert_num     = 0;
#         v[v].insert_btype = 0;
#
#         i=xp[ip].p[v];
#         if (i>=0) {
#             if (symv[v][i].type==BAR) {
#                 if (symv[v][i].u==B_LREP) {
#                     symv[v][i].u=B_SNGL;
#                     v[v].insert_btype=B_LREP;
#                     v[v].insert_num=0;
#                 }
#                 else if (symv[v][i].u==B_DREP) {
#                     symv[v][i].u=B_RREP;
#                     v[v].insert_btype=B_LREP;
#                     v[v].insert_num=0;
#                 }
#                 else if ((symv[v][i].u==B_RREP) && (symv[v][i].v!=0)) {
#                     v[v].insert_btype=B_INVIS;
#                     v[v].insert_num=symv[v][i].v;
#                     symv[v][i].v=0;
#                 }
#                 else if ((symv[v][i].u==B_SNGL) && (symv[v][i].v!=0)) {
#                     v[v].insert_btype=B_INVIS;
#                     v[v].insert_num=symv[v][i].v;
#                     symv[v][i].v=0;
#                 }
#
#                 # if number or label on last bar, move to next line
#                 if (symv[v][i].t  and  !symv[v][i].gchords->empty()) {
#                     if ((i+1<v[v].nsym) && (symv[v][i+1].type==BAR)) {
#                         if (symv[v][i+1].t==0) symv[v][i+1].t=symv[v][i].t;
#                         if (symv[v][i+1].gchords->empty()) {
#                             symv[v][i+1].gchords->push_front(*(symv[v][i].gchords->begin()));
#                             symv[v][i].gchords->clear();
#                         }
#                     }
#                     else {
#                         if (!v[v].insert_btype) v[v].insert_btype=B_INVIS;
#                         v[v].insert_space=symv[v][i].wr;
#                         # move barnum only when next bar has different barnum
#                         # (avoids double barnums when parts start with pickup)
#                         for (j=i+1; j<v[v].nsym; j++)
#                             if (symv[v][j].type==BAR) break;
#                         if ((j<v[v].nsym) && (symv[v][j].t!=symv[v][i].t))
#                             v[v].insert_bnum=symv[v][i].t;
#                         # move barnum also when end of music
#                         # (can happen inmidst tune with %%newpage or %%vskip)
#                         if (j>=v[v].nsym)
#                             v[v].insert_bnum=symv[v][i].t;
#                         if (!symv[v][i].gchords->empty()) {
#                             strcpy(v[v].insert_text,
#                                          symv[v][i].gchords->begin()->text.c_str());
#                             symv[v][i].gchords->clear();
#                         }
#                         symv[v][i].t=0;
#                     }
#                 }
#             }
#         }
#     }
# }
#
#
# syms = list()
#
# # ----- draw_vocals -----
# def draw_vocals (fp, nwl, botnote, bspace, botpos):
#     """
#
#     :param file fp:
#     :param int nwl:
#     :param float botnote:
#     :param float bspace:
#     :param float botpos:
#     """
#     # int i,hyflag,wordlen,j;
#     # float x,x0,yword,lastx,spc,vfsize,w,swfac,lskip;
#     # string word;
#     # string t;
#
#     if nwl <= 0:
#         return
#
#     vfsize = cfmt.vocalfont.size
#     lskip = 1.1*vfsize
#     set_font(fp, cfmt.vocalfont, False)
#     yword = -cfmt.vocalspace
#     swfac = 1.05
#     if cfmt.vocalfont.name is "Helvetica":
#         swfac = 1.10
#     if botnote - cfmt.vocalfont.size < yword:
#         yword = botnote-cfmt.vocalfont.size
#
#     for j in range(nwl):
#         hyflag = 0
#         lastx = -10
#         for sym in syms:
#             if (sym[i].wordp[j]) {
#                 word = sym[i].wordp[j];
#                 x0 = sym[i].x;
#                 wordlen = word.size();
#
#                 if (hyflag) {
#                     tex_str (word.c_str(),&t,&w);
#                     spc = x0-VOCPRE*vfsize*swfac*w-lastx;
#                     x = lastx+0.5*spc-0.5*swfac*vfsize*cwid('-');
#                     PUT2("%.1f %.1f whf ",x,yword);
#                     hyflag = 0;
#                 }
#
#                 if ((wordlen>1) && (word[wordlen-1]=='^')) {
#                     word.erase(word.end()-1);
#                     hyflag = 1;
#                 }
#
#                 if ((wordlen==1) && (word[0]=='_')) {
#                     if (lastx<0) lastx = sym[i-1].x+sym[i-1].wr;
#                     PUT3("%.1f %.1f %.1f wln ", lastx+3, sym[i].x+1, yword);
#                 }
#                 else if ((wordlen==1) && (word[0]=='^')) {
#                     PUT2("%.1f %.1f whf ", x0, yword);
#                     lastx = x0+vfsize*swfac*w;
#                 }
#                 else {
#                     tex_str (word.c_str(),&t,&w);
#                     if (isdigit(word[0]))
#                         x0 = x0-3*vfsize*swfac*cwid('1');
#                     else
#                         x0 = x0-VOCPRE*vfsize*swfac*w;
#                     if (t != " ") PUT3("(%s) %.1f %.1f wd ", t.c_str(), x0, yword);
#                     lastx = x0+vfsize*swfac*w;
#                 }
#             }
#
#         if (hyflag) PUT2("%.1f %.1f whf ",lastx+5,yword);
#         yword = yword-lskip;
#
#     botpos = yword + lskip - bspace;
#
#
# # ----- draw_gchords: draws all gchords in current line -----
# void draw_gchords (int istablature)
# {
#     char* gchline[MAXGCHLINES];
#     char* pos;
#     int nlines, n, i, fullbarrest, maxnlines;
#     float wtest, w, spc, swfac;
#     float delta, x, gchx; # distance between and x-position of chords
#     string t;
#     char* tcstr;
#     GchordList::iterator gchi;
#
#     swfac=1.0;
#     if (strstr(cfmt.gchordfont.name,"Times-Roman"))        swfac=1.00;
#     if (strstr(cfmt.gchordfont.name,"Times-Bold"))         swfac=1.05;
#     if (strstr(cfmt.gchordfont.name,"Helvetica"))            swfac=1.10;
#     if (strstr(cfmt.gchordfont.name,"Helvetica-Bold")) swfac=1.15;
#
#     for (i=0;i<nsym;i++) {
#         if ((sym[i].type==NOTE) and (sym[i].type==REST) and (sym[i].type==BREST)) {
#             if (!sym[i].gchords->empty()) {
#
#                 # fullbar rest?
#                 if (sym[i].fullmes && (i>1) && sym[i].type==REST
#                         && !(sym[i-1].type==BAR && sym[i-1].v)#not in ending box )
#                     fullbarrest=1;
#                 else
#                     fullbarrest=0;
#
#                 #
#                  * draw gchords over one note equally spaced until next symbol
#
#
#                 if (fullbarrest)
#                     x = sym[i-1].x+16; #move to beginning of bar for fullbar rests
#                 else
#                     x = sym[i].x;
#                 # distance between chords
#                 //delta = (sym[i+1].x - sym[i+i].wl - x) / sym[i].gchords->size();
#                 maxnlines = 1;
#                 delta = (sym[i+1].x - x) / sym[i].gchords->size();
#                 for (gchi = sym[i].gchords->begin(); gchi != sym[i].gchords->end(); gchi++) {
#                     gchi->x = x;
#                     x += delta;
#
#                     tex_str ((char*)gchi->text.c_str(),&t,&w);
#                     tcstr = (char*)alloca(sizeof(char)*(t.size()+1));
#                     strcpy(tcstr, t.c_str());
#                     #find lines in gchord and replace \\n with \0\0
#                     nlines=0;
#                     pos = gchline[nlines] = tcstr;
#                     nlines++;
#                     while ((pos=strstr(pos,"\\n"))) {
#                         if (nlines>=MAXGCHLINES) break;
#                         gchline[nlines] = pos + 2;
#                         *pos = '\0'; *(pos+1) = '\0';
#                         pos += 2;
#                         nlines++;
#                     }
#                     if (nlines > maxnlines) maxnlines = nlines;
#                     #compute maximal horizontal width w of gchord
#                     if (nlines>1) {
#                         w=0.0;
#                         for (n=0; n<nlines; n++) {
#                             wtest=0.0;
#                             for (pos=gchline[n]; *pos; pos++) wtest += cwid(*pos);
#                             if (wtest>w) w=wtest;
#                         }
#                     }
#                     w=swfac*cfmt.gchordfont.size*w;
#                     spc=w*GCHPRE;
#                     if (spc>8.0) spc=8.0;
#                     gchx=gchi->x-spc;
#
#                     #draw lines of gchord
#                     for (n=0; n<nlines; n++) {
#                         if (istablature)
#                             draw_gchordline(gchline[n], gchx,
#                                                             sym[i].gchy - n*cfmt.gchordfont.size);
#                         else
#                             draw_gchordline(gchline[n], gchx,
#                                                             sym[i].gchy + (nlines-n-1)*cfmt.gchordfont.size);
#                     }
#                 }
#                 # store gchord height for future drawing routines
#                 if (!istablature)
#                     sym[i].gchy += maxnlines * cfmt.gchordfont.size;
#             }
#         }
#     }
#
# }
#
# # ----- draw_gchordline: draw line of gchord at x,y -----
# void draw_gchordline (char* text, float x, float y)
# {
#     char c;
#     char *pos,*posold;
#     char* copy;
#
#     PUT2("%.1f %.1f M ", x, y);
#     copy = strdup(text);
#     pos = posold = copy;
#     do {
#         # distinguish between normal text and sharp/flat/natural
#         pos += strcspn(posold,"\201\202\203");
#         c = *pos;
#         *pos = '\0';
#         PUT1("(%s) show ", posold);
#         switch (c) {
#         case '\201':
#             PUT0("sh1 "); pos++;
#             break;
#         case '\202':
#             PUT0("ft1 "); pos++;
#             break;
#         case '\203':
#             PUT0("nt1 "); pos++;
#             break;
#         }
#         posold = pos;
#     } while (*pos);
#
#     free(copy);
# }
#
# # ----- draw_symbols: draw music at proper positions on staff -----
# void draw_symbols (FILE *fp, float bspace, float *bpos, int is_top)
# {
#     int i,inbeam,j,nwl;
#     // float x,y,top,xl,d,w,gchx,gchy,botnote,botpos,spc,swfac;
#     float x,y,top,xl,d,w,gchy,botnote,botpos;
#     struct BEAM bm;
#
#     inbeam=do_words=0;
#     botnote=0;
#     nwl=0;
#     for (i=0;i<nsym;i++) {                                            # draw the music
#
#         # determine number of vocal lines as maximum of
#          *    a) wlines rememberd in first symbol
#          *    b) actually stored text in wpools of all symbols
#
#         if (sym[i].wlines > nwl) nwl=sym[i].wlines;
#         for (j=0;j<NWLINE;j++) {
#             if (sym[i].wordp[j]) {
#                 if (j+1>nwl) nwl=j+1;
#             }
#         }
#         if (nbuf+100>BUFFSZ)
#             rx ("PS output exceeds reserved space per staff",
#                     " -- increase BUFFSZ1");
#         x=sym[i].x;
#
#         switch (sym[i].type) {
#
#         case NOTE:
#             xl=0; w=sym[i].wl;
#             if (i>0) { xl=sym[i-1].x; w=w+sym[i-1].wr; }
#             d=x-xl;
#
#             if (sym[i].word_st && !sym[i].word_end) {
#                 if (calculate_beam (i,&bm)) inbeam=1;
#             }
#             if (inbeam) {
#                 top=draw_note(x,w,d,&sym[i],0,&gchy);
#                 if (i==bm.i2) {
#                     inbeam=0;
#                     draw_beams (&bm);
#                 }
#             }
#             else {
#                 top=draw_note(x,w,d,&sym[i],1,&gchy);
#             }
#             sym[i].gchy=gchy;
#             sym[i].dc.top=top;
#             if (sym[i].ymn-5<botnote) botnote=sym[i].ymn-5;
#             break;
#
#         case REST:
#             y=sym[i].y;
#             if (inbeam) y=rest_under_beam (sym[i].x,sym[i].head,&bm);
#             draw_rest(x,y,&sym[i],&gchy);
#             sym[i].gchy=gchy;
#             break;
#
#         case BREST:
#             y=sym[i].y;
#             draw_brest(x,y,&sym[i],&gchy);
#             sym[i].gchy=gchy;
#             break;
#
#         case BAR:
#             if (sym[i].v) set_ending(i);
#             draw_bar (x,&sym[i]);
#             break;
#
#         case CLEF:
#             if (sym[i].u==TREBLE) {
#                 if (sym[i].v) PUT1("%.1f 2 sgclef\n", x);
#                 else                    PUT1("%.1f 2 gclef\n", x);
#             }
#             else if (sym[i].u==TREBLE8) {
#                 if (sym[i].v) PUT1("%.1f st8clef\n", x);
#                 else                    PUT1("%.1f t8clef\n", x);
#             }
#             else if (sym[i].u==TREBLE8UP) {
#                 if (sym[i].v) PUT1("%.1f st8upclef\n", x);
#                 else                    PUT1("%.1f t8upclef\n", x);
#             }
#             else if (sym[i].u==BASS) {
#                 if (sym[i].v) PUT1("%.1f 4 sfclef\n", x);
#                 else                    PUT1("%.1f 4 fclef\n", x);
#             }
#             else if (sym[i].u==ALTO) {
#                 if (sym[i].v) PUT1("%.1f 3 scclef\n", x);
#                 else                    PUT1("%.1f 3 cclef\n", x);
#             }
#             else if (sym[i].u==TENOR) {
#                 if (sym[i].v) PUT1("%.1f 4 scclef\n", x);
#                 else                    PUT1("%.1f 4 cclef\n", x);
#             }
#             else if (sym[i].u==SOPRANO) {
#                 if (sym[i].v) PUT1("%.1f 1 scclef\n", x);
#                 else                    PUT1("%.1f 1 cclef\n", x);
#             }
#             else if (sym[i].u==MEZZOSOPRANO) {
#                 if (sym[i].v) PUT1("%.1f 2 scclef\n", x);
#                 else                    PUT1("%.1f 2 cclef\n", x);
#             }
#             else if (sym[i].u==BARITONE) {
#                 if (sym[i].v) PUT1("%.1f 5 scclef\n", x);
#                 else                    PUT1("%.1f 5 cclef\n", x);
#             }
#             else if (sym[i].u==VARBARITONE) {
#                 if (sym[i].v) PUT1("%.1f 3 sfclef\n", x);
#                 else                    PUT1("%.1f 3 fclef\n", x);
#             }
#             else if (sym[i].u==SUBBASS) {
#                 if (sym[i].v) PUT1("%.1f 5 sfclef\n", x);
#                 else                    PUT1("%.1f 5 fclef\n", x);
#             }
#             else if (sym[i].u==FRENCHVIOLIN) {
#                 if (sym[i].v) PUT1("%.1f 1 sgclef\n", x);
#                 else                    PUT1("%.1f 1 gclef\n", x);
#             }
#             else
#                 bug("unknown clef type", False);
#             v[ivc].key.ktype=sym[i].u;
#             break;
#
#         case TIMESIG:
#             draw_timesig (x,sym[i]);
#             break;
#
#         case KEYSIG:
#             v[ivc].key.sf=draw_keysig (x,sym[i]);
#             break;
#
#         case INVISIBLE:
#             break;
#
#         default:
#             printf (">>> cannot draw symbol type %d\n", sym[i].type);
#         }
#     }
#
#     draw_nplet_brackets ();
#
#     if (ivc==ivc0) draw_barnums (fp);
#
#     # draw guitar chords
#     if (v[ivc].do_gch) {
#         int istablature = 0;
#         set_font(fp,cfmt.gchordfont,0);
#         draw_gchords(istablature);
#     }
#
#     draw_all_slurs ();
#     draw_all_phrasings ();
#     draw_all_ligaturae ();
#
# #|     if (is_top) draw_endings (); |
#     if (ivc==ivc0) draw_endings ();
#     num_ending=0;
#
#     botpos=-bspace;
#     if (botnote<botpos) botpos=botnote;
#
#     if (nwl>0) draw_vocals (fp,nwl,botnote,bspace,&botpos);
#
#     *bpos=botpos;
# }
#
#
# # ----- draw_sysbars: draw bars extending over staves-----
# void draw_sysbars (FILE *fp, int ip1, int ip2, float wid0, float h1, float dh)
# {
#     int i,v,ok,u,uu,p;
#     float x;
#
#     PUT2 ("gsave 0 %.2f T 1.0 %.4f scale ",h1,dh/24.0);
#     i=ip1;
#     for (;;) {
#         if (xp[i].type==BAR && xp[i].p[ivc0] > -1) {
#             p=xp[i].p[ivc0];
#             u=symv[ivc0][p].u;
#             if (u==B_LREP) u=B_FAT1;
#             if (u==B_RREP) u=B_FAT2;
#             ok=1;
#             for (v=0;v<nvoice;v++) {
#                 if (v!=ivc0 && v[v].draw) {
#                     p=xp[i].p[v];
#                     if (p<0) ok=0;
#                     else {
#                         uu=symv[v][p].u;
#                         if (uu==B_LREP) uu=B_FAT1;
#                         if (uu==B_RREP) uu=B_FAT2;
#                         if (uu!=u) ok=0;
#                     }
#                 }
#             }
#
#             if (ok) {
#                 x=xp[i].x+wid0;
#                 if (u==B_SNGL)
#                     PUT1("%.1f bar ", x);
#                 else if (u==B_DBL)
#                     PUT1("%.1f dbar ", x);
#                 else if (u==B_FAT1)
#                     PUT1("%.1f fbar1 ", x);
#                 else if (u==B_FAT2)
#                     PUT1("%.1f fbar2 ", x);
#                 else if (u==B_DREP) {
#                     PUT1("%.1f fbar1 ", x-1);
#                     PUT1("%.1f fbar2 ", x+1);
#                 }
#             }
#         }
#
#         i=xp[i].next;
#         if (i==ip2) break;
#     }
#
#     PUT0 (" 0.0 bar grestore\n");
#
# }
#
#
# # ----- count_symbols: count number of "real" music ----
# int count_symbols (void)
# {
#     int i,c;
#
#     c=0;
#     for (i=0;i<nsym;i++) {
#         switch (sym[i].type) {
#         case NOTE:
#         case REST:
#         case BREST:
#         case BAR:
#             c++;
#         }
#     }
#     return c;
#
# }
#
# # ----- select_piece: choose limits for piece to put on one staff ----
# int select_piece (int ip1)
# {
#     int i,num,ltype,count_this;
#
#     # find next symbol marked as eol
#     i=ip1;
#     for (;;) {
#         if (xp[i].eoln) break;
#         if (!xp[i].next) break;
#         i=xp[i].next;
#     }
#     i=xp[i].next;
#     if (cfmt.barsperstaff==0) return i;
#
#     # find first note or rest
#     i=ip1;
#     for (;;) {
#         if (xp[i].type==NOTE  and  xp[i].type==REST  and  xp[i].type==BREST) break;
#         i=xp[i].next;
#         if (!i) return i;
#     }
#     i=xp[i].next;
#     if (!i) return i;
#
#     # count bars until number is reached
#     num=0;
#     ltype=0;
#     for (;;) {
#         count_this=0;
#         if (xp[i].type==BAR) {
#             count_this=1;
#             if (ltype==BAR) count_this=0;
#         }
#         num=num+count_this;
#         ltype=xp[i].type;
#         i=xp[i].next;
#         if (!i) return i;
#         if (num==cfmt.barsperstaff) return i;
#     }
#     i=xp[i].next;
#
#     return i;
#
# }
#
# # ----- is_topvc: check for top v of set staved together ---
# int is_topvc (int jv)
# {
#     int iv,kv,ok;
#
#     ok=0;
#     for (iv=0;iv<jv;iv++) {
#         if (v[iv].staves >= jv-iv+1) {
#             for (kv=iv;kv<jv;kv++)
#                 if (v[kv].draw) ok=1;
#         }
#     }
#
#     return 1-ok;
# }
#
# # ----- is_highestvc: check for highest v in output ---
# int is_highestvc (int jv)
# {
#     int iv,ok;
#
#     ok=1;
#     for (iv=0;iv<jv;iv++)
#         if (v[iv].draw) {
#             ok=0;
#             break;
#         }
#
#     return ok;
# }
#
# # ----- vc_select:---
def vc_select() -> int:
    """ set flags for v selection from -V option """
    if not args.vcselstr:
        return 0

    for voice in voices:
        voice.select = False

    a = args.vcselstr.split(',')
    a = set(a)
    if not a:
        return 0
    for s in a:
        if s == '-':
            n1, n2 = s.split('-')
            for n in range(n1, n2+1):
                a.add(n)
    for i in a:
        voices[i].select = True

    if verbose >= 4:
        log.info(f"Selection <{args.vcselstr}> selected voices:")
        for i, voice in enumerate(voices):
            if voice.select:
                log.info(f" {i} {voices[i].name}")
    return len(a)


# # ----- voice_label: label v, or just return length if job==0 --
# float voice_label (FILE *fp, char *label, float h, float xc, float dx0, int job)
# {
#     float w,wid,dy,xcc;
#     char lab[81];
#     string t;
#     int n,i;
#     char *p,*q,*l[10];
#
#     if (strlen(label)==0) return 0.0;
#
#     strcpy(lab,label);
#     n=0;
#     p=lab;
#     l[0]=p;
#     while ((q=strstr(p,"\\\\"))) { *q='\0'; p=q+2; n++; l[n]=p; }
#     n++;
#
#     wid=0;
#     for (i=0;i<n;i++) {
#         tex_str(l[i],&t,&w);
#         w=cfmt.voicefont.size*w;
#         if (w>wid) wid=w;
#         if (job!=0) {
#             xcc=xc;
#             if (xcc+0.5*w>dx0) xcc=dx0-0.5*w;
#             dy = 8.0 + 0.5*cfmt.voicefont.size*(n-1-2*i) + h;
#             PUT3 (" %.2f %.2f M (%s) cshow\n",xcc,dy,t.c_str());
#         }
#     }
#     return wid;
# }
#
#
#
# # ----- mstave_deco: draw decorations over multiple staves -----
# # parameter: htab[]        sum of previous v heights
#  *                        botheight height of last v
#
# void mstave_deco (FILE *fp, int ip1, int ip2, float wid0, float hsys, float *htab, float botheight)
# {
#     int     iv,jv,nv,topv,botv;
#     float hbot,htop,ht,x0,y0,wid,wc,wcb,w,wmin;
#     float wmin1=15.0, wmin2=10.0;    # space to staff
#     int* brvoices; #voices with brackets on them
#
#     brvoices = (int*)alloca(nvoice*sizeof(int));
#     for (iv=0;iv<nvoice;iv++) brvoices[iv]=0;
#
#     topv=botv=0;
#     wmin=wmin2;
#     if (do_indent) wmin=wmin1;
#
#     # draw bar lines
#     if (mvoice>1) {
#         for (iv=0;iv<nvoice;iv++) {
#             hbot=10000; htop=-hbot; nv=1;
#             for (jv=iv;jv<iv+v[iv].staves;jv++) {
#                 if (v[jv].draw) nv++;
#                 if (v[jv].draw && (htab[jv]<hbot)) hbot=htab[jv];
#                 if (v[jv].draw && (htab[jv]>htop)) htop=htab[jv];
#             }
#             if ((hbot<htop-0.001) && (nv>1))
#                 draw_sysbars (fp,ip1,ip2,wid0,hsys-htop,htop-hbot+botheight);
#         }
#         PUT1 ("gsave 1.0 %.4f scale 0.0 bar grestore\n", (hsys+botheight)/24.0);
#     }
#
#     # next part draws v names (except on braces)
#     set_font (fp, cfmt.voicefont, 0);
#     nv=0;
#     for (iv=0;iv<nvoice;iv++) if (v[iv].draw) nv++;
#
#     # get max label width, then center labels above each other
#     wid=w=0;
#     for (iv=0;iv<nvoice;iv++) {
#         if (v[iv].draw) {
#             if (do_indent)
#                 w=voice_label (fp, v[iv].name, 0.0,0.0,0.0, 0);
#             else if (nv>1)
#                 w=voice_label (fp, v[iv].sname, 0.0,0.0,0.0, 0);
#             if (w>wid) wid=w;
#         }
#     }
#     wc=wcb=0.5*wid+wmin;
#     if (wcb<18.0) wcb=18.0;         # label on brace needs a bit more room
#
#     for (iv=0;iv<nvoice;iv++) {
#         if (v[iv].draw && (v[iv].brace==0) ) {
#             y0=hsys-htab[iv]+botheight-get_staffheight(iv,ALMOSTBRUTTO);
#             if (is_tab_key(&v[iv].key)) {
#                 #shift label up because tablines are higher than music lines
#                 y0 += 0.5* (get_staffheight(iv,NETTO) - STAFFHEIGHT);
#                 #hsys is reduced by tabflag height of top v!
#                 if ((nvoice>1) && (is_highestvc(iv)))
#                     y0 += get_staffheight(iv,ALMOSTBRUTTO)-get_staffheight(iv,NETTO);
#             }
#             if (do_indent)
#                 voice_label (fp, v[iv].name,y0,-wc,-wmin,1);
#             else if (nv>1)
#                 voice_label (fp,v[iv].sname,y0,-wc,-wmin,1);
#         }
#     }
#
#     # braces and brackets
#     for (iv=0;iv<nvoice;iv++) {
#
#         # brackets
#         htop=10000; hbot=-htop; nv=0;
#         for (jv=iv;jv<iv+v[iv].bracket;jv++) {
#             brvoices[jv]=1;
#             if (v[jv].draw) nv++;
#             if (v[jv].draw && (htab[jv]<htop)) {
#                 htop=htab[jv];
#                 topv=jv;
#             }
#             if (v[jv].draw && (htab[jv]>hbot)) {
#                 hbot=htab[jv];
#                 botv=jv;
#             }
#         }
#         if ((htop<hbot+0.001) && ((nv>1) and (v[iv].bracket==1))) {
#             ht=hbot-htop+get_staffheight(botv,ALMOSTBRUTTO)+6.0;
#             y0=hsys-hbot+botheight-get_staffheight(botv,ALMOSTBRUTTO)-3.0;
#             #subtract tabflag height of top v from bracket height
#             #tabflag height of highest v is not included in hsys
#             if (!is_highestvc(topv))
#                     ht+=get_staffheight(topv,NETTO)-get_staffheight(topv,ALMOSTBRUTTO);
#             PUT2 ("\n %.1f -3 %.1f bracket\n",ht,y0);
# 	}
#
#         # braces
#         htop=10000; hbot=-htop; nv=0;
#         for (jv=iv;jv<iv+v[iv].brace;jv++) {
#             if (v[jv].draw) nv++;
#             if (v[jv].draw && (htab[jv]<htop)) {
#                 htop=htab[jv];
#                 topv=jv;
#             }
#             if (v[jv].draw && (htab[jv]>hbot)) {
#                 hbot=htab[jv];
#                 botv=jv;
#             }
#         }
#         if (htop<hbot+0.001) {
#             ht=hbot-htop+get_staffheight(botv,ALMOSTBRUTTO);
#             #subtract tabflag height of top v from brace height
#             #tabflag height of highest v is not included in hsys
#             if (!is_highestvc(topv))
#                     ht+=get_staffheight(topv,NETTO)-get_staffheight(topv,ALMOSTBRUTTO);
#             y0=hsys-hbot+botheight-get_staffheight(botv,ALMOSTBRUTTO)+0.5*ht;
#             x0=-8;
#             # move to left when also bracket
#             if (brvoices[iv]) {
#                 x0=x0-6;
#                 wcb+=6;
#             }
#             ht=ht-2.0;
#             if (v[iv].brace==1) ht=ht+15.0;
#             if (v[iv].brace>2)    ht=ht-8.0;
#             if ((nv>1) and (v[iv].brace==1))
#                 PUT3 (" %.4f %.1f %.1f brace\n", ht/120.0, x0, y0);
#             if (do_indent)
#                 voice_label (fp, v[iv].name, y0-12.0,-wcb,-wmin,1);
#             else if (nv>1)
#                 voice_label (fp, v[iv].sname,y0-12.0,-wcb,-wmin,1);
#         }
#     }
#
# }
#

infostr = 'filename'   # latest input filename

def output_music(fp):
    """
    output for parsed symbol list

    :param fp:
    :return:
    """
    # ip1 = ip2 = mv = is_top = nsel = b = bnum = 0
    # realwidth = staffwidth = wid0 = widv = lscale = lwidth = bpos = 0.0
    # spa1 = spa2 = hsys = extra = indent = spax = 0.0
    # htap = list()   # size: 40 of 0.0

    # save current meter and key, to continue after P: or T: field
    global voices, cfmt

    for voice in voices:
        voice.meter1 = voice.meter
        voice.key1 = voice.key

    if not common.file_initialized and not common.epsf:
        pssubs.init_ps(fp, infostr)
        pssubs.init_page(fp)

    if len(voices) == 0:
        parse.init_parse_params()
        return
    if common.verbose >= 10:
        print_vsyms ()

    alfa_last = 0.1
    beta_last = 0.0
    lwidth = cfmt.staff_width
    lscale = cfmt.scale
    subs.check_margin(cfmt.left_margin)

    # initialize meter and key for voices
    for voice in voices:
        voice.meter = voice.meter0
        voice.key = voice.key0
        if not voice.meter.do_meter:
            voice.meter.display = 0

    # setup for horizontal positioning, decide which voices to draw
    nsel = vc_select()

    for voice in voices:
        if not voice.select:
            voice.sym = list()

    mvoice = False
    bnum = 0
    ivc0 = -1
    for voice in voices:
        voice.draw = False
        if len(voice.sym) > 0:
            mvoice = True
            voice.draw = True

    if mvoice:
        parse.init_parse_params()
        return

    for voice in voices:
        if voice.draw:
            set_sym_chars(0,len(voice.sym), voice.sym)
            set_beams(0,len(voice.sym), voice.sym)
            if not voice.key.is_tab_key():
                set_stems(0,len(voice.sym),voice.sym)

            b = set_sym_times(0,len(voice.sym), voice.sym, voice.meter0,
                              voice.timeinit)
            set_sym_widths(0, len(voice.nsym), voice.sym, common.ivc)
            if common.ivc == ivc0:
                bnum=b
    barinit = bnum

    if mvoice:
        style.set_style_pars(cfmt.strict1)
    else:
        style.set_style_pars(cfmt.strict2)

    set_poslist ();
    set_xpwid ();
    set_spaces ();

    # loop over pieces to output
    ip1=xp[XP_START].next;
    for (;;) {
        mline++;
        ip1=contract_keysigs (ip1);
        wid0=0;
        for (ivc=0;ivc<nvoice;ivc++) {
            nsym_st[ivc]=set_initsyms (ivc, &widv);
            if (widv>wid0) wid0=widv;
        }
        indent = (do_indent==1) ? cfmt.indent : 0.0;

        ip2=select_piece (ip1);
        ip2=check_overflow (ip1,ip2,lwidth/lscale-wid0-indent);
        if (verbose>5) printf ("output posits %d to %d\n",ip1,ip2-1);
        realwidth=set_glue (ip1,ip2,lwidth/lscale-wid0-indent);
        check_bars1 (ip1,ip2);
        check_bars2 (ip1,ip2);

        spa1=spa2=cfmt.staffsep;
        if (mvoice>1) {
            spa1=cfmt.systemsep;
            spa2=cfmt.sysstaffsep;
        }

        hsys=0;
        mv=0;

        for (ivc=0;ivc<nvoice;ivc++) {
            if (v[ivc].draw) {
		if (!is_tab_key(&v[ivc].key)) {
		    # draw music
		    mv++;
		    nsym=copy_vsyms (ivc,ip1,ip2,wid0);
		    PUT2("\n%% --- ln %d vc %d \n", mline,ivc+1);
		    if (mv==1) bskip(lscale*(0.5*spa1+24.0));
		    else             bskip(lscale*(0.5*spa2+24.0));
		    PUT3("gsave %.3f %.3f scale %.2f setlinewidth\n",
			     lscale, lscale, BASEWIDTH);
		    if (do_indent) PUT1(" %.2f 0 T ",indent);
		    staffwidth=realwidth+wid0;
		    PUT1("%.2f staff\n", staffwidth);
		    htab[ivc]=hsys;
		    spax=spa2+v[ivc].sep;
		    if (v[ivc].sep>1000.0) spax=v[ivc].sep-2000.0;

		    is_top=is_topvc(ivc);
                    draw_symbols (fp,0.5*spa2+spax-spa2,&bpos,is_top);

		    if (mv==mvoice) mstave_deco (fp,ip1,ip2,wid0,hsys,htab,STAFFHEIGHT);

		    PUT0("grestore\n");
		    bskip(-lscale*bpos);
		    hsys=hsys+0.5*spa2+24.0-bpos;
		} else {
		    # draw tablature
		    mv++;
		    nsym=copy_vsyms (ivc,ip1,ip2,wid0);
		    PUT2("\n%% --- ln %d vc %d \n", mline,ivc+1);
                    if (mv==1) bskip(lscale*(0.5*spa1+get_staffheight(ivc,ALMOSTBRUTTO)));
                    else             bskip(lscale*(0.5*spa2+get_staffheight(ivc,ALMOSTBRUTTO)));

		    PUT3("gsave %.3f %.3f scale %.2f setlinewidth\n",
			     lscale, lscale, BASEWIDTH);
		    if (do_indent) PUT1(" %.2f 0 T ",indent);
		    staffwidth=realwidth+wid0;
		    htab[ivc]=hsys;
		    spax=spa2+v[ivc].sep;
		    if (v[ivc].sep>1000.0) spax=v[ivc].sep-2000.0;

		    is_top=is_topvc(ivc);
		    draw_tab_symbols (fp,0.5*spa2+spax-spa2,&bpos,is_top);

		    if (mv==mvoice)
                        mstave_deco (fp,ip1,ip2,wid0,hsys,htab,get_staffheight(ivc,ALMOSTBRUTTO));
                    if (v[ivc].key.ktype != GERMANTAB)
                        PUT2("%.2f %d tabN\n", staffwidth, tab_numlines(&v[ivc].key));
		    PUT0("grestore\n");
                    bskip(-lscale*bpos);
                    if (v[ivc].key.ktype == GERMANTAB && tabfmt.germansepline) {
                        # separator line between German tab systems
                        PUT2("%.2f %.2f tab1\n", staffwidth*lscale,
                                 lscale*tabfont.size*0.75);
                    }
                   hsys=hsys+0.5*spa2+get_staffheight(ivc,ALMOSTBRUTTO)-bpos;
                    # do not count flagheight for top voice in system height
                    if (is_highestvc(ivc)) {
                        hsys = hsys -
                            (get_staffheight(ivc,ALMOSTBRUTTO) - get_staffheight(ivc,NETTO));
                    }
		}
	    }
        }

        extra=-bpos-0.5*spa2;
        if (mvoice>1) bskip(lscale*(spa1+bpos-0.5*spa1+extra));
        buffer_eob (fp);

        do_meter=do_indent=0;
        ip1=ip2;
        if (!ip1) break; #last symbol in xp[]
    }


    # set things to continue parsing
    for voice in voices:
        voice.sym = list()
        voice.meter0 = voice.meter = voice.meter1
        voice.key0 = voice.key = voice.key1

    init_parse_params ();

def check_selected(fp, xref_str, pat, sel_all, search_field):
    """
    :param fp:
    :param xref_str:
    :param pat:
    :param sel_all:
    :param search_field:
    """
    if not common.do_this_tune:
        if parse.is_selected(xref_str, len(pat), pat, sel_all, search_field):
            common.do_this_tune = True
            subs.write_tunetop(fp)

