
import os
import re

import constants
import music
import parse
import pssubs
from log import log
import symbol
import format
import util
from format import cfmt, font
import common
from common import voices
import cmdline
from parse import add_wd, parse_uint

args = cmdline.options()


def is_field(s: str) -> bool:
    """ Validate a field type """
    return len(s) > 2 and s[1] == ':' and s[0] in 'ABCDEFGHKLMNOPQRSTVWwXZ'


def parse_vocals(line):
    if Voice().parse_vocals(line):
        return

    # now parse a real line of music
    if not common.voices:
        common.voices.append(Voice().switch_voice(constants.DEFVOICE))


def parse_voice(line):
    ok = True
    v_spec = list()
    spec = ''
    p = line.split(' ')
    print(line)
    label = p[0]
    del p[0]
    for i in p:
        if not i:
            continue
        if '"' not in i and ok:
            v_spec.append(i)
            continue
        if '"' in i and ok:
            ok = False
            spec = i
        elif '"' not in i and not ok:
            spec = ' '.join([spec, i])
        elif '"' in i and not ok:
            ok = True
            spec = ' '.join([spec, i])
            v_spec.append(spec)
    return label, v_spec


def parse_vocals(line: str) -> bool:
    """
    parse words below a line of music
    Use '^' to mark a '-' between syllables - hope nobody needs '^' !
    """
    word = ''
    if not line.startswith('w:'):
        return False

    # increase vocal line counter in first symbol of current line
    voices[ivc].syms[common.nsym0].wlines += 1
    isym = common.nsym0 - 1
    p = line[2:].strip()
    c = 0
    while c < len(p):
        if p[c] == '_' or p[c] == '*' or p[c] == '|' or p[c] == '-':
            word += p[c]
            if p[c] == '-':
                word += '^'
            word += '\0'
            c += 1
        else:
            while p[c] != ' ' and p[c] != '\0':
                if p[c] == '_' or p[c] == '*' or p[c] == '|':
                    break
                if p[c] == '-':
                    if p[c - 1] != '\\':
                        break
                    del word[:-1]
                    word += '-'
                word += p[c]
                c += 1
            if p[c] == '-':
                word += '^'
                c += 1
            word += '\0'

        # now word contains a word, possibly with trailing '^',
        # or one of the special characters * | _ -

        if '|' in word:  # skip forward to next bar
            isym += 1
            while voices[ivc].syms[isym].type != constants.BAR and \
                    isym < voices[ivc].nsym:
                isym += 1
            if isym >= len(voices[ivc].syms):
                raise SyntaxError("Not enough bar lines for |", line)
        else:  # store word in next note
            w = 0
            while word[w] != '\0':  # replace * and ~ by space
                # cd: escaping with backslash possible
                # (does however not yet work for '*')
                word = word.replace('*', ' ')
                word = word.replace('~', ' ')
                word = word.replace('\\', ' ')
                w += 1
            isym += 1
            while voices[ivc].sym[isym].type != constants.NOTE and \
                    isym < voices[ivc].nsym:
                isym += 1
            if isym >= len(voices[ivc].nsym):
                SyntaxError("Not enough notes for words", line)
            voices[ivc].sym[isym].wordp[common.nwline] = add_wd(word)

        if p[c] == '\0':
            break

    common.nwline += 1
    return True


def write_text_block(fp, job: int, words_of_text='') -> None:
    if not words_of_text:
        return

    baseskip = cfmt.textfont.size * cfmt.lineskipfac
    parskip = cfmt.textfont.size * cfmt.parskipfac
    cfmt.textfont.set_font_str(common.page_init)

    swfac = music.set_swfac(cfmt.textfont.name)

    # Now this is stupid. All that work to just set it to 1.0

    spw = util.cwid(' ')
    fp.write("/LF \\{0 "
             f"{-baseskip:.1f}"
             " rmoveto} bind def\n")

    # output by pieces, separate at newline token
    ntxt = len(words_of_text)
    i1: int = 0
    while i1 < ntxt:
        i2 = -1
        for i in range(i1, ntxt):
            if words_of_text[i] == '$$NL$$':
                i2 = i
                break
        if i2 == -1:
            i2 = ntxt
        common.bskip(fp, baseskip)

        if job == constants.OBEYLINES:
            fp.write("0 0 M(")
            for i in range(i1, i2):
                line, w_width = music.tex_str(words_of_text[i])
                fp.write(f"{line} ")
            fp.write(") rshow\n")

        elif job == constants.OBEYCENTER:
            fp.write(f"{cfmt.staff_width / 2:.1f} 0 M(")
            for i in range(i1, i2):
                line, w_width = music.tex_str(words_of_text[i])
                fp.write(f"{line}")
                if i < i2-1:
                    fp.write(" ")
            fp.write(") cshow\n")

        elif job == constants.OBEYRIGHT:
            fp.write(f"{cfmt.staff_width:.1f} 0 M(")
            for i in range(i1, i2):
                line, w_width = music.tex_str(words_of_text[i])
                fp.write(f"{line}")
                if i < i2-1:
                    fp.write(" ")
            fp.write(") lshow\n")

        else:
            fp.write("0 0 M mark\n")
            nc = 0
            mc = -1
            wtot = -spw
            text_width = cfmt.textfont.size
            for i in range(i2-1, i1, -1):
                line, w_width = music.tex_str(words_of_text[i])
                mc += len(words_of_text)
                wtot += w_width+spw
                nc += len(line)+2
                if nc >= 72:
                    fp.write("\n")
                fp.write(f"({line})")
                if job == constants.RAGGED:
                    fp.write(" %.1f P1\n", cfmt.staff_width)
                else:
                    fp.write(" %.1f P2\n", cfmt.staff_width)
                    # first estimate:(total textwidth)/(available width)
                    text_width = wtot*swfac*cfmt.textfont.size
            if "Courier" in cfmt.textfont.name:
                text_width = 0.60 * mc * cfmt.textfont.size
            ftline0 = text_width / cfmt.staff_width
            # revised estimate: assume some chars lost at each line end
            nbreak = int(ftline0)
            text_width = text_width + 5 * nbreak * util.cwid('a') * swfac * cfmt.textfont.size
            ftline = text_width/cfmt.staff_width
            ntline = int(ftline + 1.0)
            log.info(f"first estimate {ftline0:.2f}, revised {ftline:.2f}")
            log.info(f"Output {i2-i1} words, about {ftline:.2f} lines(fac {swfac:.2f})")
            common.bskip(fp, (ntline-1)*baseskip)

        # buffer.buffer_eob(fp)
        # next line to allow pagebreak after each text "line"
        # if(!epsf && !within_tune) write_buffer(fp);
        i1 = i2+1
    common.bskip(fp, parskip)
    # buffer.buffer_eob(fp)
    # next line to allow pagebreak after each paragraph
    if not common.epsf and not common.within_tune:
        pass
        # buffer.write_buffer(fp)
    common.page_init = ""


def add_to_text_block(ln, add_final_nl):
    """
    Used only in: subs.put_text

    :param str ln:
    :param bool add_final_nl:
    :return ln, words_of_text:
    """
    word = list()
    words_of_text = list()
    c = 0
    nl = 0

    while c < len(ln):
        while ln[c] == ' ':
            c += 1
        if c >= len(ln):
            break
        while ln[c] != ' ' and c >= len(ln) and ln[c] != '\n':
            nl = 0
            if ln[c] == '\\' and ln[c + 1] == '\\':
                nl = 1
                c += 2
                break
            word.append(ln[c])
            c += 1
        if word:
            words_of_text.append(word)
            word = list()
        if nl:
            words_of_text.append("$$NL$$")
            word = list()
    if add_final_nl:
        words_of_text.append("$$NL$$")


class Comment:
    pass


class EOF:
    pass


class Music:
    pass


class ToBeContinued:
    pass


class Info:
    pass


class Blank:
    pass


class Composers:
    def __init__(self):
        self.size = 5
        self.composers = list()

    def __call__(self, value):
        if len(self.composers) <= self.size:
            self.composers.append(value)
        else:
            log.warning("Too many composer lines")

    def __len__(self):
        return len(self.composers)


class Titles:
    def __init__(self):
        self.size = 3
        self.titles = list()

    def __call__(self, value):
        if len(self.titles) <= self.size:
            self.titles.append(value)

    def __len__(self):
        return len(self.titles)

    def write_inside_title(self, fp):
        log.debug(f"write inside title <{self.titles[0]}>")
        if not self.titles:
            return

        common.bskip(fp, cfmt.subtitlefont.size + 0.2 * constants.CM)
        cfmt.subtitlefont.set_font(fp, False)

        if cfmt.titlecaps:
            t = self.titles[0].upper()
        else:
            t = self.titles[0]
        fp.write(f"({t.strip()}")

        if cfmt.titleleft:
            fp.write(") 0 0 M rshow\n")
        else:
            fp.write(f") {cfmt.staffwidth / 2:.1f} 0 M cshow\n")
        common.bskip(fp, cfmt.musicspace + 0.2 * constants.CM)


class Single:
    def __init__(self, appendable=False):
        self.appendable = appendable
        self.line = ''

    def __call__(self, line):
        if self.appendable:
            self.line = ' '.join([self.line, line])
        else:
            self.line = line


