import re

from log import log
from constants import (S_SOURCE, S_RHYTHM, S_COMPOSER)
from constants import (NWPOOL, NTEXT, TEXT_D)
from constants import (BASE, EIGHTH, SIXTEENTH)
from constants import DEFVOICE, TIMESIG
from constants import (A_NT, A_FT, A_SH)
from constants import (TREBLE, TREBLE8, TREBLE8UP, BASS, ALTO, TENOR,
                       SOPRANO, MEZZOSOPRANO, BARITONE, VARBARITONE, SUBBASS)
from constants import FRENCHVIOLIN
from constants import (FRENCHTAB, FRENCH5TAB, FRENCH4TAB, SPANISHTAB, SPANISH5TAB,
                       SPANISH4TAB, ITALIANTAB, ITALIAN8TAB, ITALIAN7TAB, ITALIAN5TAB,
                       ITALIAN4TAB, GERMANTAB)
from common import voices, ivc, cfmt
import common
import voice
import symbol
import subs
import info


symb = symbol.Symbol()
info = info.Field()

# subroutines connected with parsing the input file

# "void syntax" is replaced with SyntaxError Exception


def is_note(c: str) -> bool:
    """ checks char for valid note symbol """
    return c in "CDEFGABcdefgab^=_"


# zero_sym: moved to symbol.py
# add_sym: moved to Voice in voice.py

def char_delta(c: str, d: str) -> int:
    """ find int difference between to characters """
    if len(c) == 1 and len(d) == 1:
        return ord(c) - ord(d)
    else:
        SyntaxError(f'the inputs need to be char not string: {c}, {d}')
        return 0


def get_xref(s: str) -> int:
    """ get xref from string """
    if not s:
        log.error("xref string is empty")
        return 0

    if s.isdigit() and int(s) != 0:
        return int(s)
    else:
        log.error(f"xref string has invalid symbols: {s}")
        return 0


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
        self.dlen = EIGHTH
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

        d = BASE/self.meter2

        self.dlen = BASE
        if 4*self.meter1 < 3*self.meter2:
            self.dlen = SIXTEENTH
        self.mflag = 0


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

    def set_meter(self, mtrstr):   # def __call__(mtrstr):
        """ interpret meter string, store in struct """
        if not mtrstr:
            log.error("Empty meter string")
            return

        # if no meter, set invisible 4/4 (for default length)
        if mtrstr == "none":
            mtrstring = "4/4"
            self.display = 0
        else:
            mtrstring = mtrstr
            self.display = 1

        # if global meterdisplay option, add "display=..." string accordingly
        # (this is ugly and not extensible for more keywords, but works for now)
        if not self.meter_display and 'display=' in mtrstring:
            m = mtrstring.split('display=')
            self.display_meter = m[1]
        else:
            log.inf0(f'Meter <{self.meter_str}> is {self.meter1} '
                     f'over {self.meter2} with default '
                     f'length 1/{BASE/self.dlen}')
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

    def append_meter(self, voice: voice.Voice):
        """ add meter to list of music
        Warning: only called for inline fields normal meter music are added in set_initsyms
        """

        # must not be ignored because we need meter for counting bars!
        # if self.display == 0) return

        kk = voice.add_sym(TIMESIG)
        common.voices[common.ivc].syms.append(symbol.Symbol())
        common.voices[common.ivc].syms[kk].gchords = common.GchordList()
        common.voices[common.ivc].syms[kk].type = TIMESIG
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
            d = BASE/l2
            if d*l2 != BASE:
                log.critical(f"Length incompatible with BASE, using 1/8: {s}")
                dlen = BASE/8
            else:
                dlen = d*l1

        if common.verbose >= 4:
            print(f"Dlen    <{s}> sets default note length to {dlen}/{BASE} = 1/{BASE/dlen}")

        self.dlen = dlen



class DefaultLength(Meter):
    Body = True

    def __init__(self):
        super().__init__()
        self.default_length = EIGHTH

    def __call__(self, length, header=True):
        if '/' in length:
            top, bottom = length.split('/')
            if not top.isdigit() and not bottom.isdigit():
                log.error(f'+++Error: Default Length {length}')
                exit(3)
            self.default_length = BASE * int(top) // int(bottom)
        else:
            self.default_length = EIGHTH


class Key:
    __nht: int
    
    def __init__(self):
        """data lto specify the key"""
        self.k_type: int = 0
        self.sf: int = 0
        self.add_pitch: int = 0
        self.root_acc: int = 0
        self.root: int = 0
        self.add_transp: int = 0
        self.add_acc = [0]*7


    def set_keysig(self, s: str, init: bool) -> int:
        """
        interpret keysig string, store in struct

        This part was adapted from abc2mtex by Chris Walshaw
        updated 03 Oct 1997 Wil Macaulay - support all modes
        Returns 1 if key was actually specified, because then we want
        to transpose. Returns zero if this is just a clef change.
        """
        # maybe initialize with key C (used for K field in header)
        if init:
            self.sf = 0
            self.k_type = TREBLE
            self.add_pitch = 0
            self.root = 2
            self.root_acc = A_NT

        # check for clef specification with no other information
        if "clef=" in s and self.set_clef(s+5):
            return False
        if self.set_clef(s):
            return False

        # check for key specifier
        c = 0
        bagpipe = False
        if s[c] == 'F':
            sf = -1
            root = 5
        elif s[c] == 'C':
            sf = 0
            root = 2
        elif s[c] == 'G':
            sf = 1
            root = 6
        elif s[c] == 'D':
            sf = 2
            root = 3
        elif s[c] == 'A':
            sf = 3
            root = 0
        elif s[c] == 'E':
            sf = 4
            root = 4
        elif s[c] == 'B':
            sf = 5
            root = 1
        elif s[c] == 'H':
            bagpipe = 1

            c += 1
            if s[c] == 'P':
                sf = 0
                root = 2
            elif s[c] == 'p':
                sf = 2
                root = 3
            else:
                sf = 0
                root = 2
                log.error(f"unknown bagpipe-like key: {s}")
        else:
            log.error(f"Using C because key not recognised: {s}")
            sf = 0
            root = 2

        c += 1

        root_acc = A_NT
        if s[c] == '#':
            sf += 7
            c += 1
            root_acc = A_SH
        elif s[c] == 'b':
            sf -= 7
            c += 1
            root_acc = A_FT

        # loop over blank-delimited words: get the next token in lower case
        while True:
            while s[c].isspace():
                c += 1
            if c > len(s):
                break

            w = ''
            while not s[c].isspace() and c < len(s):
                w += s[c].lower()
                c += 1


            # now identify this word

            # first check for mode specifier
            if w.startswith("mix"):
                sf -= 1
            # dorian mode on the second note (D in C scale)
            elif w.startswith("dor"):
                sf -= 2
            # phrygian mode on the third note (E in C scale)
            elif w.startswith("phr"):
                sf -= 4
            # lydian mode on the fourth note (F in C scale)
            elif w.startswith("lyd"):
                sf += 1
            # locrian mode on the seventh note (B in C scale)
            elif w.startswith("loc"):
                sf -= 5
            # major and ionian are the same ks
            elif w.startswith("maj"):
                pass
            elif w.startswith("ion"):
                pass
            # aeolian, m, minor are the same ks - sixth note (A in C scale)
            elif w.startswith("aeo"):
                sf -= 3
            elif w.startswith("min"):
                sf -= 3
            elif w.startswith("m"):
                sf -= 3

            # check for trailing clef specifier
            elif w.startswith("clef="):
                if not self.set_clef(w+5):
                    log.error(f"unknown clef specifier: {w}")

            elif self.set_clef(w):
                # (clef specification without "clef=" prefix)
                pass
            # nothing found
            else:
                log.error(f"Unknown token in key specifier: {w}")

        # end of loop over blank-delimted words

        if common.verbose >= 4:
            print(f"Key   <{s}> gives sharpsflats {sf}, type {self.k_type}")


        # copy to struct
        self.sf         = sf
        self.root       = root
        self.root_acc   = root_acc

        return True

    def set_clef(self, s: str) -> bool:
        """
        parse clef specifier and store in struct

        RC: 0 if no clef specifier; 1 if clef identified
        """
        cleflist = {"treble": TREBLE,
                    "treble8": TREBLE8,
                    "treble8up": TREBLE8UP,
                    "bass": BASS,
                    "alto": ALTO,
                    "tenor": TENOR,
                    "soprano": SOPRANO,
                    "mezzosoprano": MEZZOSOPRANO,
                    "baritone": BARITONE,
                    "varbaritone": VARBARITONE,
                    "subbass": SUBBASS,
                    "frenchviolin": FRENCHVIOLIN}

        # get clef name length without octave modifier (+8 etc)
        loc_m = s.index('-')
        loc_p = s.index('+')

        # loop over possible music clefs
        for clef, value in cleflist.items():
            if s == clef:
                self.k_type = value
                # check for octave modifier
                if s[loc_p:].startswith("+8"):
                    self.add_pitch = 7
                elif s[loc_m:].startswith("+8"):
                    self.add_pitch = -7
                elif s[loc_p:].startswith("+0") or s[loc_m:].startswith("-0"):
                    self.add_pitch = 0
                elif s[loc_p:].startswith("+16"):
                    self.add_pitch = +14
                elif s[loc_m:].startswith("-16"):
                    self.add_pitch = -14
                else:
                    log.error(f"unknown octave modifier in clef: {s}")
                return True

        # check for tablature clef
        if self.parse_tab_key(s):
            return True

        return False

    def parse_tab_key(self, string: str) -> int:
        """
        parse "string" for tablature key

        If "string" is a tablature "clef" specification, the corresponding
        clef number is stored in "ktype" and 1 is returned.
        Otherwise 0 is returned.
        """

        if common.notab:
            return 0

        if string == "frenchtab":
            self.k_type = FRENCHTAB
            return True
        elif string == "french5tab":
            self.k_type = FRENCH5TAB
            return True
        elif string == "french4tab":
            self.k_type = FRENCH4TAB
            return True
        elif string == "spanishtab" or string == "guitartab":
            self.k_type = SPANISHTAB
            return True
        elif string == "spanish5tab" or string == "banjo5tab":
            self.k_type = SPANISH5TAB
            return True
        elif string == "spanish4tab" or string == "banjo4tab" or string == "ukuleletab":
            self.k_type = SPANISH4TAB
            return True
        elif string == "italiantab":
            self.k_type = ITALIANTAB
            return True
        elif string == "italian7tab":
            self.k_type = ITALIAN7TAB
            return True
        elif string == "italian8tab":
            self.k_type = ITALIAN8TAB
            return True
        elif string == "italian5tab":
            self.k_type = ITALIAN5TAB
            return True
        elif string == "italian4tab":
            self.k_type = ITALIAN4TAB
            return True
        elif string == "germantab":
            self.k_type = GERMANTAB
            return True

        return False

    def get_halftones(self, transpose: str) -> int:
        """
        figure out how by many halftones to transpose
        In the transposing routines: pitches A..G are coded as with 0..7
        """
        # int pit_old,pit_new,direction,stype,root_new,racc_new,Key.__nht
        # int root_old, racc_old
        # char *q
        # pit_tab associates true pitches 0-11 with letters A-G
        pit_tab = [0, 2, 3, 5, 7, 8, 10]

        if not transpose:
            return 0
        root_new=root_old = self.root
        racc_old = self.root_acc

        # parse specification for target key
        q = 0
        direction = 0

        if transpose[q] == '^':
            direction  = 1
            q += 1
        elif transpose[q] == '_':
            direction=-1
            q += 1

        stype = 1
        if transpose[q] in "ABCDEFG":
            root_new = char_delta(transpose[q], 'A')
            q += 1
            stype=2
        elif transpose[q] in "abcdefg":
            root_new = char_delta(transpose[q], 'a')
            q += 1
            stype=2

        # first case: offset was given directly as numeric argument
        if stype == 1:
            q =  str(Key.__nht)
            if direction < 0:
                Key.__nht = -Key.__nht
            if Key.__nht == 0:
                if direction < 0:
                    Key.__nht=-12
                if direction > 0:
                    Key.__nht=+12
            return Key.__nht

        # second case: root of target key was specified explicitly
        racc_new = 0
        if transpose[q] == 'b':
            racc_new = A_FT
            q += 1
        elif transpose[q] == '#':
            racc_new = A_SH
            q += 1
        elif transpose[q] != '\0':
            log.critical(f"expecting accidental in transpose spec: {transpose}")

        # get pitch as number from 0-11 for root of old key
        pit_old = pit_tab[root_old]
        if racc_old == A_FT:
            pit_old -= 1
        if racc_old == A_SH:
            pit_old += 1
        if pit_old < 0:
            pit_old+=12
        if pit_old > 11:
            pit_old-=12

        # get pitch as number from 0-11 for root of new key
        pit_new = pit_tab[root_new]
        if racc_new == A_FT:
            pit_new -= 1
        if racc_new == A_SH:
            pit_new += 1
        if pit_new < 0:
            pit_new+=12
        if pit_new > 11:
            pit_new-=12

        # number of halftones is difference
        Key.__nht = pit_new-pit_old
        if direction == 0:
            if Key.__nht > 6:
                Key.__nht -= 12
            if Key.__nht < -5:
                Key.__nht += 12
        if direction > 0 and Key.__nht <= 0:
            Key.__nht += 12
        if direction < 0 and Key.__nht >= 0:
            Key.__nht -= 12

        return Key.__nht


