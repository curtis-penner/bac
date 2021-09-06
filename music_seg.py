import tab
from constants import  (H_OVAL, H_EMPTY, NOTE, REST, BREST, WHOLE, HALF,
                        STEM, STEM_CH)
from format import Format

istab = False
bagpipe = False

cfmt = Format()


class Symbol:
    def __init__(self):
        self.type = None
        self.shhd = [0] * 8
        self.shac = [0] * 8
        self.pits = [0] * 8
        self.lens = [0] * 8
        self.accs = [0] * 8
        self.sl1 = [0] * 8
        self.sl2 = [0] * 8
        self.ti1 = [0] * 8
        self.ti2 = [0] * 8
        self.npitch = len(self.pits)
        self.len = 0
        self.stem = 0
        self.head = False
        self.xmn = 0
        self.xmx = 0
        self.yadd = 0
        self.ymn = 0
        self.ymx = 0
        self.yav = 0
        self.ylo = 0
        self.yhi = 0
        self.x = 0
        self.y = 0
        self.flags = 0
        self.word_st = False
        self.word_end = False


def set_head_directions(s: Symbol):
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


def set_stems(n1: int, n2: int, symb: list):
    # int beam, j, k, n, stem, laststem
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
            if bagpipe:
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
            if istab:
                num_flags = tab.tab_flagnumber(symb[i].lens)
            else:
                num_flags = symb[i].flags
            # take care of wish to supress beams or stems in music
            if num_flags <= 0 or (not istab and (cfmt.nobeams or cfmt.nostems)):
                if last_note >= 0:
                    symb[last_note].word_end = 1
                symb[i].word_st = True
                symb[i].word_end = True
                start_flag = True
            last_note = i


def main():
    symbols = list()
    for i in range(4):
        symbols.append(Symbol())
    set_head_directions(symbols[1])
    set_sym_chars(0, len(symbols), symbols)


if __name__ == '__main__':
    main()