class XRef:
    """
    This can be turned into a simple parse in Info
    """
    def __init__(self):
        self.xref = 0
        self.xref_str = None

    def __call__(self, s):
        value = s.strip()
        if value.isdigit() and int(value):
            self.xref = int(value)
            self.xref_str = value
            common.within_block = True
            common.within_tune = True
            common.do_this_tune = True
        else:
            self.xref = 0
            self.xref_str = ''
            common.within_block = False
            common.within_tune = False
            common.do_this_tune = False

    def get_xref(self, line: str) -> int:
        """ get xref from string """
        if not line:
            log.error("xref string is empty")
            return 0

        if not line.isdigit():
            log.error(f"xref string has invalid symbols: {line}")
            return 0
        self.xref = int(line)


class Parts:
    def __init__(self):
        self.parts = ''

    def __call__(self, line, header):
        print(line, header)

    def write_parts(self, fp) -> None:
        if self.parts:
            common.bskip(fp, cfmt.partsfont.size)
            cfmt.partsfont.set_font(fp, False)
            fp.write("0 0 M(")
            fp.write(self.parts)
            fp.write(") rshow\n")
            common.bskip(fp, cfmt.partsspace)


class Words:
    def __init__(self, appendable=False):
        self.appendable = appendable
        self.line = ''
        self.text_type: list[int] = list()

    def __call__(self, line):
        if self.appendable:
            self.line = ' '.join([self.line, line])
        else:
            self.line = line

    @staticmethod
    def put_words(fp):
        cfmt.wordsfont.set_font(fp, False)
        cfmt.wordsfont.set_font_str(common.page_init)

        n = 0
        for i in range(common.ntext):
            if common.text_type[i] == constants.TEXT_W:
                n += 1
        if not n:
            return

        common.bskip(fp, cfmt.wordsspace)
        for i in range(common.ntext):
            if common.text_type == constants.TEXT_W:
                common.bskip(fp, cfmt.lineskipfac*cfmt.wordsfont.size)
                ct = common.text[i]
                p = 0
                s: str = ''   # what is str
                if common.text[i][0].isdigit():
                    while ct[p] != '\0':
                        s += ct[p]
                        if ct[p] == ' ':
                            break
                        if ct[p-1] == ':':
                            break
                        if ct[p-1] == '.':
                            break
                    if ct[p] == ' ':
                        p += 1

                # permit page break at empty lines or stanza start
                nw = util.nwords(common.text[i])
                if not nw or s:
                    pass
                    # buffer.buffer_eob(fp)

                if nw:
                    if s:
                        fp.write("45 0 M(")
                        fp.write(s)
                        fp.write(") lshow\n")

                    if ct[p]:
                        fp.write("50 0 M(")
                        fp.write(ct[p])
                        fp.write(") rshow\n")

        # buffer.buffer_eob(fp)
        common.page_init = ""

    def add_text(self, s: str, i_type: int) -> None:
        if not common.do_output:
            return
        if len(self.text_type) >= constants.NTEXT:
            log.error(f"No more room for text line < {s}")
            return
        common.text[common.ntext] = s
        self.text_type.append(i_type)
        common.ntext += 1


class Lyrics:
    def __init__(self):
        self.parts = ''

    def __call__(self, line):
        self.parts = line


class LayoutParams:
    def __init__(self):
        pass

    def __call__(self, line, header):
        print(line)


class Meter:
    """ data to specify the meter """

    Body = True
    Header = True

    def __init__(self):
        self.meter1: int = 4   # numerator,
        self.meter2: int = 4   # denominator
        self.mflag: int = 1   # mflag: 1=C, 2=C|, 3=numerator only, otherwise 0
        self.top = ''
        self.meter_top = ''
        self.meter_display: dict = dict()
        self.display = 1   # 0 for M:none, 1 for real meter, 2 for differing display

        self.dlen: int = constants.EIGHTH
        self.meter_str: str = ''
        self.do_meter: bool = True
        self.display_top: str = ''
        self.display_meter1: int = 0
        self.display_meter2: int = 0
        self.display_mflag: int = 0

    def __call__(self, meter_str, header=False):
        self.meter_str = meter_str.strip()
        if not meter_str:
            log.error("Empty meter string")
            return

        # if no meter, set invisible 4/4 (for default length)
        if meter_str == "none":
            meter_str = "4/4"
            self.display = 0
        else:
            self.display = 1

        # if global display_meter option, add "display=..." string accordingly
        # (this is ugly and not extensible for more keywords, but works for now)
        if not self.meter_display and 'display=' in self.meter_str:
            m = self.meter_str.split('display=', 1)
            self.display_meter = m[1]
            self.set_display_meter(self.display_meter)

        if meter_str == 'C|':
            self.meter1 = 2
            self.meter2 = 4
        elif meter_str == 'C':
            self.meter1 = 4
            self.meter2 = 4
        elif '/' in meter_str:
            meters = meter_str.split('/', 1)
            if meters[0].isdigit():
                self.meter1 = int(meters[0])
            elif '+' in meter_str or ' ' in meter_str:
                self.parse_meter_token()
            else:
                self.meter1 = 4

            if meters[1].isdigit():
                self.meter2 = int(meters[1])
            else:
                log.error(f'meter bottom is not a number: {meters[1]}')
                self.meter2 = 4
        else:
            if meter_str.isdigit():
                self.meter1 = int(meter_str)
                self.meter2 = 4
            else:
                log.critical(f'Failed meter value: {meter_str}')

        self.dlen = constants.BASE
        if 4*self.meter1 < 3*self.meter2:
            self.dlen = constants.SIXTEENTH
        self.mflag = 0
        log.info(f"Dlen    <{self.dlen}> sets default note length to {self.dlen}/"
                 f"/{constants.BASE} = 1"
                 f"/{constants.BASE // self.dlen}")
        
    def set_display_meter(self, display_meter_str):   # def __call__(mtrstr):
        """ interpret display_meter string, store in struct """

        if self.display == 2:
            display = Meter()
            display(display_meter_str)
            self.display_meter1 = display.meter1
            self.display_meter2 = display.meter2
            self.display_mflag = display.mflag
            self.display_top = display.meter_top
            log.info(f"Meter <{display_meter_str}> will display")
            log.info(f'Meter <{display_meter_str}> is {self.display_meter1} '
                     f'over {self.display_meter2} with default '
                     f'length 1/{constants.BASE // self.dlen}')
        elif self.display == 0:
            self.display_meter1 = 0
            self.display_meter2 = 0
            self.display_mflag = 0
            self.display_top = ""
            print(f"Meter <{display_meter_str}> will display as <none>")

    def parse_meter_token(self):
        if '+' in self.meter_top:
            # convert the split string to integer
            m_str = self.meter_top.split('+')
            m = list()
            for i in m_str:
                m.append(int(i))
            self.meter1 = sum(m)
        else:
            m_str = self.meter_top.split(' ')
            m = list()
            for i in m_str:
                m.append(int(i))
            self.meter1 = sum(m)

    def display_meter(self, mtrstr):
        if not mtrstr:
            self.display_meter1 = 4
            self.display_meter2 = 4
            self.mflag = 0
            self.display_top = ''
            log.info(f"Meter will display as {self.display_meter1} over {self.display_meter2}")
        elif mtrstr == 'none':
            self.display = 0
            log.info(f"Meter <{mtrstr}> will display as {self.meter1} over {self.meter2}")

    def append_meter(self, voice):
        """ add meter to list of music
        Warning: only called for inline fields normal meter music are added in set_initsyms
        """

        # must not be ignored because we need meter for counting bars!
        # if self.display == 0) return

        kk = voice.add_sym(constants.TIMESIG)
        voices[ivc].syms.append(symbol.Symbol())
        voices[ivc].syms[kk].gchords = common.GchordList
        voices[ivc].syms[kk].type = constants.TIMESIG
        if self.display == 2:
            voices[ivc].syms[kk].u = self.display_meter1
            voices[ivc].syms[kk].v = self.display_meter2
            voices[ivc].syms[kk].w = self.display_mflag
            voices[ivc].syms[kk].text = self.display_top
        else:
            voices[ivc].syms[kk].u = self.meter1
            voices[ivc].syms[kk].v = self.meter2
            voices[ivc].syms[kk].w = self.mflag
            voices[ivc].syms[kk].text = self.top

        if not self.display:
            voices[ivc].syms[kk].invis = 1

    def set_dlen(self, s: str) -> None:
        """ set default length for parsed notes """
        l1, l2 = s.split('/')
        if l1.isdigit() and l2.isdigit():
            log(f"{l1}/{l2}")
        else:
            log(f'{s} is not valid')

        d = constants.BASE//l2
        if d*l2 != constants.BASE:
            log.critical(f"Length incompatible with BASE, using 1/8: {s}")
            dlen = constants.BASE//8
        else:
            dlen = d*l1

        log.info(f"Dlen    <{s}> sets default note length to {dlen}//{constants.BASE} = 1"
                 f"/{constants.BASE//dlen}")

        self.dlen = dlen


class DefaultLength(Meter):
    Body = True

    def __init__(self):
        super().__init__()
        self.default_length = constants.EIGHTH

    def __call__(self, length, header=True):
        if '/' in length:
            top, bottom = length.split('/')
            if not top.isdigit() and not bottom.isdigit():
                log.error(f'+++Error: Default Length {length}')
                exit(3)
            self.default_length = constants.BASE * int(top) // int(bottom)
        else:
            self.default_length = constants.EIGHTH