#
# # ----- shift_key: make new key by shifting Key.__nht halftones ---
# void shift_key (int sf_old, int Key.__nht, int *sfnew, int *addt)
# {
#   int sf_new,r_old,r_new,add_t,  dh,dr
#   int skey_tab[] = {2,6,3,0,4,1,5,2}
#   int fkey_tab[] = {2,5,1,4,0,3,6,2}
#   char root_tab[]={'A','B','C','D','E','F','G'}
#
#   # get sf_new by adding 7 for each halftone, then reduce mod 12
#   sf_new=sf_old+Key.__nht*7
#   sf_new=(sf_new+240)%12
#   if sf_new>=6) sf_new=sf_new-12
#
#   # get old and new root in ionian mode, shift is difference
#   r_old=2
#   if sf_old>0) r_old=skey_tab[sf_old]
#   if sf_old<0) r_old=fkey_tab[-sf_old]
#   r_new=2
#   if sf_new>0) r_new=skey_tab[sf_new]
#   if sf_new<0) r_new=fkey_tab[-sf_new]
#   add_t=r_new-r_old
#
#   # fix up add_t to get same "decade" as Key.__nht
#   dh=(Key.__nht+120)/12; dh=dh-10
#   dr=(add_t+70)/7; dr=dr-10
#   add_t=add_t+7*(dh-dr)
#
#   if verbose>=8)
#     printf ("shift_key: sf_old=%d new %d   root: old %c new %c  shift by %d\n",
#             sf_old, sf_new, root_tab[r_old], root_tab[r_new], add_t)
#
#   *sfnew=sf_new
#   *addt=add_t
#
# }
#
#
# # ----- set_transtab: setup for transposition by Key.__nht halftones ---
# void set_transtab (int Key.__nht, struct KEYSTR *key)
# {
#   int a,b,sf_old,sf_new,add_t,i,j,acc_old,acc_new,root_old,root_acc
#   # for each note A..G, these tables tell how many sharps (resp. flats)
#      the keysig must have to get the accidental on this note. Phew.
#   int sh_tab[] = {5,7,2,4,6,1,3}
#   int fl_tab[] = {3,1,6,4,2,7,5}
#   # tables for pretty printout only
#   char root_tab[]={'A','B','C','D','E','F','G'}
#   char acc_tab[][3] ={"bb","b ","  ","# ","x "}
#   char c1[6],c2[6],c3[6]
#
#   # nop if no transposition is wanted
#   if Key.__nht == 0) {
#     key.add_transp=0
#     for (i=0;i<7;i += 1) key.add_acc[i]=0
#     return
#   }
#
#   # get new sharps_flats and shift of numeric pitch; copy to key
#   sf_old   = key.sf
#   root_old = key.root
#   root_acc = key.root_acc
#   shift_key (sf_old, Key.__nht, &sf_new, &add_t)
#   key.sf = sf_new
#   key.add_transp = add_t
#
#   # set up table for conversion of accidentals
#   for (i=0;i<7;i += 1) {
#     j=i+add_t
#     j=(j+70)%7
#     acc_old=0
#     if  sf_old >= sh_tab[i]) acc_old=1
#     if -sf_old >= fl_tab[i]) acc_old=-1
#     acc_new=0
#     if  sf_new >= sh_tab[j]) acc_new=1
#     if -sf_new >= fl_tab[j]) acc_new=-1
#     key.add_acc[i]=acc_new-acc_old
#   }
#
#   # printout keysig change
#   if verbose>=3) {
#     i=root_old
#     j=i+add_t
#     j=(j+70)%7
#     acc_old=0
#     if  sf_old >= sh_tab[i]) acc_old=1
#     if -sf_old >= fl_tab[i]) acc_old=-1
#     acc_new=0
#     if  sf_new >= sh_tab[j]) acc_new=1
#     if -sf_new >= fl_tab[j]) acc_new=-1
#     strcpy(c3,"s"); if Key.__nht == 1 || Key.__nht == -1) strcpy(c3,"")
#     strcpy(c1,""); strcpy(c2,"")
#     if acc_old == -1) strcpy(c1,"b"); if acc_old == 1) strcpy(c1,"#")
#     if acc_new == -1) strcpy(c2,"b"); if acc_new == 1) strcpy(c2,"#")
#     printf ("Transpose root from %c%s to %c%s (shift by %d halftone%s)\n",
#             root_tab[i],c1,root_tab[j],c2,Key.__nht,c3)
#   }
#
#   # printout full table of transformations
#   if verbose>=4) {
#     printf ("old & new keysig    conversions\n")
#     for (i=0;i<7;i += 1) {
#       j=i+add_t
#       j=(j+70)%7
#       acc_old=0
#       if  sf_old >= sh_tab[i]) acc_old=1
#       if -sf_old >= fl_tab[i]) acc_old=-1
#       acc_new=0
#       if  sf_new >= sh_tab[j]) acc_new=1
#       if -sf_new >= fl_tab[j]) acc_new=-1
#       printf("%c%s. %c%s           ", root_tab[i],acc_tab[acc_old+2],
#              root_tab[j],acc_tab[acc_new+2])
#       for (a=-1;a<=1;a += 1) {
#         b=a+key.add_acc[i]
#         printf ("%c%s. %c%s  ", root_tab[i],acc_tab[a+2],
#                 root_tab[j],acc_tab[b+2])
#       }
#       printf ("\n")
#     }
#   }
#
# }
#
# # ----- do_transpose: transpose numeric pitch and accidental ---
# void do_transpose (struct KEYSTR key, int *pitch, int *acc)
# {
#   int pitch_old,pitch_new,sf_old,sf_new,acc_old,acc_new,i,j
#
#   pitch_old = *pitch
#   acc_old   = *acc
#   acc_new   = acc_old
#   sf_old    = key.sf
#   pitch_new=pitch_old+key.add_transp
#   i=(pitch_old+70)%7
#   j=(pitch_new+70)%7
#
#   if acc_old) {
#     if acc_old == A_DF) sf_old=-2
#     if acc_old == A_FT) sf_old=-1
#     if acc_old == A_NT) sf_old=0 
#     if acc_old == A_SH) sf_old=1
#     if acc_old == A_DS) sf_old=2
#     sf_new=sf_old+key.add_acc[i]
#     if sf_new == -2) acc_new=A_DF
#     if sf_new == -1) acc_new=A_FT
#     if sf_new ==  0) acc_new=A_NT
#     if sf_new ==  1) acc_new=A_SH
#     if sf_new ==  2) acc_new=A_DS
#   }
#   else {
#     acc_new=0
#   }
#   *pitch = pitch_new
#   *acc   = acc_new
# }
#
#
# # ----- gch_transpose: transpose guitar chord string in gch ---
# void gch_transpose (string* gch, struct KEYSTR key)
# {
#   char *q,*r
#   char* gchtrans
#   int root_old,root_new,sf_old,sf_new,ok
#   char root_tab[]={'A','B','C','D','E','F','G'}
#   char root_tub[]={'a','b','c','d','e','f','g'}
#
#   if !transposegchords || (halftones == 0)) return
#
#   q = (char*)gch.c_str()
#   gchtrans = (char*)alloca(sizeof(char)*gch.length())
#   r = gchtrans
#
#   for (;;) {
#     while (*q == ' ' || *q == '(') { *r=*q; q += 1; r += 1; }
#     if *q == '\0') break
#     ok=0
#     if strchr("ABCDEFG",*q)) {
#       root_old=*q-'A'; q += 1; ok=1
#     } elif strchr("abcdefg",*q)) {
#       root_old=*q-'a'; q += 1; ok=2
#     } else {
#       root_old=key.root
#     }
#
#     if ok) {
#       sf_old=0
#       if *q == 'b') { sf_old=-1; q += 1; }
#       if *q == '#') { sf_old= 1; q += 1; }
#       root_new=root_old+key.add_transp
#       root_new=(root_new+28)%7
#       sf_new=sf_old+key.add_acc[root_old]
#       if ok == 1) { *r=root_tab[root_new]; r += 1; }
#       if ok == 2) { *r=root_tub[root_new]; r += 1; }
#       if sf_new == -1) { *r='b'; r += 1; }
#       if sf_new ==  1) { *r='#'; r += 1; }
#     }
#
#     while (*q!=' ' and *q!='/' and *q!='\0') {*r=*q; q += 1; r += 1; }
#     if *q == '/') {*r=*q; q += 1; r += 1; }
#
#   }
#
#   *r='\0'
#   #|   printf("tr_ch: <%s>  <%s>\n", gch, str);   |
#
#   *gch = gchtrans
# }
#
#
# # ----- set_keysig: interpret keysig string, store in struct ----
# # This part was adapted from abc2mtex by Chris Walshaw
# # updated 03 Oct 1997 Wil Macaulay - support all modes
# # Returns 1 if key was actually specified, because then we want
#      to transpose. Returns zero if this is just a clef change.
# int set_keysig(char *s, struct KEYSTR *ks, int init)
# {
#     int c,sf,j,ok
#     char w[81]
#     int root,root_acc
#
#     # maybe initialize with key C (used for K field in header)
#     if init) {
#         ks->sf                 = 0
#         ks->ktype            = TREBLE
#         ks->add_pitch    = 0
#         ks->root             = 2
#         ks->root_acc     = A_NT
#     }
#
#     # check for clef specification with no other information
#     if !strncmp(s,"clef=",5) and set_clef(s+5,ks)) return 0
#     if set_clef(s,ks)) return 0
#
#     # check for key specifier
#     c=0
#     bagpipe=0
#     switch (s[c]) {
#     case 'F':
#         sf = -1; root=5
#         break
#     case 'C':
#         sf = 0; root=2
#         break
#     case 'G':
#         sf = 1; root=6
#         break
#     case 'D':
#         sf = 2; root=3
#         break
#     case 'A':
#         sf = 3; root=0
#         break
#     case 'E':
#         sf = 4; root=4
#         break
#     case 'B':
#         sf = 5; root=1
#         break
#     case 'H':
#         bagpipe=1
#         c += 1
#         if s[c] == 'P') {
#                 sf=0
#                 root=2
#         } elif s[c] == 'p') {
#                 sf=2
#                 root=3
#         } else {
#                 sf=0
#                 root=2
#                 std::cerr << "unknown bagpipe-like key: " << s << std::endl
#         }
#         break
#     default:
#         std::cerr << "Using C because key not recognised: " <<    s << std::endl
#         sf = 0
#         root=2
#     }
#     c += 1
#
#     root_acc=A_NT
#     if s[c] == '#') {
#         sf += 7
#         c += 1
#         root_acc=A_SH
#     } elif s[c] == 'b') {
#         sf -= 7
#         c += 1
#         root_acc=A_FT
#     }
#
#     # loop over blank-delimited words: get the next token in lower case
#     for (;;) {
#         while (isspace(s[c])) c += 1
#         if s[c] == '\0') break
#
#         j=0
#         while (!isspace(s[c]) and (s[c]!='\0')) { w[j]=tolower(s[c]); c += 1; j += 1; }
#         w[j]='\0'
#
#         # now identify this word
#
#         # first check for mode specifier
#         if ((strncmp(w,"mix",3)) == 0) {
#             sf -= 1
#             ok = 1
#             # dorian mode on the second note (D in C scale)
#         } elif ((strncmp(w,"dor",3)) == 0) {
#             sf -= 2
#             ok = 1
#             # phrygian mode on the third note (E in C scale)
#         } elif ((strncmp(w,"phr",3)) == 0) {
#             sf -= 4
#             ok = 1
#             # lydian mode on the fourth note (F in C scale)
#         } elif ((strncmp(w,"lyd",3)) == 0) {
#             sf += 1
#             ok = 1
#             # locrian mode on the seventh note (B in C scale)
#         } elif ((strncmp(w,"loc",3)) == 0) {
#             sf -= 5
#             ok = 1
#             # major and ionian are the same ks
#         } elif ((strncmp(w,"maj",3)) == 0) {
#             ok = 1
#         } elif ((strncmp(w,"ion",3)) == 0) {
#             ok = 1
#             # aeolian, m, minor are the same ks - sixth note (A in C scale)
#         } elif ((strncmp(w,"aeo",3)) == 0) {
#             sf -= 3
#             ok = 1
#         } elif ((strncmp(w,"min",3)) == 0) {
#             sf -= 3
#             ok = 1
#         } elif ((strcmp(w,"m")) == 0) {
#             sf -= 3
#             ok = 1
#         }
#
#         # check for trailing clef specifier
#         elif !strncmp(w,"clef=",5)) {
#             if !set_clef(w+5,ks)) {
#                 std::cerr << "unknown clef specifier: " << w << std::endl
#             }
#         }
#         elif set_clef(w,ks)) {
#             # (clef specification without "clef=" prefix)
#         }
#
#         # nothing found
#         else std::cerr << "Unknown token in key specifier: " << w << std::endl
#
#     }    # end of loop over blank-delimted words
#
#     if verbose>=4) printf ("Key     <%s> gives sharpsflats %d, type %d\n",
#                                                     s, sf, ks->ktype)
#
#     # copy to struct
#     ks->sf                 = sf
#     ks->root             = root
#     ks->root_acc     = root_acc
#
#     return 1
#
# }
#
# # ----- set_clef: parse clef specifier and store in struct ---
# # RC: 0 if no clef specifier; 1 if clef identified
# int set_clef(char* s, struct KEYSTR *ks)
# {
#     struct {    # zero terminated list of music clefs
#         const char* name; int value
#     } cleflist[] = {
#         {"treble", TREBLE},
#         {"treble8", TREBLE8},
#         {"treble8up", TREBLE8UP},
#         {"bass", BASS},
#         {"alto", ALTO},
#         {"tenor", TENOR},
#         {"soprano", SOPRANO},
#         {"mezzosoprano", MEZZOSOPRANO},
#         {"baritone", BARITONE},
#         {"varbaritone", VARBARITONE},
#         {"subbass", SUBBASS},
#         {"frenchviolin", FRENCHVIOLIN},
#         {0, 0}
#     }
#     int i, len
#
#     # get clef name length without octave modifier (+8 etc)
#     len = strcspn(s,"+-")
#
#     # loop over possible music clefs
#     for (i=0; cleflist[i].name; i += 1) {
#         if !strncmp(s,cleflist[i].name,len)) {
#             ks->ktype=cleflist[i].value
#             # check for octave modifier
#             if s[len]) {
#                 char* mod=&(s[len])
#                 if !strcmp(mod,"+8"))
#                     ks->add_pitch=7
#                 elif !strcmp(mod,"-8"))
#                     ks->add_pitch=-7
#                 elif !strcmp(mod,"+0") || !strcmp(mod,"-0"))
#                     ks->add_pitch=0
#                 elif !strcmp(mod,"+16"))
#                     ks->add_pitch=+14
#                 elif !strcmp(mod,"-16"))
#                     ks->add_pitch=-14
#                 else
#                     std::cerr << "unknown octave modifier in clef: " << s << std::endl
#             }
#             return 1
#         }
#     }
#
#     # check for tablature clef
#     if parse_tab_key(s,&ks->ktype)) return 1
#
#     return 0
# }
#
# # ----- get_halftones: figure out how by many halftones to transpose ---
# #    In the transposing routines: pitches A..G are coded as with 0..7
# int get_halftones (struct KEYSTR key, char *transpose)
# {
#     int pit_old,pit_new,direction,stype,root_new,racc_new,Key.__nht
#     int root_old, racc_old
#     char *q
#     # pit_tab associates true pitches 0-11 with letters A-G
#     int pit_tab[] = {0,2,3,5,7,8,10}
#
#     if strlen(transpose) == 0) return 0
#     root_new=root_old=key.root
#     racc_old=key.root_acc
#
#     # parse specification for target key
#     q=transpose
#     direction=0
#
#     if *q == '^') {
#         direction=1; q += 1
#     } elif *q == '_') {
#         direction=-1; q += 1
#     }
#     stype=1
#     if strchr("ABCDEFG",*q)) {
#         root_new=*q-'A'; q += 1; stype=2
#     } elif strchr("abcdefg",*q)) {
#         root_new=*q-'a'; q += 1;    stype=2
#     }
#
#     # first case: offset was given directly as numeric argument
#     if stype == 1) {
#         sscanf(q,"%d", &Key.__nht)
#         if direction<0) Key.__nht=-Key.__nht
#         if Key.__nht == 0) {
#             if direction<0) Key.__nht=-12
#             if direction>0) Key.__nht=+12
#         }
#         return Key.__nht
#     }
#
#     # second case: root of target key was specified explicitly
#     racc_new=0
#     if *q == 'b') {
#         racc_new=A_FT; q += 1
#     } elif *q == '#') {
#         racc_new=A_SH; q += 1
#     } elif *q!='\0')
#         std::cerr << "expecting accidental in transpose spec: " << transpose << std::endl
#
#     # get pitch as number from 0-11 for root of old key
#     pit_old=pit_tab[root_old]
#     if racc_old == A_FT) pit_old -= 1
#     if racc_old == A_SH) pit_old += 1
#     if pit_old<0)    pit_old+=12
#     if pit_old>11) pit_old-=12
#
#     # get pitch as number from 0-11 for root of new key
#     pit_new=pit_tab[root_new]
#     if racc_new == A_FT) pit_new -= 1
#     if racc_new == A_SH) pit_new += 1
#     if pit_new<0)    pit_new+=12
#     if pit_new>11) pit_new-=12
#
#     # number of halftones is difference
#     Key.__nht=pit_new-pit_old
#     if direction == 0) {
#         if Key.__nht>6)    Key.__nht-=12
#         if Key.__nht<-5) Key.__nht+=12
#     }
#     if direction>0 and Key.__nht<=0) Key.__nht+=12
#     if direction<0 and Key.__nht>=0) Key.__nht-=12
#
#     return Key.__nht
#
# }
#
#
#
# # ----- shift_key: make new key by shifting Key.__nht halftones ---
# void shift_key (int sf_old, int Key.__nht, int *sfnew, int *addt)
# {
#     int sf_new,r_old,r_new,add_t,    dh,dr
#     int skey_tab[] = {2,6,3,0,4,1,5,2}
#     int fkey_tab[] = {2,5,1,4,0,3,6,2}
#     char root_tab[]={'A','B','C','D','E','F','G'}
#
#     # get sf_new by adding 7 for each halftone, then reduce mod 12
#     sf_new=sf_old+Key.__nht*7
#     sf_new=(sf_new+240)%12
#     if sf_new>=6) sf_new=sf_new-12
#
#     # get old and new root in ionian mode, shift is difference
#     r_old=2
#     if sf_old>0) r_old=skey_tab[sf_old]
#     if sf_old<0) r_old=fkey_tab[-sf_old]
#     r_new=2
#     if sf_new>0) r_new=skey_tab[sf_new]
#     if sf_new<0) r_new=fkey_tab[-sf_new]
#     add_t=r_new-r_old
#
#     # fix up add_t to get same "decade" as Key.__nht
#     dh=(Key.__nht+120)/12; dh=dh-10
#     dr=(add_t+70)/7; dr=dr-10
#     add_t=add_t+7*(dh-dr)
#
#     if verbose>=8)
#         printf ("shift_key: sf_old=%d new %d     root: old %c new %c    shift by %d\n",
#                         sf_old, sf_new, root_tab[r_old], root_tab[r_new], add_t)
#
#     *sfnew=sf_new
#     *addt=add_t
#
# }
#
#
# # ----- set_transtab: setup for transposition by Key.__nht halftones ---
# void set_transtab (int Key.__nht, struct KEYSTR *key)
# {
#     int a,b,sf_old,sf_new,add_t,i,j,acc_old,acc_new,root_old,root_acc
#     # for each note A..G, these tables tell how many sharps (resp. flats)
#          the keysig must have to get the accidental on this note. Phew.
#     int sh_tab[] = {5,7,2,4,6,1,3}
#     int fl_tab[] = {3,1,6,4,2,7,5}
#     # tables for pretty printout only
#     char root_tab[]={'A','B','C','D','E','F','G'}
#     char acc_tab[][3] ={"bb","b ","    ","# ","x "}
#     char c1[6],c2[6],c3[6]
#
#     # nop if no transposition is wanted
#     if Key.__nht == 0) {
#         key->add_transp=0
#         for (i=0;i<7;i += 1) key->add_acc[i]=0
#         return
#     }
#
#     # get new sharps_flats and shift of numeric pitch; copy to key
#     sf_old     = key->sf
#     root_old = key->root
#     root_acc = key->root_acc
#     shift_key (sf_old, Key.__nht, &sf_new, &add_t)
#     key->sf = sf_new
#     key->add_transp = add_t
#
#     # set up table for conversion of accidentals
#     for (i=0;i<7;i += 1) {
#         j=i+add_t
#         j=(j+70)%7
#         acc_old=0
#         if  sf_old >= sh_tab[i]) acc_old=1
#         if -sf_old >= fl_tab[i]) acc_old=-1
#         acc_new=0
#         if  sf_new >= sh_tab[j]) acc_new=1
#         if -sf_new >= fl_tab[j]) acc_new=-1
#         key->add_acc[i]=acc_new-acc_old
#     }
#
#     # printout keysig change
#     if verbose>=3) {
#         i=root_old
#         j=i+add_t
#         j=(j+70)%7
#         acc_old=0
#         if  sf_old >= sh_tab[i]) acc_old=1
#         if -sf_old >= fl_tab[i]) acc_old=-1
#         acc_new=0
#         if  sf_new >= sh_tab[j]) acc_new=1
#         if -sf_new >= fl_tab[j]) acc_new=-1
#         strcpy(c3,"s"); if Key.__nht == 1 || Key.__nht == -1) strcpy(c3,"")
#         strcpy(c1,""); strcpy(c2,"")
#         if acc_old == -1) strcpy(c1,"b"); if acc_old == 1) strcpy(c1,"#")
#         if acc_new == -1) strcpy(c2,"b"); if acc_new == 1) strcpy(c2,"#")
#         printf ("Transpose root from %c%s to %c%s (shift by %d halftone%s)\n",
#                         root_tab[i],c1,root_tab[j],c2,Key.__nht,c3)
#     }
#
#     # printout full table of transformations
#     if verbose>=4) {
#         printf ("old & new keysig        conversions\n")
#         for (i=0;i<7;i += 1) {
#             j=i+add_t
#             j=(j+70)%7
#             acc_old=0
#             if  sf_old >= sh_tab[i]) acc_old=1
#             if -sf_old >= fl_tab[i]) acc_old=-1
#             acc_new=0
#             if  sf_new >= sh_tab[j]) acc_new=1
#             if -sf_new >= fl_tab[j]) acc_new=-1
#             printf("%c%s-> %c%s                     ", root_tab[i],acc_tab[acc_old+2],
#                          root_tab[j],acc_tab[acc_new+2])
#             for (a=-1;a<=1;a += 1) {
#                 b=a+key->add_acc[i]
#                 printf ("%c%s-> %c%s    ", root_tab[i],acc_tab[a+2],
#                                 root_tab[j],acc_tab[b+2])
#             }
#             printf ("\n")
#         }
#     }
#
# }
#
# # ----- do_transpose: transpose numeric pitch and accidental ---
# void do_transpose (struct KEYSTR key, int *pitch, int *acc)
# {
#     int pitch_old,pitch_new,sf_old,sf_new,acc_old,acc_new,i,j
#
#     pitch_old = *pitch
#     acc_old     = *acc
#     acc_new     = acc_old
#     sf_old        = key.sf
#     pitch_new=pitch_old+key.add_transp
#     i=(pitch_old+70)%7
#     j=(pitch_new+70)%7
#
#     if acc_old) {
#         if acc_old == A_DF) sf_old=-2
#         if acc_old == A_FT) sf_old=-1
#         if acc_old == A_NT) sf_old=0 
#         if acc_old == A_SH) sf_old=1
#         if acc_old == A_DS) sf_old=2
#         sf_new=sf_old+key.add_acc[i]
#         if sf_new == -2) acc_new=A_DF
#         if sf_new == -1) acc_new=A_FT
#         if sf_new ==  0) acc_new=A_NT
#         if sf_new ==  1) acc_new=A_SH
#         if sf_new ==  2) acc_new=A_DS
#     }
#     else {
#         acc_new=0
#     }
#     *pitch = pitch_new
#     *acc     = acc_new
# }
#
#
# # ----- gch_transpose: transpose guitar chord string in gch ---
# void gch_transpose (string* gch, struct KEYSTR key)
# {
#     char *q,*r
#     char* gchtrans
#     int root_old,root_new,sf_old,sf_new,ok
#     char root_tab[]={'A','B','C','D','E','F','G'}
#     char root_tub[]={'a','b','c','d','e','f','g'}
#
#     if !transposegchords || (halftones == 0)) return
#
#     q = (char*)gch->c_str()
#     gchtrans = (char*)alloca(sizeof(char)*gch->length())
#     r = gchtrans
#
#     for (;;) {
#         while (*q == ' ' || *q == '(') { *r=*q; q += 1; r += 1; }
#         if *q == '\0') break
#         ok=0
#         if strchr("ABCDEFG",*q)) {
#             root_old=*q-'A'; q += 1; ok=1
#         } elif strchr("abcdefg",*q)) {
#             root_old=*q-'a'; q += 1; ok=2
#         } else {
#             root_old=key.root
#         }
#
#         if ok) {
#             sf_old=0
#             if *q == 'b') { sf_old=-1; q += 1; }
#             if *q == '#') { sf_old= 1; q += 1; }
#             root_new=root_old+key.add_transp
#             root_new=(root_new+28)%7
#             sf_new=sf_old+key.add_acc[root_old]
#             if ok == 1) { *r=root_tab[root_new]; r += 1; }
#             if ok == 2) { *r=root_tub[root_new]; r += 1; }
#             if sf_new == -1) { *r='b'; r += 1; }
#             if sf_new ==  1) { *r='#'; r += 1; }
#         }
#
#         while (*q!=' ' and *q!='/' and *q!='\0') {*r=*q; q += 1; r += 1; }
#         if *q == '/') {*r=*q; q += 1; r += 1; }
#
#     }
#
#     *r='\0'
#     #|     printf("tr_ch: <%s>    <%s>\n", gch, str);     |
#
#     *gch = gchtrans
# }


