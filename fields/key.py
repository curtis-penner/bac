# Copyright 2019 Curtis Penner

"""
Every option in the K: field may be omitted, but the order must not be
permutated. The meaning of the individual options is:

key and mode:
The key signature should be specified with a capital letter (major mode) which
may be followed by a "#" or "b" for sharp or flat respectively. The mode
determines the accidentals and can follow immediately after the key letter
or with white spaces separated; possible mode names are maj(or) (this is
the default), min(or), m(inor), ion(ian), mix(olydian), dor(ian),
phr(ygian), lyd(ian), loc(rian), aeo(lian). Mode names are not case sensitive.
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

import utils.log
import utils.cmdline
from original import constants
from ps import tab_

log = utils.log.log()
args = utils.cmdline.options()


class Key:
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

    TREBLE = 1
    TREBLE8 = 2
    BASS = 3
    ALTO = 4

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

    def __call__(self, line, header=True):
        """
        Parse the value for key_clef

        :param line:
        :return:
        """
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
                acc_old=1
            if -sf_old >= fl_tab[i]:
                acc_old=-1
            acc_new = 0
            if sf_new >= sh_tab[j]:
                acc_new=1
            if -sf_new >= fl_tab[j]:
                acc_new=-1
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
        i=(pitch_old+70)%7
        # j=(pitch_new+70)%7

        if acc_old:
            if acc_old == self.A_DF: 
                sf_old=-2
            if acc_old == self.A_FT: 
                sf_old=-1
            if acc_old == self.A_NT: 
                sf_old=0
            if acc_old == self.A_SH: 
                sf_old=1
            if acc_old == self.A_DS: 
                sf_old=2
            sf_new=sf_old + self.add_accs[i]
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
            acc_new=0
        return pitch_new, acc_new

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

    def is_tab_key(self):
        """ 
        decide whether the clef number in "key" means tablature
        """
        return (self.key_type == tab_.FRENCHTAB or
                self.key_type == tab_.FRENCH5TAB or
                self.key_type == tab_.FRENCH4TAB or
                self.key_type == tab_.SPANISHTAB or
                self.key_type == tab_.SPANISH5TAB or
                self.key_type == tab_.SPANISH4TAB or
                self.key_type == tab_.ITALIANTAB or
                self.key_type == tab_.ITALIAN7TAB or
                self.key_type == tab_.ITALIAN8TAB or
                self.key_type == tab_.ITALIAN5TAB or
                self.key_type == tab_.ITALIAN4TAB or
                self.key_type == tab_.GERMANTAB)

    def tab_numlines(self):
        """ 
        return number of lines per tablature system
        """
        if self.key_type in [tab_.FRENCHTAB,
                             tab_.SPANISHTAB,
                             tab_.ITALIANTAB,
                             tab_.ITALIAN7TAB,
                             tab_.ITALIAN8TAB]:
            return 6
        elif self.key_type in [tab_.FRENCH5TAB,
                               tab_.SPANISH5TAB,
                               tab_.ITALIAN5TAB,
                               tab_.GERMANTAB]:
            # 5 lines should be enough for german tab
            return 5
        elif self.key_type in [tab_.FRENCH4TAB,
                               tab_.SPANISH4TAB,
                               tab_.ITALIAN4TAB]:
        
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


"""

/* ----- set_keysig: interpret keysig string, store in struct ---- */
/* This part was adapted from abc2mtex by Chris Walshaw */
/* updated 03 Oct 1997 Wil Macaulay - support all modes */
/* Returns 1 if key was actually specified, because then we want
   to transpose. Returns zero if this is just a clef change. */