class Key:
    """
    Every option in the K: field may be omitted, but the order must not be
    rearranged. The meaning of the individual options is:

    key and mode:
    The key signature should be specified with a capital letter (major mode) which
    may be followed by a "#" or "b" for sharp or flat respectively. The mode
    determines the accidentals and can follow immediately after the key letter
    or with white spaces separated; possible mode names are maj(or) (this is
    the default), min(or), m(inor), ion(ian), mix(olydian), dor(ian),
    phr(ygian), lyd(ian), loc(rian), aeo(lian). Mode names are not case-sensitive.
    When key and mode are omitted C major is assumed.

    global accidentals:
    Global accidentals are accidentals that always override key specific
    accidentals. For example, "K:D =c" would write the key signature as two
    sharps (key of D) but then mark every c as natural (which is conceptually
    the same as D mixolydian). Note that there can be several global accidentals,
    separated by spaces and each specified with an accidental, __, _, =, ^,
    or ^ ^ ; followed by a letter in lower case. Global accidentals are overridden
    by accidentals attached to notes within the body of the abc tune and are
    reset by each change of signature.

    clef and octave:
    The clef specification must be the last word in the key field. Optionally
    it may start with a "clef=" prefix.  Classical Western music notation has
    only three clef signs (G, F and C) which can appear on different music
    lines. abctab2ps supports the following clef names: treble (G on line 2;
    this is the default), treble8 (like treble, but with an "8" printed below),
    treble8up (like treble, but with an "8" printed above), frenchviolin (G on
    line 1), bass (F on line 4), varbaritone (F on line 3), subbass (F on line 5),
    alto (C on line 3), tenor (C on line 4), baritone (C on line 5), soprano
    (C on line 1), mezzo-soprano (C on line 2). Optionally the clef may contain
    an appended octave modifier (eg. "treble-8"), which changes the pitch
    interpretation.
    """
    A_SH = 1  # codes for accidentals
    A_NT = 2
    A_FT = 3
    A_DS = 4
    A_DF = 5

    bagpipe = False

    treble = 1,
    treble8 = 2,
    bass = 3,
    alto = 4,
    tenor = 5,
    soprono = 6,
    mezzosoprono = 7,
    baritone = 8,
    varbaritone = 9,
    subbass = 10,
    frenchviolin = 11,
    treble8up = 12

    # note=(root, sf)
    notes = dict(A=(0, 3),
                 B=(1, 5),
                 C=(2, 0),
                 D=(3, 2),
                 E=(4, 4),
                 F=(5, -1),
                 G=(6, 1))

    modes = {'maj': 0, 'min': -3, 'ion': 0, 'mix': 3, 'dor': 3,
             'phr': 3, 'lyd': 1, 'loc': -5, 'aeo': 3}

    # types of clefs
    clef_type = dict(treble=1,
                     treble8=2,
                     bass=3,
                     alto=4,
                     tenor=5,
                     soprono=6,
                     mezzosoprono=7,
                     baritone=8,
                     varbaritone=9,
                     subbass=10,
                     frenchviolin=11,
                     treble8up=12)

    def __init__(self):
        self.name = ''
        self.k_type = None
        self.sf = 2
        self.root = 0
        self.root_acc = Key.A_NT
        self.add_pitch = 0
        self.key_type = Key.treble
        self.add_accs = list()
        self.add_transp = 0

    def adjust_with_mode(self, key_mode):
        for mode, shift in Key.modes.items():
            if key_mode[2:].lower().startswith(mode):
                self.sf += shift
        else:
            if key_mode[2:].lower().startswith('m'):
                self.sf -= 3

    def __call__(self, line: str, header: bool = True) -> bool:
        """ Parse the value for key / clef """
        self.name = line
        parts = line.split()

        if not parts:
            self.sf = 2
            self.root = 0
            self.root_acc = Key.A_NT
            return True

        for key_mode in parts:
            if key_mode[0] in 'ABCDEFG':
                c = 0
                self.root, self.sf = Key.notes.get(key_mode[c], (2, 0))
                c += 1

                if len(key_mode) > 1:
                    if key_mode[c] in '#b':
                        if key_mode[1] == '#':
                            self.root_acc = Key.A_SH
                        elif key_mode[1] == 'b':
                            self.root_acc = Key.A_FT
                        c += 1

                if len(key_mode) > 2:
                    self.adjust_with_mode(key_mode[2:])

            if key_mode[0] in '_=^':
                self.global_accidentals(key_mode)

            if len(parts) > 1 and (key_mode.startswith('clef=') or
                                   key_mode == parts[-1]):
                self.set_clef(key_mode)
        return True

    def global_accidentals(self, km):
        c = 0
        while c < len(km):
            if km[c] == '_':
                if self.root_acc == Key.A_FT:
                    self.root_acc = Key.A_DF
                c += 1
            elif km[c] == '=':
                self.root_acc = Key.A_NT
                c += 1
            elif km[c] == '^':
                if self.root_acc == Key.A_SH:
                    self.root_acc = Key.A_DS
                c += 1
            elif km[c] in 'abcdefg':
                pass

    def set_clef(self, clef):
        if clef.startswith('clef='):
            clef = clef[5:]
        self.key_type = Key.clef_type.get(clef.lower(), Key.clef_type['treble'])

        # if '-' in clef:
        #     ptr = clef.find('-')
        # if '+' in clef:
        #     ptr = clef.find('+')

        for c in Key.clef_type.keys():
            if clef.startswith(c):
                if clef.endswith('+8'):
                    self.add_pitch = +7
                elif clef.endswith('-8'):
                    self.add_pitch = -7
                elif clef.endswith('+0') or clef.endswith('-0'):
                    self.add_pitch = 0
                elif clef.endswith('+16'):
                    self.add_pitch = +14
                elif clef.endswith('-16'):
                    self.add_pitch = -14
                else:
                    log.warning(f'unknown octave modifier in clef: {clef}')
                return True

        if self.parse_tab_key(clef):
            return True   # Todo
        return False

    def get_halftones(self, t):
        """
        figure out how by many halftones to transpose
        In the transposing routines: pitches A ... G are coded as with 0..7

        :param str t:
        :return int:
        """
        pit_tab = [0, 2, 3, 5, 7, 8, 10]

        if not t:
            return 0

        root_new = self.root
        root_old = self.root
        racc_old = self.root_acc
        direction = 0
        pit_old = 0
        racc_new = 0

        c = 0
        while c < len(t):
            if t[c] == '^':
                direction = 1
                c += 1
            elif t[c] == '_':
                direction = -1

            stype = 1
            root_new = self.root
            if t[c].upper() in 'ABCDEFG':
                root_new = 'ABCDEFG'.find(str(t[c].upper))
                c += 1
                stype = 2

            # first case: offset was given directly as numeric argument
            if stype == 1 and t[c:].isdigit():
                nht = int(t[c:])
                if direction < 0:
                    nht = -nht
                if nht == 0:
                    if direction < 0:
                        nht -= 12
                    if direction > 0:
                        nht += 12
                return nht

            # second case: root of target key was specified explicitly
            if t[c] == 'b':
                racc_new = Key.A_FT
                c += 1
            elif t[c] == '#':
                racc_new = Key.A_SH
                c += 1

        # get pitch as number from 0-11 for root of old key
        pit_new = pit_tab[root_old]
        if racc_old == Key.A_FT:
            pit_new -= 1
        if racc_old == Key.A_SH:
            pit_new += 1
        if pit_new < 0:
            pit_new += 12
        if pit_new > 11:
            pit_new -= 12

        # get pitch as number from 0 to 11 for root of new key
        pit_new = pit_tab[root_new]
        if racc_new == Key.A_FT:
            pit_new -= 1
        if racc_new == Key.A_SH:
            pit_new += 1
        if pit_new < 0:
            pit_new += 12
        if pit_new > 11:
            pit_new -= 12

        # number of halftones is difference
        nht = pit_new - pit_old
        if direction == 0:
            if nht > 6:
                nht -= 12
            if nht < -5:
                nht += 12
        if direction > 0 >= nht:
            nht += 12
        if direction < 0 <= nht:
            nht -= 12

        return nht

    def set_transtab(self, nht: int):
        """
        setup for transposition by nht halftones
        """
        # for each note A to G, these tables tell how many sharps (resp. flats)
        # the key must have to get the accidental on this note.Phew.
        sh_tab = [5, 7, 2, 4, 6, 1, 3]
        fl_tab = [3, 1, 6, 4, 2, 7, 5]
        # tables for pretty printout only
        # root_tab = ['A', 'B', 'C', 'D', 'E', 'F', 'G']   # todo
        # acc_tab = ["bb", "b ", "    ", "# ", "x "]

        # nop if no transposition is wanted
        if nht == 0:
            self.add_transp = 0
            self.add_accs = list()
            return

        # get new sharps_flats and shift of numeric pitch; copy to key
        sf_old = self.sf
        # root_old = self.root
        # root_acc = self.root_acc
        sf_new, add_t = self.shift_key(sf_old, nht)
        self.sf = sf_new
        self.add_transp = add_t

        # set up table for conversion of accidentals
        for i in range(7):
            j = i + add_t
            j = (j + 70) % 7
            acc_old = 0
            if sf_old >= sh_tab[i]:
                acc_old = 1
            if -sf_old >= fl_tab[i]:
                acc_old = -1
            acc_new = 0
            if sf_new >= sh_tab[j]:
                acc_new = 1
            if -sf_new >= fl_tab[j]:
                acc_new = -1
            self.add_accs[i] = acc_new - acc_old

        # printout key change
        # if (verbose >= 3):
        #     i = root_old;
        #     j = i + add_t;
        #     j = (j + 70) % 7;
        #     acc_old = 0;
        #     if (sf_old >= sh_tab[i]) acc_old=1;
        #     if (-sf_old >= fl_tab[i]) acc_old=-1;
        #     acc_new = 0;
        #     if (sf_new >= sh_tab[j]) acc_new=1;
        #     if (-sf_new >= fl_tab[j]) acc_new=-1;
        #     strcpy(c3, "s");
        #     if (nht == 1 | | nht == -1) strcpy(c3, "");
        #     strcpy(c1, "");
        #     strcpy(c2, "");
        #     if (acc_old == -1) strcpy(c1, "b"); if (acc_old == 1) strcpy(c1, "#");
        #     if (acc_new == -1) strcpy(c2, "b"); if (acc_new == 1) strcpy(c2, "#");
        #     printf("Transpose root from %c%s to %c%s (shift by %d halftone%s)\n",
        #         root_tab[i], c1, root_tab[j], c2, nht, c3);

        # printout full table of transformations
        # if (verbose >= 4):
        #     printf("old & new keysig        conversions\n");
        #     for (i=0;i < 7;i++) {
        #         j=i+add_t;
        #     j=(j+70) % 7;
        #     acc_old=0;
        #     if ( sf_old >= sh_tab[i]) acc_old=1;
        #     if (-sf_old >= fl_tab[i]) acc_old=-1;
        #     acc_new=0;
        #     if ( sf_new >= sh_tab[j]) acc_new=1;
        #     if (-sf_new >= fl_tab[j]) acc_new=-1;
        #     printf("%c%s. %c%s                     ", root_tab[i], acc_tab[acc_old+2],
        #     root_tab[j], acc_tab[acc_new+2]);
        #     for (a=-1;a <= 1;a++) {
        #     b=a+self.add_acc[i];
        #     printf ("%c%s. %c%s    ", root_tab[i], acc_tab[a+2],
        #     root_tab[j], acc_tab[b+2]);
        #     }
        #     printf ("\n");

    def do_transpose(self, pitch, acc):
        """
        ranspose numeric pitch and accidental

        :param int pitch:
        :param int acc:
        :return: int, int
        """
        # int pitch_old,pitch_new,sf_old,sf_new,acc_old,acc_new,i,j;
        pitch_old = pitch
        acc_old = acc
        acc_new = acc_old
        sf_old = self.sf
        pitch_new = pitch_old + self.add_transp
        i = (pitch_old + 70) % 7
        # j=(pitch_new+70)%7

        if acc_old:
            if acc_old == self.A_DF:
                sf_old = -2
            if acc_old == self.A_FT:
                sf_old = -1
            if acc_old == self.A_NT:
                sf_old = 0
            if acc_old == self.A_SH:
                sf_old = 1
            if acc_old == self.A_DS:
                sf_old = 2
            sf_new = sf_old + self.add_accs[i]
            if sf_new == -2:
                acc_new = self.A_DF
            if sf_new == -1:
                acc_new = self.A_FT
            if sf_new == 0:
                acc_new = self.A_NT
            if sf_new == 1:
                acc_new = self.A_SH
            if sf_new == 2:
                acc_new = self.A_DS
        else:
            acc_new = 0
        return pitch_new, acc_new

    def parse_tab_key(self, string: str) -> int:
        """
        parse "string" for tablature key

        If "string" is a tablature "clef" specification, the corresponding
        clef number is stored in "key_type" and 1 is returned.
        Otherwise 0 is returned.
        """

        if common.notab:
            return 0

        if string == "frenchtab":
            self.k_type = constants.FRENCHTAB
            return True
        elif string == "french5tab":
            self.k_type = constants.FRENCH5TAB
            return True
        elif string == "french4tab":
            self.k_type = constants.FRENCH4TAB
            return True
        elif string == "spanishtab" or string == "guitartab":
            self.k_type = constants.SPANISHTAB
            return True
        elif string == "spanish5tab" or string == "banjo5tab":
            self.k_type = constants.SPANISH5TAB
            return True
        elif string == "spanish4tab" or string == "banjo4tab" or string == "ukuleletab":
            self.k_type = constants.SPANISH4TAB
            return True
        elif string == "italiantab":
            self.k_type = constants.ITALIANTAB
            return True
        elif string == "italian7tab":
            self.k_type = constants.ITALIAN7TAB
            return True
        elif string == "italian8tab":
            self.k_type = constants.ITALIAN8TAB
            return True
        elif string == "italian5tab":
            self.k_type = constants.ITALIAN5TAB
            return True
        elif string == "italian4tab":
            self.k_type = constants.ITALIAN4TAB
            return True
        elif string == "germantab":
            self.k_type = constants.GERMANTAB
            return True

        return False

    def gch_transpose(self, gch):
        """ transpose guitar chord string in gch """
        # char *q,*r;
        # char* gchtrans;
        # int root_old,root_new,sf_old,sf_new,ok;

        root_tab = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
        root_tub = ['a', 'b', 'c', 'd', 'e', 'f', 'g']

        if not args.transposegchords or args.halftones == 0:
            return

        # q = (char*)gch.c_str();
        # gchtrans = (char*)alloca(sizeof(char)*gch.length());
        r = ''

        q: int = 0
        while True:
            while gch[q] == ' ' or gch[q] == '(':
                q += 1
            if gch[q] == '\0':
                break
            ok: int = 0
            if gch[q] in "ABCDEFG":
                root_old = root_tab.index(q)
                ok = 1
            elif gch[q] in "abcdefg":
                root_old = root_tub.index(q)
                ok = 1
            else:
                root_old = self.root

            if ok:
                sf_old = 0
                if gch[q] == 'b':
                    sf_old = -1
                    q += 1
                if gch[q] == '#':
                    sf_old = 1
                    q += 1
                root_new = root_old + self.add_transp
                root_new = (root_new+28) % 7
                sf_new = sf_old + self.add_accs[root_old]
                if ok == 1:
                    r = root_tab[root_new]
                    r += 1
                if ok == 2:
                    r = root_tub[root_new]
                    r += 1
                if sf_new == -1:
                    r = 'b'
                    r += 1
                if sf_new == 1:
                    r = '#'
                    r += 1

            while gch[q] != ' ' and gch[q] != '/' and gch[q] != '\0':
                r += q
                q += 1
            if gch[q] == '/':
                r += gch[q]
                q += 1
        return r

    @staticmethod
    def append_key_change(old_key, new_key) -> None:
        """ append change of key to sym list """
        voice = voices[ivc]
        n1 = old_key.sf
        t1 = Key.A_SH
        if n1 < 0:
            n1 = -n1
            t1 = Key.A_FT
        n2 = new_key.sf
        t2 = Key.A_SH

        if new_key.key_type != old_key.key_type:            # clef change
            kk = voice.add_sym(Clef)
            voice.syms[kk].u = new_key.key_type
            voice.syms[kk].v = 1

        if n2 < 0:
            n2 = -n2
            t2 = Key.A_FT
        if t1 == t2:                            # here if old and new have same type
            if n2 > n1:                                 # more new symbols ..
                kk = voice.add_sym(Key)                # draw all of them
                voice.syms[kk].u = 1
                voice.syms[kk].v = n2
                voice.syms[kk].w = 100
                voice.syms[kk].t = t1
            elif n2 < n1:                        # less new symbols ..
                kk = voice.add_sym(Key)                    # draw all new symbols and
                # neutrals
                voice.syms[kk] = 1
                voice.syms[kk].v = n1
                voice.syms[kk].w = n2+1
                voice.syms[kk].t = t2
            else:
                return

        else:                                         # here for change s->f or f->s
            kk = voice.add_sym(Key)                    # neutralize all old symbols
            voice.syms[kk].u = 1
            voice.syms[kk].v = n1
            voice.syms[kk].w = 1
            voice.syms[kk].t = t1
            kk = voice.add_sym(Key)                    # add all new symbols
            voice.syms[kk].u = 1
            voice.syms[kk].v = n2
            voice.syms[kk].w = 100
            voice.syms[kk].t = t2

    @staticmethod
    def shift_key(sf_old, nht):
        """
        make new key by shifting nht halftones ---

        :param sf_old:
        :param nht:
        :return: sf_new, add_t
        """
        skey_tab = [2, 6, 3, 0, 4, 1, 5, 2]
        fkey_tab = [2, 5, 1, 4, 0, 3, 6, 2]
        root_tab = ['A', 'B', 'C', 'D', 'E', 'F', 'G']

        sf_new = (sf_old + nht * 7) % 12
        sf_new = (sf_new + 240) % 12
        if sf_new >= 6:
            sf_new -= 12

        # get old and new root in ionian mode, shift is difference
        r_old = 2
        if sf_old > 0:
            r_old = skey_tab[sf_old]
        if sf_old < 0:
            r_old = fkey_tab[-sf_old]
        r_new = 2
        if sf_new > 0:
            r_new = skey_tab[sf_new]
        if sf_new < 0:
            r_new = fkey_tab[-sf_new]
        add_t = r_new - r_old

        # fix up add_t to get same "decade" as nht
        dh = (nht + 120) / 12
        dh = dh - 10
        dr = (add_t + 70) / 7
        dr = dr - 10
        add_t = add_t + 7 * (dh - dr)

        log.info(f"shift_key: sf_old={sf_old} new {sf_new}     "
                 f"root: old {root_tab[r_old]} new {root_tab[r_new]}    "
                 f"shift by {add_t}")

        return sf_new, add_t

    def is_tab_key(self):
        """
        decide whether the clef number in "key" means tablature
        """
        return (self.key_type == constants.FRENCHTAB or
                self.key_type == constants.FRENCH5TAB or
                self.key_type == constants.FRENCH4TAB or
                self.key_type == constants.SPANISHTAB or
                self.key_type == constants.SPANISH5TAB or
                self.key_type == constants.SPANISH4TAB or
                self.key_type == constants.ITALIANTAB or
                self.key_type == constants.ITALIAN7TAB or
                self.key_type == constants.ITALIAN8TAB or
                self.key_type == constants.ITALIAN5TAB or
                self.key_type == constants.ITALIAN4TAB or
                self.key_type == constants.GERMANTAB)

    def tab_numlines(self):
        """
        return number of lines per tablature system
        """
        if self.key_type in [constants.FRENCHTAB,
                             constants.SPANISHTAB,
                             constants.ITALIANTAB,
                             constants.ITALIAN7TAB,
                             constants.ITALIAN8TAB]:
            return 6
        elif self.key_type in [constants.FRENCH5TAB,
                               constants.SPANISH5TAB,
                               constants.ITALIAN5TAB,
                               constants.GERMANTAB]:
            # 5 lines should be enough for german tab
            return 5
        elif self.key_type in [constants.FRENCH4TAB,
                               constants.SPANISH4TAB,
                               constants.ITALIAN4TAB]:

            return 4
        else:
            return 0

    def numeric_pitch(self, note):
        """
        :param note:
        :return int:
        """
        caps = list('CDEFGAB')
        lower = list('cdefgab')
        try:
            if note == 'z':
                return 14
            if note.isupper():
                return caps.index(note) + 16 + self.add_pitch
            elif note.islower():
                return lower.index(note) + 23 + self.add_pitch
        except ValueError as ve:
            log.error(ve)
            log.error(f"numeric_pitch: cannot identify <{note}>\n")
        return self.add_pitch