def init_parse_params():
    """
    initialize variables for parsing

    :return:
    """
    common.slur = 0
    common.nwpool = 0
    common.nwline = 0
    common.ntinext = 0

    # for continuation after output: reset nsym, switch to first v
    for voice in common.voices:
        voice.sym = list()
        # this would suppress tie/repeat carryover from previous page:
        voice.insert_btype = 0
        voice.end_slur = 0

    symb.ivc = 0
    symb.word = False
    symb.carryover = False
    symb.last_note = symb.last_real_note = -1
    symb.pplet = symb.qplet = symb.rplet = 0
    symb.num_ending = 0
    symb.mes1 = symb.mes2 = 0
    field.prep_gchlst = list()
    field.prep_deco = list()


def add_text(s: str, t_type: int) -> None:
    if not common.do_output:
        return
    if len(common.text) >= NTEXT:
        log.warning(f"No more room for text line < {s}")
        return
    common.text.append(s)
    common.text_type.append(t_type)



# # ----- get_default_info: set info to default, except xref field ---
# void get_default_info (void)
# {
#     char savestr[STRLINFO]
#
#     strcpy (savestr, info.xref)
#     info=default_info
#     strcpy (info.xref, savestr)
#
# }
#
# # ----- is_info_field: identify any type of info field ----
# int is_info_field (char *str)
# {
#     if strlen(str)<2) return 0
#     if str[1]!=':')     return 0
#     if str[0] == '|')     return 0;     # |: at start of music line
#     return 1
# }
#
# # ----- is_end_line: identify eof -----
# int is_end_line (const char *str)
# {
#     if strlen(str)<3) return 0
#     if str[0] == 'E' and str[1] == 'N' and str[2] == 'D') return 1
#     return 0
# }