int set_keysig(char *s, struct KEYSTR *ks, int init)
{
  int c,sf,j,ok;
  char w[81];
  int root,root_acc;

  /* maybe initialize with key C (used for K field in header) */
  if (init) {
    ks->sf         = 0;
    ks->ktype      = TREBLE;
    ks->add_pitch  = 0;
    ks->root       = 2;
    ks->root_acc   = A_NT;
  }

  /* check for clef specification with no other information */
  if (!strncmp(s,"clef=",5) && set_clef(s+5,ks)) return 0;
  if (set_clef(s,ks)) return 0;

  /* check for key specifier */
  c=0;
  bagpipe=0;
  switch (s[c]) {
  case 'F':
    sf = -1; root=5;
    break;
  case 'C':
    sf = 0; root=2;
    break;
  case 'G':
    sf = 1; root=6;
    break;
  case 'D':
    sf = 2; root=3;
    break;
  case 'A':
    sf = 3; root=0;
    break;
  case 'E':
    sf = 4; root=4;
    break;
  case 'B':
    sf = 5; root=1;
    break;
  case 'H':
    bagpipe=1;
    c++;
    if (s[c] == 'P') {
        sf=0;
        root=2;
    } else if (s[c] == 'p') {
        sf=2;
        root=3;
    } else {
        sf=0;
        root=2;
        std::cerr << "unknown bagpipe-like key: " << s << std::endl;
    }
    break;
  default:
    std::cerr << "Using C because key not recognised: " <<  s << std::endl;
    sf = 0;
    root=2;
  }
  c++;

  root_acc=A_NT;
  if (s[c] == '#') {
    sf += 7;
    c += 1;
    root_acc=A_SH;
  } else if (s[c] == 'b') {
    sf -= 7;
    c += 1;
    root_acc=A_FT;
  }

  /* loop over blank-delimited words: get the next token in lower case */
  for (;;) {
    while (isspace(s[c])) c++;
    if (s[c]=='\0') break;

    j=0;
    while (!isspace(s[c]) && (s[c]!='\0')) { w[j]=tolower(s[c]); c++; j++; }
    w[j]='\0';

    /* now identify this word */

    /* first check for mode specifier */
    if ((strncmp(w,"mix",3)) == 0) {
      sf -= 1;
      ok = 1;
      /* dorian mode on the second note (D in C scale) */
    } else if ((strncmp(w,"dor",3)) == 0) {
      sf -= 2;
      ok = 1;
      /* phrygian mode on the third note (E in C scale) */
    } else if ((strncmp(w,"phr",3)) == 0) {
      sf -= 4;
      ok = 1;
      /* lydian mode on the fourth note (F in C scale) */
    } else if ((strncmp(w,"lyd",3)) == 0) {
      sf += 1;
      ok = 1;
      /* locrian mode on the seventh note (B in C scale) */
    } else if ((strncmp(w,"loc",3)) == 0) {
      sf -= 5;
      ok = 1;
      /* major and ionian are the same ks */
    } else if ((strncmp(w,"maj",3)) == 0) {
      ok = 1;
    } else if ((strncmp(w,"ion",3)) == 0) {
      ok = 1;
      /* aeolian, m, minor are the same ks - sixth note (A in C scale) */
    } else if ((strncmp(w,"aeo",3)) == 0) {
      sf -= 3;
      ok = 1;
    } else if ((strncmp(w,"min",3)) == 0) {
      sf -= 3;
      ok = 1;
    } else if ((strcmp(w,"m")) == 0) {
      sf -= 3;
      ok = 1;
    }

    /* check for trailing clef specifier */
    else if (!strncmp(w,"clef=",5)) {
      if (!set_clef(w+5,ks)) {
        std::cerr << "unknown clef specifier: " << w << std::endl;
      }
    }
    else if (set_clef(w,ks)) {
      /* (clef specification without "clef=" prefix) */
    }

    /* nothing found */
    else std::cerr << "Unknown token in key specifier: " << w << std::endl;

  }  /* end of loop over blank-delimted words */

  if (verbose>=4) printf ("Key   <%s> gives sharpsflats %d, type %d\n",
                          s, sf, ks->ktype);

  /* copy to struct */
  ks->sf         = sf;
  ks->root       = root;
  ks->root_acc   = root_acc;

  return 1;

}

/* ----- set_clef: parse clef specifier and store in struct --- */
/* RC: 0 if no clef specifier; 1 if clef identified */
int set_clef(char* s, struct KEYSTR *ks)
{
  struct {  /* zero terminated list of music clefs */
    const char* name; int value;
  } cleflist[] = {
    {"treble", TREBLE},
    {"treble8", TREBLE8},
    {"treble8up", TREBLE8UP},
    {"bass", BASS},
    {"alto", ALTO},
    {"tenor", TENOR},
    {"soprano", SOPRANO},
    {"mezzosoprano", MEZZOSOPRANO},
    {"baritone", BARITONE},
    {"varbaritone", VARBARITONE},
    {"subbass", SUBBASS},
    {"frenchviolin", FRENCHVIOLIN},
    {0, 0}
  };
  int i, len;

  /* get clef name length without octave modifier (+8 etc) */
  len = strcspn(s,"+-");

  /* loop over possible music clefs */
  for (i=0; cleflist[i].name; i++) {
    if (!strncmp(s,cleflist[i].name,len)) {
      ks->ktype=cleflist[i].value;
      /* check for octave modifier */
      if (s[len]) {
        char* mod=&(s[len]);
        if (!strcmp(mod,"+8"))
          ks->add_pitch=7;
        else if (!strcmp(mod,"-8"))
          ks->add_pitch=-7;
        else if (!strcmp(mod,"+0") || !strcmp(mod,"-0"))
          ks->add_pitch=0;
        else if (!strcmp(mod,"+16"))
          ks->add_pitch=+14;
        else if (!strcmp(mod,"-16"))
          ks->add_pitch=-14;
        else
          std::cerr << "unknown octave modifier in clef: " << s << std::endl;
      }
      return 1;
    }
  }

  /* check for tablature clef */
  if (parse_tab_key(s,&ks->ktype)) return 1;

  return 0;
}