class Clef(Key):
    pass


class Tempo:
    def __init__(self):
        self.tempo = ''

    def __call__(self, line):
        self.tempo = line

    def write_inside_tempo(self, fp) -> None:
        # print metronome marks only when wished
        if self.tempo_is_metronome_mark() and not cfmt.printmetronome:
            return

        common.bskip(fp, cfmt.partsfont.size)
        self.write_tempo(fp, voices[ivc].meter)
        common.bskip(fp, 0.1*constants.CM)

    def tempo_is_metronome_mark(self) -> bool:
        NotImplemented(self.tempo)
        return True

    def write_tempo(self, fp, meter: Meter) -> None:
        log.error(f"write tempo <{self.tempo}>")
        font.set_font(fp, cfmt.tempofont, False)
        fp.write(" 18 0 M\n")
        t = self.tempo
        r = 0
        while len(t) > r:
            while t[r] == ' ':
                r += 1   # skip blanks
            if t[r] == '\0':
                break

            if t[r] == '"':   # write string
                r += 1
                q = ''
                while t[r] != '"' and t[r] != '\0':
                    q += t[r]
                    r += 1
                if t[r] == '"':
                    r += 1
                if q:
                    fp.write("6 0 rmoveto (")
                    fp.write(q)
                    fp.write(") rshow 12 0 \n")
            else:     # write tempo denotation
                q = ""
                while t[r] != ' ' and t[r] != '\0':
                    q = t[r]
                    r += 1
                err = False
                value = 0
                i = 0
                while i < len(q):
                    # dlen = constants.QUARTER
                    if '=' in q:
                        if q[i] == 'C' or q[i] == 'c':
                            i += 1
                            dlen = meter.dlen
                            div = False
                            if q == '/':
                                div = True
                                i += 1
                            fac = 0
                            while q[i].isdigit():
                                dig = int(q[i])
                                fac = 10*fac+dig
                                i += 1

                            if div:
                                if fac == 0:
                                    fac = 2
                                if dlen % fac:
                                    log.error(f"Bad length divisor in tempo: {q}")
                                # dlen = dlen/fac
                            else:
                                if fac > 0:
                                    dlen *= fac
                            if q[i] != '=':
                                err = True
                            i += 1
                            if not q.isdigit():
                                err = True
                            value = int(q[i])
                        elif q[i].isdigit:
                            t = q[i:]
                            f, value = t.split('=', 1)
                            # top, bot = f.split('/')
                            # sscanf(q,"%d/%d=%d", &top,&bot,&value)
                            # dlen = constants.BASE*top/bot
                        else:
                            err = True
                    else:
                        if q[i].isdigit():
                            value = int(q[i])
                        else:
                            err = True
                if err:  # draw note=value
                    log.error(f"+++ invalid tempo specifier: {q[i:]}")
                else:
                    s = symbol.Symbol()
                    # s.len = dlen
                    symbol.Note().identify_note(s, q)
                    sc = 0.55*cfmt.tempofont.size/10.0
                    fp.write(f"gsave {sc:.2f} {sc:.2f} scale 15 3 rmoveto currentpoint\n")
                    if s.head == constants.H_OVAL:
                        fp.write("HD")
                    if s.head == constants.H_EMPTY:
                        fp.write("Hd")
                    if s.head == constants.H_FULL:
                        fp.write("hd")
                    dx = 4.0
                    if s.dots:
                        dotx = 8
                        doty = 0
                        if s.flags > 0:
                            dotx += 4
                        if s.head == constants.H_EMPTY:
                            dotx += 1
                        if s.head == constants.H_OVAL:
                            dotx += 2
                        for i in range(s.dots):
                            fp.write(f" {dotx:.1f} {doty:.1f} dt")
                            dx = dotx
                            dotx = dotx+3.5
                    stem = 16.0
                    if s.flags > 1:
                        stem += 3*(s.flags-1)
                    if s.len < constants.WHOLE:
                        fp.write(f" {stem:.1f} su")
                    if s.flags:
                        fp.write(f" {stem:.1f} f{s.flags}u")
                    if s.flags and dx < 6.0:
                        dx = 6.0
                    dx = (dx+18)*sc
                    fp.write(f" grestore {dx:.2f} 0 rmoveto ( = {value}) rshow\n")

    def tempo_is_metronomemark(self) -> bool:
        """ checks whether a tempostring is a metronome mark("1/4=100")
        or a verbose text(eg. "Andante"). In abc, verbose tempo texts
        must start with double quotes """
        p: str = ''
        for p in self.tempo:
            if p.isspace():
                continue
            if p == '"':
                return False
            else:
                break
        if p:
            return True  # only when actually text found
        else:
            return False


