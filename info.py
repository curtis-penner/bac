import re

import buffer
import constants
import music
import subs
import pssubs
from log import log
import symbol
import format
import parse
from format import cfmt, font
import common


def is_info_field(s: str) -> bool:
    """ identify any type of info field
    |: at start of music line """
    return len(s) < 0 or not s[1] != ':' or s[0] == '|'


def is_field(s: str) -> bool:
    """ Validate a field type """
    return len(s) > 2 and s[1] == ':' and s[0] in 'ABCDEFGHKLMNOPQRSTVWwXZ'


def end_of_file(filename) -> None:
    log.warning(f'end_of_filename: {filename}')


def end_of_filenames():
    log.warning('end_of_filenames')


def parse_info(line):
    f_key, f_value = line.split(':', 1)
    log.warning(f'key: {f_key}, value: {f_value}')


class Voice:   # struct to characterize a v
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
        self.label: int = 0   # identifier string, eg. a number
        self.name = ''   # full name of this v
        self.sname = ''   # short name
        self.meter = Meter()   # meter
        self.meter0 = Meter()   # meter
        self.meter1 = Meter()   # meter
        self.key = Key()   # keysig
        self.key0 = Key()   # keysig
        self.key1 = Key()   # keysig
        self.stems = 0   # +1 or -1 to force stem direction
        self.staves = 0
        self.brace = 0
        self.bracket = 0
        self.do_gch = 0   # 1 to output gchords for this v
        self.sep = 0.0   # for space to next v below
        self.syms = list()    # number of music
        self.nsym = len(self.syms)
        self.draw = False   # flag if want to draw this v
        self.select = True   # flag if selected for output
        self.insert_btype = constants.B_INVIS
        self.insert_num = 0   # to split bars over linebreaks
        self.insert_bnum = 0   # same for bar number
        self.insert_space = 0.0   # space to insert after init syms
        self.end_slur = 0   # for a-b slurs
        self.insert_text = ''   # string over inserted barline
        self.timeinit = 0.0   # carryover time between parts

    def __call__(self, line: str, body: bool = False) -> None:
        Voice.body = body
        max_vc = 5
        if len(common.voices) >= max_vc:
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
        for voice in common.voices:
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

    def switch_voice(self, line: str) -> None:
        """  read spec for a v, return v number
        example of a string:

         The syntax of a v definition is

        V: <label> <par1>=<value1> <par2>=<value2>  ...

        where <label> is used to switch to the v in later V: lines.
        Each <par> = <value> pair sets one parameter for the current v.
        <par> can be any of the following parameters or abbreviations:


        :param line:
        :return:
        """
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
                    pass   # ignore abc2midi parameter for compatibility
                else:
                    log.error(f'Unknown option in v spec: {k}')
        common.voices.append(self)

    #
    # /* ----- switch_voice: read spec for a v, return v number ----- */
    # int switch_voice (std::string str)
    # {
    #     int j,np,newv;
    #     const char *r;
    #     char *q;
    #     char t1[STRLINFO],t2[STRLINFO];
    #
    #     if (!do_this_tune) return 0;
    #
    #     j=-1;
    #
    #     /* start loop over v options: parse t1=t2 */
    #     r = str.c_str();
    #     np=newv=0;
    #     for (;;) {
    #         while (isspace(*r)) r++;
    #         if (*r=='\0') break;
    #         strcpy(t1,"");
    #         strcpy(t2,"");
    #         q=t1;
    #         while (!isspace(*r) && *r!='\0' && *r!='=') { *q=*r; r++; q++; }
    #         *q='\0';
    #         if (*r=='=') {
    #             r++;
    #             q=t2;
    #             if (*r=='"') {
    #                 r++;
    #                 while (*r!='"' && *r!='\0') { *q=*r; r++; q++; }
    #                 if (*r=='"') r++;
    #             }
    #             else {
    #                 while (!isspace(*r) && *r!='\0') { *q=*r; r++; q++; }
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
    """ parse words below a line of music
    Use '^' to mark a '-' between syllables - hope nobody needs '^' !
    """
    word = ''
    if not line.startswith('w:'):
        return False

    # increase vocal line counter in first symbol of current line
    common.voices[common.ivc].syms[common.nsym0].wlines += 1
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
            while common.voices[common.ivc].syms[isym].type != constants.BAR and \
                    isym < common.voices[common.ivc].nsym:
                isym += 1
            if isym >= len(common.voices[common.ivc].syms):
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
            while common.voices[common.ivc].sym[isym].type != constants.NOTE and \
                    isym < common.voices[common.ivc].nsym:
                isym += 1
            if isym >= len(common.voices[common.ivc].nsym):
                SyntaxError("Not enough notes for words", line)
            common.voices[common.ivc].sym[isym].wordp[common.nwline] = parse.add_wd(word)

        if p[c] == '\0':
            break

    common.nwline += 1
    return True


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
        font.set_font(fp, cfmt.subtitlefont, 0)

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
            return True
        else:
            self.xref = 0
            self.xref_str = ''
            return False

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