def is_pseudocomment(ps: str) -> bool:
    return len(str) > 2 and ps.startswith('%%')


def is_comment(comment: str) -> bool:
    return len(comment) > 1 and (comment[0] == '%' or comment[0] == '\\')


def is_cmdline(cmd: str) -> bool:
    """ command line """
    return len(str) > 2 and cmd[0] == '%' and cmd[1] == '!'


# # ----- find_voice -----
# int find_voice (char *vid, int *newv)
# {
#     int i
#
#     for (i=0;i<nvoice;i += 1)
#         if !strcmp(vid,voice[i].id)) {
#             *newv=0
#             return i
#         }
#
#     i=nvoice
#     if i>=maxVc) {
#         realloc_structs(maxSyms,maxVc+allocVc)
#     }
#
#     strcpy(voice[i].id,        vid)
#     strcpy(voice[i].name,    "")
#     strcpy(voice[i].sname, "")
#     voice[i].meter = default_meter
#     voice[i].key     = default_key
#     voice[i].stems        = 0
#     voice[i].staves = voice[i].brace = voice[i].bracket = 0
#     voice[i].do_gch     = 1
#     voice[i].sep            = 0.0
#     voice[i].nsym         = 0
#     voice[i].select     = 1
#     // new systems must start with invisible bar as anchor for barnumbers
#     //voice[i].insert_btype = voice[i].insert_num = 0
#     //voice[i].insert_bnum = 0
#     voice[i].insert_btype = B_INVIS
#     voice[i].insert_num = 0
#     voice[i].insert_bnum = barinit
#     voice[i].insert_space = 0.0
#     voice[i].end_slur = 0
#     voice[i].timeinit = 0.0
#     strcpy(voice[i].insert_text, "")
#     nvoice += 1
#     if verbose>5)
#         printf ("Make new voice %d with id \"%s\"\n", i,voice[i].id)
#     *newv=1
#     return i
#
# }
#
# # ----- switch_voice: read spec for a voice, return voice number -----
# int switch_voice (std::string str)
# {
#         int j,np,newv
#         const char *r
#         char *q
#         char t1[STRLINFO],t2[STRLINFO]
#
#         if !do_this_tune) return 0
#
#         j=-1
#
#         # start loop over voice options: parse t1=t2
#         r = str.c_str()
#         np=newv=0
#         for (;;) {
#                 while (isspace(*r)) r += 1
#                 if *r == '\0') break
#                 strcpy(t1,"")
#                 strcpy(t2,"")
#                 q=t1
#                 while (!isspace(*r) and *r!='\0' and *r!='=') { *q=*r; r += 1; q += 1; }
#                 *q='\0'
#                 if *r == '=') {
#                         r += 1
#                         q=t2
#                         if *r == '"') {
#                                 r += 1
#                                 while (*r!='"' and *r!='\0') { *q=*r; r += 1; q += 1; }
#                                 if *r == '"') r += 1
#                         }
#                         else {
#                                 while (!isspace(*r) and *r!='\0') { *q=*r; r += 1; q += 1; }
#                         }
#                         *q='\0'
#                 }
#                 np += 1
#
#                 # interpret the parsed option. First case is identifier.
#                 if np == 1) {
#                         j=find_voice (t1,&newv)
#                 }
#
#                 else {                                                 # interpret option
#                         if j<0) bug("j invalid in switch_voice", true)
#                         if            (!strcmp(t1,"name")        || !strcmp(t1,"nm"))
#                                 strcpy(voice[j].name,    t2)
#
#                         elif !strcmp(t1,"sname")     || !strcmp(t1,"snm"))
#                                 strcpy(voice[j].sname, t2)
#
#                         elif !strcmp(t1,"staves")    || !strcmp(t1,"stv"))
#                                 voice[j].staves    = atoi(t2)
#
#                         elif !strcmp(t1,"brace")     || !strcmp(t1,"brc"))
#                                 voice[j].brace     = atoi(t2)
#
#                         elif !strcmp(t1,"bracket") || !strcmp(t1,"brk"))
#                                 voice[j].bracket = atoi(t2)
#
#                         elif !strcmp(t1,"gchords") || !strcmp(t1,"gch"))
#                                 g_logv (str.c_str(),t2,&voice[j].do_gch)
#
#                         # for sspace: add 2000 as flag if not incremental
#                         elif !strcmp(t1,"space")     || !strcmp(t1,"spc")) {
#                                 g_unum (str.c_str(),t2,&voice[j].sep)
#                                 if t2[0]!='+' and t2[0]!='-') voice[j].sep += 2000.0
#                         }
#
#                         elif !strcmp(t1,"clef")        || !strcmp(t1,"cl")) {
#                                 if !set_clef(t2,&voice[j].key))
#                                         std::cerr << "Unknown clef in voice spec: " << t2 << std::endl
#                         }
#                         elif !strcmp(t1,"stems") || !strcmp(t1,"stm")) {
#                                 if            (!strcmp(t2,"up"))        voice[j].stems=1
#                                 elif !strcmp(t2,"down"))    voice[j].stems=-1
#                                 elif !strcmp(t2,"free"))    voice[j].stems=0
#                                 else std::cerr << "Unknown stem setting in voice spec: " << t2 << std::endl
#                         }
#                         elif !strcmp(t1,"octave")) {
#                                 ; # ignore abc2midi parameter for compatibility
#                         }
#                         else std::cerr << "Unknown option in voice spec: " << t1 << std::endl
#                 }
#
#         }
#
#         # if new voice was initialized, save settings im meter0, key0
#         if newv) {
#                 voice[j].meter0 = voice[j].meter
#                 voice[j].key0     = voice[j].key
#         }
#
#         if verbose>7)
#                 printf ("Switch to voice %d    <%s> <%s> <%s>    clef=%d\n",
#                                 j,voice[j].id,voice[j].name,voice[j].sname,
#                                 voice[j].key.ktype)
#
#         nsym0=voice[j].nsym;    # set nsym0 to decide about eoln later.. ugly
#         return j
#
# }
#