class Voice:
    """ Multi stave music
    abctab2ps supports multi stave music (scores). There are two different
    ways for the notation of scores. You can either define the different voices
    in V: lines at the end of the header just before the first music line
    and use inline V: references "[V:...]" to associate music lines with specific
    voices, as in the following example:

    X:1
    T:Sonata II
    C:B. Marcello, 1712
    M:C
    L:1/8
    K:DDorian
    %
    V:F clef=treble    name=Flauto space=+5pt
    V:B clef=bass      name=Basso
    %
    Q:"Adagio"
    [V:F] ad fe/d/ eA z A | dd d/e/f/g/ aA z a |
    [V:B] d2 d'2 ^c'2 =c'2 | =b2 _b2 aa/g/ fd |

    Alternatively, you can write all music of a specific v immediately
    after its v definition. In this notation the above example reads:

    X:1
    T:Sonata II
    C:B. Marcello, 1712
    M:C
    L:1/8
    K:DDorian
    %
    Q:"Adagio"
    V:F clef=treble    name=Flauto space=+5pt
    ad fe/d/ eA z A | dd d/e/f/g/ aA z a |
    %
    V:B clef=bass      name=Basso
    d2 d'2 ^c'2 =c'2 | =b2 _b2 aa/g/ fd |
    """
    body: bool = False
    header: bool = False

    def __init__(self):
        self.label: int = 0  # identifier string, eg. a number
        self.name = ''  # full name of this v
        self.sname = ''  # short name
        self.meter = Meter()  # meter
        self.meter0 = Meter()  # meter
        self.meter1 = Meter()  # meter
        self.key = Key()  # keysig
        self.key0 = Key()  # keysig
        self.key1 = Key()  # keysig
        self.stems = 0  # +1 or -1 to force stem direction
        self.staves = 0
        self.brace = 0
        self.bracket = 0
        self.do_gch = 0  # 1 to output gchords for this v
        self.sep = 0.0  # for space to next v below
        self.syms = list()  # number of music
        self.nsym = len(self.syms)
        self.draw = False  # flag if want to draw this v
        self.select = True  # flag if selected for output
        self.insert_btype = constants.B_INVIS
        self.insert_num = 0  # to split bars over linebreaks
        self.insert_bnum = 0  # same for bar number
        self.insert_space = 0.0  # space to insert after init syms
        self.end_slur = 0  # for a-b slurs
        self.insert_text = ''  # string over inserted barline
        self.timeinit = 0.0  # carryover time between parts

    def __call__(self, line: str, body: bool = False) -> None:
        Voice.body = body
        max_vc = 5
        if len(voices) >= max_vc:
            log.error("Too many voices; use -maxv to increase limit. "
                      f"Its now {max_vc}")
        self.switch_voice(line)
        log.warning(f'Make new v with id "{self.label}"')

    def add_sym(self, s_type) -> int:
        """
        Add an empty symbol instance to the syms list.
        Returns index for new symbol at end of list. This may not be
        necessary when using python.

        :param str s_type:
        """
        sym = symbol.Symbol()
        sym.type = s_type
        self.syms.append(sym)
        return len(self.syms)

    @staticmethod
    def find_voice(vc: str) -> bool:
        """ return bool is a voice is in voices """
        for voice in voices:
            return vc == voice.label

    # /* ----- find_voice ----- */
    # int find_voice (char *vid, int *newv)
    # {
    #   int i;
    #
    #   for (i=0;i<nvoice;i++)
    #     if (!strcmp(vid,v[i].id)) {
    #       *newv=0;
    #       return i;
    #     }
    #
    #   i=nvoice;
    #   if (i>=maxVc) {
    #     realloc_structs(maxSyms,maxVc+allocVc);
    #   }
    #
    #   strcpy(v[i].id,    vid);
    #   strcpy(v[i].name,  "");
    #   strcpy(v[i].sname, "");
    #   v[i].meter = default_meter;
    #   v[i].key   = default_key;
    #   v[i].stems    = 0;
    #   v[i].staves = v[i].brace = v[i].bracket = 0;
    #   v[i].do_gch   = 1;
    #   v[i].sep      = 0.0;
    #   v[i].nsym     = 0;
    #   v[i].select   = 1;
    #   // new systems must start with invisible bar as anchor for barnumbers
    #   //v[i].insert_btype = v[i].insert_num = 0;
    #   //v[i].insert_bnum = 0;
    #   v[i].insert_btype = B_INVIS;
    #   v[i].insert_num = 0;
    #   v[i].insert_bnum = barinit;
    #   v[i].insert_space = 0.0;
    #   v[i].end_slur = 0;
    #   v[i].timeinit = 0.0;
    #   strcpy(v[i].insert_text, "");
    #   nvoice++;
    #   if (verbose>5)
    #     printf ("Make new v %d with id \"%s\"\n", i,v[i].id);
    #   *newv=1;
    #   return i;
    #
    # }

    def switch_voice(self, line: str) -> bool:
        """  read spec for a v, return v number
        example of a string:

         The syntax of a v definition is

        V: <label> <par1>=<value1> <par2>=<value2>  ...

        where <label> is used to switch to the v in later V: lines.
        Each <par> = <value> pair sets one parameter for the current v.
        <par> can be any of the following parameters or abbreviations:
        """
        if not common.do_this_tune:
            return False
        if not line:
            exit(0)
        self.label, voice_fields = parse_voice(line)
        for field in voice_fields:
            if '=' not in field:
                continue
            else:
                k, v = field.split('=')
                if k == 'name' or k == 'nm':
                    setattr(self, 'name', v)
                elif k == 'sname' or k == 'snm':
                    setattr(self, 'sname', v)
                elif k == 'staves' or k == 'stv':
                    setattr(self, 'staves', int(v))
                elif k == 'brace' or k == 'brc':
                    setattr(self, 'brace', int(v))
                elif k == 'bracket' or k == 'brk':
                    setattr(self, 'bracket', int(v))
                elif k == 'gchords' or k == 'gch':
                    setattr(self, 'do_gch', format.g_logv(v))
                elif k == 'space' or k == 'spc':
                    if not v.startswith(' ') or not v.startswith('-'):
                        setattr(self, 'sep', format.g_unum(v) + 2000)
                    else:
                        setattr(self, k, format.g_unum(v))
                    setattr(self, 'bracket', int(v))
                elif k == 'clef' or k == 'cl':
                    if not field.key.set_clef(v):
                        log.error(f'Unknown clef in v spec: {v}')
                elif k == 'strms' or k == 'stm':
                    if v == 'up':
                        setattr(self, k, 1)
                    elif v == 'down':
                        setattr(self, k, -1)
                    elif v == 'free':
                        setattr(self, k, 0)
                    else:
                        log.error(f'Unknown stem setting in v spec: {v}')
                elif k == 'octave':
                    pass  # ignore abc2midi parameter for compatibility
                else:
                    log.error(f'Unknown option in v spec: {k}')
        voices.append(self)

    #
    # /* ----- switch_voice: read spec for a v, return v number ----- */
    # int switch_voice (std::string str)
    # {
    #
    #     if (!do_this_tune) return 0;
    #
    #     j=-1;
    #
    #     /* start loop over v options: parse t1=t2 */
    #     r = str.c_str();
    #     np=newv=0;
    #     for (;;) {
    #         while (isspace(*r)) r += 1;
    #         if (*r=='\0') break;
    #         strcpy(t1,"");
    #         strcpy(t2,"");
    #         q=t1;
    #         while (!isspace(*r) && *r!='\0' && *r!='=') { *q=*r; r += 1; q++; }
    #         *q='\0';
    #         if (*r=='=') {
    #             r += 1;
    #             q=t2;
    #             if (*r=='"') {
    #                 r += 1;
    #                 while (*r!='"' && *r!='\0') { *q=*r; r += 1; q++; }
    #                 if (*r=='"') r += 1;
    #             }
    #             else {
    #                 while (!isspace(*r) && *r!='\0') { *q=*r; r += 1; q++; }
    #             }
    #             *q='\0';
    #         }
    #         np++;
    #
    #         /* interpret the parsed option. First case is identifier. */
    #         if (np==1) {
    #             j=find_voice (t1,&newv);
    #         } else {                         /* interpret option */
    #             if (j<0) bug("j invalid in switch_voice", true);
    #             if      (!strcmp(t1,"name")    || !strcmp(t1,"nm"))
    #                 strcpy(v[j].name,  t2);
    #
    #             else if (!strcmp(t1,"sname")   || !strcmp(t1,"snm"))
    #                 strcpy(v[j].sname, t2);
    #
    #             else if (!strcmp(t1,"staves")  || !strcmp(t1,"stv"))
    #                 v[j].staves  = atoi(t2);
    #
    #             else if (!strcmp(t1,"brace")   || !strcmp(t1,"brc"))
    #                 v[j].brace   = atoi(t2);
    #
    #             else if (!strcmp(t1,"bracket") || !strcmp(t1,"brk"))
    #                 v[j].bracket = atoi(t2);
    #
    #             else if (!strcmp(t1,"gchords") || !strcmp(t1,"gch"))
    #                 g_logv (str.c_str(),t2,&v[j].do_gch);
    #
    #             /* for sspace: add 2000 as flag if not incremental */
    #             else if (!strcmp(t1,"space")   || !strcmp(t1,"spc")) {
    #                 g_unum (str.c_str(),t2,&v[j].sep);
    #                 if (t2[0]!='+' && t2[0]!='-') v[j].sep += 2000.0;
    #             }
    #
    #             else if (!strcmp(t1,"clef")    || !strcmp(t1,"cl")) {
    #                 if (!set_clef(t2,&v[j].key))
    #                     std::cerr << "Unknown clef in v spec: " << t2 << std::endl;
    #             }
    #             else if (!strcmp(t1,"stems") || !strcmp(t1,"stm")) {
    #                 if      (!strcmp(t2,"up"))    v[j].stems=1;
    #                 else if (!strcmp(t2,"down"))  v[j].stems=-1;
    #                 else if (!strcmp(t2,"free"))  v[j].stems=0;
    #                 else std::cerr << "Unknown stem setting in v spec: " << t2 << std::endl;
    #             }
    #             else if (!strcmp(t1,"octave")) {
    #                 ; /* ignore abc2midi parameter for compatibility */
    #             }
    #             else std::cerr << "Unknown option in v spec: " << t1 << std::endl;
    #         }
    #
    #     }
    #
    #     /* if new v was initialized, save settings im meter0, key0 */
    #     if (newv) {
    #         v[j].meter0 = v[j].meter;
    #         v[j].key0   = v[j].key;
    #     }
    #
    #     if (verbose>7)
    #         printf ("Switch to v %d  <%s> <%s> <%s>  clef=%d\n",
    #                 j,v[j].id,v[j].name,v[j].sname,
    #                 v[j].key.ktype);
    #
    #     nsym0=v[j].nsym;  /* set nsym0 to decide about eoln later.. ugly */
    #     return j;
    #
    # }


