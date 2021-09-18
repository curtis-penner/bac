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
# from constants import (SYMBOL, KEYSTR, GchordList)
from symbol import Symbol
import log
import format
import constants

voices = list()
max_vc = 5


class Voice:   # struct to characterize a v
    def __init__(self):
        self.label = ''   # identifier string, eg. a number
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
        self.draw = False   # flag if want to draw this v
        self.select = True   # flag if selected for output
        self.insert_btype = constants.B_INVIS
        self.insert_num = 0   # to split bars over linebreaks
        self.insert_bnum = 0   # same for bar number
        self.insert_space = 0.0   # space to insert after init syms
        self.end_slur = 0   # for a-b slurs
        self.insert_text = ''   # string over inserted barline
        self.timeinit = 0.0   # carryover time between parts

    def __call__(self, line, header):
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
        max_syms = 800
        k = len(self.syms)
        if k >= max_syms:
            # realloc_structs(maxSyms+allocSyms, maxVc)
            return k
        t_sym = Symbol()
        t_sym.type = s_type
        self.syms.append(t_sym)
        return len(self.syms)

    @staticmethod
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


"""
/* ----- find_voice ----- */
int find_voice (char *vid, int *newv)
{
  int i;

  for (i=0;i<nvoice;i++)
    if (!strcmp(vid,v[i].id)) {
      *newv=0;
      return i;
    }

  i=nvoice;
  if (i>=maxVc) {
    realloc_structs(maxSyms,maxVc+allocVc);
  }

  strcpy(v[i].id,    vid);
  strcpy(v[i].name,  "");
  strcpy(v[i].sname, "");
  v[i].meter = default_meter;
  v[i].key   = default_key;
  v[i].stems    = 0;
  v[i].staves = v[i].brace = v[i].bracket = 0;
  v[i].do_gch   = 1;
  v[i].sep      = 0.0;
  v[i].nsym     = 0;
  v[i].select   = 1;
  // new systems must start with invisible bar as anchor for barnumbers
  //v[i].insert_btype = v[i].insert_num = 0;
  //v[i].insert_bnum = 0;
  v[i].insert_btype = B_INVIS;
  v[i].insert_num = 0;
  v[i].insert_bnum = barinit;
  v[i].insert_space = 0.0;
  v[i].end_slur = 0;
  v[i].timeinit = 0.0;
  strcpy(v[i].insert_text, "");
  nvoice++;
  if (verbose>5)
    printf ("Make new v %d with id \"%s\"\n", i,v[i].id);
  *newv=1;
  return i;

}

/* ----- switch_voice: read spec for a v, return v number ----- */
int switch_voice (std::string str)
{
    int j,np,newv;
    const char *r;
    char *q;
    char t1[STRLINFO],t2[STRLINFO];

    if (!do_this_tune) return 0;

    j=-1;

    /* start loop over v options: parse t1=t2 */
    r = str.c_str();
    np=newv=0;
    for (;;) {
        while (isspace(*r)) r++;
        if (*r=='\0') break;
        strcpy(t1,"");
        strcpy(t2,"");
        q=t1;
        while (!isspace(*r) && *r!='\0' && *r!='=') { *q=*r; r++; q++; }
        *q='\0';
        if (*r=='=') {
            r++;
            q=t2;
            if (*r=='"') {
                r++;
                while (*r!='"' && *r!='\0') { *q=*r; r++; q++; }
                if (*r=='"') r++;
            }
            else {
                while (!isspace(*r) && *r!='\0') { *q=*r; r++; q++; }
            }
            *q='\0';
        }
        np++;

        /* interpret the parsed option. First case is identifier. */
        if (np==1) {
            j=find_voice (t1,&newv);
        } else {                         /* interpret option */
            if (j<0) bug("j invalid in switch_voice", true);
            if      (!strcmp(t1,"name")    || !strcmp(t1,"nm"))
                strcpy(v[j].name,  t2);

            else if (!strcmp(t1,"sname")   || !strcmp(t1,"snm"))
                strcpy(v[j].sname, t2);

            else if (!strcmp(t1,"staves")  || !strcmp(t1,"stv"))
                v[j].staves  = atoi(t2);

            else if (!strcmp(t1,"brace")   || !strcmp(t1,"brc"))
                v[j].brace   = atoi(t2);

            else if (!strcmp(t1,"bracket") || !strcmp(t1,"brk"))
                v[j].bracket = atoi(t2);

            else if (!strcmp(t1,"gchords") || !strcmp(t1,"gch"))
                g_logv (str.c_str(),t2,&v[j].do_gch);

            /* for sspace: add 2000 as flag if not incremental */
            else if (!strcmp(t1,"space")   || !strcmp(t1,"spc")) {
                g_unum (str.c_str(),t2,&v[j].sep);
                if (t2[0]!='+' && t2[0]!='-') v[j].sep += 2000.0;
            }

            else if (!strcmp(t1,"clef")    || !strcmp(t1,"cl")) {
                if (!set_clef(t2,&v[j].key))
                    std::cerr << "Unknown clef in v spec: " << t2 << std::endl;
            }
            else if (!strcmp(t1,"stems") || !strcmp(t1,"stm")) {
                if      (!strcmp(t2,"up"))    v[j].stems=1;
                else if (!strcmp(t2,"down"))  v[j].stems=-1;
                else if (!strcmp(t2,"free"))  v[j].stems=0;
                else std::cerr << "Unknown stem setting in v spec: " << t2 << std::endl;
            }
            else if (!strcmp(t1,"octave")) {
                ; /* ignore abc2midi parameter for compatibility */
            }
            else std::cerr << "Unknown option in v spec: " << t1 << std::endl;
        }

    }

    /* if new v was initialized, save settings im meter0, key0 */
    if (newv) {
        v[j].meter0 = v[j].meter;
        v[j].key0   = v[j].key;
    }

    if (verbose>7)
        printf ("Switch to v %d  <%s> <%s> <%s>  clef=%d\n",
                j,v[j].id,v[j].name,v[j].sname,
                v[j].key.ktype);

    nsym0=v[j].nsym;  /* set nsym0 to decide about eoln later.. ugly */
    return j;

}


/* ----- parse_vocals: parse words below a line of music ----- */
/* Use '^' to mark a '-' between syllables - hope nobody needs '^' ! */
int parse_vocals (char *line)
{
    int isym;
    char *c,*c1,*w;
    char word[81];

    if ((line[0]!='w') || (line[1]!=':')) return 0;
    p0=line;

    /* increase vocal line counter in first symbol of current line */
    symv[ivc][nsym0].wlines++;

    isym=nsym0-1;
    c=line+2;
    for (;;) {
        while(*c==' ') c++;
        if (*c=='\0') break;
        c1=c;
        if ((*c=='_') || (*c=='*') || (*c=='|') || (*c=='-')) {
            word[0]=*c;
            if (*c=='-') word[0]='^';
            word[1]='\0';
            c++;
        }
        else {
            w=word;
            *w='\0';
            while ((*c!=' ') && (*c!='\0')) {
                if ((*c=='_') || (*c=='*') || (*c=='|')) break;
                if (*c=='-') {
                    if (*(c-1) != '\\') break;
                    w--;
                    *w='-';
                }
                *w=*c; w++; c++;
            }
            if (*c=='-') { *w='^' ; w++; c++; }
            *w='\0';
        }

        /* now word contains a word, possibly with trailing '^',
           or one of the special characters * | _ -               */

        if (!strcmp(word,"|")) {               /* skip forward to next bar */
            isym++;
            while ((symv[ivc][isym].type!=BAR) && (isym<v[ivc].nsym)) isym++;
            if (isym>=v[ivc].nsym)
            { syntax("Not enough bar lines for |",c1); break; }
        }

        else {                                 /* store word in next note */
            w=word;
            while (*w!='\0') {                   /* replace * and ~ by space */
                /* cd: escaping with backslash possible */
                /* (does however not yet work for '*') */
                if ( ((*w=='*') || (*w=='~')) && !(w>word && *(w-1)=='\\') ) *w=' ';
                w++;
            }
            isym++;
            while ((symv[ivc][isym].type!=NOTE) && (isym<v[ivc].nsym)) isym++;
            if (isym>=v[ivc].nsym)
            { syntax ("Not enough notes for words",c1); break; }
            symv[ivc][isym].wordp[nwline]=add_wd(word);
        }

        if (*c=='\0') break;
    }

    nwline++;
    return 1;
}


"""


