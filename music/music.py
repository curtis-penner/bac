import logging
from collections import deque

logging.basicConfig(filename='symbol.log')
log = logging.getLogger('symbol')
log.setLevel(logging.INFO)


def syntax_error(e, l, n):
    log.critical(str(e) + l + str(n))


def parse(line):
    bar = Bar()
    notes = Note()
    deco = Decorator()
    space = Space()
    m_line = deque(list(line))
    while m_line:
        m_line = space.is_space(m_line)
        m_line = deco.decorator(m_line)
        m_line = bar.parse_for_bar(m_line)
        m_line = notes.parse(m_line)


class Bar(object):
    bar_symbols = '|[]:'
    types = set('|', '||', '|]', '[|', '::', ':|', '|:', ':|:', '|[')

    def __init__(self):
        self.bar_str = None

    def parse_for_bar(self, line):
        while line:
            if line[0] in Bar.bar_symbols:
                self.bar_str += line.popleft()
            else:
                break
        if self.bar_str and self.bar_str in Bar.types:
            logging.info(self.bar_str)

        return line


class Note(object):
    Symbols = 'abcdefgABCDEFG'
    SymbolSymbols =",'=/<>#_"
    SymbolNumbers = '0123456789'

    def __init__(self):
        self.note = None

    def parse(self, line):
        """
        :param line: deque list
        :return:
        """
        if line[0] in Note.Symbols:
            self.note = line.popleft()
            while line:
                if line[0] in Note.SymbolNumbers or line[0] in Note.SymbolSymbols:
                    self.note += line.popleft()
                else:
                    break
            logging.info(self.note)
        return line

    def draw_note(self, x, w, d, fl):
        """
        gchy: gchord y position

        :param float x:
        :param float w:
        :param float d:
        :param bool fl:
        :return float, float: top, ghcy
        """
        slen0 = constants.STEM
        gchy = constants.STAFFHEIGHT + cfmt.gchordspace

        self.draw_gracenotes(x, w, d)  # draw grace notes

        if cfmt.historicstyle:
            historic = 'h'
        else:
            historic = ''

        c = 'd'
        cc = 'u'
        if self.stem == 1:
            c = 'u'
            cc = 'd'
        stem_len = self.stem * (self.ys - self.y)

        # for (m=0;m<s->npitch;m++)
        for m in range(self.npitch):
            if m > 0:
                put(" ")
            # this needs to be looked at
            self._draw_basic_note(x, w, d, m)  # draw note heads
            xx = 3 * (self.pits[m] - 18) + self.yadd - self.y
            xx = xx * xx
            if not cfmt.nostems:  # stems can be suppressed
                if xx < 0.01:  # add stem
                    if self.stem:
                        put(f' {stem_len:.1f} s{c}{historic}')
                    if fl and self.flags > 0:  # add flags
                        put(f' {stem_len:.1f} f{self.flags}{c}{historic}')

                if m > 0 and self.pits[m] == self.pits[m - 1]:  # unions
                    if self.stem:
                        put(f' {slen0:.2f} s{cc}{historic}')
                    if self.flags > 0:
                        put(f' {slen0:.1f} f{self.flags}{cc}{historic}')

        top, top2 = self.draw_decorations(x)  # add decorations

        y = self.ymn  # lower ledger lines
        if y <= -6:
            for i in range(-6, y, -6):
                put(f' {i} hl')
            if self.len >= constants.BREVIS:
                put("2")
            elif self.head == constants.H_OVAL:
                put("1")

        y = self.ymx  # upper ledger lines
        if y >= 30:
            for i in range(30, y, 6):
                put(f" {i} hl")
            if self.len >= constants.BREVIS:
                put("2")
            elif self.head == constants.H_OVAL:
                put("1")

        if not self.gchords:  # position guitar chord
            yc = gchy
            if yc < y + 8:
                yc = y + 8
            if yc < self.ys + 4:
                yc = self.ys + 4
            if yc < top2:
                yc = top2
            gchy = yc
        put("\n")
        return top, gchy


class Decorator(object):
    def __init__(self):
        self.deco = None

    def decorator(self, line):
        while line:
            if line[0] == '~':
                self.deco += line.popleft()
                log.info('Decorator: ' + self.deco)
            else:
                break
        return line


class Space(object):
    def __init__(self):
        self.space = False

    def is_space(self, d_list):
        while d_list:
            if d_list[0].isspace():
                self.space = d_list.popleft()
            else:
                break
        return d_list



if __name__ == '__main__':
    m = '|:A2 AG ABc|~E2 DA DEG|A2 ~A2 Bcd|~e2 BA B'
    parse(m)