class Field:
    header = False
    body = False

    def __init__(self):
        # self.area = Single()   # A:
        # self.book = Single()   # B:
        # self.composer = Composers()   # C:
        # self.discography = Single()   # D:
        # self.layout_parameter = LayoutParams()   # E:
        # self.file_name = Single(True)   # F:
        # self.group = Single()   # G:
        # self.history = History()   # H:
        self.key = Key()   # K:
        self.dlen = DefaultLength()   # L:
        self.meter = Meter()   # M:
        # self.notes = Single(True)   # N:
        # self.origin = Single()   # O:
        # self.parts = Parts()   # P:
        # self.tempo = Tempo()   # Q:
        self.rhythm = Single()   # R:
        # self.source = Single()   # S:
        self.titles = Titles()   # T:
        # self.voice = Voice()   # V:
        # self.lyrics = Lyrics()   # W:
        # self.words = Words()   # w:
        self.xref = XRef()   # X:
        # self.transcription_note = Single()   # Z:

    def __call__(self, line: str) -> None:
        key, value = line.split(':', 1)
        key = key.strip()
        value = value.strip()

        if is_field(line):
            if not common.within_block:
                if key == 'X':
                    ret_val = self.xref(value)
                    if ret_val:
                        Field.header = True
                        self.do_tune = True

                return

            log.debug(f"process_line: {key}:{value}")
            if key == 'K':
                self.key(value, Field.header)
                self.within_block = False
            elif key == 'M':
                self.meter(value, Field.header)
            elif key == 'A':
                self.area(value)
            elif key == 'B':
                self.book(value)
            elif key == 'C':
                self.composer(value)
            elif key == 'D':
                self.discography(value)
            elif key == 'E':
                self.layout_parameter(value, Field.header)
            elif key == 'F':
                self.file_name(value)
            elif key == 'G':
                self.group(value)
            elif key == 'H':
                self.history(value, Field.header)
            elif key == 'L':
                self.dlen(value, Field.header)
            elif key == 'N':
                self.notes(value)
            elif key == 'O':
                self.origin(value)
            elif key == 'P':
                self.parts(value, Field.header)
            elif key == 'Q':
                self.tempo(value)
            elif key == 'S':
                self.source(value)
            elif key == 'T':
                self.titles(value)
            elif key == 'V':
                self.voice(value, Field.header)
            elif key == 'Z':
                self.transcription_note(value)

        if key in ['E', 'K', 'L', 'M', 'P', 'V', 'w', 'W'] and Field.body:
            log.debug(f"process_line: {key}:{value}")
            if key == 'M':
                self.meter(value, Field.body)
            elif key == 'K':
                self.key(value, Field.body)
            elif key == 'V':
                self.voice(value, Field.body)
            elif key == 'P':
                self.parts(value, Field.body)
            elif key == 'L':
                self.dlen(value, Field.body)
            elif key == 'w':
                self.lyrics(value)
            elif key == 'W':
                self.words(value)

    def is_selected(self, xref_str: str, pat: list,
                    select_all: bool, search_field: str) -> bool:
        """ check selection for current info fields """
        # true if select_all or if no selectors given
        if select_all:
            return True
        if not xref_str and len(pat) == 0:
            return True

        m = 0
        for i in range(len(pat)):
            if search_field == constants.S_COMPOSER:
                for j in range(len(self.composer)):
                    if not m:
                        m = re.match(self.composer.composers[j], pat[i])
            elif search_field == constants.S_SOURCE:
                m = re.match(self.source.line, pat[i])
            elif search_field == constants.S_RHYTHM:
                m = re.match(self.rhythm.line, pat[i])
            else:
                m = re.match(self.titles.titles[0], pat[i])
                if not m and len(self.titles) >= 2:
                    m = re.match(self.titles.titles[1], pat[i])
                if not m and len(self.titles.titles[2]) == 3:
                    m = re.match(self.titles.titles[2], pat[i])
            if m:
                return True

        # check xref against string of numbers
        # This is wrong. Need to check with doc to valid the need to rework.
        p: list = self.xref.xref_str.replace(",", " ").xref_str.replace("-", " ").split()
        a = parse.parse_uint(p[0])
        if not a:
            return False  # can happen if invalid chars in string
        b = parse_uint(p[1])
        if not b:
            if self.xref.xref >= a:
                return True
        else:
            for i in range(a, b):
                if self.xref.xref == i:
                    return True
        if self.xref.xref == a:
            return True
        return False

    def check_selected(self, fp, xref_str: str, pat: list, sel_all: bool, search_field: str):
        """
        :param fp:
        :param xref_str:
        :param pat:
        :param sel_all:
        :param search_field:
        """
        if not common.do_this_tune:
            if self.is_selected(xref_str, pat, sel_all, search_field):
                common.do_this_tune = True
                fp.write(f"\n\n%% --- tune {common.tunenum + 1} {self.titles.titles[0]}\n")
                if not common.epsf:
                    common.bskip(fp, cfmt.topspace)

    @staticmethod
    def epsf_title(title: str) -> str:
        title.replace(' ', '_')
        return title

    @staticmethod
    def close_output_file(fp) -> bool:
        """
        This should not have to exist with python.  Using context switches the
        output will always be closed, even with errors. """
        if fp.closed():
            return True

        filename = fp.name
        pssubs.close_page(fp)
        pssubs.close_ps(fp)
        fp.close()

        common.file_open = False
        common.file_initialized = False

        if common.tunenum == 0:
            log.warning(f"No tunes written to output file. Removing {filename}")
            os.remove(filename)
            return True
        else:
            m = util.get_file_size(common.output)
            print(f'Output written to {common.output} (pages: {common.page_number}, '
                  f'titles: {common.tunenum}, bytes: {m}')
            return False

    @staticmethod
    def check_margin(fp, new_posx: float):
        """ do horizontal shift if needed """
        dif = new_posx - common.posx
        if dif * dif < 0.001:
            return
        fp.write(f"{dif:.2f} 0 T\n")
        common.posx = new_posx

    def process_line(self, fp, line):    # i_type: object, xref_str: str, pat: list, sel_all: bool, search_field0: str):
        if common.within_block:
            log.info(f"process_line, type {i_type.__name__} ")

        if xref_str:  # start of new block
            if not common.epsf:
                pass
                # buffer.write_buffer(fp)  # flush stuff left from %% lines
            if common.within_block:
                log.error("+++ Last tune not closed properly")
            common.within_block = True
            common.within_tune = False
            common.do_this_tune = False
            self.titles.titles = list()
            cfmt.init_pdims()
            return
        elif isinstance(i_type, Titles):
            if not common.within_block:
                return
            if common.within_tune:  # title within tune
                if common.do_this_tune:
                    music.output_music(fp)
                    self.titles.write_inside_title(fp)
                    common.do_meter = True
                    common.do_indent = True
                    common.bar_init = cfmt.barinit
            else:
                self.check_selected(fp, xref_str, pat, sel_all, search_field0)
            return
        elif self.tempo:
            if not common.within_block:
                return
            if common.within_tune:   # tempo within tune
                if common.do_this_tune:
                    music.output_music(fp)
                    self.tempo.write_inside_tempo(fp)
            else:
                self.check_selected(fp, xref_str, pat, sel_all, search_field0)
            return
        elif isinstance(i_type, Key):
            if not common.within_block:
                return
            if common.within_tune:
                if common.do_this_tune:
                    self.handle_inside_field(type)
            else:   # end of header ... start now
                self.check_selected(fp, xref_str, pat, sel_all, search_field0)
                if common.do_this_tune:
                    common.tunenum += 1
                    log.warning(f"---- start {self.xref.xref} ({self.titles.titles[0]}) ----")
                    # self.key.halftones = self.key.get_halftones(transpose)
                    # self.key.set_transtab(self.key.halftones)
                    cfmt.check_margin(cfmt.leftmargin)
                    self.write_heading(fp)
                    # voices = list()
                    symbol.Symbol().init_parse_params()
                    # insert is now set in set_meter (for invisible meter)
                    self.meter.insert = 1

                    common.number_of_music_lines = 0
                    common.do_indent = True
                    common.do_meter = True
                    common.bar_init = cfmt.barinit
                    common.write_num = False
            common.within_tune = True
            return
        elif isinstance(i_type, Meter):
            if not common.within_block:
                return
            if common.do_this_tune and common.within_tune:
                self.handle_inside_field(i_type)
            return
        elif isinstance(i_type, DefaultLength):
            if not common.within_block:
                return
            if common.do_this_tune and common.within_tune:
                self.handle_inside_field(i_type)
            return
        elif isinstance(i_type, Parts):
            if not common.within_block:
                return
            if common.do_this_tune and common.within_tune:
                music.output_music(fp)
                self.parts.write_parts(fp)
            return

        elif isinstance(i_type, Voice):
            if common.do_this_tune and common.within_block:
                if not common.within_tune:
                    log.info(f"+++ Voice field not allowed in header: V:{common.lvoiceid}")
                else:
                    pass
                    # ivc = self.voice.switch_voice(common.lvoiceid)
            return
        elif isinstance(i_type, Blank) or isinstance(i_type, EOF):
            if common.do_this_tune:
                music.output_music(fp)
                self.words.put_words(fp)
                if cfmt.writehistory:
                    self.history.put_history(fp)
                if common.epsf:
                    self.close_output_file(fp)
                    if common.choose_outname:
                        fnm = self.epsf_title(self.titles.titles[0])
                        fnm += ".eps"
                    else:
                        common.nepsf += 1
                        fnm = f"{common.file_open}.{common.nepsf:03d}.eps"
                    finf = f"{common.in_file[0]} ({self.xref.xref})"
                    if not os.path.exists(fnm):
                        raise FileExistsError
                    with open(fnm, 'w') as feps:
                        pssubs.init_ps(feps, finf, 
                                       cfmt.leftmargin-5, common.posy+common.bposy-5,
                                       cfmt.leftmargin+cfmt.staffwidth+5,
                                       cfmt.pageheight-cfmt.topmargin)
                        pssubs.init_epsf(feps)
                        # buffer.write_buffer(feps)
                        log.info(f"\n[{fnm}] {self.titles.titles[0]}")
                        pssubs.close_epsf(feps)
                        feps.close()
                        common.in_page = False
                        cfmt.init_pdims()
                else:
                    pass
                    # buffer.buffer_eob(fp)
                    # buffer.write_buffer(fp)

            # info = Info()
            if common.within_block and not common.within_tune:
                log.debug(f"\n+++ Header not closed in tune {self.xref.xref}")
            common.within_tune = False
            common.within_block = False
            common.do_this_tune = False
            return

    def handle_inside_field(self, t_type: object) -> None:
        """ act on info field inside body of tune """
        # Todo, rework handle_inside_field(t_type)
        if not voices:
            common.ivc = self.voice.switch_voice(constants.DEFVOICE)
        if isinstance(t_type, Meter):
            self.meter(voices[common.ivc].meter.meter_str)
            self.meter.append_meter(voices[common.ivc].meter.meter_str)
        elif isinstance(t_type, DefaultLength):
            self.dlen(voices[common.ivc].meter.dlen)
        elif isinstance(t_type, Key):
            old_key = voices[common.ivc].key
            rc = self.key(voices[common.ivc].key, False)
            if rc:
                voices[ivc].key.set_transtab(common.halftones, )
            self.key.append_key_change(old_key, voices[common.ivc].key)
        elif isinstance(t_type, Voice):
            common.ivc = self.voice.switch_voice(common.lvoiceid)

    def write_heading(self, fp):
        line_width: float = cfmt.staffwidth

        # write the main title
        common.bskip(fp, cfmt.titlefont.size + cfmt.titlespace)
        cfmt.titlefont.set_font(fp, True)
        if cfmt.withxrefs:
            fp.write(f"{self.xref.xref}. ")
        t = self.titles.titles[0]
        if cfmt.titlecaps:
            t = t.upper()
        fp.write(t)
        if cfmt.titleleft:
            fp.write(") 0 0 M rshow")
        else:
            fp.write(f") {line_width/2:.1f} 0 M cshow\n", )

        # write second title
        if len(self.titles) > 1:
            common.bskip(fp, cfmt.subtitlespace + cfmt.subtitlefont.size)
            font(fp, cfmt.subtitlefont, True)
            t = self.titles.titles[1]
            if cfmt.titlecaps:
                t = t.upper()
            fp.write(t)
            if cfmt.titleleft:
                fp.write(") 0 0 M rshow\n")
            else:
                fp.write(f") {line_width/2:.1f} 0 M cshow\n")

        # write third title
        if len(self.titles) > 2:
            common.bskip(fp, cfmt.subtitlespace+cfmt.subtitlefont.size)
            font(fp, cfmt.subtitlefont, True)
            t = self.titles.titles[2]
            if cfmt.titlecaps:
                t = t.upper()
            fp.write(t)
            if cfmt.titleleft:
                fp.write(") 0 0 M rshow\n")
        else:
            fp.write(f") {line_width/2:.1f} 0 M cshow\n")

        # write composer, origin
        if self.composer.composers or self.origin.line:
            font.set_font(fp, cfmt.composerfont, False)
            common.bskip(fp, cfmt.composerspace)
            ncl: int = len(self.composer.composers)
            if self.origin and not self.composer.composers:
                ncl = 1
            for composer in self.composer.composers:
                common.bskip(fp, cfmt.composerfont.size)
                fp.write(f"{line_width:.1f} 0 M(")
                fp.write(composer)
                if composer == self.composer.composers[-1] and self.origin:
                    fp.write("(")
                    fp.write(self.origin)
                    fp.write(")")
                fp.write(") lshow\n")
            down1: float = cfmt.composerspace+cfmt.musicspace+ncl*cfmt.composerfont.size
        else:
            common.bskip(fp, cfmt.composerfont.size+cfmt.composerspace)
            down1: float = cfmt.composerspace+cfmt.musicspace+cfmt.composerfont.size
        common.bskip(fp, cfmt.musicspace)

        # decide whether we need extra shift for parts and tempo
        down2: float = cfmt.composerspace+cfmt.musicspace
        if self.parts.parts:
            down2 = down2+cfmt.partsspace+cfmt.partsfont.size
        if self.tempo.tempo:
            down2 = down2+cfmt.partsspace+cfmt.partsfont.size
        if down2 > down1:
            common.bskip(fp, down2-down1)

        # write tempo and parts
        if self.parts.parts or self.tempo.tempo:
            print_tempo = len(self.tempo.tempo) > 0
            if print_tempo and self.tempo.tempo_is_metronomemark() and cfmt.printmetronome:
                print_tempo = False

            if print_tempo:
                common.bskip(fp, -0.2*constants.CM)
                fp.write(f" {cfmt.indent*cfmt.scale:.2f} 0 T ")
                self.tempo.write_tempo(fp, voices[ivc].meter)
                fp.write(f" {-cfmt.indent*cfmt.scale:.2f} 0 T ")
                common.bskip(fp, -cfmt.tempofont.size)

            if self.parts:
                common.bskip(fp, -cfmt.partsspace)
                font.set_font(fp, cfmt.partsfont, False)
                fp.write("0 0 M(")
                fp.write(self.parts.parts)
                fp.write(") rshow\n")
                common.bskip(fp, cfmt.partsspace)

            if print_tempo:
                common.bskip(fp, cfmt.tempofont.size+0.3*constants.CM)