music = music.Music()
cfmt = format.Format()


def is_field(line):
    return len(line) > 2 and line[1] == ':' \
           and line[0] in 'ABCDEFGHIKLMNOPQRSTVWwXYZ'


def end_of_file(filename):
    log.warning(f'end_of_filename: {filename}')


def end_of_filenames():
    log.warning('end_of_filenames')


def parse_info(line):
    f_key, f_value = line.split(':', 1)
    log.warning(f'key: {f_key}, value: {f_value}')


class Composers:
    def __init__(self):
        self.size = 5
        self.composers = list()

    def __call__(self, value):
        if len(self.composers) <= self.size:
            self.composers.append(value)

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

    # def do_this(self):
    #     if not Field.within_block:
    #         return
    #     if Field.do_tune:  # title within tune
    #         if do_this_tune:
    #             output_music(fp)
    #             self.write_inside_title(common.fp);
    #             Field.do_meter = True
    #             Field.do_indent = True
    #             barinit = cfmt.barinit
    #     else:
    #         check_selected(common.fp, xref_str, npat, pat, sel_all, search_field)

    # def write_inside_title(self, fp):


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

    def get_xref(self, line):
        """
        get xref from string

        :param line:
        :return:
        """
        if not line:
            log.error("xref string is empty")
            return 0

        if not line.isdigit():
            log.error(f"xref string has invalid symbols: {line}")
            return 0
        self.xref = int(line)

    """
    /* ----- get_xref: get xref from string ----- */
    int get_xref (char *str)
    {

      int a,ok;
      char *q;

      if (strlen(str)==0) {
          std::cerr << "xref string is empty" << std::endl;
        return 0;
      }
      q=str;
      ok=1;
      while (*q != '\0') {
        if (!isdigit(*q)) ok=0;
        q++;
      }
      if (!ok) {
         std::cerr << "xref string has invalid symbols: " << str << std::endl;
        return 0;
      }

      sscanf (str, "%d", &a);

      return a;
    }
    """


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
    def __init__(self):
        self.parts = ''

    def __call__(self, line):
        self.parts = line


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


