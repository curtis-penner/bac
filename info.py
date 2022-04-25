import re

import buffer
import constants
import music
import subs
from log import log
from key import Key
import symbol
import format
import parse
from format import cfmt, font
import common


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
        :param header:
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
    """
    parse words below a line of music

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
                if word[w] == '*' or word[w] == '~' or not word[w - 1] == '\\':
                    word[w] = ' '
                w += 1
            isym += 1
            while common.voices[common.ivc].sym[isym].type != constants.NOTE and \
                    isym < common.voices[common.ivc].nsym:
                isym += 1
            if isym >= len(common.voices[common.ivc].nsym):
                SyntaxError("Not enough notes for words", line)
            common.voices[common.ivc].sym[isym].wordp[common.nwline] = parse.add_wd(word);

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


class Tempo:
    def __init__(self):
        self.parts = ''

    def __call__(self, line):
        self.parts = line


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
        self.meter1 = 4
        self.meter2 = 4   # numerator, denominator*/
        self.mflag = 1   # mflag: 1=C, 2=C|, 3=numerator only, otherwise 0
        self.top = ''
        self.meter_top = ''
        self.meter_display = dict()
        self.display = 1   # 0 for M:none, 1 for real meter, 2 for differing display
        self.meter1 = 4
        self.meter2 = 4
        self.dlen = constants.EIGHTH
        self.meter_str = None
        self.do_meter = True
        self.dismeter1: int = 4
        self.dismeter2: int = 4
        self.dismflag:int = 0

    def __call__(self, meter_str, header=False):
        self.meter_str = meter_str.strip()
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

        d = constants.BASE/self.meter2

        self.dlen = constants.BASE
        if 4*self.meter1 < 3*self.meter2:
            self.dlen = constants.SIXTEENTH
        self.mflag = 0
        
    def set_meter(self, mtrstr):   # def __call__(mtrstr):
        """ interpret meter string, store in struct """
        if not mtrstr:
            log.error("Empty meter string")
            return

        # if no meter, set invisible 4/4 (for default length)
        if mtrstr == "none":
            mtr_string = "4/4"
            self.display = 0
        else:
            mtr_string = mtrstr
            self.display = 1

        # if global meterdisplay option, add "display=..." string accordingly
        # (this is ugly and not extensible for more keywords, but works for now)
        if not self.meter_display and 'display=' in mtr_string:
            m = mtr_string.split('display=')
            self.display_meter = m[1]
        else:
            log.inf0(f'Meter <{self.meter_str}> is {self.meter1} '
                     f'over {self.meter2} with default '
                     f'length 1/{constants.BASE//self.dlen}')
            if self.display == 2:
                self.dismeter1 = dismeter1
                self.dismeter2 = dismeter2
                self.dismflag = dismflag
                self.distop = meter_distop
                print(f"Meter <{mtrstr}> will display")
            elif self.display == 0:
                self.dismeter1 = 0
                self.dismeter2 = 0
                self.dismflag = 0
                self.distop = ""
                print(f"Meter <{mtrstr}> will display as <none>")

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


        # store parsed data in struct
        self.meter1 = meter1
        self.meter2 = meter2
        self.mflag = mflag
        if not self.dlen:
            self.dlen = dlen
        self.top = meter_top

    def display_meter(self, mtrstr):
        if not mtrstr:
            self.dismeter1 = 4
            self.dismeter2 = 4
            self.mflag = 0
            self.distop = ''
            log.info(f"Meter will display as {self.dismeter1} over {self.dismeter2}")
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
            common.voices[common.ivc].syms[kk].u = self.dismeter1
            common.voices[common.ivc].syms[kk].v = self.dismeter2
            common.voices[common.ivc].syms[kk].w = self.dismflag
            common.voices[common.ivc].syms[kk].text = self.distop
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


class Field:
    header = False
    body = False

    def __init__(self):
        self.area = Single()
        self.book = Single()
        self.composer = Composers()
        self.discography = Single()
        self.layout_parameter = LayoutParams()
        self.file_name = Single(True)
        self.group = Single()
        self.history = History()
        self.key_clef = Key()
        self.default_note_length = DefaultLength()
        self.meter = Meter()
        self.notes = Single(True)
        self.origin = Single()
        self.parts = Parts()
        self.tempo = Tempo()
        self.rhythm = Single()
        self.source = Single()
        self.titles = Titles()
        self.voice = Voice()
        self.lyrics = Lyrics()
        self.words = Words()
        self.xref = XRef()
        self.transcription_note = Single()

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
                self.key_clef(value, Field.header)
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
                self.key_clef(value, Field.body)
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

    def process_line(self, fp, type: object, xref_str: str, pat: list,
                     sel_all: bool, search_field: str):
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
        elif self.titles:
            if not common.within_block:
                return
            if common.within_tune:  # title within tune
                if (common.do_this_tune):
                    music.output_music(fp)
                    self.titles.write_inside_title(fp)
                    common.do_meter = True
                    common.do_indent = True
                    common.bar_init = cfmt.barinit
            else:
                check_selected(fp, xref_str, npat, pat, sel_all,
                               search_field)
            return
    #     elif self.tempo:
    #         if not within_block:
    #             return
    #         if within_tune:   # tempo within tune
    #             if do_this_tune:
    #                 output_music(fp)
    #                 write_inside_tempo(fp)
    #         else:
    #             check_selected(fp, xref_str, npat, pat, sel_all, search_field);
    #         return
    #     elif self.key:
    #         if not within_block:
    #             break;
    #         if within_tune:
    #             if do_this_tune:
    #                 handle_inside_field(type);
    #         else:   # end of header.. start now
    #             check_selected(fp, xref_str, npat, pat, sel_all, search_field);
    #             if do_this_tune:
    #                 tunenum++;
    #                 if verbose >= 3:
    #                     log.warning(f"---- start {xrefnum} ({info.title}) "
    #                                 f"----\n")
    #                 set_keysig(info.key, default_key, True);
    #                 halftones=get_halftones(default_key, transpose);
    #                 set_transtab(halftones, default_key);
    #                 set_meter(info.meter, default_meter);
    #                 set_dlen(info.len, default_meter);
    #                 check_margin(cfmt.leftmargin);
    #                 write_heading(fp);
    #                 nvoice=0
    #                 init_parse_params();
    #                 # insert is now set in set_meter (for invisible meter)
    #                 default_meter.insert=1;
    #
    #                 mline=0;
    #                 do_indent=do_meter=1;
    #                 barinit=cfmt.barinit;
    #                 writenum=0;
    #         within_tune = 1;
    #         break;
    #     elif self.meter:
    #         if not within_block:
    #             break;
    #         if do_this_tune and within_tune:
    #             handle_inside_field(type);
    #         break;
    #         case
    #         DLEN:
    #         if (!within_block) break;
    #         if (do_this_tune & & within_tune) handle_inside_field(type);
    #         break;
    #
    #         case
    #         PARTS:
    #         if (!within_block) break;
    #         if (do_this_tune & & within_tune) {
    #         output_music (fp);
    #         write_parts(fp);
    #         }
    #         break;
    #
    #         case
    #         VOICE:
    #         if (do_this_tune & & within_block) {
    #         if (!within_tune)
    #         printf ("+++ Voice field not allowed in header: V:%s\n", lvoiceid);
    #         else
    #         ivc=switch_voice (lvoiceid);
    #         }
    #         break;
    #
    #         case
    #         BLANK:  # end of block or file
    #         case
    #         E_O_F:
    #         if (do_this_tune) {
    #         output_music (fp);
    #         put_words (fp);
    #         if (cfmt.writehistory) put_history (fp);
    #         if (epsf) {
    #         close_output_file ();
    #         if (choose_outname) {
    #         epsf_title (info.title, fnm);
    #         strcat (fnm, ".eps");
    #         }
    #         else {
    #         nepsf++;
    #         sprintf (fnm, "%s%03d.eps", outf, nepsf);
    #         }
    #         sprintf (finf, "%s (%d)", in_file[0], xrefnum);
    #         if ((feps = fopen (fnm, "w")) == NULL)
    #         rx ("Cannot open output file ", fnm);
    #         init_ps (feps, finf, 1,
    #         cfmt.leftmargin-5, posy+bposy-5,
    #         cfmt.leftmargin+cfmt.staffwidth+5,
    #         cfmt.pageheight-cfmt.topmargin);
    #         init_epsf (feps);
    #         write_buffer (feps);
    #         printf ("\n[%s] %s", fnm, info.title);
    #         close_epsf (feps);
    #         fclose (feps);
    #         in_page=0;
    #         init_pdims ();
    #         }
    #         else {
    #         buffer_eob (fp);
    #         write_buffer (fp);
    #         if ((verbose == 0) & & (tunenum % 10 == 0)) printf (".");
    #         if (verbose == 2) printf ("%s - ", info.title);
    #         }
    #         verbose=0;
    #         }
    #         info = default_info;
    #         if (within_block & & !within_tune)
    #             printf("\n+++ Header not closed in tune %d\n", xrefnum);
    #         within_tune = within_block = do_this_tune = 0;
    #         break;
    #
    #         }
    #         }

    def handle_inside_field(self, t_type: object) -> None:
        """ act on info field inside body of tune """
        # Todo, rework handle_inside_field(t_type)
        if not common.voices:
            common.ivc = self.voice.switch_voice(constants.DEFVOICE)

        if isinstance(t_type, Meter):
            self.meter.set_meter(self.meter, common.voices[common.ivc].meter)
            t_type.append_meter(common.voices[common.ivc].meter, )
        elif isinstance(t_type, info.DefaultLength):
            t_type.set_dlen(self.len, common.voices[common.ivc].meter)
        elif isinstance(t_type, Key):
            oldkey = common.voices[common.ivc].key
            rc = Key.set_keysig(self.key, common.voices[common.ivc].key, 0)
            if rc:
                Key.set_transtab(halftones, common.voices[common.ivc].key)
            Key.append_key_change(oldkey, voices[ivc].key)
        elif isinstance(t_type, voice.Voice):
            ivc = voice.switch_voice(lvoiceid)


    def is_selected(self, xref_str: str, pat: list, select_all: bool, search_field: int) -> bool:
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

    def check_selected(self, fp, xref_str: str, pat: list, sel_all: bool, search_field: int):
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


def get_default_info(info):
    """
    set info to default, except xref field

    This I don't understand why?  or how it is used.

    :param info:
    :return:
    """
    # char savestr[STRLINFO];
    save_str = info.xref
    info = Field()
    info.xref = save_str

    # strcpy (savestr, info.xref);
    # info=default_info;
    # strcpy (info.xref, savestr);

#
# /* ----- is_info_field: identify any type of info field ---- */
# int is_info_field (char *str)
# {
#   if (strlen(str)<2) return 0;
#   if (str[1]!=':')   return 0;
#   if (str[0]=='|')   return 0;   /* |: at start of music line */
#   return 1;
# }
#
#
# /* ----- info_field: identify info line, store in proper place  ---- */
# /* switch within_block: either goes to default_info or info.
#    Only xref ALWAYS goes to info. */
# int info_field (char *str)
# {
#     char s[STRLINFO];
#     struct ISTRUCT *inf;
#     int i;
#
#     if (within_block) {
#         inf=&info;
#     }
#     else {
#         inf=&default_info;
#     }
#
#     if (strlen(str)<2) return 0;
#     if (str[1]!=':')   return 0;
#     if (str[0]=='|')   return 0;   /* |: at start of music line */
#
#     for (i=0;i<strlen(str);i++) if (str[i]=='%') str[i]='\0';
#
#     /* info fields must not be longer than STRLINFO characters */
#     strnzcpy(s,str,STRLINFO);
#
#     if (s[0]=='X') {
#         strip (info.xref,   &s[2]);
#         xrefnum=get_xref(info.xref);
#         return XREF;
#     }
#
#     else if (s[0]=='A') strip (inf->area,   &s[2]);
#     else if (s[0]=='B') strip (inf->book,   &s[2]);
#     else if (s[0]=='C') {
#         if (inf->ncomp>=NCOMP)
#             std::cerr << "Too many composer lines\n";
#         else {
#             strip (inf->comp[inf->ncomp],&s[2]);
#             inf->ncomp++;
#         }
#     }
#     else if (s[0]=='D') {
#         strip (inf->disc,   &s[2]);
#         add_text (&s[2], TEXT_D);
#     }
#
#     else if (s[0]=='F') strip (inf->file,   &s[2]);
#     else if (s[0]=='G') strip (inf->group,  &s[2]);
#     else if (s[0]=='H') {
#         strip (inf->hist,   &s[2]);
#         add_text (&s[2], TEXT_H);
#         return HISTORY;
#     }
#     else if (s[0]=='W') {
#         add_text (&s[2], TEXT_W);
#         return WORDS;
#     }
#     else if (s[0]=='I') strip (inf->info,   &s[2]);
#     else if (s[0]=='K') {
#         strip (inf->key,    &s[2]);
#         return KEY;
#     }
#     else if (s[0]=='L') {
#         strip (inf->len,    &s[2]);
#         return DLEN;
#     }
#     else if (s[0]=='M') {
#         strip (inf->meter,  &s[2]);
#         return METER;
#     }
#     else if (s[0]=='N') {
#         strip (inf->notes,  &s[2]);
#         add_text (&s[2], TEXT_N);
#     }
#     else if (s[0]=='O') strip (inf->orig,   &s[2]);
#     else if (s[0]=='R') strip (inf->rhyth,  &s[2]);
#     else if (s[0]=='P') {
#         strip (inf->parts,  &s[2]);
#         return PARTS;
#     }
#     else if (s[0]=='S') strip (inf->src,    &s[2]);
#     else if (s[0]=='T') {
#         //strip (t, &s[2]);
#         numtitle++;
#         if (numtitle>3) numtitle=3;
#         if (numtitle==1)      strip (inf->title,  &s[2]);
#         else if (numtitle==2) strip (inf->title2, &s[2]);
#         else if (numtitle==3) strip (inf->title3, &s[2]);
#         return TITLE;
#     }
#     else if (s[0]=='V') {
#         strip (lvoiceid,  &s[2]);
#         if (!*lvoiceid) {
#             syntax("missing v specifier",p);
#             return 0;
#         }
#         return VOICE;
#     }
#     else if (s[0]=='Z') {
#         strip (inf->trans,  &s[2]);
#         add_text (&s[2], TEXT_Z);
#     }
#     else if (s[0]=='Q') {
#         strip (inf->tempo,  &s[2]);
#         return TEMPO;
#     }
#
#     else if (s[0]=='E') ;
#
#     else {
#         return 0;
#     }
#
#     return INFO;
# }
#
#
# /* ----- handle_inside_field: act on info field inside body of tune --- */
# void handle_inside_field(int type)
# {
#     struct KEYSTR oldkey;
#     int rc;
#
#     if (type==METER) {
#         if (nvoice==0) ivc=switch_voice (DEFVOICE);
#         set_meter (info.meter,&v[ivc].meter);
#         append_meter (&(v[ivc].meter));
#     }
#
#     else if (type==DLEN) {
#         if (nvoice==0) ivc=switch_voice (DEFVOICE);
#         set_dlen (info.len,  &v[ivc].meter);
#     }
#
#     else if (type==KEY) {
#         if (nvoice==0) ivc=switch_voice (DEFVOICE);
#         oldkey=v[ivc].key;
#         rc=set_keysig(info.key,&v[ivc].key,0);
#         if (rc) set_transtab (halftones,&v[ivc].key);
#         append_key_change(oldkey,v[ivc].key);
#     }
#
#     else if (type==VOICE) {
#         ivc=switch_voice (lvoiceid);
#     }
#
# }
#
#
#
# /* ----- decomment_line: cut off after % ----- */
# void decomment_line (char *ln)
# {
#     char* p;
#     int inquotes = 0; /* do not remove inside double quotes */
#     for (p=ln; *p; p++) {
#         if (*p=='"') {if (inquotes) inquotes=0; else inquotes=1;}
#         if ((*p=='%') && !inquotes) *p='\0';
#     }
#