/* ----- get_halftones: figure out how by many halftones to transpose --- */
/*  In the transposing routines: pitches A..G are coded as with 0..7 */
int get_halftones (struct KEYSTR key, char *transpose)
{
  int pit_old,pit_new,direction,stype,root_new,racc_new,nht;
  int root_old, racc_old;
  char *q;
  /* pit_tab associates true pitches 0-11 with letters A-G */
  int pit_tab[] = {0,2,3,5,7,8,10};

  if (strlen(transpose)==0) return 0;
  root_new=root_old=key.root;
  racc_old=key.root_acc;

  /* parse specification for target key */
  q=transpose;
  direction=0;

  if (*q=='^') {
    direction=1; q++;
  } else if (*q=='_') {
    direction=-1; q++;
  }
  stype=1;
  if (strchr("ABCDEFG",*q)) {
    root_new=*q-'A'; q++; stype=2;
  } else if (strchr("abcdefg",*q)) {
    root_new=*q-'a'; q++;  stype=2;
  }

  /* first case: offset was given directly as numeric argument */
  if (stype==1) {
    sscanf(q,"%d", &nht);
    if (direction<0) nht=-nht;
    if (nht==0) {
      if (direction<0) nht=-12;
      if (direction>0) nht=+12;
    }
    return nht;
  }

  /* second case: root of target key was specified explicitly */
  racc_new=0;
  if (*q=='b') {
    racc_new=A_FT; q++;
  } else if (*q=='#') {
    racc_new=A_SH; q++;
  } else if (*q!='\0')
    std::cerr << "expecting accidental in transpose spec: " << transpose << std::endl;

  /* get pitch as number from 0-11 for root of old key */
  pit_old=pit_tab[root_old];
  if (racc_old==A_FT) pit_old--;
  if (racc_old==A_SH) pit_old++;
  if (pit_old<0)  pit_old+=12;
  if (pit_old>11) pit_old-=12;

  /* get pitch as number from 0-11 for root of new key */
  pit_new=pit_tab[root_new];
  if (racc_new==A_FT) pit_new--;
  if (racc_new==A_SH) pit_new++;
  if (pit_new<0)  pit_new+=12;
  if (pit_new>11) pit_new-=12;

  /* number of halftones is difference */
  nht=pit_new-pit_old;
  if (direction==0) {
    if (nht>6)  nht-=12;
    if (nht<-5) nht+=12;
  }
  if (direction>0 && nht<=0) nht+=12;
  if (direction<0 && nht>=0) nht-=12;

  return nht;

}



/* ----- shift_key: make new key by shifting nht halftones --- */
void shift_key (int sf_old, int nht, int *sfnew, int *addt)
{
  int sf_new,r_old,r_new,add_t,  dh,dr;
  int skey_tab[] = {2,6,3,0,4,1,5,2};
  int fkey_tab[] = {2,5,1,4,0,3,6,2};
  char root_tab[]={'A','B','C','D','E','F','G'};

  /* get sf_new by adding 7 for each halftone, then reduce mod 12 */
  sf_new=sf_old+nht*7;
  sf_new=(sf_new+240)%12;
  if (sf_new>=6) sf_new=sf_new-12;

  /* get old and new root in ionian mode, shift is difference */
  r_old=2;
  if (sf_old>0) r_old=skey_tab[sf_old];
  if (sf_old<0) r_old=fkey_tab[-sf_old];
  r_new=2;
  if (sf_new>0) r_new=skey_tab[sf_new];
  if (sf_new<0) r_new=fkey_tab[-sf_new];
  add_t=r_new-r_old;

  /* fix up add_t to get same "decade" as nht */
  dh=(nht+120)/12; dh=dh-10;
  dr=(add_t+70)/7; dr=dr-10;
  add_t=add_t+7*(dh-dr);

  if (verbose>=8)
    printf ("shift_key: sf_old=%d new %d   root: old %c new %c  shift by %d\n",
            sf_old, sf_new, root_tab[r_old], root_tab[r_new], add_t);

  *sfnew=sf_new;
  *addt=add_t;

}


