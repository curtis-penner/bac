# Copyright (c) 2019. Curtis Penner

"""
Grace notes can be written by enclosing them in curly braces ({}).

 The first two examples show the meaning of grace notes according to the abc
 standard, which specifies that grace notes have no explicit time values and
 the following meaning:

    - A single grace note is an accacciatura (see the second example above).
    In abctab2ps, the stroke through the flag can optionally be suppressed
    with the format parameter %%nogracestroke.

    - Multiple grace notes are drawn as beamed sixteenth notes.

This does not allow for the notation of long appoggiaturas. To overcome
this limitation, abctab2ps allows for a length specifier in the grace
notes (see the third example above). The length applies to all grace
notes within the same pair of braces; when more than one length is specified,
the last length holds (see the last example above).

When the following note is a chord, appogiaturas and accacciaturas are tied
to the first note given in the chord.
"""

import utils.log
from utils.util import put
import constants
from music.symbol import Symbol, is_note
from fields.key import Key
import format

cfmt = format.Format()

log = utils.log.log
key = Key()
voices = list()


class Grace(Symbol):
    max_grace = 30  # maximum number of grace notes
    d_grace = 1  # codes for decoration

    def __init__(self):  # describes grace notes
        """
        n is the number of grace notes by counting the pitches.
        That is being dropped.
        """
        super().__init__()
        self.pgr = list()  # pitches
        self.agr = list()  # accidentals
        self.lgr = 0   # note length.
        # When zero (default), treated as accacciatura

    def parse_grace_sequence(self, line):
        """
        result is stored in arguments when no grace sequence => arguments
        are not altered

        :param str line:
        return str: line (altered or not)
        """
        if not line.startswith('{'):
            return line   # not grace, return line

        self.lgr = 0  # default is no length => accacciatura
        n = line[1:].find('}')

        if n < 0:
            log.critical(f'Unbalanced grace note sequence: {line}')
            exit(-1)
        # todo: put in a error for more then 30 in length

        gs = line[1:n]
        p = 0
        while p < len(gs) or p <= Grace.max_grace:
            if not is_note(gs[p]):
                log.error(f'Unexpected symbol {gs[p]} in grace note sequence ')
                p += 1

            self.agr[n] = 0
            if gs[p] == '=':
                self.agr[n] = constants.A_NT
            if gs[p] == '^':
                if gs[p + 1] == '^':
                    self.agr[n] = constants.A_DS
                    p += 1
                else:
                    self.agr[n] = constants.A_SH

            if gs[p] == '_':
                if gs[p + 1] == '_':
                    self.agr[n] = constants.A_DF
                    p += 1
                else:
                    self.agr[n] = constants.A_FT

            if self.agr[n]:
                p += 1

            self.pgr[n] = key.numeric_pitch(gs[p])
            p += 1
            while gs[p] == '\'':
                self.pgr[n] += 7
                p += 1
            while gs[p] == ',':
                self.pgr[n] -= 7
                p += 1

            self.pgr[n], self.agr[n] = key.do_transpose(voices[ivc].key.)

            # parse_length() returns default length when no length specified
            # => we may only call it when explicit length specified
            if gs[p] == '/' or gs[p].isdigit():
                self.lgr = parse.parse_length()
        return line[n + 1:]

    def draw_gracenotes(self, x, w, d):
        """
        This is called only by draw_note.

        :param float x:
        :param float w:
        :param float d:
        """
        n = len(self.agr)
        if not n:
            return
        gr_len = self.gr.note_len

        fac_x = 0.3
        fac = d / w - 1
        if fac < 0:
            fac = 0
        fac = 1 + (fac * fac_x) / (fac + fac_x)

        ii = 0
        a = 0
        b = 35
        dx = 0
        for m in range(self.npitch):  # room for accidentals
            dd = -self.shhd[m]
            if self.accs[m]:
                dd = -self.shhd[m] + self.shac[m]
            if self.accs[m] == constants.A_FT or self.accs[m] == constants.A_NT:
                dd = dd - 2
            if dx < dd:
                dx = dd

        xx = x - fac * (dx + constants.GSPACE0)
        xg = list()
        yg = [3 * (i - 18) + self.yadd for i in self.gr.p]
        if yg[:-1] >= self.ymx:
            xx += 1
        if yg[:-1] < self.ymn and n == 1:
            xx -= 2
        for i in range(n - 1):
            if yg[i] > yg[i + 1] + 8:
                xx += fac * 1.8
            xg.append(xx)
            xx -= fac * constants.GSPACE
            if self.agr[i]:
                xx -= 3.5

        if n > 1:
            # linear fit through stems
            px = [i + constants.GSTEM_XOFF for i in xg]
            py = [i + constants.GSTEM for i in yg]
            s1 = n
            sx = sum(px)
            sy = sum(py)
            sxx = sum([i * i for i in px])
            sxy = sum([a * b for a, b in zip(px, py)])

            delta = s1 * sxx - sx * sx  # beam fct: y = ax+b
            a = (s1 * sxy - sx * sy) / delta
            if a > constants.BEAM_SLOPE:
                a = constants.BEAM_SLOPE
            if a < -constants.BEAM_SLOPE:
                a = -constants.BEAM_SLOPE
            b = (sy - a * sx) / s1

            if key.bagpipe:
                a = 0
                b = 35

            lmin = 100  # shift to get min stems
            px = [i + constants.GSTEM_XOFF for i in xg]
            py = [a * i + b for i in px]
            for a, b in zip(py, yg):
                if a - b < lmin:
                    lmin = a - b
            if lmin < 10:
                b += 10 - lmin

        for i in range(n):  # draw grace notes
            if n > 1 and not gr_len or gr_len < constants.HALF:
                px = xg[i] + constants.GSTEM_XOFF
                py = a * px + b
                lg = py - yg[i]
                put(f"%{xg[i]:.1f} %{yg[i]:.1f} %{lg:.1f} gnt ")
            else:
                lg = constants.GSTEM
                if gr_len > constants.EIGHTH:
                    lg += 1
                if not gr_len and cfmt.nogracestroke:
                    put(f"{xg[i]:.1f} {yg[i]:.1f} {lg:.1f} gn8 ")
                elif not gr_len:
                    put(f"{xg[i]:.1f} {yg[i]:.1f} {lg:.1f} gn8s ")
                elif gr_len > constants.HALF:
                    put(f"{xg[i]:.1f} {yg[i]:.1f} gn1 ")
                elif gr_len == constants.HALF:
                    put(f"{xg[i]:.1f} {yg[i]:.1f} {lg:.1f} gn2 ")
                elif gr_len == constants.QUARTER:
                    put(f"{xg[i]:.1f} {yg[i]:.1f} {lg:.1f} gnt ")
                elif gr_len == constants.EIGHTH:
                    put(f"{xg[i]:.1f} {yg[i]:.1f} {lg:.1f} gn8 ")
                else:  # gr_len < EIGHTH
                    put(f"{xg[i]:.1f} {yg[i]:.1f} {lg:.1f} gn16 ")

            acc = self.agr[i]
            if acc == constants.A_SH:
                put(f"{xg[i] - 4.5:.1f} {yg[i]:.1f} gsh0 ")
            if acc == constants.A_FT:
                put(f"{xg[i] - 4.5:.1f} {yg[i]:.1f} gft0 ")
            if acc == constants.A_NT:
                put(f"{xg[i] - 4.5:.1f} {yg[i]:.1f} gnt0 ")
            if acc == constants.A_DS:
                put(f"{xg[i] - 4.5:.1f} {yg[i]:.1f} gds0 ")
            if acc == constants.A_DF:
                put(f"{xg[i] - 4.5:.1f} {yg[i]:.1f} gdf0 ")

            y = int(yg[i])  # ledger lines
            if y <= -6:
                if y % 6:
                    put(f"{xg[i]:.1f} {y + 3} ghl ")
                else:
                    put(f"{xg[i]:.1f} {y} ghl ")
            if y >= 30:
                if y % 6:
                    put(f"{xg[i]:.1f} {y - 3} ghl ")
                else:
                    put(f"{xg[i]:.1f} {y} ghl ")

        if n > 1:  # beam
            if not gr_len and key.bagpipe:
                put(f"{px[0]:.1f} {py[0]:.1f} {px[n - 1]:.1f} {py[n - 1]:.1f} gbm3 ")
            elif not gr_len:
                put(f"{px[0]:.1f} {py[0]:.1f} {px[n - 1]:.1f} {py[n - 1]:.1f} gbm2 ")
            elif gr_len == constants.EIGHTH:
                put(f"{px[0]:.1f} {py[0]:.1f} {px[n - 1]:.1f} {py[n - 1]:.1f} gbm1 ")
            elif gr_len == constants.SIXTEENTH:
                put(f"{px[0]:.1f} {py[0]:.1f} {px[n - 1]:.1f} {py[n - 1]:.1f} gbm2 ")
            elif gr_len < constants.SIXTEENTH:
                put(f"{px[0]:.1f} {py[0]:.1f} {px[n - 1]:.1f} {py[n - 1]:.1f} gbm3 ")

        bet1 = 0.2  # slur
        bet2 = 0.8
        yy = 1000
        for i in range(n - 1, 0, -1):
            if yg[i] <= yy:
                yy = yg[i]
                ii = i
        x0 = xg[ii]
        y0 = yg[ii] - 5
        if i > 0:
            x0 = x0 - 4
            y0 = y0 + 1
        x3 = x - 1
        if self.npitch > 1:
            yslurhead = 3 * (self.grcpit - 18) + self.yadd
        else:
            yslurhead = self.ymn
        y3 = yslurhead - 5
        dy1 = (x3 - x0) * 0.4
        if dy1 > 3:
            dy1 = 3
        dy2 = dy1

        if yg[ii] > yslurhead + 7:
            x0 = xg[ii] - 1
            y0 = yg[ii] - 4.5
            y3 = yslurhead + 1.5
            x3 = x - dx - 5.5
            dy2 = (y0 - y3) * 0.2
            dy1 = (y0 - y3) * 0.8
            bet1 = 0.0

        if y3 > y0 + 4:
            y3 = y0 + 4
            x0 = xg[ii] + 2
            y0 = yg[ii] - 4

        x1 = bet1 * x3 + (1 - bet1) * x0
        y1 = bet1 * y3 + (1 - bet1) * y0 - dy1
        x2 = bet2 * x3 + (1 - bet2) * x0
        y2 = bet2 * y3 + (1 - bet2) * y0 - dy2

        put(f" {x1:.1f} {y1:.1f} {x2:.1f} {y2:.1f}")
        put(f" {x3:.1f} {y3:.1f} {x0:.1f} {y0:.1f} gsl\n")