#
# def print_line_type(t: object) -> None:
#     if isinstance(t, Comment):
#         print("COMMENT")
#     elif isinstance(t, Music):
#         print("MUSIC")
#     elif isinstance(t, ToBeContinued):
#         print("TO_BE_CONTINUED")
#     elif isinstance(t, EOF):
#         print("E_O_F")
#     elif isinstance(t, Info):
#         print("INFO")
#     elif isinstance(t, Titles):
#         print("TITLE")
#     elif isinstance(t, Meter):
#         print("METER")
#     elif isinstance(t, Parts):
#         print("PARTS")
#     elif isinstance(t, Key):
#         print("KEY")
#     elif isinstance(t, XRef):
#         print("XREF")
#     elif isinstance(t, DefaultLength):
#         print("DLEN")
#     elif isinstance(t, History):
#         print("HISTORY")
#     elif isinstance(t, Tempo):
#         print("TEMPO")
#     elif isinstance(t, Blank):
#         print("BLANK")
#     elif isinstance(t, Voice):
#         print("VOICE")
#     else:
#         print("UNKNOWN LINE TYPE")

    def get_default_info(self) -> object:
        """ set info to default, except xref field """
        save_str = self.xref.xref_str
        info = Field()
        info.xref.xref_str = save_str
        return info