/* ----- set_transtab: setup for transposition by nht halftones --- */
void set_transtab (int nht, struct KEYSTR *key)
{
  int a,b,sf_old,sf_new,add_t,i,j,acc_old,acc_new,root_old,root_acc;
  /* for each note A..G, these tables tell how many sharps (resp. flats)
     the keysig must have to get the accidental on this note. Phew. */
  int sh_tab[] = {5,7,2,4,6,1,3};
  int fl_tab[] = {3,1,6,4,2,7,5};
  /* tables for pretty printout only */
  char root_tab[]={'A','B','C','D','E','F','G'};
  char acc_tab[][3] ={"bb","b ","  ","# ","x "};
  char c1[6],c2[6],c3[6];

  /* nop if no transposition is wanted */
  if (nht==0) {
    key->add_transp=0;
    for (i=0;i<7;i++) key->add_acc[i]=0;
    return;
  }

  /* get new sharps_flats and shift of numeric pitch; copy to key */
  sf_old   = key->sf;
  root_old = key->root;
  root_acc = key->root_acc;
  shift_key (sf_old, nht, &sf_new, &add_t);
  key->sf = sf_new;
  key->add_transp = add_t;

  /* set up table for conversion of accidentals */
  for (i=0;i<7;i++) {
    j=i+add_t;
    j=(j+70)%7;
    acc_old=0;
    if ( sf_old >= sh_tab[i]) acc_old=1;
    if (-sf_old >= fl_tab[i]) acc_old=-1;
    acc_new=0;
    if ( sf_new >= sh_tab[j]) acc_new=1;
    if (-sf_new >= fl_tab[j]) acc_new=-1;
    key->add_acc[i]=acc_new-acc_old;
  }

  /* printout keysig change */
  if (verbose>=3) {
    i=root_old;
    j=i+add_t;
    j=(j+70)%7;
    acc_old=0;
    if ( sf_old >= sh_tab[i]) acc_old=1;
    if (-sf_old >= fl_tab[i]) acc_old=-1;
    acc_new=0;
    if ( sf_new >= sh_tab[j]) acc_new=1;
    if (-sf_new >= fl_tab[j]) acc_new=-1;
    strcpy(c3,"s"); if (nht==1 || nht==-1) strcpy(c3,"");
    strcpy(c1,""); strcpy(c2,"");
    if (acc_old==-1) strcpy(c1,"b"); if (acc_old==1) strcpy(c1,"#");
    if (acc_new==-1) strcpy(c2,"b"); if (acc_new==1) strcpy(c2,"#");
    printf ("Transpose root from %c%s to %c%s (shift by %d halftone%s)\n",
            root_tab[i],c1,root_tab[j],c2,nht,c3);
  }

  /* printout full table of transformations */
  if (verbose>=4) {
    printf ("old & new keysig    conversions\n");
    for (i=0;i<7;i++) {
      j=i+add_t;
      j=(j+70)%7;
      acc_old=0;
      if ( sf_old >= sh_tab[i]) acc_old=1;
      if (-sf_old >= fl_tab[i]) acc_old=-1;
      acc_new=0;
      if ( sf_new >= sh_tab[j]) acc_new=1;
      if (-sf_new >= fl_tab[j]) acc_new=-1;
      printf("%c%s-> %c%s           ", root_tab[i],acc_tab[acc_old+2],
             root_tab[j],acc_tab[acc_new+2]);
      for (a=-1;a<=1;a++) {
        b=a+key->add_acc[i];
        printf ("%c%s-> %c%s  ", root_tab[i],acc_tab[a+2],
                root_tab[j],acc_tab[b+2]);
      }
      printf ("\n");
    }
  }

}