def info_field(s: str) -> bool:
    """ identify info line, store in proper place
    switch within_block: either goes to default_info or info.
    Only xref ALWAYS goes to info.
    """
    # char s[STRLINFO]
    # struct ISTRUCT *inf
    # int i

    if not common.within_block:
        inf = info.Field()

    if info.is_field(s):
        return False

    index = s.index('%')
    s = s[2:index]

    if s.startswith('X'):
        info.xref(s)
    elif s.startswith('A'):
        info.area(s)
    elif s.startswith('B'):
        info.book(s)
    elif s.startswith('C'):
        info.composer(s)
    elif s.startswith('D'):
        info.discography(s, appendable=True)
    elif s.startswith('F'):
        info.file_name(s)
    elif s.startswith('G'):
        info.group(s)
    elif s.startswith('H'):
        info.history(s, appendable=True)
    elif s.startswith('W'):
        info.words(s, appendable=True)
    elif s.startswith('K'):
        info.key_clef(s)
    elif s.startswith('L'):
        info.default_note_length(s)
    elif s.startswith('M'):
        info.meter(s)
    elif s.startswith('N'):
        info.notes(s, appendable=True)
    elif s.startswith('O'):
        info.origin(s)
    elif s.startswith('R'):
        info.rhythm(s)
    elif s.startswith('P'):
        info.parts(s)
    elif s.startswith( 'S'):
        info.source(s)
    elif s.startswith( 'T'):
        info.titles(s)
    elif s.startswith( 'V'):
        info.voice(s)
    elif s.startswith( 'Z'):
        info.transciptoin_note(s)
    elif s.startswith( 'Q'):
        info.tempo(s)
    elif s.startswith( 'E'):
        info.layout_parameter(s)
    else:
        return False
    return True






# # ----- append_key_change: append change of key to sym list ------
# void append_key_change(struct KEYSTR oldkey, struct KEYSTR newkey)
# {
#         int n1,n2,t1,t2,kk
#
#         n1=oldkey.sf
#         t1=A_SH
#         if n1<0) { n1=-n1; t1=A_FT; }
#         n2=newkey.sf
#         t2=A_SH
#
#         if newkey.ktype != oldkey.ktype) {            # clef change
#                 kk=add_sym(CLEF)
#                 voices[ivc].syms[kk].u=newkey.ktype
#                 voices[ivc].syms[kk].v=1
#         }
#
#         if n2<0) { n2=-n2; t2=A_FT; }
#         if t1 == t2) {                            # here if old and new have same type
#                 if n2>n1) {                                 # more new symbols ..
#                         kk=add_sym(KEYSIG);                # draw all of them
#                         voices[ivc].syms[kk].u=1
#                         voices[ivc].syms[kk].v=n2
#                         voices[ivc].syms[kk].w=100
#                         voices[ivc].syms[kk].t=t1
#                 }
#                 elif n2<n1) {                        # less new symbols ..
#                         kk=add_sym(KEYSIG);                    # draw all new symbols and neutrals
#                         voices[ivc].syms[kk].u=1
#                         voices[ivc].syms[kk].v=n1
#                         voices[ivc].syms[kk].w=n2+1
#                         voices[ivc].syms[kk].t=t2
#                 }
#                 else return
#         }
#         else {                                         # here for change s->f or f->s
#                 kk=add_sym(KEYSIG);                    # neutralize all old symbols
#                 voices[ivc].syms[kk].u=1
#                 voices[ivc].syms[kk].v=n1
#                 voices[ivc].syms[kk].w=1
#                 voices[ivc].syms[kk].t=t1
#                 kk=add_sym(KEYSIG);                    # add all new symbols
#                 voices[ivc].syms[kk].u=1
#                 voices[ivc].syms[kk].v=n2
#                 voices[ivc].syms[kk].w=100
#                 voices[ivc].syms[kk].t=t2
#         }
#
# }
#
#
#
# # ----- numeric_pitch ------
# # adapted from abc2mtex by Chris Walshaw
# int numeric_pitch(char note)
# {
#
#         if note == 'z')
#                 return 14
#         if note >= 'C' and note <= 'G')
#                 return(note-'C'+16+voices[ivc].key.add_pitch)
#         elif note >= 'A' and note <= 'B')
#                 return(note-'A'+21+voices[ivc].key.add_pitch)
#         elif note >= 'c' and note <= 'g')
#                 return(note-'c'+23+voices[ivc].key.add_pitch)
#         elif note >= 'a' and note <= 'b')
#                 return(note-'a'+28+voices[ivc].key.add_pitch)
#         printf ("numeric_pitch: cannot identify <%c>\n", note)
#         return(0)
# }
#
# # ----- symbolic_pitch: translate numeric pitch back to symbol ------
# int symbolic_pitch(int pit, char *str)
# {
#         int    p,r,s
#         char ltab1[7] = {'C','D','E','F','G','A','B'}
#         char ltab2[7] = {'c','d','e','f','g','a','b'}
#
#         p=pit-16
#         r=(p+700)%7
#         s=(p-r)/7
#
#         if p<7) {
#                 sprintf (str,"%c,,,,,",ltab1[r])
#                 str[1-s]='\0'
#         }
#         else {
# '''
# """
#                 sprintf (str,"%c'''''",ltab2[r])
#                 str[s]='\0'
# """
# '''
#         }
#         return 0
# }


def handle_inside_field(t_type: object) -> None:
    """ act on info field inside body of tune """
    # Todo, rework handle_inside_field(t_type)
    if not common.voices:
        common.ivc = voice.Voice.switch_voice(DEFVOICE)

    if isinstance(t_type, Meter):
        t_type.set_meter(info.meter, voices[ivc].meter)
        t_type.append_meter(common.voices[common.ivc].meter, )
    elif isinstance(t_type, info.DefaultLength):
            t_type.set_dlen(info.len, common.voices[common.ivc].meter)
    elif isinstance(t_type, Key):
            oldkey = common.voices[common.ivc].key
            rc= Key.set_keysig(info.key,common.voices[common.ivc].key, 0)
            if rc:
                Key.set_transtab(halftones, common.voices[common.ivc].key)
            Key.append_key_change(oldkey,voices[ivc].key)
    elif isinstance(t_type, voice.Voice):
            ivc = voice.switch_voice(lvoiceid)


def parse_uint(p) -> int:
    """ parse for unsigned integer """
    if not p.isdigit():
        number  = 0
    else:
        number = int(p)
    if common.db > 3:
        print(f"    parsed unsigned int {number}\n", )
    return number