def put_text(fp, t_type: object, s: str) -> None:
    # int i,n
    # float baseskip,parskip

    n = 0
    for i in range(common.ntext):
        if common.text_type[i] == t_type:
            n += 1
    if n == 0:
        return

    # baseskip = cfmt.textfont.size * cfmt.lineskipfac
    # parskip = cfmt.textfont.size * cfmt.parskipfac
    fp.write("0 0 M\n")
    common.words_of_text = ''
    add_to_text_block(s, False)
    for i in range(common.ntext):
        if common.text_type[i] == t_type:
            add_to_text_block(common.text[i], True)
    write_text_block(fp, constants.RAGGED)
    # buffer.buffer_eob(fp)


class History(Field):

    def __call__(self, line, header=False):
        self.line = line
        self.header = header

    def put_history(self, fp):
        cfmt.textfont.set_font(fp, False)
        cfmt.textfont.set_font_str(common.page_init)
        baseskip = cfmt.textfont.size * cfmt.lineskipfac
        parskip = cfmt.textfont.size * cfmt.parskipfac

        common.bskip(fp, cfmt.textspace)

        if self.rhythm.line:
            common.bskip(fp, baseskip)
            fp.write("0 0 M(Rhythm: ")
            fp.write(self.rhythm.line)
            fp.write(") show\n")
            common.bskip(fp, parskip)

        if self.book:
            common.bskip(fp, 0.5*constants.CM)
            fp.write("0 0 M(Book: ")
            fp.write(self.book.line)
            fp.write(") show\n")
            common.bskip(fp, parskip)

        if self.source:
            common.bskip(fp, 0.5*constants.CM)
            fp.write("0 0 M(Source: ")
            fp.write(self.source.line)
            fp.write(") show\n")
            common.bskip(fp, parskip)

        put_text(fp, self.discography, "Discography: ")
        put_text(fp, self.notes, "Notes: ")
        put_text(fp, self.transcription_note, "Transcription: ")

        ok = False
        for i in range(common.ntext):
            if common.text_type[i] == constants.TEXT_H:
                common.bskip(fp, 0.5*constants.CM)
                fp.write("0 0 M(")
                fp.write(common.text[i])
                fp.write(") show\n")
                ok = True
        if ok:
            common.bskip(fp, parskip)
        # buffer.buffer_eob(fp)
        common.page_init = ""

#
#
# def process_text_block(fp_in, fp, job: bool) -> None:
#     add_final_nl = False
#     if job == constants.OBEYLINES:
#         add_final_nl = True
#     music.output_music(fp)
#     # buffer.buffer_eob(fp)
#     common.cfmt.textfont.set_font(fp, False)
#     common.words_of_text = ""
#     for i in range(100):
#         ln = fp_in.read()
#         if ln == '':
#             log.error("EOF reached scanning text block")
#         common.linenum += 1
#         log.warning(f"{common.linenum:3d}  {ln} \n")
#         if ln.startswith('%%'):
#             del ln[0:1]
#
#         if ln == "endtext":
#             break
#
#         if job != constants.SKIP:
#             if not ln:
#                 field.write_text_block(fp, job)
#                 common.words_of_text = ''
#             else:
#                 field.add_to_text_block(ln, add_final_nl)
#     if job != constants.SKIP:
#         field.write_text_block(fp, job)