#
# void reset_info (struct ISTRUCT *inf)
# {
#
#     # reset all info fields except info.xref
#
#     strcpy(inf.parts,    "");
#     strcpy(inf.area,     "");
#     strcpy(inf.book,     "");
#     inf.ncomp = 0;
#     strcpy(inf.disc,     "");
#     strcpy(inf.file,     "");
#     strcpy(inf.group,    "");
#     strcpy(inf.hist,     "");
#     strcpy(inf.info,     "");
#     strcpy(inf.key,        "C");
#     strcpy(inf.meter,    "none");
#     strcpy(inf.notes,    "");
#     strcpy(inf.orig,     "");
#     strcpy(inf.rhyth,    "");
#     strcpy(inf.src,        "");
#     strcpy(inf.title,    "");
#     strcpy(inf.title2, "");
#     strcpy(inf.title3, "");
#     strcpy(inf.trans,    "");
#     strcpy(inf.tempo,    "");
# }



class Field:
    header = False
    body = False

    do_tune = False
    do_music = False
    within_block = False

    def __init__(self):
        self.area = Single()
        self.book = Single()
        self.composer = Composers()
        self.discography = Single()
        self.layout_parameter = LayoutParams()
        self.file_name = Single(True)
        self.group = Single()
        self.history = Single(True)
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
        self.transciptoin_note = Single()

    def __call__(self, line):
        key, value = line.split(':', 1)
        key = key.strip()
        value = value.strip()

        if self.is_field(key) and Field.header:
            if not self.within_block:
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
                self.history(value)
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
                self.transciptoin_note(value)

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

    @staticmethod
    def is_field(s):
        """
        Validate a field type

        :param s:
        :return bool:
        """
        return len(s) > 2 and s[1] == ':' and s[0] in 'ABCDEFGHKLMNOPQRSTVWwXZ'

    def get_default_info(self):
        """ set info to default, except xref field """
        savestr = self.xref
        # default_info = default_info.Field()
        self.xref = savestr

    # def process_line(self, fp, type, xref_str, pat, sel_all, search_field):
    #     """
    #
    #     :param fp: filename or pointer?
    #     :param type: won't be using
    #     :param xref_str:
    #     :param pat: list of strings
    #     :param sel_all: bool
    #     :param search_field: int
    #     """
    #     fnm = ''
    #     finf = list()
    #     feps = None
    #
    #     if common.within_block:
    #         log.info(f"process_line, type {type} ")
    #         print_linetype(type)
    #
    #     if self.xref:   # start of new block
    #         if not epsf:
    #             write_buffer (fp)   # flush stuff left from %% lines
    #         if within_block:
    #             log.error("\n+++ Last tune not closed properly\n");
    #         get_default_info ();
    #         within_block    = True
    #         within_tune     = False
    #         do_this_tune    = False
    #         self.Title = list()
    #         init_pdims();
    #         cfmt = Format()
    #         return
    #     elif self.titles:
    #         if not within_block:
    #             return
    #         if within_tune:   # title within tune
    #             if (do_this_tune ):
    #                 output_music(fp)
    #                 write_inside_title(fp);
    #                 do_meter = do_indent = True
    #                 barinit = cfmt.barinit
    #         else:
    #             check_selected(fp, xref_str, npat, pat, sel_all,
    #                            search_field)
    #         return
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
# }