# # ----- parse_bar: parse for some kind of bar ----
# int parse_bar (void)
# {
#         int k
#         GchordList::iterator ii
#
#         # special cases: [1 or [2 without a preceeding bar, [|
#         if *p == '[') {
#                 if strchr("123456789",*(p+1))) {
#                         k=add_sym (BAR)
#                         voices[ivc].syms[k].u=B_INVIS
#                         voices[ivc].syms[k].v=chartoi(*(p+1))
#                         p=p+2
#                         return 1
#                 }
#         }
#
#         # identify valid standard bar types
#         if *p == '|') {
#                 p += 1
#                 if *p == '|') {
#                         k=add_sym (BAR)
#                         voices[ivc].syms[k].u=B_DBL
#                         p += 1
#                 }
#                 elif *p == ':') {
#                         k=add_sym(BAR)
#                         voices[ivc].syms[k].u=B_LREP
#                         p += 1
#                 }
#                 elif *p == ']') {                                    # code |] for fat end bar
#                         k=add_sym(BAR)
#                         voices[ivc].syms[k].u=B_FAT2
#                         p=p+1
#                 }
#                 else {
#                         k=add_sym(BAR)
#                         voices[ivc].syms[k].u=B_SNGL
#                 }
#         }
#         elif *p == ':') {
#                 if *(p+1) == '|') {
#                         k=add_sym(BAR)
#                         voices[ivc].syms[k].u=B_RREP
#                         p+=2
#                 }
#                 elif *(p+1) == ':') {
#                         k=add_sym(BAR)
#                         voices[ivc].syms[k].u=B_DREP
#                         p+=2; }
#                 else {
#                         # ':' is decoration in tablature
#                          *syntax ("Syntax error parsing bar", p-1)
#
#                         return 0
#                 }
#         }
#
#         elif ((*p == '[') and (*(p+1) == '|') and (*(p+2) == ']')) {    # code [|] invis
#                 k=add_sym(BAR)
#                 voices[ivc].syms[k].u=B_INVIS
#                 p=p+3
#         }
#
#         elif ((*p == '[') and (*(p+1) == '|')) {        # code [| for thick-thin bar
#                 k=add_sym(BAR)
#                 voices[ivc].syms[k].u=B_FAT1
#                 p=p+2
#         }
#
#         else return 0
#
#         # copy over preparsed stuff (gchords, decos)
#         strcpy(voices[ivc].syms[k].text,"")
#         if !prep_gchlst.empty()) {
#                 for (ii=prep_gchlst.begin(); ii!=prep_gchlst.end(); ii += 1) {
#                         voices[ivc].syms[k].gchords->push_back(*ii)
#                 }
#                 prep_gchlst.clear()
#         }
#         if prep_deco.n) {
#                 for (int i=0; i<prep_deco.n; i += 1) {
#                         int deco=prep_deco.t[i]
#                         if ((deco!=D_STACC) and (deco!=D_SLIDE))
#                                 voices[ivc].syms[k].dc.add(deco)
#                 }
#                 prep_deco.clear()
#         }
#
#         # see if valid bar is followed by specifier for first or second ending
#         if strchr("123456789",*p)) {
#                 voices[ivc].syms[k].v=chartoi(*p); p += 1
#         } elif ((*p == '[') and (strchr("123456789",*(p+1)))) {
#                 voices[ivc].syms[k].v=chartoi(*(p+1)); p=p+2
#         } elif ((*p == ' ') and (*(p+1) == '[') and (strchr("123456789",*(p+2)))) {
#                 voices[ivc].syms[k].v=chartoi(*(p+2)); p=p+3
#         }
#
#         return 1
# }
#
# # ----- parse_space:  ----
# def parse_space() -> bool:
#     """ parse for whitespace """
#     # int rc
#
#     rc = False
#     while ((*p == ' ')||(*p == '\t')) {
#             rc=1
#             p += 1
#     }
#     if db>3) if rc) printf ("    parsed whitespace\n")
#     return rc
# }
#
# # ----- parse_esc: parse for escape sequence -----
# int parse_esc (void)
# {
#
#         int nseq
#         char *pp
#
#         if *p == '\\') {                                         # try for \...\ sequence
#                 p += 1
#                 nseq=0
#                 while ((*p!='\\') and (*p!=0)) {
#                         escseq[nseq]=*p
#                         nseq += 1
#                         p += 1
#                 }
#                 if *p == '\\') {
#                         p += 1
#                         escseq[nseq]=0
#                         if db>3) printf ("    parsed esc sequence <%s>\n", escseq)
#                         return ESCSEQ
#                 }
#                 else {
#                         if cfmt.breakall) return DUMMY
#                         if db>3) printf ("    parsed esc to EOL.. continuation\n")
#                 }
#                 return CONTINUE
#         }
#
#         # next, try for [..] sequence
#         if ((*p == '[') and (*(p+1)>='A') and (*(p+1)<='Z') and (*(p+2) == ':')) {
#                 pp=p
#                 p += 1
#                 nseq=0
#                 while ((*p!=']') and (*p!=0)) {
#                         escseq[nseq]=*p
#                         nseq += 1
#                         p += 1
#                 }
#                 if *p == ']') {
#                         p += 1
#                         escseq[nseq]=0
#                         if db>3) printf ("    parsed esc sequence <%s>\n", escseq)
#                         return ESCSEQ
#                 }
#                 syntax ("Escape sequence [..] not closed", pp)
#                 return ESCSEQ
#         }
#         return 0
# }
#
#
# # ----- parse_nl: parse for newline -----
# int parse_nl (void)
# {
#
#         if ((*p == '\\')and(*(p+1) == '\\')) {
#                 p+=2
#                 return 1
#         }
#         else
#                 return 0
# }
#
# # ----- parse_gchord: parse guitar chord, add to global prep_gchlst -----
# int parse_gchord ()
# {
#         char *q
#         int n=0
#         Gchord gchnew
#
#         if *p != '"') return 0
#
#         q=p
#         p += 1
#         //n=strlen(gch)
#         //if n > 0) syntax ("Overwrite unused guitar chord", q)
#
#         while ((*p != '"') and (*p != 0)) {
#                 gchnew.text += *p
#                 n += 1
#                 if n >= 200) {
#                         syntax ("String for guitar chord too long", q)
#                         return 1
#                 }
#                 p += 1
#         }
#         if *p == 0) {
#                 syntax ("EOL reached while parsing guitar chord", q)
#                 return 1
#         }
#         p += 1
#         if db>3) printf("    parse guitar chord <%s>\n", gchnew.text.c_str())
#         gch_transpose(&gchnew.text, voices[ivc].key)
#         prep_gchlst.push_back(gchnew)
#
#         #|     gch_transpose (voices[ivc].key); |
#
#         return 1
# }
#
#
# # ----- parse_deco: parse for decoration, add to global prep_deco -----
# int parse_deco ()
# {
#         int deco,n
#         # mapping abc code to decorations
#         # for no abbreviation, set abbrev=0; for no !..! set fullname=""
#         struct s_deconame { int index; const char abbrev; const char* fullname; }
#         static struct s_deconame deconame[] = {
#                 {D_GRACE,     '~', "!grace!"},
#                 {D_STACC,     '.', "!staccato!"},
#                 {D_SLIDE,     'J', "!slide!"},
#                 {D_TENUTO,    'N', "!tenuto!"},
#                 {D_HOLD,        'H', "!fermata!"},
#                 {D_ROLL,        'R', "!roll!"},
#                 {D_TRILL,     'T', "!trill!"},
#                 {D_UPBOW,     'u', "!upbow!"},
#                 {D_DOWNBOW, 'v', "!downbow!"},
#                 {D_HAT,         'K', "!sforzando!"},
#                 {D_ATT,         'k', "!accent!"},
#                 {D_ATT,         'L', "!emphasis!"}, #for abc standard 1.7.6 compliance
#                 {D_SEGNO,     'S', "!segno!"},
#                 {D_CODA,        'O', "!coda!"},
#                 {D_PRALLER, 'P', "!pralltriller!"},
#                 {D_PRALLER, 'P', "!uppermordent!"}, #for abc standard 1.7.6 compliance
#                 {D_MORDENT, 'M', "!mordent!"},
#                 {D_MORDENT, 'M', "!lowermordent!"}, #for abc standard 1.7.6 compliance
#                 {D_TURN,         0,    "!turn!"},
#                 {D_PLUS,         0,    "!plus!"},
#                 {D_PLUS,         0,    "!+!"}, #for abc standard 1.7.6 compliance
#                 {D_CROSS,     'X', "!x!"},
#                 {D_DYN_PP,     0,    "!pp!"},
#                 {D_DYN_P,        0,    "!p!"},
#                 {D_DYN_MP,     0,    "!mp!"},
#                 {D_DYN_MF,     0,    "!mf!"},
#                 {D_DYN_F,        0,    "!f!"},
#                 {D_DYN_FF,     0,    "!ff!"},
#                 {D_DYN_SF,     0,    "!sf!"},
#                 {D_DYN_SFZ,    0,    "!sfz!"},
#                 {D_BREATH,     0,    "!breath!"},
#                 {D_WEDGE,        0,    "!wedge!" },
#                 {0, 0, ""} #end marker
#         }
#         struct s_deconame* dn
#
#         n=0
#
#         for (;;) {
#                 deco=0
#
#                 #check for fullname deco
#                 if *p == '!') {
#                         int slen
#                         char* q
#                         q = strchr(p+1,'!')
#                         if !q) {
#                                 syntax ("Deco sign '!' not closed",p)
#                                 p += 1
#                                 return n
#                         } else {
#                                 slen = q+1-p
#                                 #lookup in table
#                                 for (dn=deconame; dn->index; dn += 1) {
#                                         if 0 == strncmp(p,dn->fullname,slen)) {
#                                                 deco = dn->index
#                                                 break
#                                         }
#                                 }
#                                 if !deco) syntax("Unknown decoration",p+1)
#                                 p += slen
#                         }
#                 }
#                 #check for abbrev deco
#                 else {
#                         for (dn=deconame; dn->index; dn += 1) {
#                                 if dn->abbrev and (*p == dn->abbrev)) {
#                                         deco = dn->index
#                                         p += 1
#                                         break
#                                 }
#                         }
#                 }
#
#                 if deco) {
#                         prep_deco.add(deco)
#                         n += 1
#                 }
#                 else
#                         printf("There is no decorator\n")
#                         break
#         }
#
#         return n
# }
#
#
# # ----- parse_length:---
def parse_length(line, p) -> int:
    """ parse length specifer for note or rest """

    n_len = voices[ivc].meter.dlen   # start with default length

    try:
        if n_len <= 0:
            SyntaxError(f"got len<=0 from current voice {line[p]}")


        if line[p].isdigit():    # multiply note length
                fac = parse_uint()
                if not fac:
                    fac = 1
                n_len *= fac

        if line[p] == '/':   # divide note length
            while line[p] == '/':
                p += 1
                if line[p].isdigit():
                    fac = parse_uint()
                else:
                    fac = 2
                if n_len % fac:
                    SyntaxError(f"Bad length divisor {line[p-1]}")
                    return n_len

                n_len = n_len/fac

    except SyntaxError as se:
        print(f"{se} Cannot proceed without default length. Emergency stop.")
        exit(1)

    return n_len

