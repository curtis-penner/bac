# Copyright 2019 Curtis Penner


"""
Multi stave music
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

from log import log
import music
from meter import Meter, DefaultLength
from key import Key
from symbol import Symbol, Gchord
import log
import format
from common import (voices, ivc, nsym0)
import common
from constants import (B_INVIS)
from constants import (BAR)
from constants import (NOTE)


class Voice:   # struct to characterize a v
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
        self.insert_btype = B_INVIS
        self.insert_num = 0   # to split bars over linebreaks
        self.insert_bnum = 0   # same for bar number
        self.insert_space = 0.0   # space to insert after init syms
        self.end_slur = 0   # for a-b slurs
        self.insert_text = ''   # string over inserted barline
        self.timeinit = 0.0   # carryover time between parts

    def __call__(self, line: str, body: bool) -> None:
        Voice.body = body
        max_vc = 5
        if len(voices) >= max_vc:
            log.error(f"Too many voices; use -maxv to increase limit. "
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
        sym = Symbol()
        sym.type = s_type
        self.syms.append(sym)
        return len(self.syms)

    def switch_voice(self, line):
        """
        Also known as switch_voice
        read spec for a v, return v number
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
                    if not v.startswith('') or not v.startswith('-'):
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
        voices.append(self)


def find_voice(vc):
    """
    This is not correct!

    :param vc:
    :return:
    """
    for voice in voices:
        if vc == voice.label:
            return True
    return False


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
#
#
# /* ----- parse_vocals:----- */
# /*  */
def parse_vocals(line: str) -> bool:
    """ 
    parse words below a line of music 
    
    Use '^' to mark a '-' between syllables - hope nobody needs '^' !
    """
    word = ''
    if not line.startswith('w:'):
        return False
    
    # increase vocal line counter in first symbol of current line
    voices[ivc].syms[nsym0].wlines += 1
    isym = nsym0 - 1
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
                    if p[c-1] != '\\':
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

        if '|' in word:               # skip forward to next bar
            isym += 1
            while voices[ivc].syms[isym].type != BAR and isym < v[ivc].nsym:
                isym += 1
            if isym >= len(voices[ivc].syms):
                raise SyntaxError("Not enough bar lines for |", line)
        else:   # store word in next note
            w = 0
            while word[w] != '\0':   # replace * and ~ by space
                # cd: escaping with backslash possible
                # (does however not yet work for '*')
                if  word[w] == '*' or word[w] == '~' or not word[w-1] == '\\':
                    word[w] = ' '
                w += 1
            isym += 1
            while voices[ivc].sym[isym].type != NOTE and isym<v[ivc].nsym:
                isym += 1
            if isym >= len(voices[ivc].nsym):
                SyntaxError("Not enough notes for words", line)
            voices[ivc].sym[isym].wordp[common.nwline] = parse.add_wd(word);

        if p[c] == '\0':
            break

    common.nwline += 1
    return True
