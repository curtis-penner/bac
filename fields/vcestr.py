# Copyright 2018 Curtis Penner

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

Alternatively, you can write all music of a specific voice immediately
after its voice definition. In this notation the above example reads:

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

from fields.meter import Meter
from fields.key import Key
# from constants import (SYMBOL, KEYSTR, GchordList)
from music.symbol import Symbol
import utils.log
import format
from original import constants

log = utils.log.log()

voices = list()
max_vc = 5


class Voice:   # struct to characterize a voice
    def __init__(self):
        self.label = ''   # identifier string, eg. a number
        self.name = ''   # full name of this voice
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
        self.do_gch = 0   # 1 to output gchords for this voice
        self.sep = 0.0   # for space to next voice below
        self.syms = list()    # number of music
        self.draw = False   # flag if want to draw this voice
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
        log.warning(f'Make new voice with id "{self.label}"')

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
        read spec for a voice, return voice number
        example of a string:

         The syntax of a voice definition is

        V: <label> <par1>=<value1> <par2>=<value2>  ...

        where <label> is used to switch to the voice in later V: lines.
        Each <par> = <value> pair sets one parameter for the current voice.
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
                        log.error(f'Unknown clef in voice spec: {v}')
                elif k == 'strms' or k == 'stm':
                    if v == 'up':
                        setattr(self, k, 1)
                    elif v == 'down':
                        setattr(self, k, -1)
                    elif v == 'free':
                        setattr(self, k, 0)
                    else:
                        log.error(f'Unknown stem setting in voice spec: {v}')
                elif k == 'octave':
                    pass   # ignore abc2midi parameter for compatibility
                else:
                    log.error(f'Unknown option in voice spec: {k}')
        voices.append(self)


"""
/* ----- find_voice ----- */
int find_voice (char *vid, int *newv)
{
  int i;

  for (i=0;i<nvoice;i++)
    if (!strcmp(vid,voice[i].id)) {
      *newv=0;
      return i;
    }

  i=nvoice;
  if (i>=maxVc) {
    realloc_structs(maxSyms,maxVc+allocVc);
  }

  strcpy(voice[i].id,    vid);
  strcpy(voice[i].name,  "");
  strcpy(voice[i].sname, "");
  voice[i].meter = default_meter;
  voice[i].key   = default_key;
  voice[i].stems    = 0;
  voice[i].staves = voice[i].brace = voice[i].bracket = 0;
  voice[i].do_gch   = 1;
  voice[i].sep      = 0.0;
  voice[i].nsym     = 0;
  voice[i].select   = 1;
  // new systems must start with invisible bar as anchor for barnumbers
  //voice[i].insert_btype = voice[i].insert_num = 0;
  //voice[i].insert_bnum = 0;
  voice[i].insert_btype = B_INVIS;
  voice[i].insert_num = 0;
  voice[i].insert_bnum = barinit;
  voice[i].insert_space = 0.0;
  voice[i].end_slur = 0;
  voice[i].timeinit = 0.0;
  strcpy(voice[i].insert_text, "");
  nvoice++;
  if (verbose>5)
    printf ("Make new voice %d with id \"%s\"\n", i,voice[i].id);
  *newv=1;
  return i;

}

/* ----- switch_voice: read spec for a voice, return voice number ----- */
int switch_voice (std::string str)
{
    int j,np,newv;
    const char *r;
    char *q;
    char t1[STRLINFO],t2[STRLINFO];

    if (!do_this_tune) return 0;

    j=-1;

    /* start loop over voice options: parse t1=t2 */
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
                strcpy(voice[j].name,  t2);

            else if (!strcmp(t1,"sname")   || !strcmp(t1,"snm"))
                strcpy(voice[j].sname, t2);

            else if (!strcmp(t1,"staves")  || !strcmp(t1,"stv"))
                voice[j].staves  = atoi(t2);

            else if (!strcmp(t1,"brace")   || !strcmp(t1,"brc"))
                voice[j].brace   = atoi(t2);

            else if (!strcmp(t1,"bracket") || !strcmp(t1,"brk"))
                voice[j].bracket = atoi(t2);

            else if (!strcmp(t1,"gchords") || !strcmp(t1,"gch"))
                g_logv (str.c_str(),t2,&voice[j].do_gch);

            /* for sspace: add 2000 as flag if not incremental */
            else if (!strcmp(t1,"space")   || !strcmp(t1,"spc")) {
                g_unum (str.c_str(),t2,&voice[j].sep);
                if (t2[0]!='+' && t2[0]!='-') voice[j].sep += 2000.0;
            }

            else if (!strcmp(t1,"clef")    || !strcmp(t1,"cl")) {
                if (!set_clef(t2,&voice[j].key))
                    std::cerr << "Unknown clef in voice spec: " << t2 << std::endl;
            }
            else if (!strcmp(t1,"stems") || !strcmp(t1,"stm")) {
                if      (!strcmp(t2,"up"))    voice[j].stems=1;
                else if (!strcmp(t2,"down"))  voice[j].stems=-1;
                else if (!strcmp(t2,"free"))  voice[j].stems=0;
                else std::cerr << "Unknown stem setting in voice spec: " << t2 << std::endl;
            }
            else if (!strcmp(t1,"octave")) {
                ; /* ignore abc2midi parameter for compatibility */
            }
            else std::cerr << "Unknown option in voice spec: " << t1 << std::endl;
        }

    }

    /* if new voice was initialized, save settings im meter0, key0 */
    if (newv) {
        voice[j].meter0 = voice[j].meter;
        voice[j].key0   = voice[j].key;
    }

    if (verbose>7)
        printf ("Switch to voice %d  <%s> <%s> <%s>  clef=%d\n",
                j,voice[j].id,voice[j].name,voice[j].sname,
                voice[j].key.ktype);

    nsym0=voice[j].nsym;  /* set nsym0 to decide about eoln later.. ugly */
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
            while ((symv[ivc][isym].type!=BAR) && (isym<voice[ivc].nsym)) isym++;
            if (isym>=voice[ivc].nsym)
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
            while ((symv[ivc][isym].type!=NOTE) && (isym<voice[ivc].nsym)) isym++;
            if (isym>=voice[ivc].nsym)
            { syntax ("Not enough notes for words",c1); break; }
            symv[ivc][isym].wordp[nwline]=add_wd(word);
        }

        if (*c=='\0') break;
    }

    nwline++;
    return 1;
}


"""