#
# # ----- parse_brestnum parses the number of measures on a brest
# int parse_brestnum (void)
# {
#         int fac,len
#         len=1
#         if isdigit(*p)) {                                 # multiply note length
#                 fac=parse_uint ()
#                 if fac == 0) fac=1
#                 len *= fac
#         }
#         return len
# }
#
# # ----- parse_grace_sequence ---------
# #
#  * result is stored in arguments
#  * when no grace sequence => arguments are not altered
#
# int parse_grace_sequence (int *pgr, int *agr, int* len)
# {
#         char *p0
#         int n
#
#         p0=p
#         if *p != '{') return 0
#         p += 1
#
#         *len = 0;     # default is no length => accacciatura
#         n=0
#         while (*p != '}') {
#                 if *p == '\0') {
#                         syntax ("Unbalanced grace note sequence", p0)
#                         return 0
#                 }
#                 if !isnote(*p)) {
#                         syntax ("Unexpected symbol in grace note sequence", p)
#                         p += 1
#                 }
#                 if n >= MAXGRACE) {
#                         p += 1; continue
#                 }
#                 agr[n]=0
#                 if *p == '=') agr[n]=A_NT
#                 if *p == '^') {
#                         if *(p+1) == '^') { agr[n]=A_DS; p += 1; }
#                         else agr[n]=A_SH
#                 }
#                 if *p == '_') {
#                         if *(p+1) == '_') { agr[n]=A_DF; p += 1; }
#                         else agr[n]=A_FT
#                 }
#                 if agr[n]) p += 1
#
#                 pgr[n] = numeric_pitch(*p)
#                 p += 1
#                 while (*p == '\'') { pgr[n] += 7; p += 1; }
#                 while (*p == ',') {    pgr[n] -= 7; p += 1; }
#
#                 do_transpose (voices[ivc].key, &pgr[n], &agr[n])
#
#                 # parse_length() returns default length when no length specified
#                 # => we may only call it when explicit length specified
#                 if *p == '/' || isdigit(*p))
#                         *len=parse_length ()
#                 n += 1
#         }
#
#         p += 1
#         return n
# }
#
# # ----- identify_note: set head type, dots, flags for note ---
# void identify_note (struct SYMBOL *s, char *q)
# {
#         int head,base,len,flags,dots
#
#         if s->len==0) s->len=s->lens[0]
#         len=s->len
#
#         # set flag if duration equals (or gretaer) length of one measure
#         if nvoice>0) {
#                 if len>=(WHOLE*voices[ivc].meter.meter1)/voices[ivc].meter.meter2)
#                         s->fullmes=1
#         }
#
#         base=LONGA
#         if len>=LONGA)                            base=LONGA
#         elif len>=BREVIS)                base=BREVIS
#         elif len>=WHOLE)                 base=WHOLE
#         elif len>=HALF)                    base=HALF
#         elif len>=QUARTER)             base=QUARTER
#         elif len>=EIGHTH)                base=EIGHTH
#         elif len>=SIXTEENTH)         base=SIXTEENTH
#         elif len>=THIRTYSECOND)    base=THIRTYSECOND
#         elif len>=SIXTYFOURTH)     base=SIXTYFOURTH
#         else syntax("Cannot identify head for note",q)
#
#         if base>=WHOLE)         head=H_OVAL
#         elif base == HALF) head=H_EMPTY
#         else                                 head=H_FULL
#
#         if base == SIXTYFOURTH)                flags=4
#         elif base == THIRTYSECOND)    flags=3
#         elif base == SIXTEENTH)         flags=2
#         elif base == EIGHTH)                flags=1
#         else                                                    flags=0
#
#         dots=0
#         if len == base)                        dots=0
#         elif 2*len == 3*base)     dots=1
#         elif 4*len == 7*base)     dots=2
#         elif 8*len == 15*base)    dots=3
#         else syntax("Cannot handle note length for note",q)
#
#         #    printf ("identify_note: length %d gives head %d, dots %d, flags %d\n",
#                 len,head,dots,flags)
#
#         s->head=head
#         s->dots=dots
#         s->flags=flags
# }
#
#
# # ----- double_note: change note length for > or < char ---
# # Note: if voices[ivc].syms[i] is a chord, the length shifted to the following
#      note is taken from the first note head. Problem: the crazy syntax
#      permits different lengths within a chord.
# void double_note (int i, int num, int sign, char *q)
# {
#         int m,shift,j,len
#
#         if ((voices[ivc].syms[i].type!=NOTE) and (voices[ivc].syms[i].type!=REST))
#                 bug("sym is not NOTE or REST in double_note", true)
#
#         shift=0
#         len=voices[ivc].syms[i].lens[0]
#         for (j=0;j<num;j += 1) {
#                 len=len/2
#                 shift -= sign*len
#                 voices[ivc].syms[i].len += sign*len
#                 for (m=0;m<voices[ivc].syms[i].npitch;m += 1) voices[ivc].syms[i].lens[m] += sign*len
#         }
#         identify_note (&voices[ivc].syms[i],q)
#         carryover += shift
# }
#
# # ----- parse_basic_note: parse note or rest with pitch and length --
# int parse_basic_note (int *pitch, int *length, int *accidental)
# {
#         int pit,len,acc
#
#         acc=pit=0;                                             # look for accidental sign
#         if *p == '=') acc=A_NT
#         if *p == '^') {
#                 if *(p+1)=='^') { acc=A_DS; p += 1; }
#                 else acc=A_SH
#         }
#         if *p == '_') {
#                 if *(p+1) == '_') { acc=A_DF; p += 1; }
#                 else acc=A_FT
#         }
#
#         if acc) {
#                 p += 1
#                 if !strchr("CDEFGABcdefgab",*p)) {
#                         syntax("Missing note after accidental", p-1)
#                         return 0
#                 }
#         }
#         if !isnote(*p)) {
#                 syntax ("Expecting note", p)
#                 p += 1
#                 return 0
#         }
#
#         pit= numeric_pitch(*p);                         # basic pitch
#         p += 1
#
#         while (*p == '\'') {                                # eat up following ' chars
#                 pit += 7
#                 p += 1
#         }
#
#         while (*p == ',') {                                 # eat up following , chars
#                 pit -= 7
#                 p += 1
#         }
#
#         len=parse_length()
#
#         do_transpose (voices[ivc].key, &pit, &acc)
#
#         *pitch=pit
#         *length=len
#         *accidental=acc
#
#         if db>3) printf ("    parsed basic note,"
#                         "length %d/%d = 1/%d, pitch %d\n",
#                         len,BASE,BASE/len,pit)
#
#         return 1
#
# }
#
#
# # ----- parse_note: parse for one note or rest with all trimmings ---
# int parse_note (void)
# {
#         int k,deco,i,chord,m,type,rc,sl1,sl2,j,n
#         int pitch,length,accidental,invis
#         char *q,*q0
#         GchordList::iterator ii
#         #grace sequence must be remembered in static variables,
#         #because otherwise it is lost after slurs
#         static int ngr = 0
#         static int pgr[MAXGRACE],agr[MAXGRACE],lgr
#
#         n=parse_grace_sequence(pgr,agr,&lgr);     # grace notes
#         if n) ngr = n
#
#         parse_gchord();                             # permit chord after graces
#
#         deco=parse_deco();                            # decorations
#
#         parse_gchord();                             # permit chord after deco
#
#         chord=0;                                                         # determine if chord
#         q=p
#         if ((*p == '+') || (*p == '[')) { chord=1; p += 1; }
#
#         type=invis=0
#         parse_deco(); # allow for decos within chord
#         if isnote(*p)) type=NOTE
#         if chord and (*p == '(')) type=NOTE
#         if chord and (*p == ')')) type=NOTE;     # this just for better error msg
#         if *p == 'z') type=REST
#         if *p == 'Z') type=BREST
#         if ((*p == 'x')||(*p == 'X')) {type=REST; invis=1; }
#         if !type) return 0
#
#         k=add_sym(type);                                         # add new symbol to list
#
#
#         voices[ivc].syms[k].dc.n=prep_deco.n;             # copy over pre-parsed stuff
#         for (i=0;i<prep_deco.n;i += 1)
#                 voices[ivc].syms[k].dc.t[i]=prep_deco.t[i]
#         prep_deco.clear()
#         if ngr) {
#                 voices[ivc].syms[k].gr.n=ngr
#                 voices[ivc].syms[k].gr.len=lgr
#                 for (i=0;i<ngr;i += 1) {
#                         voices[ivc].syms[k].gr.p[i]=pgr[i]
#                         voices[ivc].syms[k].gr.a[i]=agr[i]
#                 }
#                 ngr = 0
#         } else {
#                 voices[ivc].syms[k].gr.n=0
#                 voices[ivc].syms[k].gr.len=0
#         }
#
#         if !prep_gchlst.empty()) {
#                 #gch_transpose (voices[ivc].key)
#                 for (ii=prep_gchlst.begin(); ii!=prep_gchlst.end(); ii += 1) {
#                         voices[ivc].syms[k].gchords->push_back(*ii)
#                 }
#                 prep_gchlst.clear()
#         }
#
#         q0=p
#         if type == REST) {
#                 p += 1
#                 voices[ivc].syms[k].lens[0] = parse_length()
#                 voices[ivc].syms[k].npitch=1
#                 voices[ivc].syms[k].invis=invis
#                 if db>3) printf ("    parsed rest, length %d/%d = 1/%d\n",
#                                 voices[ivc].syms[k].lens[0],BASE,BASE/voices[ivc].syms[k].lens[0])
#         }
#         elif type == BREST) {
#                 p += 1
#                 voices[ivc].syms[k].lens[0] = (WHOLE*voices[ivc].meter.meter1)/voices[ivc].meter.meter2
#                 voices[ivc].syms[k].len = voices[ivc].syms[k].lens[0]
#                 voices[ivc].syms[k].fullmes = parse_brestnum()
#                 voices[ivc].syms[k].npitch=1
#         }
#         else {
#                 m=0;                                                                 # get pitch and length
#                 sl1=sl2=0
#                 for (;;) {
#                         if chord and (*p == '(')) {
#                                 sl1 += 1
#                                 voices[ivc].syms[k].sl1[m]=sl1
#                                 p += 1
#                         }
#                         if ((deco=parse_deco())) {         # for extra decorations within chord
#                                 for (i=0;i<deco;i += 1) voices[ivc].syms[k].dc.add(prep_deco.t[i])
#                                 prep_deco.clear()
#                         }
#
#                         rc=parse_basic_note (&pitch,&length,&accidental)
#                         if rc == 0) { voices[ivc].nsym -= 1 return 0; }
#                         voices[ivc].syms[k].pits[m] = pitch
#                         voices[ivc].syms[k].lens[m] = length
#                         voices[ivc].syms[k].accs[m] = accidental
#                         voices[ivc].syms[k].ti1[m]    = voices[ivc].syms[k].ti2[m] = 0
#                         for (j=0;j<ntinext;j += 1)
#                                 if tinext[j] == voices[ivc].syms[k].pits[m]) voices[ivc].syms[k].ti2[m]=1
#
#                         if chord and (*p == '-')) {voices[ivc].syms[k].ti1[m]=1; p += 1;}
#
#                         if chord and (*p == ')')) {
#                                 sl2 += 1
#                                 voices[ivc].syms[k].sl2[m]=sl2
#                                 p += 1
#                         }
#
#                         if chord and (*p == '-')) {voices[ivc].syms[k].ti1[m]=1; p += 1;}
#
#                         m += 1
#
#                         if !chord) break
#                         if ((*p == '+')||(*p == ']')) {
#                                 p += 1
#                                 break
#                         }
#                         if *p == '\0') {
#                                 if chord) syntax ("Chord not closed", q)
#                                 return type
#                         }
#                 }
#                 ntinext=0
#                 for (j=0;j<m;j += 1)
#                         if voices[ivc].syms[k].ti1[j]) {
#                                 tinext[ntinext]=voices[ivc].syms[k].pits[j]
#                                 ntinext += 1
#                         }
#                 voices[ivc].syms[k].npitch=m
#                 if m>0) {
#                         voices[ivc].syms[k].grcpit = voices[ivc].syms[k].pits[0]
#                 }
#         }
#
#         for (m=0;m<voices[ivc].syms[k].npitch;m += 1) {     # add carryover from > or <
#                 if voices[ivc].syms[k].lens[m]+carryover<=0) {
#                         syntax("> leads to zero or negative note length",q0)
#                 }
#                 else
#                         voices[ivc].syms[k].lens[m] += carryover
#         }
#         carryover=0
#
#         if db>3) printf ("    parsed note, decos %d, text <%s>\n",
#                         voices[ivc].syms[k].dc.n, voices[ivc].syms[k].text)
#
#
#         voices[ivc].syms[k].yadd=0
#         if voices[ivc].key.ktype == BASS)                 voices[ivc].syms[k].yadd=-6
#         if voices[ivc].key.ktype == ALTO)                 voices[ivc].syms[k].yadd=-3
#         if voices[ivc].key.ktype == TENOR)                voices[ivc].syms[k].yadd=+3
#         if voices[ivc].key.ktype == SOPRANO)            voices[ivc].syms[k].yadd=+6
#         if voices[ivc].key.ktype == MEZZOSOPRANO) voices[ivc].syms[k].yadd=-9
#         if voices[ivc].key.ktype == BARITONE)         voices[ivc].syms[k].yadd=-12
#         if voices[ivc].key.ktype == VARBARITONE)    voices[ivc].syms[k].yadd=-12
#         if voices[ivc].key.ktype == SUBBASS)            voices[ivc].syms[k].yadd=0
#         if voices[ivc].key.ktype == FRENCHVIOLIN) voices[ivc].syms[k].yadd=-6
#
#         if type!=BREST)
#                 identify_note (&voices[ivc].syms[k],q0)
#         return type
# }
#
#
# # ----- parse_sym: parse a symbol and return its type --------
# int parse_sym (void)
# {
#         int i
#
#         if parse_gchord())     return GCHORD
#         if parse_deco())         return DECO
#         if parse_bar())            return BAR
#         if parse_space())        return SPACE
#         if parse_nl())             return NEWLINE
#         if ((i=parse_esc()))    return i
#         if ((i=parse_note())) return i
#
#         return 0
# }
#
def add_wd(s: str) -> str:
    l = len(s)
    if not l:
        return ''
    if common.nwpool+l+1 > NWPOOL:
            log.error("Overflow while parsing vocals; increase NWPOOL and recompile.")
            exit()

    common.wpool = common.wpool[:common.nwpool] + s + common.wpool[common.nwpool:]
    rp = common.wpool[:common.nwpool]
    common.nwpool = common.nwpool+l+1
    return rp