class Tempo:
    def __init__(self):
        self.tempo = ''

    def __call__(self, line):
        self.parts = line

    def write_inside_tempo(self, fp) -> None:
        # print metronome marks only when wished
        if self.tempo_is_metronome_mark() and not cfmt.printmetronome:
            return

        common.bskip(fp, cfmt.partsfont.size)
        self.write_tempo(fp, self.tempo, common.voices[common.ivc].meter)
        common.bskip(fp, 0.1*constants.CM)

    def tempo_is_metronome_mark(self) -> bool:
        NotImplemented(self.tempo)
        return True

    def write_tempo(self, fp, t: str, v:list) -> None:
        pass


class Words:
    def __init__(self, appendable=False):
        self.appendable = appendable
        self.line = ''

    def __call__(self, line):
        if self.appendable:
            self.line = ' '.join([self.line, line])
        else:
            self.line = line


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


class History:
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

    def append_meter(self, voice: Voice):
        """ add meter to list of music
        Warning: only called for inline fields normal meter music are added in set_initsyms
        """

        # must not be ignored because we need meter for counting bars!
        # if self.display == 0) return

        kk = voice.add_sym(constants.TIMESIG)
        common.voices[common.ivc].syms.append(symbol.Symbol())
        common.voices[common.ivc].syms[kk].gchords = common.GchordList()
        common.voices[common.ivc].syms[kk].type = constants.TIMESIG
        if self.display == 2:
            common.voices[common.ivc].syms[kk].u = self.display_meter1
            common.voices[common.ivc].syms[kk].v = self.display_meter2
            common.voices[common.ivc].syms[kk].w = self.display_mflag
            common.voices[common.ivc].syms[kk].text = self.display_top
        else:
            common.voices[common.ivc].syms[kk].u = self.meter1
            common.voices[common.ivc].syms[kk].v = self.meter2
            common.voices[common.ivc].syms[kk].w = self.mflag
            common.voices[common.ivc].syms[kk].text = self.top

        if not self.display:
            common.voices[common.ivc].syms[kk].invis = 1

    def set_dlen(self, s: str) -> None:
        """ set default length for parsed notes """
        # int l1,l2,d,dlen

        l1: int = 0
        l2: int = 1
        s = f"{l1}/{l2}"
        if not l1:
            return   # empty string.. don't change default length
        else:
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
    (C on line 1), mezzosoprano (C on line 2). Optionally the clef may contain
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
            return True
        return False

    def get_halftones(self, t):
        """
        figure out how by many halftones to transpose
        In the transposing routines: pitches A..G are coded as with 0..7

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

        # get pitch as number from 0 - 11 for root of new key * /
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

    def set_transtab(self, nht, key):
        """
        setup for transposition by nht halftones

        :param int nht:
        :param instande key:
        :return:
        """
        # int a, b, sf_old, sf_new, add_t, i, j, acc_old, acc_new, root_old, root_acc;
        # for each note A..G, these tables tell how many sharps (resp. flats)
        # the keysig must have to get the accidental on this note.Phew.
        sh_tab = [5, 7, 2, 4, 6, 1, 3]
        fl_tab = [3, 1, 6, 4, 2, 7, 5]
        # tables for pretty printout only
        # root_tab = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
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
            key.add_acc[i] = acc_new - acc_old

        # printout keysig change
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

    '''
    def gch_transpose(self, gch):
        """
        transpose guitar chord string in gch

        :param gch:
        :return:
        """
        # char *q,*r;
        # char* gchtrans;
        # int root_old,root_new,sf_old,sf_new,ok;
        root_tab = ['A','B','C','D','E','F','G']
        root_tub = ['a','b','c','d','e','f','g']

        if not args.transposegchords or args.halftones == 0:
            return

        # q = (char*)gch.c_str();
        # gchtrans = (char*)alloca(sizeof(char)*gch.length());
        gchtrans = len(gch)
        r = gchtrans

        while True:
            while (*q==' ' || *q=='(') { *r=*q; q++; r++; }
            if (*q=='\0') break;
            ok = 0
            if q in "ABCDEFG":
                root_old = root_tab.index(q)
                ok = 1
            elif q in "abcdefg":
                root_old = root_tub.index(q)
                ok = 1
            else:
                root_old = self.root

            if ok:
                sf_old = 0
                if q == 'b':
                    sf_old = -1
                    q += 1
                if q == '#':
                    sf_old = 1
                    q += 1
                root_new = root_old + self.add_transp
                root_new = (root_new+28)%7
                sf_new = sf_old + self.add_acc[root_old]
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


            while q !=' ' and q != '/' and q != '\0':
                r = q
                q += 1
                r += 1
            if *q=='/':
                r = *q
                q += 1
                r += 1
        r = '\0'
        return gchtrans;

    def append_key_change(self, gch):
        """
        :param int gch:
        """
        print(gch)

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

    def parse_tab_key(self, string):
        """
        parse "string" for tablature key 
        If "string" is a tablature "clef" specification, the corresponding
        clef number is stored in "key_type" and 1 is returned.
        Otherwise 0 is returned.

        :param string: 
        :return bool: 
        """
        if constants.notab:
            return False

        if string == "frenchtab":
            self.key_type = tab_.FRENCHTAB
            return True
        elif string == "french5tab":
            self.key_type = tab_.FRENCH5TAB
            return True

        elif string == "french4tab":
            self.key_type = tab_.FRENCH4TAB
            return True

        elif string == "spanishtab" or string == "guitartab":
            self.key_type = tab_.SPANISHTAB
            return True
        elif string == "spanish5tab" or string == "banjo5tab":
            self.key_type = tab_.SPANISH5TAB
            return True
        elif string == "spanish4tab" or string == "banjo4tab" or \
                string == "ukuleletab":
            self.key_type = tab_.SPANISH4TAB
            return True
        elif string == "italiantab":
            self.key_type = tab_.ITALIANTAB
            return True
        elif string == "italian7tab":
            self.key_type = tab_.ITALIAN7TAB
            return True
        elif string == "italian8tab":
            self.key_type = tab_.ITALIAN8TAB
            return True
        elif string == "italian5tab":
            self.key_type = tab_.ITALIAN5TAB
            return True
        elif string == "italian4tab":
            self.key_type = tab_.ITALIAN4TAB
            return True
        elif string == "germantab":
            self.key_type = tab_.GERMANTAB
            return True
        return False
    '''

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


class Field:
    header = False
    body = False

    def __init__(self):
        self.area = Single()   # A:
        self.book = Single()   # B:
        self.composer = Composers()   # C:
        self.discography = Single()   # D:
        self.layout_parameter = LayoutParams()   # E:
        self.file_name = Single(True)   # F:
        self.group = Single()   # G:
        self.history = History()   # H:
        self.key = Key()   # K:
        self.default_note_length = DefaultLength()   # L:
        self.meter = Meter()   # M:
        self.notes = Single(True)   # N:
        self.origin = Single()   # O:
        self.parts = Parts()   # P:
        self.tempo = Tempo()   # Q:
        self.rhythm = Single()   # R:
        self.source = Single()   # S:
        self.titles = Titles()   # T:
        self.voice = Voice()   # V:
        self.lyrics = Lyrics()   # W:
        self.words = Words()   # w:
        self.xref = XRef()   # X:
        self.transcription_note = Single()   # Z:

    def __call__(self, line):
        key, value = line.split(':', 1)
        key = key.strip()
        value = value.strip()

        if is_field(key) and Field.header:
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
                self.default_note_length(value, Field.header)
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
                self.default_note_length(value, Field.body)
            elif key == 'w':
                self.lyrics(value)
            elif key == 'W':
                self.words(value)

    def is_selected(self, xref_str: str, pat: list, select_all: bool, search_field: str) -> bool:
        """ check selection for current info fields """
        # true if select_all or if no selectors given
        if select_all:
            return True
        if not xref_str and len(pat) == 0:
            return True

        m = 0
        for i in range(len(pat)):                        #patterns
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
        self.xref.xref_str = self.xref.xref_str.replace(",", " ")
        self.xref.xref_str = self.xref.xref_str.replace("-", " ")

        p = self.xref.xref_str.split()
        a = parse.parse_uint(p[0])
        if not a:
            return False  # can happen if invalid chars in string
        b = parse.parse_uint(p[1])
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


    def process_line(self, fp, i_type: object, xref_str: str, pat: list, sel_all: bool,
                     search_field0: str):
        if common.within_block:
            log.info(f"process_line, type {type.__name__} ")
            # print_line_type(type)

        if xref_str:  # start of new block
            if not common.epsf:
                buffer.write_buffer(fp)  # flush stuff left from %% lines
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
            else:   # end of header.. start now
                self.check_selected(fp, xref_str, pat, sel_all, search_field0)
                if common.do_this_tune:
                    common.tunenum += 1
                    log.warning(f"---- start {xrefnum} ({self.titles.titles[0]}) ----")
                    self.key.set_keysig(info.key, default_key, True)
                    self.key.halftones = self.key.get_halftones(transpose)
                    self.key.set_transtab(self.key.halftones)
                    self.meter.set_meter(info.meter, default_meter)
                    self.default_note_length(default_meter)
                    cfmt.check_margin(cfmt.leftmargin)
                    subs.write_heading(fp)
                    self.voice.nvoice = 0
                    parse.init_parse_params()
                    # insert is now set in set_meter (for invisible meter)
                    self.meter.default_meter.insert = 1

                    common.mline = False
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
                subs.write_parts(fp)
            return

        elif isinstance(i_type, Voice):
            if common.do_this_tune and common.within_block:
                if not common.within_tune:
                    log.info(f"+++ Voice field not allowed in header: V:{common.lvoiceid}")
                else:
                    common.ivc = self.voice.switch_voice(common.lvoiceid)
            return
        elif isinstance(i_type, Blank) or isinstance(i_type, EOF):
            if common.do_this_tune:
                music.output_music(fp)
                subs.put_words(fp)
                if cfmt.writehistory:
                    subs.put_history(fp)
                if common.epsf:
                    subs.close_output_file(fp)
                    if common.choose_outname:
                        fnm = subs.epsf_title(self.titles)
                        fnm += ".eps"
                    else:
                        common.nepsf += 1
                        fnm = f"{common.outf}{common.nepsf:03d}.eps")
                    finf = f"{in_file[0]} ({xrefnum})"
                    try:
                        feps = open(fnm, "w")
                    except FileExistsError as fee:
                        log.error(fee)
                        log.error(f"Cannot open output file {fnm}")
                    pssubs.init_ps(feps, finf, 1,
                                   cfmt.leftmargin-5,
                                   common.posy+common.bposy-5,
                                   cfmt.leftmargin+cfmt.staffwidth+5,
                                   cfmt.pageheight-cfmt.topmargin)
                    pssubs.init_epsf(feps)
                    buffer.write_buffer(feps)
                    log.info(f"\n[{fnm}] {self.titles.titles[0]}")
                    pssubs.close_epsf(feps)
                    feps.close()
                    common.in_page = False
                    cfmt.init_pdims()
                else:
                    buffer.buffer_eob(fp)
                    buffer.write_buffer(fp)

            info = Info()
            if common.within_block and not common.within_tune:
                log.debug(f"\n+++ Header not closed in tune {self.xref.xref}")
            common.within_tune = False
            common.within_block = False
            common.do_this_tune = False
            return

    def handle_inside_field(self, t_type: object) -> None:
        """ act on info field inside body of tune """
        # Todo, rework handle_inside_field(t_type)
        if not common.voices:
            common.ivc = self.voice.switch_voice(constants.DEFVOICE)
        if isinstance(t_type, Meter):
            self.meter.set_meter(common.voices[common.ivc].meter.meter_str)
            self.meter.append_meter(common.voices[common.ivc].meter.meter_str)
        elif isinstance(t_type, DefaultLength):
            self.default_note_length(common.voices[common.ivc].meter.dlen)
        elif isinstance(t_type, Key):
            oldkey = common.voices[common.ivc].key
            rc = self.key(common.voices[common.ivc].key., 0)
            if rc:
                self.key.set_transtab(self.key.halftones,
                                      common.voices[common.ivc].key)
            self.key.append_key_change(oldkey, common.voices[common.ivc].key)
        elif isinstance(t_type, Voice):
            common.ivc = self.voice.switch_voice(common.lvoiceid)



    # # ----- write_heading    -----
    # def write_heading(fp):
    #
    #     # float lwidth,down1,down2
    #     # int i,ncl
    #     # char t[STRLINFO]
    #
    #     lwidth = cfmt.staffwidth
    #
    #     # write the main title
    #     common.bskip(cfmt.titlefont.size + cfmt.titlespace)
    #     cfmt.titlefont.set_font(fp, True)
    #     if cfmt.withxrefs:
    #         fp.write(f"{xrefnum}. ")
    #     t = info.titles[0]
    #     if(cfmt.titlecaps) cap_str(t)
    #     put_str(t)
    #     if cfmt.titleleft:
    #         put(") 0 0 M rshow")
    #     else:
    #         put(f") {lwidth/2:.1f} 0 M cshow\n", )
    #
    #     # write second title
    #     if len(info.titles) >=2:
    #         util.bskip(cfmt.subtitlespace + cfmt.subtitlefont.size)
    #         set_font(fp,cfmt.subtitlefont,1)
    #         strcpy(t,info.title2)
    #         if(cfmt.titlecaps) cap_str(t)
    #         put_str(t)
    #         if(cfmt.titleleft) PUT0(") 0 0 M rshow\n")
    #         else PUT1(") %.1f 0 M cshow\n", lwidth/2)
    #     }
    #
    #     # write third title
    #     if(numtitle>=3) {
    #         bskip(cfmt.subtitlespace+cfmt.subtitlefont.size)
    #         set_font(fp,cfmt.subtitlefont,1)
    #         strcpy(t,info.title3)
    #         if(cfmt.titlecaps) cap_str(t)
    #         put_str(t)
    #         if(cfmt.titleleft) PUT0(") 0 0 M rshow\n")
    #         else PUT1(") %.1f 0 M cshow\n", lwidth/2)
    #     }
    #
    #     # write composer, origin
    #     if((info.ncomp>0) ||(strlen(info.orig)>0)) {
    #         set_font(fp,cfmt.composerfont,0)
    #         bskip(cfmt.composerspace)
    #         ncl=info.ncomp
    #         if((strlen(info.orig)>0) &&(ncl<1)) ncl=1
    #         for(i=0;i<ncl;i++) {
    #             bskip(cfmt.composerfont.size)
    #             PUT1("%.1f 0 M(", lwidth)
    #             put_str(info.comp[i])
    #             if((i==ncl-1)&&(strlen(info.orig)>0)) {
    #                 put_str("(")
    #                 put_str(info.orig)
    #                 put_str(")")
    #             }
    #             PUT0(") lshow\n")
    #         }
    #         down1=cfmt.composerspace+cfmt.musicspace+ncl*cfmt.composerfont.size
    #     }
    #     else {
    #         bskip(cfmt.composerfont.size+cfmt.composerspace)
    #         down1=cfmt.composerspace+cfmt.musicspace+cfmt.composerfont.size
    #     }
    #     bskip(cfmt.musicspace)
    #
    #     # decide whether we need extra shift for parts and tempo
    #     down2=cfmt.composerspace+cfmt.musicspace
    #     if(strlen(info.parts)>0) down2=down2+cfmt.partsspace+cfmt.partsfont.size
    #     if(strlen(info.tempo)>0) down2=down2+cfmt.partsspace+cfmt.partsfont.size
    #     if(down2>down1) bskip(down2-down1)
    #
    #     # write tempo and parts
    #     if(strlen(info.parts)>0 || strlen(info.tempo)>0) {
    #         int printtempo =(strlen(info.tempo)>0)
    #         if(printtempo &&
    #                 tempo_is_metronomemark(info.tempo) && !cfmt.printmetronome)
    #             printtempo = 0
    #
    #         if(printtempo) {
    #             bskip(-0.2*CM)
    #             PUT1(" %.2f 0 T ", cfmt.indent*cfmt.scale)
    #             write_tempo(fp, info.tempo, default_meter)
    #             PUT1(" %.2f 0 T ", -cfmt.indent*cfmt.scale)
    #             bskip(-cfmt.tempofont.size)
    #         }
    #
    #         if(strlen(info.parts)>0) {
    #             bskip(-cfmt.partsspace)
    #             set_font(fp,cfmt.partsfont,0)
    #             PUT0("0 0 M(")
    #             put_str(info.parts)
    #             PUT0(") rshow\n")
    #             bskip(cfmt.partsspace)
    #         }
    #
    #         if(printtempo) bskip(cfmt.tempofont.size+0.3*CM)
    #
    #     }
    #
    #
    # }

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



#
# /* ----- add_text ---- */
# void add_text (char *str, int type)
# {
#   if (not do_output) { return; }
#   if (ntext>=NTEXT) {
#       std::cerr << "No more room for text line <" << str << ">\n";
#       return;
#   }
#   strcpy (text[ntext], str);
#   text_type[ntext]=type;
#   ntext++;
# }
#
#

    def get_default_info(self) -> object:
        """
        set info to default, except xref field
        :param info:
        :return:
        """
        save_str = self.xref.xref_str
        info = Field()
        info.xref.xref_str = save_str
        return info