/* ----- do_transpose: transpose numeric pitch and accidental --- */
void do_transpose (struct KEYSTR key, int *pitch, int *acc)
{
  int pitch_old,pitch_new,sf_old,sf_new,acc_old,acc_new,i,j;

  pitch_old = *pitch;
  acc_old   = *acc;
  acc_new   = acc_old;
  sf_old    = key.sf;
  pitch_new=pitch_old+key.add_transp;
  i=(pitch_old+70)%7;
  j=(pitch_new+70)%7;

  if (acc_old) {
    if (acc_old==A_DF) sf_old=-2;
    if (acc_old==A_FT) sf_old=-1;
    if (acc_old==A_NT) sf_old=0 ;
    if (acc_old==A_SH) sf_old=1;
    if (acc_old==A_DS) sf_old=2;
    sf_new=sf_old+key.add_acc[i];
    if (sf_new==-2) acc_new=A_DF;
    if (sf_new==-1) acc_new=A_FT;
    if (sf_new== 0) acc_new=A_NT;
    if (sf_new== 1) acc_new=A_SH;
    if (sf_new== 2) acc_new=A_DS;
  }
  else {
    acc_new=0;
  }
  *pitch = pitch_new;
  *acc   = acc_new;
}


/* ----- gch_transpose: transpose guitar chord string in gch --- */
void gch_transpose (string* gch, struct KEYSTR key)
{
  char *q,*r;
  char* gchtrans;
  int root_old,root_new,sf_old,sf_new,ok;
  char root_tab[]={'A','B','C','D','E','F','G'};
  char root_tub[]={'a','b','c','d','e','f','g'};

  if (!transposegchords || (halftones==0)) return;

  q = (char*)gch->c_str();
  gchtrans = (char*)alloca(sizeof(char)*gch->length());
  r = gchtrans;

  for (;;) {
    while (*q==' ' || *q=='(') { *r=*q; q++; r++; }
    if (*q=='\0') break;
    ok=0;
    if (strchr("ABCDEFG",*q)) {
      root_old=*q-'A'; q++; ok=1;
    } else if (strchr("abcdefg",*q)) {
      root_old=*q-'a'; q++; ok=2;
    } else {
      root_old=key.root;
    }

    if (ok) {
      sf_old=0;
      if (*q=='b') { sf_old=-1; q++; }
      if (*q=='#') { sf_old= 1; q++; }
      root_new=root_old+key.add_transp;
      root_new=(root_new+28)%7;
      sf_new=sf_old+key.add_acc[root_old];
      if (ok==1) { *r=root_tab[root_new]; r++; }
      if (ok==2) { *r=root_tub[root_new]; r++; }
      if (sf_new==-1) { *r='b'; r++; }
      if (sf_new== 1) { *r='#'; r++; }
    }

    while (*q!=' ' && *q!='/' && *q!='\0') {*r=*q; q++; r++; }
    if (*q=='/') {*r=*q; q++; r++; }

  }

  *r='\0';
  /*|   printf("tr_ch: <%s>  <%s>\n", gch, str);   |*/

  *gch = gchtrans;
}


/* ----- append_key_change: append change of key to sym list ------ */
void append_key_change(struct KEYSTR oldkey, struct KEYSTR newkey)
{
    int n1,n2,t1,t2,kk;

    n1=oldkey.sf;
    t1=A_SH;
    if (n1<0) { n1=-n1; t1=A_FT; }
    n2=newkey.sf;
    t2=A_SH;

    if (newkey.ktype != oldkey.ktype) {      /* clef change */
        kk=add_sym(CLEF);
        symv[ivc][kk].u=newkey.ktype;
        symv[ivc][kk].v=1;
    }

    if (n2<0) { n2=-n2; t2=A_FT; }
    if (t1==t2) {              /* here if old and new have same type */
        if (n2>n1) {                 /* more new music ..*/
            kk=add_sym(KEYSIG);        /* draw all of them */
            symv[ivc][kk].u=1;
            symv[ivc][kk].v=n2;
            symv[ivc][kk].w=100;
            symv[ivc][kk].t=t1;
        }
        else if (n2<n1) {            /* less new music .. */
            kk=add_sym(KEYSIG);          /* draw all new music and neutrals */
            symv[ivc][kk].u=1;
            symv[ivc][kk].v=n1;
            symv[ivc][kk].w=n2+1;
            symv[ivc][kk].t=t2;
        }
        else return;
    }
    else {                     /* here for change s->f or f->s */
        kk=add_sym(KEYSIG);          /* neutralize all old music */
        symv[ivc][kk].u=1;
        symv[ivc][kk].v=n1;
        symv[ivc][kk].w=1;
        symv[ivc][kk].t=t1;
        kk=add_sym(KEYSIG);          /* add all new music */
        symv[ivc][kk].u=1;
        symv[ivc][kk].v=n2;
        symv[ivc][kk].w=100;
        symv[ivc][kk].t=t2;
    }

}



"""