#
# # ----- parse_vocals: parse words below a line of music -----
# # Use '^' to mark a '-' between syllables - hope nobody needs '^' !
# int parse_vocals (char *line)
# {
#         int isym
#         char *c,*c1,*w
#         char word[81]
#
#         if ((line[0]!='w') || (line[1]!=':')) return 0
#         p0=line
#
#         # increase vocal line counter in first symbol of current line
#         voices[ivc].syms[nsym0].wlines += 1
#
#         isym=nsym0-1
#         c=line+2
#         for (;;) {
#                 while(*c == ' ') c += 1
#                 if *c == '\0') break
#                 c1=c
#                 if ((*c == '_') || (*c == '*') || (*c == '|') || (*c == '-')) {
#                         word[0]=*c
#                         if *c == '-') word[0]='^'
#                         word[1]='\0'
#                         c += 1
#                 }
#                 else {
#                         w=word
#                         *w='\0'
#                         while ((*c!=' ') and (*c!='\0')) {
#                                 if ((*c == '_') || (*c == '*') || (*c == '|')) break
#                                 if *c == '-') {
#                                         if *(c-1) != '\\') break
#                                         w -= 1
#                                         *w='-'
#                                 }
#                                 *w=*c; w += 1; c += 1
#                         }
#                         if *c == '-') { *w='^' ; w += 1; c += 1; }
#                         *w='\0'
#                 }
#
#                 # now word contains a word, possibly with trailing '^',
#                      or one of the special characters * | _ -
#
#                 if !strcmp(word,"|")) {                             # skip forward to next bar
#                         isym += 1
#                         while ((voices[ivc].syms[isym].type!=BAR) and (isym<voices[ivc].nsym)) isym += 1
#                         if isym>=voices[ivc].nsym)
#                         { syntax("Not enough bar lines for |",c1); break; }
#                 }
#
#                 else {                                                                 # store word in next note
#                         w=word
#                         while (*w!='\0') {                                     # replace * and ~ by space
#                                 # cd: escaping with backslash possible
#                                 # (does however not yet work for '*')
#                                 if  ((*w == '*') || (*w == '~')) and !(w>word and *(w-1) == '\\') ) *w=' '
#                                 w += 1
#                         }
#                         isym += 1
#                         while ((voices[ivc].syms[isym].type!=NOTE) and (isym<voices[ivc].nsym)) isym += 1
#                         if isym>=voices[ivc].nsym)
#                         { syntax ("Not enough notes for words",c1); break; }
#                         voices[ivc].syms[isym].wordp[nwline]=add_wd(word)
#                 }
#
#                 if *c == '\0') break
#         }
#
#         nwline += 1
#         return 1
# }
#
#
# # ----- parse_music_line:-----
def parse_music_line(line: str) -> int:
    """ parse a music line into symbols """
    # int num,nbr,n,itype,i
    # char msg[81]


    if ivc >= len(voices):
        log.critical(f"Trying to parse undefined voice {True}")
        exit(1)

    common.nwline = 0
    s_type = 0
    nsym0 = len(voices[ivc].syms)

    nbr = 0
    p0 = line
    p = 0

    while p < len(line):
        if p > len(line):
            break   # emergency exit
        s_type = parse_sym()
        n = (voices[ivc].syms)
        i = n-1
        if common.db > 4 and s_type:
            print(f"     sym[{n-1}] code ({voices[ivc].syms[n-1].type},{voices[ivc].syms[n-1].u}")

        if s_type == NEWLINE:
            if n > 0 and not cfmt.continueall and not cfmt.barsperstaff:
                voices[ivc].syms[i].eoln=1
                if common.word:
                    voices[ivc].syms[common.last_note].word_end = True
                    common.word = False
                    
        if s_type == ESCSEQ:
            if db > 3:
                print(f"Handle escape sequence <{escseq}>")
            itype = info_field(escseq)
            handle_inside_field(itype)

        if s_type == REST:
            if pplet:   # n-plet can start on rest
                voices[ivc].syms[i].p_plet = pplet
                voices[ivc].syms[i].q_plet = qplet
                voices[ivc].syms[i].r_plet = rplet
                pplet=0
            common.last_note = i     # need this so > and < work
            p1 = p

        if s_type == NOTE:
            if not common.word:
                voices[ivc].syms[i].word_st = True
                word = True
            if nbr and cfmt.slurisligatura:
                voices[ivc].syms[i].lig1 += nbr
            else:
                voices[ivc].syms[i].slur_st += nbr
            nbr=0
            if voices[ivc].end_slur:
                voices[ivc].syms[i].slur_end += 1
            voices[ivc].end_slur = 0
    
            if pplet:                                    # start of n-plet
                voices[ivc].syms[i].p_plet = pplet
                voices[ivc].syms[i].q_plet = qplet
                voices[ivc].syms[i].r_plet = rplet
                pplet=0
            last_note = last_real_note = i
            p1 = p

        if common.word and s_type == BAR or s_type == SPACE:
            if last_real_note >= 0:
                voices[ivc].syms[last_real_note].word_end = True
                common.word = False

        if not s_type:
            if p == '-':   # a-b tie
                voices[ivc].syms[common.last_note].slur_st += 1
                voices[ivc].end_slur=1
                p += 1

            elif p == '(':
                p += 1
                if p.isdigit():
                    pplet = char_delta(line[p],'0')
                    qplet = 0
                    rplet = pplet
                    p += 1
                    if p == ':':
                        p += 1
                        if p.isdigit():
                            qplet = char_delta(line[p],'0')
                            p += 1
                        if p == ':':
                            p += 1
                            if p.isdigit():
                                rplet = char_delta(line[p],'0')
                                p += 1
                else:
                    nbr += 1
            elif *p == ')':
                if common.last_note > 0:
                    if cfmt.slurisligatura:
                        voices[ivc].syms[common.last_note].lig2 += 1
                    else:
                        voices[ivc].syms[common.last_note].slur_end += 1
                else:
                    SyntaxError(f"Unexpected symbol {p}")
                p += 1
            elif *p == '>':
                num=1
                p += 1
                while *p == '>':
                    num += 1
                    p += 1
                if last_note < 0:
                    SyntaxError("No note before > sign", p)
                else:
                    double_note(last_note, num, 1, p1)
            elif *p == '<':
                    num = 1
                    p += 1
                    while *p == '<':
                        num += 1
                        p += 1
                    if last_note < 0:
                            SyntaxError("No note before < sign", p)
                    else:
                            double_note (last_note, num, -1, p1)
            elif *p == '*':      # ignore stars for now
                p += 1
            elif *p == '!':      # ditto for '!'
                p += 1
            else:
                if *p != '\0':
                    msg = f"Unexpected symbol '{line[p]}'"
                else:
                    msg = f"Unexpected end of line"
                SyntaxError(msg, line[p])
                p += 1

    # maybe set end-of-line marker, if symbols were added
    n = len(voices[ivc].syms)

    if n > nsym0:
        if s_type == CONTINUE or cfmt.barsperstaff or cfmt.continueall:
            voices[ivc].syms[n-1].eoln = False
        else:
            # add invisible bar, if last symbol no bar
            if voices[ivc].syms[n-1].s_type != BAR:
                i = add_sym(BAR)
                voices[ivc].syms[i].u = B_INVIS
                n = i+1
            }
            voices[ivc].syms[n-1].eoln=1

    # break words at end of line
    if common.word and voices[ivc].syms[n-1].eoln:
        voices[ivc].syms[common.last_note].word_end = True
        common.word = False

    return TO_BE_CONTINUED



def is_selected(xref_str: str, pat, select_all: bool,
                search_field: int) -> bool:
    """ check selection for current info fields """
    global field

    # true if select_all or if no selectors given
    if select_all:
        return True
    if not xref_str and len(pat) == 0:
        return True

    m = 0
    for i in range(len(pat)):                        #patterns
        if search_field == S_COMPOSER:
            for j in range(len(field.composer)):
                if not m:
                    m = re.match(field.composer[j], pat[i])
        elif search_field == S_SOURCE:
                m = re.match(field.source, pat[i])
        elif search_field == S_RHYTHM:
                m = re.match(field.rhythm, pat[i])
        else:
                m = re.match(field.titles[0], pat[i])
                if not m and len(field.titles) >= 2:
                    m = re.match(field.titles[1], pat[i])
                if not m and len(field.titles[2]) == 3:
                    m = re.match(field.titles[2], pat[i])
        if m:
            return True

    # check xref against string of numbers
    # This is wrong. Need to check with doc to valid the need to rework.
    field.xref.xref_str = field.xref.xref_str.replace(",", " ")
    field.xref.xref_str = field.xref.xref_str.replace("-", " ")

    p = field.xref.xref_str.split()
    a = parse_uint(p[0])
    if not a:
        return False  # can happen if invalid chars in string
    b = parse_uint(p[1])
    if not b:
        if field.xref.xref >= a:
            return True
    else:
        for i in range(a, b):
            if field.xref.xref == i:
                return True
    if field.xref.xref == a:
        return True


    return False


def rehash_selectors(sel_str: list[str]) -> tuple:
    """
    split selectors into patterns and xrefs

    todo: find the meaning and structure of sel_str
    """
    xref_str = ''
    pat = list()
    for value in sel_str:
        if not value or value.startswith('-'):   # skip any flags
            pass
        elif subs.is_xrefstr(value):
            xref_str = value
        else:  # pattern with * or +
            if '*' in value or '+' in value:
                pat.append(value)
            else:   # simple pattern
                pat.append("*" + value + '*')

    return pat, xref_str

def decomment_line(ln: str) -> str:
    """
    cut off after %

    :param ln:
    :return:
    """
    inquotes = False   # do not remove inside double quotes
    for i, p in enumerate(list(ln)):
        if p == '"':
            if inquotes:
                    inquotes = False
            else:
                inquotes = True
        if p == '%' and not inquotes:
            return ln[0:i]
    return ln


def do_index(filename, xref_str: str, pat: list, select_all: bool, search_field: int) -> None:
    """ print index of abc file """
    # int type,within_tune
    # string linestr
    # static char* line = NULL
    from constants import (XREF, KEY)
    import info

    linenum = 0
    verbose = common.vb
    numtitle = 0
    write_history = 0
    common.within_tune = False
    common.within_block = False
    common.do_this_tune = False
    info = info.Field()

    with open(filename) as fp:
        lines = fp.readlines()
    for line in lines:
        if is_comment(line):
            continue
        line = decomment_line(line)
        f_type = info.get_default_info()   # todo this right?
                
        if f_type == XREF:
            if common.within_block:
                print(f"+++ Tune {info.xref.xref} not closed properly ")
            numtitle = 0
            common.within_tune = False
            common.within_block = True
            ntext = 0
            break
            
        elif f_type == KEY:
            if not common.within_block:
                break
            if not common.within_tune:
                common.tnum2 += 1
                if is_selected(xref_str, pat, select_all, search_field):
                    print(f"    {info.xref.xref:-4d} {info.key_clef.key_type:-5s} {info.meter:-4s}")
                    if search_field == S_SOURCE:
                        print(f"    {info.source:-15s}")

                    elif search_field == S_RHYTHM:
                        print(f"    {info.rhythm:-8s}")
                    elif search_field == S_COMPOSER:
                        print(f"    {info.composer[0]:-15s}")
                    if numtitle == 3:
                        print(f"    {info.titles[0]} - {info.titles[1]} - {info.titles[2]}")
                    if numtitle == 2:
                        print(f"    {info.titles[0]} - {info.titles[1]}")
                    if numtitle==1:
                        print(f"    {info.titles[0]}")
                    
                    print()
                    common.tnum1 += 1
                common.within_tune=1
            break

        if not line:
            if common.within_block and not common.within_tune:
                print(f"+++ Header not closed in tune {info.xref.xref}")
            common.within_tune = False
            common.within_block = False
            info = info.Field()
    if common.within_block and not common.within_tune:
        print(f"+++ Header not closed in for tune {info.xref.xref}", )

