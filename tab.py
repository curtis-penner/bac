# Copyright 2019 Curtis Penner
import os

import util
from constants import (RHSIMPLE, RHMODERN, RHDIAMOND, RHNONE, RHGRID, RHMODERNBEAMS)
from constants import (BRUMMER_ABC, BRUMMER_1AB, BRUMMER_123)
from constants import (TABFONTDIRS, STAFFHEIGHT)
from constants import (GCHORD, NEWLINE, ESCSEQ)
import common
from log import log
import format
import parse
import cmdline
import voice
import key


args = cmdline.options()
tab_key = key.Key()
voice = voice.Voice()
voices = list()

TAB_prevlen = 0   # no previous notelength


class Tabformat:
    usraddflags = False  # True if user explicitly sets that parameter

    """
    tablature format parameters 
    """
    def __init__(self):
        # Format
        self.addflags = 2   # how many more flags in tabrhythm 
        self.rhstyle = RHSIMPLE   # rhythm flag style
        self.allflags = 0   # whether all flags are to be printed 
        self.firstflag = 0   # whether only changing flags are to be printed
        self.ledgeabove = 0   # bourdon ledger lines above symbol? 
        self.flagspace = 0.0   # additional space between flag and tab system 
        self.gchordspace = 10   # distance between gchord and tablature 
        self.brummer = BRUMMER_ABC   # sytle for brumemr in german tab
        self.germansepline = 1   # draw separator line in German tab
        # Font
        self.size = 14   # font size and line distance
        self.scale = 1.0   # scale factor for font 
        self.frfont = "frFrancisque"   # font for frenchtab 
        self.itfont = "itTimes"   # font for italiantab 
        self.defont = "deCourier"   # font for germantab

    @staticmethod
    def _parse_voice(line):
        try:
            assert line
            values = line.split(' ', 1)
            assert '=' not in values[0]

        except AssertionError as ae:
            print(ae)
            exit(-1)

    def read_tab_format(self, line):
        """
        Reads a tab format line
        format parameters are stored in the instance of tabformat.
        Returns true, if the parameter is a tab format specifier.

        :param line: 
        :return:
        """
        self._parse_voice(line)
        key, value = line.split(' ', 1)
        value = value.strip()

        if key == 'tabfontfsize'and value.isnumber():
            val = float(value)
            if val <= 0:
                msg = f"illegal value for 'tabfontsize': {value}"
                log.error(msg)
            self.size = val
            return True

        if key == "tabfontscale" and value.isnumber():
            val = float(value)
            if val <= 0.0:
                msg = f"illegal value for 'tabfontscale': {value}"
                log.error(msg)
            self.scale = val
            return True

        if key == "tabaddflags" and value.isdigit():
            self.addflags = int(value)
            Tabformat.usraddflags = True
            return True

        if key == "tabrhstyle":
            if value == "simple":
                self.rhstyle = RHSIMPLE
                if not Tabformat.usraddflags:
                    self.addflags = 2
                return True
            elif value == "grid":
                self.rhstyle = RHGRID
                if not Tabformat.usraddflags:
                    self.addflags = 2
                return True
            elif value == "diamond":
                self.rhstyle = RHDIAMOND
                if not Tabformat.usraddflags:
                    self.addflags = 0
                return True
            elif value == "modernbeams":
                self.rhstyle = RHMODERNBEAMS
                if not Tabformat.usraddflags:
                    self.addflags = 0
                return True
            elif value == "modern":
                self.rhstyle = RHMODERN
                if not Tabformat.usraddflags:
                    self.addflags = 0
                return True
            elif value == "none":
                self.rhstyle = RHNONE
                if not Tabformat.usraddflags:
                    self.addflags = 0
                return True
            else:
                return False
        if key == "taballflags":
            self.allflags = format.g_logv(value)
            return True
        if key == "tabfirstflag":
            self.firstflag = format.g_logv(value)
            return True
        if key == "tabfontfrench":
            if value.startwith("fr") or value == "none":
                self.frfont = value 
            else: 
                self.frfont = ''.join(['fr', value])
                return True
        if key == "tabfontitalian":
            if value.startswith("it") or value == "none":
                self.itfont = value 
            else: 
                self.itfont = ''.join(['it', value])
                return True
        if key == "tabfontgerman":
            if value.startswith("de") or value == "none":
                self.defont = value 
            else: 
                self.defont = ''.join(['de', value])
                return True
        if key == "tabledgeabove":
            self.ledgeabove = format.g_logv(value)
            return True
        if key == "tabflagspace":
            self.flagspace = format.g_unum(value)
            return True
        if key == "tabgchordspace":
            self.gchordspace = format.g_unum(value)
            return True
        if key == "tabbrummer":
            if value == "ABC":
                self.brummer = BRUMMER_ABC
                return True
            elif value == "1AB":
                self.brummer = BRUMMER_1AB
                return True
            elif value == "123":
                self.brummer = BRUMMER_123
                return True
            else:
                return False
        if key == "tabgermansepline":
            self.germansepline = format.g_logv(value)
            return True

        return False

    def parse_tab_args(self, args):
        """
        parse command line arguments starting with -tab

        :param args:
        """
        if args.tabsize <= 0:
            log.error(f'illegal tablature fontsize: {args.tabsize}')
        if not args.frfont:
            self.frfont = None
        if not args.itfont:
            self.itfont = None
        if not args.defont:
            self.defont = None

    def print_tab_format(self):
        """
        print tablature format parameters

        :param self:
        :return:
        """
        log.info("    selfsize        %d", self.size)
        log.info("    selfscale     %0.1f", self.scale)
        log.info("    tabaddflags        %d", self.addflags)

        if self.rhstyle == RHSIMPLE:
            log.info("    tabrhstyle         simple")
        elif self.rhstyle == RHMODERN:
            log.info("    tabrhstyle         modern")
        elif self.rhstyle == RHDIAMOND:
            log.info("    tabrhstyle         diamond")
        elif self.rhstyle == RHNONE:
            log.info("    tabrhstyle         none")
        elif self.rhstyle == RHGRID:
            log.info("    tabrhstyle         grid")
        elif self.rhstyle == RHMODERNBEAMS:
            log.info("    tabrhstyle         modernbeams")
        log.info(f"    taballflags    {self.allflags}")
        log.info(f"    tabfirstflag   {self.firstflag}")
        log.info(f"    tabfontfrench  {self.frfont}")
        log.info(f"    tabfontitalian {self.itfont}")
        log.info(f"    tabfontgerman  {self.defont}")
        log.info(f"    tabledgeabove  {self.ledgeabove}")
        log.info(f"    tabflagspace   {self.flagspace:.1f}pt")
        log.info(f"    tabgchordspace {self.gchordspace:.1f}pt")
        if self.rhstyle == BRUMMER_ABC:
            log.info("    tabbrummer         ABC")
        elif self.rhstyle == BRUMMER_1AB:
            log.info("    tabbrummer         1AB")
        elif self.rhstyle == BRUMMER_123:
            log.info("    tabbrummer         123")
        log.info(f"    tabgermansepline  {self.germansepline}")

def parse_tab_line(line):
    """ parse a tablature line into music """
    if not voice:
        log.critical("Trying to parse undefined v")
        exit(-1)

    # check for mixing of tablature and music within one line
    voicespec, line = util.get_field_value('V', line)

    if not tab_key.is_tab_key():
        print(f"+++ Error line {common.linenum}: "
              "Tablature and music must not be mixed within one line")

    common.nwline = 0
    nsym0 = len(voice.syms)

    nbr = 0
    p0 = line
    pmx = ''

    tab_type = 0
    p = 0
    while p < len(line):
        tab_type = parse_tab_sym()
        n = len(voices[common.ivc].nsyms)
        i = n-1
        if common.db > 4 and tab_type:
            log.debug(f"     sym[{n-1}] code ({voices[common.ivc].syms[n-1].type},"
                  f"{voices[common.ivc].syms[n-1].u})\n")


        if tab_type == NEWLINE:
            if n > 0 and not common.cfmt.continueall and not common.cfmt.barsperstaff:
                voices[common.ivc].syms[i].eoln = True
                if common.word:
                    voices[ common.ivc].syms[common.last_note].word_end = True
                    common.word = False

        if tab_type == ESCSEQ:
            if common.db > 3:
                log.debug(f"Handle escape sequence <{common.escseq}>")
            if parse.info_field(common.escseq):
                handle_inside_field(itype)

        if (tab_type == REST) {
            if (pplet) {                                     # n-plet can start on rest
                voices[common.ivc].syms[i].p_plet=pplet;
                voices[common.ivc].syms[i].q_plet=qplet;
                voices[common.ivc].syms[i].r_plet=rplet;
                pplet=0;
            }
            last_note=i;                                 # need this so > and < work
            p1=p;
        }

        if (tab_type==NOTE) {
            if (!word) {
                voices[common.ivc].syms[i].word_st=1;
                word=1;
            }
            voices[common.ivc].syms[i].slur_st+=nbr;
            nbr=0;
            if (voice[ivc].end_slur) voices[common.ivc].syms[i].slur_end++;
            voice[ivc].end_slur=0;

            if (pplet) {                                     # start of n-plet
                voices[common.ivc].syms[i].p_plet=pplet;
                voices[common.ivc].syms[i].q_plet=qplet;
                voices[common.ivc].syms[i].r_plet=rplet;
                pplet=0;
            }
            last_note=last_real_note=i;
            p1=p;
        }

        if (word && ((tab_type==BAR)||(tab_type==SPACE))) {
            if (last_real_note>=0) symv[ivc][last_real_note].word_end=1;
            word=0;
        }

        if (!type) {

            if (*p == '-') {                                    # a-b tie
                symv[ivc][last_note].slur_st++;
                voice[ivc].end_slur=1;
                p++;
            }

            else if (*p == '(') {
                p++;
                if (isdigit(*p)) {
                    pplet=*p-'0'; qplet=0; rplet=pplet;
                    p++;
                    if (*p == ':') {
                        p++;
                        if (isdigit(*p)) { qplet=*p-'0';    p++; }
                        if (*p == ':') {
                            p++;
                            if (isdigit(*p)) { rplet=*p-'0';    p++; }
                        }
                    }
                }
                else {
                    nbr++;
                }
            }
            else if (*p == ')') {
                if (last_note>0)
                    symv[ivc][last_note].slur_end++;
                else
                    syntax ("Unexpected tablature symbol",p);
                p++;
            }
            else if (*p == '>') {
                num=1;
                p++;
                while (*p == '>') { num++; p++; }
                if (last_note<0) {
                    syntax ("No note before > sign", p);
                } else {
                    double_note (last_note, num, 1, p1);
                    symv[ivc][last_note].invis = 0;
                }
            }
            else if (*p == '<') {
                num=1;
                p++;
                while (*p == '<') { num++; p++; }
                if (last_note<0) {
                    syntax ("No note before < sign", p);
                } else {
                    double_note (last_note, num, -1, p1);
                    symv[ivc][last_note].invis = 0;
                }
#
#
# def only_tabvoices(voices):
#     """
#     check whether all selected voices are tablature
#
#     :return bool: search music lines (false); no music line found (true)
#     """
#     for voice in voices:
#         return not (voice.select and not tab_key.is_tab_key(voice.key))
#
# }
#                 else if (*p == '*')         # ignore stars for now
#                     p++;
#                 else if (*p == '!')         # ditto for '!'
#                     p++;
#                 else {
#                     if (*p != '\0')
#                         sprintf (msg, "Unexpected tablature symbol \'%c\'", *p);
#                     else
#                         sprintf (msg, "Unexpected end of line");
#                     syntax (msg, p);
#                     p++;
#                 }
#             }
#         }
#
#         # maybe set end-of-line marker, if music were added
#         n=voice[ivc].nsym;
#
#         if (n>nsym0) {
#             symv[ivc][n-1].eoln=1;
#             if (type==CONTINUE)         symv[ivc][n-1].eoln=0;
#             if (cfmt.barsperstaff)    symv[ivc][n-1].eoln=0;
#             if (cfmt.continueall)     symv[ivc][n-1].eoln=0;
#         }
#
#
#
#         # break words at end of line
#         if (word && (symv[ivc][n-1].eoln==1)) {
#             symv[ivc][last_note].word_end=1;
#             word=0;
#         }
#
#         return TO_BE_CONTINUED;
#     }
#
#
def parse_tab_sym():
    """
    parse a tablature symbol and return its type
    :return int:
    """
    i = 0
    if parse_gchord():
        return GCHORD;
    if parse_tabdeco():
        return DECO;
    if parse_bar():
        return BAR;
    if parse_space():
        return SPACE;
    if parse_nl():
        return NEWLINE;
    i = parse_esc()
    if i:
        return i;
    i=parse_tab_chord()
    if i:
        return i;
    return i
#
#     #*************************************************************************
#      * parse_tab_chord - parses one chord of tablature and adds it to symbols
#      *************************************************************************
#     int parse_tab_chord(void)
#     {
#         int k,chord,type,sl1,sl2,j,i;
#         int m,npitch;                            #notecounter in chord
#         int course,length,invis;     #symbol characteristics
#         char *q,*q0;
#         // int ndeco;            #chord decorations
#         const char* tabdecos = "'UVX*#";    #decos that may appear inside chord
#         int notedeco;                            #note decoration inside chord
#         GchordList::iterator ii;
#
#         # not yet used variables from parse_note():
#          *int ngr,pgr[30],agr[30];
#
#
#         # explicit calls to parse_gchord() and parse_tabdeco() not needed
#          * because no grace notes in tablature allowed
#          * gchords and decos are preparsed in parse_tab_sym()
#
#
#         # determine if chord
#         chord=0;
#         q=p;
#         if (*p=='[') { chord=1; p++; }
#
#         # note or rest?
#         type=0;
#         if (strchr(",abcdefghijklmnopqrstuvwy{", *p)) type=NOTE;
#         //if (!strncmp("!ten(!",p,6) || !strncmp("!ten)!",p,6)) type=NOTE;
#         if (chord && strchr(tabdecos,*p)) type=NOTE;
#         if (chord && (*p=='(')) type=NOTE;
#         if (chord && (*p==')')) type=NOTE;     # this just for better error msg
#         if ((*p=='z')||(*p=='x')) type=REST;
#         if (*p=='Z') type=BREST;
#         if (!type) return 0;
#
#         k=add_sym(type);                                         # add new symbol to list
#
#         symv[ivc][k].dc.n=prep_deco.n;             # copy over pre-parsed stuff
#         for (i=0;i<prep_deco.n;i++)
#             symv[ivc][k].dc.t[i]=prep_deco.t[i];
#         prep_deco.clear();
#         if (!prep_gchlst.empty()) {
#             for (ii=prep_gchlst.begin(); ii!=prep_gchlst.end(); ii++) {
#                 symv[ivc][k].gchords->push_back(*ii);
#             }
#             prep_gchlst.clear();
#         }
#
#         q0=p;
#         if (type==BREST) {
#             p++;
#             symv[ivc][k].lens[0] = (WHOLE*voice[ivc].meter.meter1)/voice[ivc].meter.meter2;
#             symv[ivc][k].len = symv[ivc][k].lens[0];
#             symv[ivc][k].fullmes = parse_brestnum();
#             symv[ivc][k].npitch=1;
#         }
#         else if (type==REST) {
#             p++;
#             length = parse_tab_length();
#             # if not specified, length is inherited from previous chord
#             if (!length) {
#                 if (!TAB_prevlen) TAB_prevlen = voice[ivc].meter.dlen;
#                 length = TAB_prevlen;
#                 invis = 1;
#             } else {
#                 if (*q0=='z') #visible rest
#                     invis = 0;
#                 else                 #'x' is invisible rest
#                     invis = 1;
#                 TAB_prevlen = length;
#             }
#             symv[ivc][k].npitch = 1;
#             symv[ivc][k].lens[0] = length;
#             symv[ivc][k].invis = invis;
#             if (db>3) printf ("    parsed rest, length %d/%d = 1/%d\n",
#                                                 symv[ivc][k].lens[0],BASE,BASE/symv[ivc][k].lens[0]);
#         } else {
#             # type==NOTE
#             # get pitch and length
#             m=npitch=0; # current note index and actual number of notes
#             sl1=sl2=0;
#             course = 1;
#             length = 0;
#             notedeco = 0;
#             for (;;) {
#
#                 # illegal music in chord
#                 if (chord && !isalpha(*p) && !isdigit(*p) &&
#                         !strchr(",(){}]/",*p) && !strchr(tabdecos,*p) &&
#                         strncmp("!ten(!",p,6) && strncmp("!ten)!",p,6)) {
#                     syntax ("Unexpected symbol in chord",p);
#                     return type;
#                 }
#                 if (*p=='}') {
#                     syntax ("Unmatched closing bourdon brace",p);
#                     return type;
#                 }
#
#                 # commas mark empty courses
#                 if (*p==',') {
#                     course++; p++;
#                     continue;
#                 }
#
#                 # start slur
#                 if (chord && (*p=='(')) {
#             if (*(p+1)==',')
#                 syntax ("Slurs on empty courses not supported",p);
#             sl1++;
#             symv[ivc][k].sl1[m]=sl1;
#                     p++;
#                 }
#
#                 # start or end tenuto
#                 if (chord && 0 == strncmp(p,"!ten(!",6)) {
#                     symv[ivc][k].ten_st++;
#                     symv[ivc][k].ten1[m]=1;
#                     p += 6; continue;
#                 }
#                 if (chord && 0 == strncmp(p,"!ten)!",6)) {
#                     symv[ivc][k].ten_end++;
#                     symv[ivc][k].ten2[m]=1;
#                     p += 6; continue;
#                 }
#
#                 # decos within chord
#                 if (chord) {
#                     # single character decos
#                     switch (*p) {
#                     case '\'':
#                         notedeco=D_TABACC; p++;
#                         break;
#                     case 'X':
#                         notedeco=D_TABX; p++;
#                         break;
#                     case 'U':
#                         notedeco=D_TABU; p++;
#                         break;
#                     case 'V':
#                         notedeco=D_TABV; p++;
#                         break;
#                     case '*':
#                         notedeco=D_TABSTAR; p++;
#                         break;
#                     case '#':
#                         notedeco=D_TABCROSS; p++;
#                         break;
#                     case 'L':
#                         notedeco=D_TABOLINE; p++;
#                         break;
#                     }
#                 }
#
#                 # interpret tab letter
#                 # course is stored as "pitch" and letter as "accidental"
#                 # stopped strings
#                 if (islower(*p)) {
#                     symv[ivc][k].pits[m] = course;
#                     symv[ivc][k].accs[m] = *p;
#                     course++;
#                     p++;
#                     npitch++;
#                 }
#                 # bass strings (bourdons or "diapasons")
#                 else if (*p=='{') {
#                     int bassnumber;
#                     char *qq;
#
#                     course = 7;
#                     p++;
#                     while ((*p!='}') && (*p!='\0')) {
#                         if (*p==',') {
#                             course++;
#                         } else if (isalpha(*p)) {
#                             symv[ivc][k].pits[m] = course;
#                             symv[ivc][k].accs[m] = tolower(*p);
#                             npitch++;
#                             break;
#                         } else if (isdigit(*p)) {
#                             bassnumber = atoi(p);
#                             symv[ivc][k].pits[m] = course;
#                             # bass numbers are coded in A-N
#                             symv[ivc][k].accs[m] = bassnumber-1+(int)'A';
#                             npitch++;
#                             break;
#                         }
#                         p++;
#                     }
#                     # position p after end of bourdon
#                     qq = strpbrk(p,"}|] ");
#                     if (!qq || (*qq!='}')) {
#                         if (qq) p=qq;
#                         syntax ("Bourdon not closed", q);
#                         return type;
#                     }
#                     p=qq+1;
#                 }
#
#                 # end slur
#                 if (chord && (*p==')')) {
#                     sl2++;
#                     symv[ivc][k].sl2[m]=sl2;
#                     p++;
#                 }
#
#                 # interpret length
#                 if (isdigit(*p) || (*p=='/'))
#                     length = parse_tab_length();
#
#                 # ties
#                 symv[ivc][k].ti1[m] = symv[ivc][k].ti2[m] = 0;
#                 for (j=0;j<ntinext;j++)
#                     if (tinext[j]==symv[ivc][k].pits[m]) symv[ivc][k].ti2[m]=1;
#                 if (chord && (*p=='-')) {symv[ivc][k].ti1[m]=1; p++;}
#
#                 # tie again (?)
#                 if (chord && (*p=='-')) {symv[ivc][k].ti1[m]=1; p++;}
#
#                 # copy over preparsed note deco for this last note
#                 symv[ivc][k].tabdeco[m]=notedeco;
#                 notedeco=0;
#
#                 # increase note index for next loop
#                 m++;
#
#                 # tabchord end
#                 if ((!chord) || (*p==']') || (*p=='\0')) {
#
#                     # set length for all notes in chord...
#                     if (!length) {
#                         if (!TAB_prevlen) TAB_prevlen = voice[ivc].meter.dlen;
#                         length = TAB_prevlen;
#                         invis = 1;
#                     } else {
#                         invis = 0;
#                         TAB_prevlen = length;
#                     }
#                     for (j=0;j<m;j++) symv[ivc][k].lens[j] = length;
#                     symv[ivc][k].invis = invis;
#
#                     # ... and stop parsing
#                     if (!chord)
#                         break;
#                     else if (*p==']') {
#                         p++;
#                         break;
#                     }
#                     else if (*p=='\0') {
#                         if (chord) syntax ("Chord not closed", q);
#                         return type;
#                     }
#                 }
#             }
#             ntinext=0;
#             for (j=0;j<m;j++)
#                 if (symv[ivc][k].ti1[j]) {
#                     tinext[ntinext]=symv[ivc][k].pits[j];
#                     ntinext++;
#                 }
#
#             # check for flag (rest) without chord
#             if (!symv[ivc][k].accs[0])
#                         symv[ivc][k].npitch = 0;
#             else
#                 symv[ivc][k].npitch=npitch;
#         }
#
#         # add carryover from > or <
#         if (carryover != 0) {
#             for (m=0;m<symv[ivc][k].npitch;m++) {
#                 if (symv[ivc][k].lens[m]+carryover<=0)
#                     syntax("> leads to zero or negative note length",q0);
#                 else
#                     symv[ivc][k].lens[m] += carryover;
#             }
#             symv[ivc][k].invis = 0;
#         }
#         carryover=0;
#
#         if (db>3)
#             printf ("    parsed tab chord, voices %d, top course %d,"
#                             " top letter <%c>, length %d\n",
#                             symv[ivc][k].npitch, symv[ivc][k].pits[0],
#                             symv[ivc][k].accs[0], symv[ivc][k].lens[0]);
#
#         symv[ivc][k].yadd=0;
#         if (type!=BREST)
#             identify_note (&symv[ivc][k],q0);
#
#         return type;
#     }
#
#
#     #*************************************************************************
#      * parse_tabdeco - parse decorations for entire chord
#      *     decos are stored in global variable prep_deco
#      *     returns the number of decorations
#      *************************************************************************
#     int parse_tabdeco ()
#     {
#         int deco,n;
#         # mapping abc code to decorations
#         # for no abbreviation, set abbrev=0; for no !..! set fullname=""
#         struct s_deconame { int index; char abbrev; const char* fullname; };
#         static struct s_deconame deconame[] = {
#             {D_HOLD,             'H', "!fermata!"},
#             {D_TABTRILL,     'T', "!trill!"},
#             {D_SEGNO,            'S', "!segno!"},
#             {D_CODA,             'O', "!coda!"},
#             {D_INDEX,            '.', ""},
#             //{D_MEDIUS,         ':', ""}, #needs special treatment (repeat sign)
#             {D_ANNULARIUS, ';', ""},
#             {D_POLLIX,         '+', ""},
#             {D_TABACC,         '\'', ""},
#             {D_TABX,             'X', ""},
#             {D_TABU,             'U', ""},
#             {D_TABV,             'V', ""},
#             {D_TABSTAR,        '*', ""},
#             {D_TABCROSS,     '#', ""},
#             {D_TABOLINE,     'L', ""},
#             {D_STRUMUP,         0, "!strumup!"},
#             {D_STRUMDOWN,     0, "!strumdown!"},
#             {D_DYN_PP,            0,    "!pp!"},
#             {D_DYN_P,             0,    "!p!"},
#             {D_DYN_MP,            0,    "!mp!"},
#             {D_DYN_MF,            0,    "!mf!"},
#             {D_DYN_F,             0,    "!f!"},
#             {D_DYN_FF,            0,    "!ff!"},
#             {D_DYN_SF,            0,    "!sf!"},
#             {D_DYN_SFZ,         0,    "!sfz!"},
#             {0, 0, ""} #end marker
#         };
#         struct s_deconame* dn;
#
#         n=0;
#
#         for (;;) {
#             deco=0;
#
#             #special treatment for ambiguous decos (':' also means repeat)
#             if ((*p == ':') && (*(p+1) != ':') && (*(p+1) != '|')) {
#                 deco = D_MEDIUS;
#                 p++;
#             }
#             #check for fullname deco
#             else if (*p == '!') {
#                 int slen;
#                 char* q;
#                 q = strchr(p+1,'!');
#                 if (!q) {
#                     syntax ("Deco sign '!' not closed",p);
#                     p++;
#                     return n;
#                 } else {
#                     slen = q+1-p;
#                     #lookup in table
#                     for (dn=deconame; dn->index; dn++) {
#                         if (0 == strncmp(p,dn->fullname,slen)) {
#                             deco = dn->index;
#                             break;
#                         }
#                     }
#                     if (!deco) syntax("Unknown tabdeco",p+1);
#                     p += slen;
#                 }
#             }
#             #check for abbrev deco
#             else {
#                 for (dn=deconame; dn->index; dn++) {
#                     if (dn->abbrev && (*p == dn->abbrev)) {
#                         deco = dn->index;
#                         p++;
#                         break;
#                     }
#                 }
#             }
#
#             if (deco) {
#                 prep_deco.add(deco);
#                 n++;
#             }
#             else
#                 break;
#         }
#
#         return n;
#     }
#
#
#     #*************************************************************************
#      * parse_tab_length - parse length specifer for note or rest
#      *     if no length is specified, zero is returned
#      *************************************************************************
#     int parse_tab_length (void)
#     {
#         int len,fac;
#
#         if ((!isdigit(*p)) && (*p!='/')) {
#             len = 0;
#         } else {
#             len=voice[ivc].meter.dlen;                    # start with default length
#             if (len<=0) {
#                 syntax("got len<=0 from current v", p);
#                 printf("Cannot proceed without default length. Emergency stop.\n");
#                 exit(1);
#             }
#
#             if (isdigit(*p)) {                                 # multiply note length
#                 fac=parse_uint ();
#                 #if (fac==0) fac=1;
#                 len *= fac;
#             }
#             if (*p=='/') {                                     # divide note length
#                 while (*p=='/') {
#                     p++;
#                     if (isdigit(*p))
#                         fac=parse_uint();
#                     else
#                         fac=2;
#                     if (len%fac) {
#                         syntax ("Bad length divisor", p-1);
#                         return len;
#                     }
#                     len=len/fac;
#                 }
#             }
#         }
#
#         return len;
#
#     }
#
#
#     #*************************************************************************
#      * draw_tab_symbols - draws tablature symbols at proper position on staff
#      *************************************************************************
#     void draw_tab_symbols (FILE *fp, float bspace, float *bpos, int is_top)
#     {
#         int i,j,inbeam,fermata,nwl,lastlen;
#         float x,botnote,gchy;
#         struct BEAM bm;
#         # not yet used variables from draw_symbols():
#          *float y,top,xl,d,botpos;
#
#
#         inbeam=do_words=0;
#         botnote=0;
#         nwl=0;
#         lastlen=0;
#
#         for (i=0;i<nsym;i++) {                                            # draw the music
#
#             fermata=0;
#             for (j=0;j<NWLINE;j++)
#                 if (sym[i].wordp[j]) {
#                     if (j+1>nwl) nwl=j+1;
#                 }
#             if (nbuf+100>BUFFSZ)
#                 rx ("PS output exceeds reserved space per staff",
#                         " -- increase BUFFSZ1");
#             x=sym[i].x;
#             gchy=-tabfmt.gchordspace;
#
#             switch (sym[i].type) {
#
#             case NOTE:
#                 draw_tabnote(x,&sym[i],&gchy);
#             # check for fermata (supresses tabflag)
#             for (j=0;j<sym[i].dc.n;j++)
#             if (sym[i].dc.t[j]==D_HOLD) {
#                 fermata=1;
#                 break;
#             }
#             # check for beam
#                 if (((tabfmt.rhstyle==RHGRID) || (tabfmt.rhstyle==RHMODERNBEAMS))
#                         && sym[i].word_st && !sym[i].word_end) {
#                     if (calculate_tabbeam (i,&bm)) inbeam=1;
#                 }
#                 if (tabfmt.firstflag) {
#                     if (lastlen!=sym[i].len && !fermata) {
#                         draw_tabflag(x,&sym[i]);
#                         lastlen=sym[i].len;
#                     } else {
#                         PUT0("\n");
#                     }
#                     if (fermata)
#                         lastlen=0;
#                     break;
#                 }
#                 if ((!sym[i].invis || tabfmt.allflags) && !fermata && !inbeam) {
#                     draw_tabflag(x,&sym[i]);
#                 } else if (inbeam) {
#                     if (i==bm.i2) {
#                         inbeam=0;
#                 draw_tabbeams(&bm, tabfmt.rhstyle);
#                     }
#                 } else {
#                     PUT0("\n");
#             }
#                 break;
#
#             case REST:
#             for (j=0;j<sym[i].dc.n;j++)
#             if (sym[i].dc.t[j]==D_HOLD) {
#                 fermata=1;
#                 break;
#             }
#                 if (!sym[i].invis && !fermata)
#                     draw_tabrest(x,&sym[i]);
#                 break;
#
#             case BREST:
#                 draw_tabbrest(x,&sym[i]);
#                 break;
#
#             case BAR:
#                 if (sym[i].v) set_ending(i);
#                 draw_tabbar (x,&sym[i]);
#                 lastlen=0;
#                 break;
#
#             case TIMESIG:
#                 draw_tabtimesig (x,&sym[i]);
#                 break;
#
#             case INVISIBLE:
#                 break;
#
#             case CLEF:
#             case KEYSIG:
#                 # have no meaning in tablature
#                 break;
#
#             default:
#                 printf (">>> cannot draw symbol type %d\n", sym[i].type);
#             }
#
#         # chord and bar decorations
#         draw_tabdeco(x,&sym[i],&gchy);
#
#             sym[i].gchy=gchy-cfmt.gchordfont.size;;
#         }
#
#         if (ivc==ivc0) draw_tabbarnums (fp);
#
#         if (tabfmt.rhstyle!=RHNONE) draw_tabnplets();
#
#         draw_tabslurs();
#         draw_tabtenutos();
#
#         # draw guitar chords
#         if (voice[ivc].do_gch) {
#             int istablature = 1;
#             set_font(fp,cfmt.gchordfont,0);
#             draw_gchords(istablature);
#         }
#
#         #|     if (is_top) draw_endings (); |
#         if (ivc==ivc0) draw_tabendings ();
#         num_ending=0;
#
#         # >>>>>>> not yet implemented
#         botpos=-bspace;
#         if (botnote<botpos) botpos=botnote;
#
#         if (nwl>0) draw_vocals (fp,nwl,botnote,bspace,&botpos);
#
#         *bpos=botpos;
#         <<<<<<<
#
#         # add space below tab line
#         # (do something more clever some day)
#         *bpos = -(bspace + tabfont.size);
#     }
#
#
#     #*************************************************************************
#      * draw_tabnote - draws notes of chord at position x
#      *************************************************************************
#     void draw_tabnote (float x, struct SYMBOL *s, float* gchy)
#     {
#         int j,nbourdon;
#         #warning about bourdon suppression already printed?
#         static int bourdonwarning=0;
#
#         switch (voice[ivc].key.ktype) {
#         case FRENCHTAB:
#             nbourdon = 0;
#             for (j=0;j<s->npitch;j++) {
#                 if (s->pits[j] < 7) {
#                     PUT3("%.1f %d (%c) tabfshow ", x, s->pits[j], s->accs[j]);
#                 } else {
#                     if (islower(s->accs[j])) {
#                         # bourdons on fingerboard
#                         if (!tabfmt.ledgeabove)
#                             PUT4("%.1f %d %d (%c) tabfbourdon ", x, nbourdon, s->pits[j]-7, s->accs[j]);
#                         else
#                             PUT4("%.1f %d %d (%c) tabf1bourdon ", x, nbourdon, s->pits[j]-7, s->accs[j]);
#                         nbourdon++;
#                     } else {
#                         # long bass strings
#                         PUT2("%.1f 7.4 (%c) tabfshow ", x, s->accs[j]);
#                     }
#                     # extra space for guitar chords
#                     *gchy=*gchy+2-tabfont.size;
#                 }
#             }
#             break;
#         case FRENCH5TAB:
#             for (j=0;j<s->npitch;j++) {
#                 #five+one courses only
#                 if (s->pits[j] < 7) {
#                     PUT3("%.1f %d (%c) tabfshow ", x, s->pits[j]+1, s->accs[j]);
#                     # extra space for guitar chords
#                     if (s->pits[j] == 6) *gchy=*gchy+2-tabfont.size;
#                 } else if (!bourdonwarning) {
#                     bourdonwarning=1;
#                     std::cerr << "Warning: french5tab only supports 6 courses" << std::endl;
#                 }
#             }
#             break;
#         case FRENCH4TAB:
#             for (j=0;j<s->npitch;j++) {
#                 #four+one courses only
#                 if (s->pits[j] < 6) {
#                     PUT3("%.1f %d (%c) tabfshow ", x, s->pits[j]+2, s->accs[j]);
#                     # extra space for guitar chords
#                     if (s->pits[j] == 5) *gchy=*gchy+2-tabfont.size;
#                 } else if (!bourdonwarning) {
#                     bourdonwarning=1;
#                     std::cerr << "Warning: french4tab only supports 5 courses" << std::endl;
#                 }
#             }
#             break;
#         case SPANISHTAB:
#             for (j=0;j<s->npitch;j++) {
#                 #six courses only
#                 if (s->pits[j] < 7) {
#                     PUT3("%.1f %d (%c) tabsshow ", x, s->pits[j], s->accs[j]);
#                 } else if (!bourdonwarning) {
#                     bourdonwarning=1;
#                     std::cerr << "Warning: diapasons are ignored in spanishtab" << std::endl;
#                 }
#             }
#             break;
#         case SPANISH5TAB:
#             for (j=0;j<s->npitch;j++) {
#                 #five courses only
#                 if (s->pits[j] < 6) {
#                     PUT3("%.1f %d (%c) tabsshow ", x, s->pits[j]+1, s->accs[j]);
#                 } else if (!bourdonwarning) {
#                     bourdonwarning=1;
#                     std::cerr << "Warning: spanish5tab/banjo5tab only supports 5 courses" << std::endl;
#                 }
#             }
#             break;
#         case SPANISH4TAB:
#             for (j=0;j<s->npitch;j++) {
#                 #four courses only
#                 if (s->pits[j] < 5) {
#                     PUT3("%.1f %d (%c) tabsshow ", x, s->pits[j]+2, s->accs[j]);
#                 } else if (!bourdonwarning) {
#                     bourdonwarning=1;
#                     std::cerr << "Warning: spanish4tab/banjo4tab/ukuleletab only supports 4 courses" << std::endl;
#                 }
#             }
#             break;
#         case ITALIANTAB:
#             for (j=0;j<s->npitch;j++) {
#                 #six courses only
#                 if (s->pits[j] < 7) {
#                     PUT3("%.1f %d (%c) tabsshow ", x, 7-s->pits[j], s->accs[j]);
#                 } else if (!bourdonwarning) {
#                     bourdonwarning=1;
#                     std::cerr << "Warning: diapasons are ignored in italiantab" << std::endl;
#                 }
#             }
#             break;
#         case ITALIAN7TAB:
#             for (j=0;j<s->npitch;j++) {
#                 if (s->pits[j] < 7) {
#                     PUT3("%.1f %d (%c) tabsshow ", x, 7-s->pits[j], s->accs[j]);
#                 } else {
#                     if (isupper(s->accs[j]) && (s->accs[j]>'G')) {
#                         PUT2("%.1f 0 (%c) tabsshow ", x, s->accs[j]);
#                     } else {
#                         #translate french style bourdons to italian style
#                         if (islower(s->accs[j])) { #fingerboard bourdons
#                             switch (s->pits[j]) {
#                             case 7:    PUT2("%.1f (%c) tabibourdon ", x, s->accs[j]); break;
#                             case 8:    PUT1("%.1f 0 (H) tabsshow ", x); break;
#                             case 9:    PUT1("%.1f 0 (I) tabsshow ", x); break;
#                             case 10: PUT1("%.1f 0 (J) tabsshow ", x); break;
#                             case 11: PUT1("%.1f 0 (K) tabsshow ", x); break;
#                             }
#                         } else {                                    #numbers 4-7
#                             switch (s->accs[j]) {
#                             case 'D': PUT1("%.1f 0 (K) tabsshow ", x); break;
#                             case 'E': PUT1("%.1f 0 (L) tabsshow ", x); break;
#                             case 'F': PUT1("%.1f 0 (M) tabsshow ", x); break;
#                             case 'G': PUT1("%.1f 0 (N) tabsshow ", x); break;
#                             }
#                         }
#                     }
#                 }
#             }
#             break;
#         case ITALIAN8TAB:
#             for (j=0;j<s->npitch;j++) {
#                 if (s->pits[j] < 7) {
#                     PUT3("%.1f %d (%c) tabsshow ", x, 7-s->pits[j], s->accs[j]);
#                 } else {
#                     if (isupper(s->accs[j]) && (s->accs[j]>'G')) {
#                         PUT2("%.1f 0 (%c) tabsshow ", x, s->accs[j]);
#                     } else {
#                         #translate french style bourdons to italian style
#                         if (islower(s->accs[j])) { #fingerboard bourdons
#                             switch (s->pits[j]) {
#                             case 7:    PUT2("%.1f (%c) tabibourdon ", x, s->accs[j]); break;
#                             case 8:    PUT2("%.1f (%c) tabi8bourdon ", x, s->accs[j]); break;
#                             case 9:    PUT1("%.1f 0 (I) tabsshow ", x); break;
#                             case 10: PUT1("%.1f 0 (J) tabsshow ", x); break;
#                             case 11: PUT1("%.1f 0 (K) tabsshow ", x); break;
#                             }
#                         } else {                                    #numbers 4-7
#                             switch (s->accs[j]) {
#                             case 'D': PUT1("%.1f 0 (K) tabsshow ", x); break;
#                             case 'E': PUT1("%.1f 0 (L) tabsshow ", x); break;
#                             case 'F': PUT1("%.1f 0 (M) tabsshow ", x); break;
#                             case 'G': PUT1("%.1f 0 (N) tabsshow ", x); break;
#                             }
#                         }
#                     }
#                 }
#             }
#             break;
#         case ITALIAN5TAB:
#             for (j=0;j<s->npitch;j++) {
#                 #five courses only
#                 if (s->pits[j] < 6) {
#                     PUT3("%.1f %d (%c) tabsshow ", x, 7-s->pits[j], s->accs[j]);
#                 } else if (!bourdonwarning) {
#                     bourdonwarning=1;
#                     std::cerr << "Warning: italian5tab only supports 5 courses" << std::endl;
#                 }
#             }
#             break;
#         case ITALIAN4TAB:
#             for (j=0;j<s->npitch;j++) {
#                 #four courses only
#                 if (s->pits[j] < 5) {
#                     PUT3("%.1f %d (%c) tabsshow ", x, 7-s->pits[j], s->accs[j]);
#                 } else if (!bourdonwarning) {
#                     bourdonwarning=1;
#                     std::cerr << "Warning: italian4tab only supports 4 courses" << std::endl;
#                 }
#             }
#             break;
#         case GERMANTAB:
#             {
#                 for (j=0;j<s->npitch;j++) {
#                     #six courses only
#                     if (s->pits[j] < 7) {
#                         PUT3("%.1f %d (\\%o) tabgshow ", x, j+1, german_tabcode(s->pits[j], s->accs[j]));
#                     } else if (!bourdonwarning) {
#                         bourdonwarning=1;
#                         std::cerr << "Warning: diapasons are ignored in germantab" << std::endl;
#                     }
#                 }
#                 break;
#             }
#         }
#
#     }
#
#     #*************************************************************************
#      * tab_flagnumber - compute number of flags to given length
#      *************************************************************************
#     int tab_flagnumber (int len)
#     {
#         int flags;
#
#         # cannot use SYMBOL.flags because it is truncated at zero
#         if (len>=LONGA)                            flags=-4;
#         else if (len>=BREVIS)                flags=-3;
#         else if (len>=WHOLE)                 flags=-2;
#         else if (len>=HALF)                    flags=-1;
#         else if (len>=QUARTER)             flags=0;
#         else if (len>=EIGHTH)                flags=1;
#         else if (len>=SIXTEENTH)         flags=2;
#         else if (len>=THIRTYSECOND)    flags=3;
#         else if (len>=SIXTYFOURTH)     flags=4;
#         else                                                 flags=0;
#         flags += tabfmt.addflags;
#         return flags;
#     }
#
#     #*************************************************************************
#      * tab_flagspace - return space between tablature system and rhythm flags
#      *************************************************************************
#     float tab_flagspace (struct KEYSTR *key)
#     {
#         float y;
#
#         y = tabfont.size + tabfmt.flagspace;
#         if (key->ktype == ITALIAN7TAB)
#             y += 0.8*tabfont.size;
#         else if (key->ktype == ITALIAN8TAB)
#             y += 1.8*tabfont.size;
#         return y;
#     }
#
#     #*************************************************************************
#      * draw_tabflag - draws flag at position x
#      *************************************************************************
#     void draw_tabflag (float x, struct SYMBOL *s)
#     {
#         int flags;
#         float y;
#
#         y = get_staffheight(ivc,NETTO) + tab_flagspace(&voice[ivc].key);
#         flags = tab_flagnumber(s->len);
#
#         switch (tabfmt.rhstyle) {
#         case RHNONE:
#             #no rhythm flags
#             return;
#             break;
#         case RHSIMPLE:
#         case RHGRID:
#             PUT3("%.1f %.1f %d tabsflag ", x, y, flags);
#             break;
#         case RHDIAMOND:
#             if (flags <= -4)
#                 PUT2("%.1f %.1f tablonga ", x, y);
#             else if (flags == -3)
#                 PUT2("%.1f %.1f tabbrevis ", x, y);
#             else
#                 PUT3("%.1f %.1f %d tabdflag ", x, y, flags);
#             break;
#         case RHMODERN:
#         case RHMODERNBEAMS:
#             if (flags <= -4)
#                 PUT2("%.1f %.1f tablonga ", x, y);
#             else if (flags == -3)
#                 PUT2("%.1f %.1f tabbrevis ", x, y);
#             else
#                 PUT3("%.1f %.1f %d tabmflag ", x, y, flags);
#             break;
#         }
#
#         if (s->dots > 0) {
#             PUT3("%.1f %.1f %d tabdt\n", x+2, y, s->dots);
#         } else {
#             PUT0("\n");
#         }
#     }
#
#     #*************************************************************************
#      * draw_tabrest - draws rest at position x
#      *************************************************************************
#     void draw_tabrest (float x, struct SYMBOL *s)
#     {
#         int flags;
#         float y;
#
#         y = get_staffheight(ivc,NETTO) + tab_flagspace(&voice[ivc].key);
#         flags = tab_flagnumber(s->len);
#
#         switch (tabfmt.rhstyle) {
#         case RHNONE:
#             #no rhythm flags
#             return;
#             break;
#         case RHSIMPLE:
#         case RHGRID:
#             PUT3("%.1f %.1f %d tabsrest ", x, y, flags);
#             break;
#         case RHDIAMOND:
#             if (flags <= -4)
#                 PUT2("%.1f %.1f tablonga ", x, y);
#             else if (flags == -3)
#                 PUT2("%.1f %.1f tabbrevis ", x, y);
#             else
#                 PUT3("%.1f %.1f %d tabdrest ", x, y, flags);
#             break;
#         case RHMODERN:
#         case RHMODERNBEAMS:
#             PUT3("%.1f %.1f %d tabmrest ", x, y, flags);
#             break;
#         }
#
#         if (s->dots > 0) {
#             PUT3("%.1f %.1f %d tabdt\n", x+2, y, s->dots);
#         } else {
#             PUT0("\n");
#         }
#
#     }
#
#     #*************************************************************************
#      * draw_tabbrest - draws multibar rest at position x
#      *************************************************************************
#     void draw_tabbrest (float x, struct SYMBOL *s)
#     {
#         float y;
#
#         y = get_staffheight(ivc,NETTO) + tab_flagspace(&voice[ivc].key);
#
#         #do not care about rhstyle
#         PUT1("(%d) ", s->fullmes);
#         PUT4("%.2f %.2f %.2f %.2f", x, y+9, x, y);
#         PUT0(" tabbrest");
#         PUT0("\n");
#
#     }
#
#     #*************************************************************************
#      * draw_tabbar - draws bar at position x
#      *************************************************************************
#     void draw_tabbar (float x, struct SYMBOL *s)
#     {
#
#         if (s->u==B_SNGL)                                                # draw the bar
#             PUT2("%.1f %.1f tabbar\n", x, get_staffheight(ivc,NETTO));
#         else if (s->u==B_DBL)
#             PUT2("%.1f %.1f tabdbar\n", x, get_staffheight(ivc,NETTO));
#         else if (s->u==B_LREP)
#             PUT4("%.1f %.1f tabfbar1 %.1f %d tabrdots\n",
#                      x, get_staffheight(ivc,NETTO), x+10,
#                      tab_numlines(&voice[ivc].key)-1);
#         else if (s->u==B_RREP) {
#             PUT4("%.1f %.1f tabfbar2 %.1f %d tabrdots\n",
#                      x, get_staffheight(ivc,NETTO), x-10,
#                      tab_numlines(&voice[ivc].key)-1);
#         }
#         else if (s->u==B_DREP) {
#             PUT4("%.1f %.1f tabfbar1 %.1f %d tabrdots\n",
#                      x-1, get_staffheight(ivc,NETTO), x+9,
#                      tab_numlines(&voice[ivc].key)-1);
#             PUT4("%.1f %.1f tabfbar2 %.1f %d tabrdots\n",
#                      x+1, get_staffheight(ivc,NETTO), x-9,
#                      tab_numlines(&voice[ivc].key)-1);
#         }
#         else if (s->u==B_FAT1)
#             PUT2("%.1f %.1f tabfbar1\n", x, get_staffheight(ivc,NETTO));
#         else if (s->u==B_FAT2)
#             PUT2("%.1f %.1f tabfbar2\n", x, get_staffheight(ivc,NETTO));
#         else if (s->u==B_INVIS)
#             ;
#         else
#             printf (">>> dont know how to draw bar type %d\n", s->u);
#
#         PUT0("\n");
#
#     }
#
#     #*************************************************************************
#      * draw_tabbarnums - draws numbers on bar lines
#      *************************************************************************
#     void draw_tabbarnums (FILE *fp)
#     {
#         int i,last,ok,got_note;
#
#         last=0;
#         got_note=0;
#         for (i=0;i<nsym;i++) {
#             if ((sym[i].type==NOTE)||(sym[i].type==REST)||(sym[i].type==BREST))
#                 got_note=1;
#
#             if ((sym[i].type==BAR) && (sym[i].gchords && !sym[i].gchords->empty())) {
#                 if (last != 2) set_font (fp, cfmt.barlabelfont, 0);
#                 PUT3 (" %.1f %.1f M (%s) cshow ",
#                             sym[i].x, get_staffheight(ivc,NETTO)+tabfont.size,
#                             sym[i].gchords->begin()->text.c_str());
#                 last=2;
#             }
#
#             if ((sym[i].type==BAR) && sym[i].t) {
#                 ok=0;
#                 if ((cfmt.barnums>0) && (sym[i].t%cfmt.barnums==0)) ok=1;
#                 if ((cfmt.barnums==0) && (!got_note) && (sym[i].t > 1)) ok=1;
#                 if ((cfmt.barnums!=0) && (!sym[i].gchords->empty())) ok=0;
#
#                 if (ok) {
#                     if (last != 1) set_font (fp, cfmt.barnumfont, 0);
#     #|         if ((mvoice>1) && (cfmt.barnums==0))    |
#                     if (cfmt.barnums==0)
#                         PUT2 (" 0 %.1f M (%d) rshow ",
#                                     get_staffheight(ivc,NETTO)+tabfont.size, sym[i].t);
#                     else
#                         PUT3 (" %.1f %.1f M (%d) cshow ",
#                                     sym[i].x, get_staffheight(ivc,NETTO)+tabfont.size, sym[i].t);
#                     last=1;
#                 }
#             }
#         }
#         PUT0("\n");
#     }
#
#     #*************************************************************************
#      * draw_tabendings - draws first/second endings
#      *************************************************************************
#     void draw_tabendings (void)
#     {
#         int i;
#         float height;
#
#         height = get_staffheight(ivc,BRUTTO) + 5.0;
#         for (i=0;i<num_ending;i++) {
#             if (ending[i].b<0)
#                 PUT4("%.1f %.1f %.1f (%d) end2\n",
#                          ending[i].a, ending[i].a+50, height, ending[i].num);
#             else {
#                 if (ending[i].type==E_CLOSED) {
#                     PUT4("%.1f %.1f %.1f (%d) end1\n",
#                              ending[i].a, ending[i].b, height, ending[i].num);
#                 }
#                 else {
#                     PUT4("%.1f %.1f %.1f (%d) end2\n",
#                              ending[i].a, ending[i].b, height, ending[i].num);
#                 }
#             }
#         }
#         num_ending=0;
#     }
#
#     #*************************************************************************
#      * calculate_tabbeam - set start/end and other parameters for beam
#      *                                         starting at sym[i0]
#      *************************************************************************
#     int calculate_tabbeam (int i0, struct BEAM *bm)
#     {
#         int j,j1,j2;
#
#         j1=i0;                                            # find first and last note in beam
#         j2=-1;
#         for (j=i0;j<nsym;j++)
#             if (sym[j].word_end) {
#                 j2=j;
#                 break;
#             }
#         if (j2==-1) {
#             return 0;
#         }
#
#         for (j=j1;j<=j2;j++) sym[j].xs=sym[j].x;
#
#         bm->i1=j1;                                            # save beam parameters in struct
#         bm->i2=j2;
#         bm->a=0;    #beam fct: y=ax+b
#         bm->b=20; #tabflag height
#         bm->stem=0;
#         bm->t=1.5;
#         return 1;
#     }
#
#
#     #*************************************************************************
#      * draw_tabbeams - draw the beams for one word in tablature
#      *                                 only used when tabrhstyle=grid
#      *************************************************************************
#     void draw_tabbeams (struct BEAM *bm, int rhstyle)
#     {
#         int j,j1,j2,j3,inbeam,k1,k2,num,p,r;
#         int nflags,nthbeam;
#         float x1,x2,xn,dx;
#         float y,dy;
#
#         j1=bm->i1;
#         j2=bm->i2;
#
#         # modernflags stems are shorter and shifted to the right
#         # => adjust stemoffset dx and vertical beam distance dy
#         if (rhstyle == RHMODERNBEAMS) {
#             dx = 2.6; dy = 2.5;
#         } else {
#             dx = 0.0; dy = 4.0;
#         }
#
#         # draw stems
#         y = get_staffheight(ivc,NETTO) + tab_flagspace(&voice[ivc].key);
#         for (j=j1;j<=j2;j++) {
#             if (rhstyle == RHMODERNBEAMS)
#                 PUT2("%.1f %.1f 0 tabmflag ", sym[j].x, y);
#             else
#                 PUT2("%.1f %.1f 0 tabsflag ", sym[j].x, y);
#             if (sym[j].dots > 0)
#                 PUT3("%.1f %.1f %d tabdt\n", sym[j].x+2, y, sym[j].dots);
#             else
#                 PUT0("\n");
#         }
#         y += 20.0; #tabflag height
#
#         # make first beam over whole word
#         x1=sym[j1].x + dx;
#         x2=sym[j2].x + dx;
#         num=sym[j1].u;
#         for (j=j1;j<=j2;j++) {        # numbers for nplets on same beam
#             if (sym[j].p_plet>0) {
#                 p=sym[j].p_plet;
#                 r=sym[j].r_plet;
#                 j3=j+r-1;
#                 if (j3<=j2) {
#                     xn=0.5*(sym[j].x+sym[j3].x);
#                     PUT3("%.1f %.1f (%d) bnum\n", xn, y+5, p);
#                     sym[j].p_plet=0;
#                 }
#             }
#         }
#         PUT5("%.1f %.1f %.1f %.1f %.1f bm\n", x1,y,x2,y,bm->t);
#         y = y - bm->t - dy;
#
#         # loop over beams where 'nthbeam' or more flags
#         for (nthbeam=2;nthbeam<5;nthbeam++) {
#             k1=k2=0;
#             inbeam=0;
#             for (j=j1;j<=j2;j++) {
#                 if (sym[j].type!=NOTE) continue;
#                 nflags=tab_flagnumber(sym[j].len);
#                 if ((!inbeam) && (nflags>=nthbeam)) {
#                     k1=j;
#                     inbeam=1;
#                 }
#                 if (inbeam && ((nflags<nthbeam) || (j==j2))) {
#                     if ((nflags>=nthbeam) && (j==j2)) k2=j;
#                     x1=sym[k1].x + dx;
#                     x2=sym[k2].x + dx;
#                     inbeam=0;
#                     if (k1==k2) {
#                         if (k1==j1)
#                             PUT5("%.1f %.1f %.1f %.1f %.1f bm\n", x1,y,x1+BEAM_STUB,y,bm->t);
#                         else
#                             PUT5("%.1f %.1f %.1f %.1f %.1f bm\n", x1-BEAM_STUB,y,x1,y,bm->t);
#                     }
#                     else
#                         PUT5("%.1f %.1f %.1f %.1f %.1f bm\n", x1,y,x2,y,bm->t);;
#                     inbeam=0;
#                 }
#                 k2=j;
#             }
#             y = y - bm->t - dy;
#         }
#     }
#
#     #*************************************************************************
#      * draw_tabtimesig - draws time signature at position x
#      *************************************************************************
#     void draw_tabtimesig (float x, struct SYMBOL *s)
#     {
#         if (s->invis) return;
#         if (s->w==1)
#             PUT2("%.1f %d tabcsig\n", x, tab_numlines(&voice[ivc].key));
#         else if (s->w==2)
#             PUT2("%.1f %d tabctsig\n", x, tab_numlines(&voice[ivc].key));
#         else if (s->w==3)
#             PUT3("%.1f %d (%s) tabt1sig\n", x, tab_numlines(&voice[ivc].key), s->text);
#         else
#     #        PUT4("%.1f %.1f (%d) (%d) tabtsig\n",
#                 x, get_staffheight(ivc,NETTO), s->u, s->v);
#             PUT4("%.1f %d (%s) (%d) tabtsig\n",
#                      x, tab_numlines(&voice[ivc].key), s->text, s->v);
#     }
#
#     #*************************************************************************
#      * draw_tabdeco - draws chord decoration at position x
#      *        gchy (vertical position of gchords) is adjusted if necessary
#      *************************************************************************
#     void draw_tabdeco (float x, struct SYMBOL *s, float* gchy)
#     {
#         int i,italian, german;
#         float fingeringshift, tablineshift, line;
#
#         # tablature system inverted?
#         italian = ((voice[ivc].key.ktype==ITALIANTAB) ||
#                              (voice[ivc].key.ktype==ITALIAN7TAB) ||
#                              (voice[ivc].key.ktype==ITALIAN8TAB) ||
#                              (voice[ivc].key.ktype==ITALIAN5TAB) ||
#                              (voice[ivc].key.ktype==ITALIAN4TAB));
#
#         # german tablature?
#         german = (voice[ivc].key.ktype==GERMANTAB);
#
#         # frenchtab is drawn between lines, italiantab on the lines
#         # this also affects some decorations
#         if ((voice[ivc].key.ktype==FRENCHTAB) ||
#                 (voice[ivc].key.ktype==FRENCH5TAB) ||
#                 (voice[ivc].key.ktype==FRENCH4TAB))
#             fingeringshift=0.0;
#         else if (voice[ivc].key.ktype==GERMANTAB)
#             fingeringshift=1.6;
#         else #spanishtab or italiantab
#             fingeringshift=0.25;
#
#         # german tablature draws letters at lower positions
#         if (voice[ivc].key.ktype==GERMANTAB)
#             tablineshift = 1.5;
#         else
#             tablineshift = 0.0;
#
#
#
#         # decorations, applying to an entire chord
#         for (i=0;i<s->dc.n;i++) {
#         switch (s->dc.t[i]) {
#         case D_HOLD:
#                 PUT2("%.1f %.1f hld\n", x,
#                          get_staffheight(ivc,NETTO) + tab_flagspace(&voice[ivc].key));
#             break;
#         case D_INDEX:
#                 if (!italian)
#                     PUT2("%.1f %.2f tabi\n", x,
#                              fingeringshift+tabline(lowest_course(s)));
#                 else
#                     PUT2("%.1f %.2f tabi\n", x,
#                              fingeringshift+tabline(highest_course(s)));
#             break;
#         case D_MEDIUS:
#                 if (!italian)
#                     PUT2("%.1f %.2f tabm\n", x,
#                              fingeringshift+tabline(lowest_course(s)));
#                 else
#                     PUT2("%.1f %.2f tabm\n", x,
#                              fingeringshift+tabline(highest_course(s)));
#             break;
#         case D_ANNULARIUS:
#                 if (!italian)
#                     PUT2("%.1f %.2f taba\n", x,
#                              fingeringshift+tabline(lowest_course(s)));
#                 else
#                     PUT2("%.1f %.2f taba\n", x,
#                              fingeringshift+tabline(highest_course(s)));
#             break;
#         case D_POLLIX:
#                 if (voice[ivc].key.ktype==SPANISHTAB)
#                     PUT2("%.1f %.2f tabpguitar\n", x,
#                              fingeringshift+tabline(lowest_course(s)));
#                 else
#                     if (!italian)
#                         PUT2("%.1f %.2f tabp\n", x,
#                                  fingeringshift+tabline(lowest_course(s)));
#                     else
#                         PUT2("%.1f %.2f tabp\n", x,
#                                  fingeringshift+tabline(highest_course(s)));
#             break;
#         case D_TABACC:
#             PUT2("%.1f %.1f tabacc\n", x+1+(float)tabfont.size/2.0,
#                          tablineshift+tabline(highest_course(s)));
#             break;
#         case D_TABX:
#             PUT2("%.1f %.1f tabx\n", x+1+(float)tabfont.size/2.0,
#                          tablineshift+tabline(highest_course(s)));
#             break;
#         case D_TABU:
#             PUT2("%.1f %.1f tabu\n", x+1+(float)tabfont.size/2.0,
#                          tablineshift+tabline(highest_course(s)));
#             break;
#         case D_TABV:
#             PUT2("%.1f %.2f tabv\n", x,
#                          0.125+fingeringshift+tabline(highest_course(s)));
#             break;
#         case D_TABSTAR:
#             PUT2("%.1f %.1f tabstar\n", x+1+(float)tabfont.size/2.0,
#                          tablineshift+tabline(highest_course(s)));
#             break;
#         case D_TABCROSS:
#             PUT2("%.1f %.1f tabcross\n", x+1+(float)tabfont.size/2.0,
#                          tablineshift+tabline(highest_course(s)));
#             break;
#         case D_TABOLINE:
#                 if (italian)
#                     std::cerr << "Warning: decoration 'L' (oblique line) ignored in italiantab" << std::endl;
#                 else if (german)
#                     std::cerr << "Warning: decoration 'L' (oblique line) ignored in germantab" << std::endl;
#                 else
#                     PUT2("%.1f %.2f taboline\n", x,
#                              tablineshift+fingeringshift+tabline(lowest_course(s)));
#             break;
#         case D_TABTRILL:
#                 if (voice[ivc].key.ktype==FRENCHTAB) {
#                     #replace with accent in frenchtab
#                     PUT2("%.1f %d tabacc\n", x+1+(float)tabfont.size/2.0,
#                              tabline(highest_course(s)));
#                 } else {
#                     PUT2("%.1f %.1f tabtrl\n", x, *gchy-12);
#                     *gchy-=18;
#                 }
#             break;
#         case D_STRUMUP:
#                 if (italian) {
#                     PUT2("%.1f %.1f tabstrdn\n", x, *gchy);
#                 } else {
#                     PUT2("%.1f %.1f tabstrup\n", x, *gchy);
#                 }
#                 *gchy-=14;
#             break;
#         case D_STRUMDOWN:
#                 if (italian) {
#                     PUT2("%.1f %.1f tabstrup\n", x, *gchy);
#                 } else {
#                     PUT2("%.1f %.1f tabstrdn\n", x, *gchy);
#                 }
#                 *gchy-=14;
#             break;
#         case D_SEGNO:
#                 PUT2("%.1f %.1f sgno\n", x, *gchy-20);
#                 *gchy-=22;
#             break;
#         case D_CODA:
#                 PUT2("%.1f %.1f coda\n", x, *gchy-20);
#                 *gchy-=22;
#             break;
#         case D_DYN_PP:
#                 PUT2("(pp) %.1f %.1f dyn\n", x, *gchy-16);
#                 *gchy-=18;
#             break;
#         case D_DYN_P:
#                 PUT2("(p) %.1f %.1f dyn\n", x, *gchy-16);
#                 *gchy-=18;
#             break;
#         case D_DYN_MP:
#                 PUT2("(mp) %.1f %.1f dyn\n", x, *gchy-16);
#                 *gchy-=18;
#             break;
#         case D_DYN_MF:
#                 PUT2("(mf) %.1f %.1f dyn\n", x, *gchy-16);
#                 *gchy-=18;
#             break;
#         case D_DYN_F:
#                 PUT2("(f) %.1f %.1f dyn\n", x, *gchy-16);
#                 *gchy-=18;
#             break;
#         case D_DYN_FF:
#                 PUT2("(ff) %.1f %.1f dyn\n", x, *gchy-16);
#                 *gchy-=18;
#             break;
#         case D_DYN_SF:
#                 PUT2("(sf) %.1f %.1f dyn\n", x, *gchy-16);
#                 *gchy-=18;
#             break;
#         case D_DYN_SFZ:
#                 PUT2("(sfz) %.1f %.1f dyn\n", x, *gchy-16);
#                 *gchy-=18;
#             break;
#         }
#         }
#
#         # decorations applying to individual notes
#         for (i=0;i<s->npitch;i++) {
#             if (german)
#                 line = i+1;
#             else
#                 line = tabline(s->pits[i]);
#             switch (s->tabdeco[i]) {
#         case D_TABACC:
#             PUT2("%.1f %.1f tabacc\n", x+1+(float)tabfont.size/2.0,
#                          tablineshift+line);
#             break;
#         case D_TABX:
#             PUT2("%.1f %.1f tabx\n", x+1+(float)tabfont.size/2.0,
#                          tablineshift+line);
#             break;
#         case D_TABU:
#             PUT2("%.1f %.1f tabu\n", x+1+(float)tabfont.size/2.0,
#                          tablineshift+line);
#             break;
#         case D_TABV:
#             PUT2("%.1f %.2f tabv\n", x, 0.125+fingeringshift+line);
#             break;
#         case D_TABSTAR:
#             PUT2("%.1f %.1f tabstar\n", x+1+(float)tabfont.size/2.0,
#                          tablineshift+line);
#             break;
#         case D_TABCROSS:
#             PUT2("%.1f %.1f tabcross\n", x+1+(float)tabfont.size/2.0,
#                          tablineshift+line);
#             break;
#         case D_TABOLINE:
#                 if (italian)
#                     std::cerr << "Warning: decoration 'L' (oblique line) ignored in italiantab" << std::endl;
#                 else if (german)
#                     std::cerr << "Warning: decoration 'L' (oblique line) ignored in germantab" << std::endl;
#                 else
#                     PUT2("%.1f %.2f taboline\n", x, fingeringshift+line);
#             break;
#             }
#         }
#     }
#
#     #*************************************************************************
#      * draw_tabslurs - draw all slurs in current line
#      *************************************************************************
#     void draw_tabslurs (void)
#     {
#         int i,m1,m2,i1,i2;
#
#         # flags for slurs across line breaks
#         static int normalleftover = 0;
#         static int chordleftover = 0;
#
#         #
#          * slurs outside of chords
#
#         # close slurs from previous line
#         if (normalleftover) {
#             normalleftover=0;
#             i=0;
#             while (!sym[i].slur_end && (i<nsym)) i++;
#             if (i<nsym)
#                 draw_tabnormalslur(-1,i);
#         }
#         # draw slurs starting in this line
#         i1=i2=-1;
#         for (i=0;i<nsym;i++) {
#             if ((sym[i].type==NOTE) && sym[i].slur_st) {
#                 i1=i;
#                 while (!sym[i].slur_end && (i<nsym)) i++;
#                 i2=i;
#                 draw_tabnormalslur(i1,i2);
#                 if (i2>=nsym)
#                     normalleftover=1;
#             }
#         }
#
#         #
#          * slurs inside of chords
#          * (only slurs between neighbouring chords are allowed)
#
#         # close slurs from previous line
#         if (chordleftover) {
#             chordleftover=0;
#             i=0;
#             while (i<nsym) {
#                 int slurend=0;
#                 if (sym[i].type==NOTE) {
#                     for (m2=0;m2<sym[i].npitch;m2++)
#                         if (sym[i].ti2[m2] || sym[i].sl2[m2])
#                             {slurend=1; break;}
#                 }
#                 if (slurend) break;
#                 i++;
#             }
#             if (i<nsym)
#                 draw_tabchordslurs(-1,i);
#         }
#         # draw slurs starting this line
#         for (i=0;i<nsym;i++) {
#             if (sym[i].type==NOTE) {
#                 # determine start and end of next chord-tie
#                 i1=-1;
#                 for (m1=0;m1<sym[i].npitch;m1++) {
#                     if ((sym[i].ti1[m1]) || (sym[i].sl1[m1])) {
#                         i1=i;
#                         i++;
#                         while (i<nsym) {
#                             int slurend=0;
#                             if (sym[i].type==NOTE) {
#                                 for (m2=0;m2<sym[i].npitch;m2++)
#                                     if (sym[i].ti2[m2] || sym[i].sl2[m2])
#                                         {slurend=1; break;}
#                             }
#                             if (slurend) break;
#                             i++;
#                         }
#                         i2=i;
#                         break;
#                     }
#                 }
#                 if (i1>=0)
#                     draw_tabchordslurs(i1,i2);
#                 if (i2>=nsym)
#                     chordleftover=1;
#             }
#         }
#     }
#
#     #*************************************************************************
#      * draw_tabnormalslur - draws slur between specified symbols
#      *        if to >= nsym, slur is drawn till end of line
#      *        if from < 0, slur is drawn from line beginning
#      *************************************************************************
#     void draw_tabnormalslur (int from, int to)
#     {
#         int hc1,hc2,cut;
#         float x1,y1,x2,y2,direction,height,shift;
#
#         x1=y1=x2=y2=0;
#
#         #
#          * get positions for slur
#
#         if (from >= 0) {
#             x1 = sym[from].x;
#             hc1 = tabline(highest_course(&sym[from]));
#             y1 = (6-hc1) * tabfont.size;
#
#             # horizontal shift if next course in chord used
#             if ((sym[from].npitch > 1) && (next_line(&sym[from],hc1) == hc1+1))
#                 x1 += 0.5 * tabfont.size;
#         }
#         if (to < nsym) {
#             x2 = sym[to].x;
#             hc2 = tabline(highest_course(&sym[to]));
#             y2 = (6-hc2) * tabfont.size;
#     =
#             # horizontal shift if next course in chord used
#             if ((sym[to].npitch > 1) && (next_line(&sym[to],hc2) == hc2+1))
#                 x2 -= 0.5 * tabfont.size;
#         }
#
#         # special treatment of slurs over line breaks
#         if (from < 0) {
#             cut=prev_scut(to);
#             x1=sym[cut].x;
#             if (cut==to) x1-=30;
#             y1=y2;
#         }
#         if (to >= nsym) {
#             cut=next_scut(from);
#             x2=sym[cut].x;
#             if (cut==from) x2+=30;
#             y2=y1;
#         }
#
#
#         direction = -1;
#         shift = -2 - tab_slurshift();
#         #height=direction*(0.04*(x2-x1)+5);
#         height = direction * tabfont.size;
#         output_slur (x1,y1,x2,y2,direction,height,shift);
#     }
#
#     #*************************************************************************
#      * draw_tabchordslurs - draws slurs between specified chords
#      *        if to >= nsym, slurs are drawn till end of line
#      *        if from < 0, slurs are drawn from line beginning
#      *************************************************************************
#     void draw_tabchordslurs (int from, int to)
#     {
#         int m,m1,m2,hc1,hc2,cut;
#         float x1,y1,x2,y2,direction,height,shift;
#
#         #
#          * slurs within one line
#
#
#         if ((from>=0) && (to<nsym)) {
#             m2=0;
#             for (m1=0;m1<sym[from].npitch;m1++) {
#                 # ties
#                 if (sym[from].ti1[m1]) {
#                     sym[from].ti1[m1] = 0;    #mark as done
#                     for (m=m2;m<sym[to].npitch;m++)
#                         if (sym[to].ti2[m]) {
#                             m2=m;
#                             sym[to].ti2[m] = 0; #mark as done
#                             break;
#                         }
#                     # get positions for slur
#                     x1 = sym[from].x;
#                     hc1 = tabline(sym[from].pits[m1]);
#                     y1 = (6-hc1) * tabfont.size;
#                     x2 = sym[to].x;
#                     hc2 = tabline(sym[to].pits[m2]);
#                     y2 = (6-hc2) * tabfont.size;
#                     # extra space if next course in chords used
#                     if ((sym[from].npitch > 1) && (next_line(&sym[from],hc1) == hc1+1))
#                         x1 += 0.5 * tabfont.size;
#                     if ((sym[to].npitch > 1) && (next_line(&sym[to],hc2) == hc2+1))
#                         x2 -= 0.5 * tabfont.size;
#                     direction = -1;
#                     shift = -2 - tab_slurshift();
#                     #height=direction*(0.04*(x2-x1)+5);
#                     height = direction * tabfont.size;
#                     output_slur (x1,y1,x2,y2,direction,height,shift);
#                 }
#                 # slurs
#                 if (sym[from].sl1[m1]) {
#                     sym[from].sl1[m1] = 0;    #mark as done
#                     for (m=m2;m<sym[to].npitch;m++)
#                         if (sym[to].sl2[m]) {
#                             m2=m;
#                             sym[to].sl2[m] = 0; #mark as done
#                             break;
#                         }
#                     # get positions for slur
#                     x1 = sym[from].x;
#                     hc1 = tabline(sym[from].pits[m1]);
#                     y1 = (6-hc1) * tabfont.size;
#                     x2 = sym[to].x;
#                     hc2 = tabline(sym[to].pits[m2]);
#                     y2 = (6-hc2) * tabfont.size;
#                     # extra space if next course in chords used
#                     if ((sym[from].npitch > 1) && (next_line(&sym[from],hc1) == hc1+1))
#                         x1 += 0.5 * tabfont.size;
#                     if ((sym[to].npitch > 1) && (next_line(&sym[to],hc2) == hc2+1))
#                         x2 -= 0.5 * tabfont.size;
#                     direction = -1;
#                     shift = -2 - tab_slurshift();
#                     #height=direction*(0.04*(x2-x1)+5);
#                     height = direction * tabfont.size;
#                     output_slur (x1,y1,x2,y2,direction,height,shift);
#                 }
#             }
#         }
#
#
#         #
#          * special treatment for slurs across line breaks
#
#
#         #slur start in previous line
#         if (from<0) {
#             for (m2=0;m2<sym[to].npitch;m2++) {
#                 # ties
#                 if (sym[to].ti2[m2]) {
#                     sym[to].ti2[m2] = 0;    #mark as done
#                     # get positions for slur
#                     x2 = sym[to].x;
#                     hc2 = tabline(sym[to].pits[m2]);
#                     y2 = (6-hc2) * tabfont.size;
#                     cut=prev_scut(to);
#                     x1=sym[cut].x;
#                     if (cut==to) x1-=30;
#                     hc1 = hc2;
#                     y1 = y2;
#                     # extra space if next course in chords used
#                     if ((sym[to].npitch > 1) && (next_line(&sym[to],hc2) == hc2+1))
#                         x2 -= 0.5 * tabfont.size;
#                     direction = -1;
#                     shift = -2 - tab_slurshift();
#                     #height=direction*(0.04*(x2-x1)+5);
#                     height = direction * tabfont.size;
#                     output_slur (x1,y1,x2,y2,direction,height,shift);
#                 }
#                 # slurs
#                 if (sym[to].sl2[m2]) {
#                     sym[to].sl2[m2] = 0;    #mark as done
#                     # get positions for slur
#                     x2 = sym[to].x;
#                     hc2 = tabline(sym[to].pits[m2]);
#                     y2 = (6-hc2) * tabfont.size;
#                     cut=prev_scut(to);
#                     x1=sym[cut].x;
#                     if (cut==to) x1-=30;
#                     hc1 = hc2;
#                     y1 = y2;
#                     # extra space if next course in chords used
#                     if ((sym[to].npitch > 1) && (next_line(&sym[to],hc2) == hc2+1))
#                         x2 -= 0.5 * tabfont.size;
#                     direction = -1;
#                     shift = -2 - tab_slurshift();
#                     #height=direction*(0.04*(x2-x1)+5);
#                     height = direction * tabfont.size;
#                     output_slur (x1,y1,x2,y2,direction,height,shift);
#                 }
#             }
#         }
#
#         # slur end in next line
#         if (to>=nsym) {
#             for (m1=0;m1<sym[from].npitch;m1++) {
#                 # ties
#                 if (sym[from].ti1[m1]) {
#                     sym[from].ti1[m1] = 0;    #mark as done
#                     # get positions for slur
#                     x1 = sym[from].x;
#                     hc1 = tabline(sym[from].pits[m1]);
#                     y1 = (6-hc1) * tabfont.size;
#                     cut=next_scut(from);
#                     x2=sym[cut].x;
#                     if (cut==from) x2+=30;
#                     hc2 = hc1;
#                     y2 = y1;
#                     # extra space if next course in chords used
#                     if ((sym[from].npitch > 1) && (next_line(&sym[from],hc1) == hc1+1))
#                         x1 += 0.5 * tabfont.size;
#                     direction = -1;
#                     shift = -2 - tab_slurshift();
#                     #height=direction*(0.04*(x2-x1)+5);
#                     height = direction * tabfont.size;
#                     output_slur (x1,y1,x2,y2,direction,height,shift);
#                 }
#                 # slurs
#                 if (sym[from].sl1[m1]) {
#                     sym[from].sl1[m1] = 0;    #mark as done
#                     # get positions for slur
#                     x1 = sym[from].x;
#                     hc1 = tabline(sym[from].pits[m1]);
#                     y1 = (6-hc1) * tabfont.size;
#                     cut=next_scut(from);
#                     x2=sym[cut].x;
#                     if (cut==from) x2+=30;
#                     hc2 = hc1;
#                     y2 = y1;
#                     # extra space if next course in chords used
#                     if ((sym[from].npitch > 1) && (next_line(&sym[from],hc1) == hc1+1))
#                         x1 += 0.5 * tabfont.size;
#                     direction = -1;
#                     shift = -2 - tab_slurshift();
#                     #height=direction*(0.04*(x2-x1)+5);
#                     height = direction * tabfont.size;
#                     output_slur (x1,y1,x2,y2,direction,height,shift);
#                 }
#             }
#         }
#     }
#
#     #*************************************************************************
#      * tab_slurhift - return veritcal shift for tablature slurs
#      *     in current voice. A return value > 0 means a shift towards
#      *     the next higher course
#      *************************************************************************
#     float tab_slurshift()
#     {
#         if (voice[ivc].key.ktype==FRENCHTAB ||
#                 voice[ivc].key.ktype==FRENCH5TAB ||
#                 voice[ivc].key.ktype==FRENCH4TAB)
#             return 0.0;
#         else #italiantab or spanishtab
#             return 0.25 * tabfont.size;
#     }
#
#     #*************************************************************************
#      * draw_tabtenutos - draw all tenuto strokes in current line
#      *************************************************************************
#     void draw_tabtenutos (void)
#     {
#         int i,m,m1,m2,from,to,hc1,hc2;
#         float x1,y1,x2,y2;
#
#         from=to=-1;
#         for (i=0;i<nsym;i++) {
#             # find start and end of tenuto sign
#             if (sym[i].type==NOTE && sym[i].ten_st) {
#                 from=i;
#                 while (!sym[i].ten_end && (i<nsym)) i++;
#                 to=i;
#                 # draw all tenuto strokes between these chords
#                 if (to<nsym) {    // tenuto ends in same line
#                     for (m1=0, m2=0; m1<sym[from].npitch; m1++) {
#                         if (sym[from].ten1[m1]) {
#                             sym[from].ten1[m1] = 0;    #mark as done
#                             for (m=m2; m<sym[to].npitch; m++)
#                                 if (sym[to].ten2[m]) {
#                                     m2=m;
#                                     sym[to].ten2[m] = 0; #mark as done
#                                     break;
#                                 }
#                             # no further matching tenuto end?
#                             if (m2 >= sym[to].npitch) break;
#                             #
#                              * get positions for tenuto stroke
#                              * when no fret sign (i.e. 'y') include chord into tenuto stroke,
#                              * otherwise exclude it
#
#                             x1 = sym[from].x;
#                             if (sym[from].accs[m1] == 'y') x1 -= tabfont.size/2.0;
#                             else x1 += tabfont.size;
#                             hc1 = tabline(sym[from].pits[m1]);
#                             y1 = (6-hc1) * tabfont.size + 1.5;
#                             x2 = sym[to].x;
#                             if (sym[to].accs[m2] == 'y') x2 += tabfont.size/2.0;
#                             else x2 -= tabfont.size;
#                             hc2 = tabline(sym[to].pits[m2]);
#                             y2 = (6-hc2+1) * tabfont.size - 1.5;
#                             //output_slur (x1,y1,x2,y2,direction,height,shift);
#                             PUT4("%.1f %.1f %.1f %.1f tabten ", x1, y1, x2, y2);
#                         }
#                     }
#                 }
#             }
#         }
#     }
#
#     #*************************************************************************
#      * tab_nplets - draw nplets in current line
#      *************************************************************************
#     void draw_tabnplets (void)
#     {
#         int i,j,k,p,r,c;
#
#         #find start of nplets
#         for (i=0;i<nsym;i++) {
#             if ((sym[i].type==NOTE) || (sym[i].type==REST)) {
#                 if (sym[i].p_plet>0) {
#                     p=sym[i].p_plet;
#                     r=sym[i].r_plet;
#                     c=r;
#                     k=i;
#                     #find end of nplet
#                     for (j=i;j<nsym;j++) {
#                         if ((sym[j].type==NOTE) || (sym[j].type==REST)) {
#                             c--;
#                             k=j;
#                             if (c==0) break;
#                         }
#                     }
#                     #draw nplet
#                     output_slur (sym[i].x+2, 6*tabfont.size,
#                                              sym[k].x, 6*tabfont.size,
#                                              1, 10, 0);
#                     PUT3("%.1f %.1f (%d) bnum\n",
#                              0.5*(sym[i].x+sym[k].x), 6.0*tabfont.size+5, p);
#                 }
#             }
#         }
#     }
#
#     #*************************************************************************
#      * tabline - returns tablature line corresponding to given course
#      *************************************************************************
#     int tabline (int course)
#     {
#         # all bourdons are printed on 7th line
#         if (voice[ivc].key.ktype == ITALIAN8TAB) {
#             if (course>8) course=7;
#         } else {
#             if (course>7) course=7;
#         }
#
#         switch (voice[ivc].key.ktype) {
#         case ITALIANTAB:
#         case ITALIAN7TAB:
#         case ITALIAN8TAB:
#         case ITALIAN5TAB:
#         case ITALIAN4TAB:
#             return (7-course);
#             break;
#         case FRENCH5TAB:
#         case SPANISH5TAB:
#             return (course+1);
#             break;
#         case FRENCH4TAB:
#         case SPANISH4TAB:
#             return (course+2);
#             break;
#         default:
#             return course;
#             break;
#         }
#     }
#
#     #*************************************************************************
#      * lowest_course - returns lowest course in chord
#      *************************************************************************
#     int lowest_course (struct SYMBOL *s)
#     {
#         int i,onlyy;
#         int lowc=0;
#
#         // y (invisible symbol) may only be ignored
#         // when other symbols are present => check for this
#         onlyy = 1;
#         for (i=0;i<s->npitch;i++) {
#             if (s->accs[i] != 'y') {
#                 onlyy = 0; break;
#             }
#         }
#
#         if (voice[ivc].key.ktype==GERMANTAB) {
#             for (i=s->npitch-1;i>=0;i--)
#                 lowc++;
#
#         } else {
#             for (i=s->npitch-1;i>=0;i--) {
#                 if (s->pits[i]>lowc && (s->accs[i] != 'y' || onlyy))
#                     lowc=s->pits[i];
#             }
#             if (lowc>7)
#                 lowc=7;
#         }
#
#         return lowc;
#     }
#
#     #*************************************************************************
#      * highest_course - returns highest course in chord
#      *************************************************************************
#     int highest_course (struct SYMBOL *s)
#     {
#         int i,onlyy;
#         int highc=10;
#
#         if (voice[ivc].key.ktype==GERMANTAB)
#             return 1;
#
#         // y (invisible symbol) may only be ignored
#         // when other symbols are present => check for this
#         onlyy = 1;
#         for (i=0;i<s->npitch;i++) {
#             if (s->accs[i] != 'y') {
#                 onlyy = 0; break;
#             }
#         }
#
#         for (i=0;i<s->npitch;i++) {
#         if (s->pits[i]<highc && (s->accs[i] != 'y' || onlyy))
#             highc=s->pits[i];
#         }
#         if (highc>7)
#         highc=7;
#
#         return highc;
#     }
#
#     #*************************************************************************
#      * next_line - returns next used tabline tablature line lower than
#      *     hc in chord. If next line is not found, 0 is returned
#      *************************************************************************
#     int next_line (struct SYMBOL *s, int hc)
#     {
#         int i,nextc;
#
#         if (voice[ivc].key.ktype==FRENCHTAB ||
#                 voice[ivc].key.ktype==FRENCH5TAB ||
#                 voice[ivc].key.ktype==FRENCH4TAB ||
#                 voice[ivc].key.ktype==SPANISHTAB ||
#                 voice[ivc].key.ktype==SPANISH5TAB ||
#                 voice[ivc].key.ktype==SPANISH4TAB) {
#             # search larger course numbers
#             nextc=99;
#             for (i=0;i<s->npitch;i++) {
#                 if ((s->pits[i]<nextc) && (s->pits[i]>hc))
#                     nextc=s->pits[i];
#             }
#             if (nextc==99)
#                 return 0;
#             if (nextc>7)
#                 nextc=7;
#         } else {
#             # italiantab: search smaller course numbers
#             hc = 6-hc;             #translate line to course
#             nextc = 0;
#             for (i=0;i<s->npitch;i++) {
#                 if ((s->pits[i]>nextc) && (s->pits[i]<hc))
#                     nextc=s->pits[i];
#             }
#             if (nextc>=6)
#                 return 0;
#             nextc = 6-nextc; #translate course to line
#         }
#
#         return nextc;
#     }
#
    def open_tabfontfile(self, basename):
        """
        find first fontfile in directorylist $ABCTABFONTS
        and open it. If $ABCTABFONTS is unset, standard directories are
        searched. If the file cannot be found, NULL is returned.

        :param self:
        :param basename:
        :return:
        """
        # get font directory list
        font_dirs = os.environ.get('ABCTABFONT', None)
        if not font_dirs:
            font_dirs = TABFONTDIRS
        font_file = '.'.join([basename, 'ps'])

        for font_dir in font_dirs:
            t = [f for f in os.listdir(font_dir)
                 if os.path.isfile(os.path.join(font_dir, font_file))]
            if t:
                return t
        return

    def def_tabfonts(self, fp):
        """
        writes font definitions into outfile
        from fontfile is removed by getline() and rewritten,
        to achieve native line breaks on each platform

        It is not possible to decide automatically, whether tab
        is needed, because only one tune is accessible at a time

        - load french font (can be suppressed with %%tabfontfrench none)
        - load italian font (can be suppressed with %%tabfontitalian none)
        - load german font (can be suppressed with %%tabfontgerman none)

        :param fp:
        :return:
        """
        if args.notab:    # when global flag set
            return

        font_list = [self.frfont, self.itfont, self.defont]
        for tab_font in font_list:
            if tab_font == "none":
                fp.write('\n')
                with self.open_tabfontfile(tab_font) as fontfp:
                    if not fontfp:
                        log.error('Please check the environment variable '
                                  'ABCTABFONTS\n'
                                  f'Cannot find tablature font file: {self.frfont}')
                    lines = fontfp.readlines()
                    for line in lines:
                        if line.startswith('%!'):
                            fp.write(line)


    def def_tabsyms(self, fp, cfmt):
        """
        writes PS macros for tablature into outfile

        :param fp:
        :param cfmt:
        :return:
        """

        # when global flag set
        if args.notab:
            return

        # It is not possible to decide automatically, whether tab is needed,
        # because only one tune is accessible at a time

        # tablature system
        fp.write("\n/tabN { %% l n tabN - n line tab\n"
                 "    gsave %3.2f setlinewidth 0 0 moveto\n"
                 "    {dup 0 rlineto dup neg %d rmoveto} repeat\n"
                 "    pop stroke grestore\n"
                 "} bind def\n" % (cfmt.stafflinethickness, self.size))

        fp.write("\n/tab1 { %% l y tab1 - tab separator line\n"
                 "    gsave %3.2f setlinewidth 0 exch moveto 0 rlineto\n"
                 "    stroke grestore\n"
                 "} bind def\n" % cfmt.stafflinethickness)

        # time signatures
        fp.write("\n/tabcsig { %% x n tabcsig - C time sig\n"
                 "    gsave 1.2 setlinewidth\n"
                 "    6 sub %.1f mul %.1f add moveto currentpoint\n"
                 "    -10 0 -10 %d 0 %d rcurveto\n"
                 "    -15 0 -15 -%d 0 -%d rcurveto\n"
                 "    fill moveto 7 3.5 rmoveto\n"
                 "    -3.5 -3.5 -3.5 -3.5 -7 -3.5 rcurveto\n"
                 "    -15 0 -15 %d 0 %d rcurveto\n"
                 "    3.5 0 3.5 0 7 -3.5 rcurveto\n"
                 "    currentpoint stroke moveto 0.5 0 rmoveto\n"
                 "    currentpoint exch -2 add exch -2 add 2 0 360 arc\n"
                 "    fill grestore\n"
                 "} bind def\n" % (self.size * 0.5, self.size * 1.5,
                                   self.size * 2, self.size * 2,
                                   self.size * 2, self.size * 2,
                                   self.size * 2, self.size * 2))

        fp.write("\n/tabctsig { %% x n tabctsig - C| timesig\n"
                 "    2 copy tabcsig\n"
                 "    6 sub %.1f mul %.1f add moveto 0 %d rlineto stroke\n"
                 "} bind def\n" % (self.size * 0.5,
                                   self.size * 0.5,
                                   self.size * 4))
        # beware that tab is higher than music
        fp.write("\n/tabtsig { %% x n (top) (bot) tabtsig - time signature\n"
                 "    4 -2 roll -5 add %d mul moveto /bx false def\n"
                 "    gsave /NewCenturySchlbk-Bold 16 selectfont %.1f %.1f scale\n"
                 "    0 1.0 rmoveto currentpoint 3 -1 roll cshow\n"
                 "    moveto 0 %d %.1f div rmoveto cshow grestore\n"
                 "} bind def\n" % (self.size,
                                   3 * self.size / STAFFHEIGHT,
                                   3 * self.size / STAFFHEIGHT,
                                   2 * self.size,
                                   3 * self.size / STAFFHEIGHT))
        fp.write(
            "\n/tabt1sig { %% x n (top) tabt1sig - timesig without denominator\n"
            "    3 1 roll 6 sub %.1f mul %.1f add moveto /bx false def\n"
            "    gsave /NewCenturySchlbk-Bold 16 selectfont %.1f %.1f scale\n"
            "    cshow grestore\n"
            "} bind def\n" % (self.size * 0.5,
                              self.size * 1.8,
                              3 * self.size / STAFFHEIGHT,
                              3 * self.size / STAFFHEIGHT))

        # tablature letter
        fp.write(
            "\n/tabfshow { %% x n (c) tabfshow - french tabletter c on course n\n"
            "    3 1 roll\n"
            # raise one point so that line is not touched
            "    -6 add -%d mul 1 add moveto\n"
            #                                ^^^^^
            "    gsave /FrenchTabfont %.1f selectfont\n"
            "    /bx false def cshow grestore\n"
            "} bind def\n" % (self.size, self.size * self.scale))
        fp.write(
            "\n/tabsshow { %% x n (c) tabsshow - spanish tabletter c on course n\n"
            "    3 1 roll\n"
            "    -5.5 add -%d mul moveto\n"
            "    gsave /ItalianTabfont %.1f selectfont\n"
            "    /bx false def cshow grestore\n"
            "} bind def\n" % (self.size, self.size * self.scale))
        fp.write("\n/tabgshow { %% x n (c) tabgshow - german tabletter c at pos n\n"
                 "    3 1 roll\n"
                 "    -4.25 add -%d mul moveto\n"
                 "    gsave /GermanTabfont %.1f selectfont\n"
                 "    /bx false def cshow grestore\n"
                 "} bind def\n" % (self.size, self.size * self.scale))

        # rhythm flags
        fp.write("\n/tabbrevis { %% x y tabbrevis - brevis\n"
                 "    gsave 0.8 setlinewidth\n"
                 "    2 copy moveto -4 1.5 rmoveto\n"
                 "    8 0 rlineto 0 1.5 rlineto -8 0 rlineto 0 -1.5 rlineto fill\n"
                 "    2 copy moveto -4 5.5 rmoveto\n"
                 "    8 0 rlineto 0 1.5 rlineto -8 0 rlineto 0 -1.5 rlineto fill\n"
                 "    2 copy moveto -4 0 rmoveto 0 9 rlineto stroke\n"
                 "    moveto 4 0 rmoveto 0 9 rlineto stroke\n"
                 "    grestore\n"
                 "} bind def\n")
        fp.write("\n/tablonga { %% x y tablonga - longa\n"
                 "    gsave 0.8 setlinewidth\n"
                 "    2 copy 4 add tabbrevis\n"
                 "    moveto 4 0 rmoveto 0 5 rlineto stroke\n"
                 "    grestore\n"
                 "} bind def\n")
        fp.write(
            "\n/tabsflag { %% x y n tabsflag - stem with n flags (simple style)\n"
            "    gsave 1 setlinewidth\n"
            "    3 1 roll moveto 0 20 rlineto\n"
            "    currentpoint stroke moveto\n"
            "    dup 0 lt {\n"
            "        dup neg {\n"
            "            -4 -2 rlineto 1 -1 rlineto 3 2 rlineto 0 1 rlineto\n"
            "            currentpoint fill moveto 0 -5 rmoveto\n"
            "        } repeat\n"
            "    } if\n"
            "    dup 0 gt {\n"
            "        {\n"
            "            1.2 -1 rlineto \n"
            "            2 -1 6 -1 6 -3 rcurveto\n"
            "            -1.2 -1.2 rlineto\n"
            "            0 2 -4 2 -6 3 rcurveto\n"
            "            0 2.2 rlineto\n"
            "            currentpoint fill moveto\n"
            "            0 -5 rmoveto\n"
            "        } repeat\n"
            "    } {pop} ifelse    grestore\n"
            "} bind def\n")
        fp.write(
            "\n/tabdflag { %% x y n tabdflag - stem with n flags (diamond style)\n"
            "    gsave 1 setlinewidth\n"
            "    3 1 roll moveto\n"
            "    dup 0 lt {\n"
            "        4 4 rlineto currentpoint\n"
            "        -0.4 0.4 rlineto -4 -4 rlineto 0.4 -0.4 rlineto fill moveto\n"
            "        -4 4 rlineto currentpoint\n"
            "        -1.1 -1.1 rlineto 4 -4 rlineto 1.1 1.1 rlineto fill moveto\n"
            "        -4 -4 rlineto currentpoint\n"
            "        0.4 -0.4 rlineto 4 4 rlineto -0.4 0.4 rlineto fill moveto\n"
            "        4 -4 rlineto currentpoint\n"
            "        1.1 1.1 rlineto -4 4 rlineto -1.1 -1.1 rlineto fill moveto\n"
            "        0 8 rmoveto\n"
            "    } {\n"
            "        4 4 rlineto -4 4 rlineto -4 -4 rlineto 4 -4 rlineto\n"
            "        currentpoint fill moveto 0 8 rmoveto\n"
            "    } ifelse\n"
            "    dup -2 gt {\n"
            "        0 setlinejoin 0 setlinecap\n"
            "        0 20 8 sub rlineto \n"
            "    } if\n"
            "    dup 0 gt {\n"
            "        {\n"
            "            6 -3 rlineto\n"
            "            -6 0 rmoveto\n"
            "        } repeat\n"
            "    } {pop} ifelse\n"
            "    stroke grestore\n"
            "} bind def\n")
        fp.write(
            "\n/tabmflag { %% x y n tabmflag - stem with n flags (modern style)\n"
            "    gsave 1 setlinewidth\n"
            "    3 1 roll moveto\n"
            "    dup 0 lt {\n"
            "        2.5 7 rmoveto\n"
            "        0 -1 0 -7 -5 -7 rcurveto -2 0 0 7 5 7 rcurveto\n"
            "        currentpoint stroke moveto\n"
            "    } {\n"
            "        3 7 rmoveto\n"
            "        0 -1 0 -7 -5 -7 rcurveto -2 0 0 7 5 7 rcurveto\n"
            "        currentpoint fill moveto -0.5 0 rmoveto\n"
            "    } ifelse\n"
            "    dup -2 gt {\n"
            "        0 20 7 sub rlineto\n"
            "        currentpoint stroke moveto\n"
            "    } if \n"
            "    dup 0 gt {\n"
            "        1.2 -0.2 rlineto currentpoint\n"
            "        -1.2 -1.2 rlineto closepath fill moveto\n"
            "        {\n"
            "            2.4 -0.4 7 0 3.5 -5 rcurveto\n"
            "            -1.2 -1.2 rlineto currentpoint\n"
            "            3.5 5 -1.1 4.6 -3.5 5 rcurveto 1.2 1.2 rlineto\n"
            "            fill moveto\n"
            "        } repeat\n"
            "    } {pop} ifelse grestore\n"
            "} bind def\n")

        # rests (only modern style has own implemetation)
        fp.write(
            "\n/tabsrest { %% usage x y n tabsrest - rest with n flags (simple style)\n"
            "    tabsflag\n"
            "} bind def\n")
        fp.write(
            "\n/tabdrest { %% usage x y n tabdrest - rest with n flags (diamond style)\n"
            "    tabdflag\n"
            "} bind def\n")
        fp.write(
            "\n/tabmrest { %% usage x y n tabmrest - rest with n flags (modern style)\n"
            "    gsave 1 setlinewidth\n"
            "    3 1 roll moveto\n"
            "    dup -4 le { %% longa rest\n"
            "        gsave 0.8 setlinewidth\n"
            "        currentpoint -5 5 rmoveto\n"
            "        10 0 rlineto 0 3 rlineto -10 0 rlineto 0 -3 rlineto fill\n"
            "        moveto currentpoint -5 4 rmoveto 0 5 rlineto stroke\n"
            "        moveto 5 0 rmoveto 0 9 rlineto stroke grestore\n"
            "    } if\n"
            "    dup -3 eq { %% brevis rest\n"
            "        gsave 0.8 setlinewidth\n"
            "        currentpoint -5 1 rmoveto\n"
            "        10 0 rlineto 0 3 rlineto -10 0 rlineto 0 -3 rlineto fill\n"
            "        moveto currentpoint -5 0 rmoveto 0 5 rlineto stroke\n"
            "        moveto 5 0 rmoveto 0 5 rlineto stroke grestore\n"
            "    } if\n"
            "    dup -2 eq { %% whole note rest\n"
            "        -5 3 rmoveto 10 0 rlineto\n"
            "        currentpoint stroke moveto -2 -3 rmoveto\n"
            "        0 3 rlineto -6 0 rlineto 0 -3 rlineto 6 0 rlineto fill\n"
            "    } if\n"
            "    dup -1 eq { %% half note rest\n"
            "        -5 0 rmoveto 10 0 rlineto\n"
            "        currentpoint stroke moveto -2 0 rmoveto\n"
            "        0 3 rlineto -6 0 rlineto 0 -3 rlineto 6 0 rlineto fill\n"
            "} if\n"
            "    dup 0 eq { %% crotchet rest\n"
            "        -2 4 1 4 3 3 rcurveto currentpoint -1.5 1.5 rlineto\n"
            "        -2 1 -5 1 -3 -3 rcurveto 1.5 -1.5 rlineto fill moveto\n"
            "        -1 1 rmoveto\n"
            "        -5 5 3 4 -2 9 rcurveto -1.5 1.5 rlineto\n"
            "        5 -5 -3 -4 2 -9 rcurveto 1.5 -1.5 rlineto fill\n"
            "    } if\n"
            "    dup 1 ge { %% (semi)quaver rests\n"
            "        2 8 rlineto dup dup 0.5 mul exch 2 mul rlineto\n"
            "        currentpoint stroke moveto\n"
            "        {\n"
            "            -2 -2 -3 -2 -5 -2 rcurveto \n"
            "            currentpoint 1.5 add 1.5 -90 0 arcn \n"
            "            0 -1 2.5 0 3.5 0.5 rcurveto\n"
            "            currentpoint fill moveto\n"
            "            -1 -4 rmoveto\n"
            "        } repeat\n"
            "    } {pop} ifelse grestore\n"
            "} bind def\n")

        # multibar rests
        fp.write("\n/tabbrest { %% usage (n) x yn x y tabbrest - multibar rest\n"
                 "     gsave moveto currentpoint 0.8 setlinewidth\n"
                 "     0 -6 rmoveto 0 12 rlineto 40 0 rmoveto 0 -12 rlineto stroke\n"
                 "     3 setlinewidth moveto 40 0 rlineto stroke\n"
                 "     moveto 20 0 rmoveto /Times-Bold 13 selectfont cshow grestore\n"
                 "} bind def\n")

        # dots after flag
        fp.write("\n/tabdt { %% x y n tabdt - n dots after flag\n"
                 "    3 1 roll moveto 1 1 rmoveto currentpoint 3 2 roll\n"
                 "    {\n"
                 "        exch 3 add exch newpath\n"
                 "        1 0 360 arc\n"
                 "        currentpoint fill closepath\n"
                 "    } repeat\n"
                 "    pop pop\n"
                 "} bind def\n")

        # Bourdon string
        # version with ledger lines BEFORE letter
        fp.write(
            "\n/tabfbourdon { %% x m n (c) - n-th bourdon stopped at c drawn at course 7+m in frenchtab\n"
            "    gsave .75 setlinewidth\n"
            "    4 1 roll 2 index\n"
            "    -%.1f add 2 index -%d mul -2 add moveto\n"
            "    { -%.1f -%d rlineto %.1f %d rmoveto} repeat stroke\n"
            "    1 add -%d mul 1 add moveto\n"
            "    /FrenchTabfont %.1f selectfont\n"
            "    /bx false def cshow grestore\n"
            "} bind def\n" % (self.scale, self.size,
                              0.5 * self.size, self.size - 2,
                              0.5 * self.size - 2.5, self.size - 2,
                              self.size, self.size * self.scale))
        # alternative version with ledger lines ABOVE letter
        fp.write(
            "\n/tabf1bourdon { %% x m n (c) - n-th bourdon stopped at c drawn at course 7+m in frenchtab\n"
            "    gsave .75 setlinewidth\n"
            "    4 1 roll 3 1 roll 2 index exch 2 index 2 index\n"
            "    .5 mul neg -%.1f add add 1 index -%d mul -7 add moveto\n"
            "    4 -1 roll 3 -1 roll\n"
            "    {%d 4 rlineto -%.1f -7 rmoveto} repeat stroke\n"
            "    -3 mul -%d add 1 add exch -%d mul add moveto\n"
            "    /FrenchTabfont %.1f selectfont\n"
            "    /bx false def cshow grestore\n"
            "} bind def\n" % (0.5 * self.size, self.size,
                              self.size, -0.5 + self.size,
                              self.size, self.size,
                              self.size * self.scale))
        # italian tablature seventh course
        fp.write(
            "\n/tabibourdon { %% x (c) tabibourdon - (c) on 7th course in italiantab\n"
            "    gsave .75 setlinewidth\n"
            "    exch dup %d moveto -%d 0 rmoveto %d 0 rlineto stroke\n"
            "    0 3 -1 roll tabsshow grestore\n"
            "} bind def\n" % (
                6 * self.size, self.size // 2, self.size + 1
            ))
        # italian tablature eighth course
        fp.write(
            "\n/tabi8bourdon { %% x (c) tabi8bourdon - (c) on 8th course in italiantab\n"
            "    gsave .75 setlinewidth\n"
            "    exch dup %d moveto -%d 0 rmoveto %d 0 rlineto currentpoint stroke\n"
            "    moveto 0 %d rmoveto -14 0 rlineto stroke\n"
            "    -1 3 -1 roll tabsshow grestore\n"
            "} bind def\n" % (
                6 * self.size, self.size // 2, self.size + 1,
                self.size
            ))

        # different bar lines
        fp.write(
            "\n/tabbar { %% x h tabbar - single bar in tab\n"
            "    exch 0 moveto 0 exch rlineto stroke\n"
            "} bind def\n"
        )
        fp.write(
            "\n/tabdbar { %% x h tabdbar - thin double bar in tab\n"
            "    exch 0 moveto dup 0 exch rlineto dup -3 exch neg rmoveto\n"
            "    0 exch rlineto stroke\n"
            "} bind def\n"
        )
        fp.write(
            "\n/tabfbar1 { %% x h tabfbar1 - fat double bar at start\n"
            "    exch 0 moveto dup 0 exch rlineto 3 0 rlineto \n"
            "    dup 0 exch neg rlineto currentpoint fill moveto\n"
            "    3 0 rmoveto dup 0 exch rlineto stroke\n"
            "} bind def\n"
        )
        fp.write(
            "\n/tabfbar2 { %% x tabfbar2 - fat double bar at end\n"
            "    exch 0 moveto dup 0 exch rlineto -3 0 rlineto \n"
            "    dup 0 exch neg rlineto currentpoint fill moveto\n"
            "    -3 0 rmoveto dup 0 exch rlineto stroke\n"
            "} bind def\n"
        )

        # repeat dots
        fp.write(
            "\n/tabrdots { %% x n rdots - n repeat dots\n"
            "    exch 0 moveto 0 %.1f rmoveto currentpoint 2 copy 1.2 0 360 arc\n"
            "    3 -1 roll 2 sub {moveto 0 %d rmoveto    currentpoint 2 copy 1.2 0 360 arc} repeat\n"
            "    moveto 0 %d rmoveto    currentpoint 1.2 0 360 arc fill\n"
            "} bind def\n" % (
                0.5 * self.size, self.size, self.size
            ))

        # first/second endings
        dy = 15  # use dy=6 for small boxes
        fp.write("\n/tabend1 { %% x1 x2 h (str) tabend1 - mark first ending\n"
                 "    4 1 roll -%d add dup 3 1 roll moveto 0 %d rlineto 2 copy %d add lineto 0 -%d rlineto stroke\n"
                 "    moveto 4 %d rmoveto gsave /Times-Roman 13 selectfont 1.2 0.95 scale\n"
                 "    show grestore\n"
                 "} bind def\n" % (dy, dy, dy, dy, dy - 10))
        fp.write("\n/tabend2 { %% x1 x2 h (str) tabend2 - mark second ending\n"
                 "    4 1 roll dup 3 1 roll moveto 2 copy lineto 0 -%d rlineto stroke\n"
                 "    moveto 4 -10 rmoveto gsave /Times-Roman 13 selectfont 1.2 0.95 scale\n"
                 "    show grestore\n"
                 "} bind def\n" % dy)

        # grace signs
        fp.write(
            "\n/tabtrl { %% x y tabtrl - trill\n"
            "    gsave /Times-BoldItalic 14 selectfont\n"
            "    moveto -4 0 rmoveto (tr.) show grestore\n"
            "} bind def\n"
        )
        fp.write(
            "\n/tabacc { %% usage x n tabacc - accent from above\n"
            "    -6 add -%d mul -2.5 add moveto\n"
            "    1 1 2 1 2 4 rcurveto\n"
            "    currentpoint 1.5 add 1.5 -90 0 arcn\n"
            "    0 -3 -3 -3.5 -3.5 -5.5 rcurveto fill\n"
            "} bind def\n" % self.size)
        fp.write(
            "\n/tabx { %% usage x n tabx - mordent\n"
            "    -6 add -%d mul -3.5 add moveto\n"
            "    gsave 0.7 setlinewidth\n"
            "    5 7 rlineto -5 0 rmoveto 5 -7 rlineto\n"
            "    stroke grestore\n"
            "} bind def\n" % self.size)
        fp.write(
            "\n/tabu { %% usage x n tabu - arc starting at x\n"
            "    -6 add -%d mul -2 add moveto\n"
            "    gsave 1.0 setlinewidth\n"
            "    2 -4 5 -4 7 0 rcurveto\n"
            "    stroke grestore\n"
            "} bind def\n" % self.size)
        fp.write(
            "\n/tabv { %% usage x n tabu - arc centered at x\n"
            "    -6 add -%d mul -2 add exch -3.5 add exch moveto\n"
            "    gsave 1.0 setlinewidth\n"
            "    2 -4 5 -4 7 0 rcurveto\n"
            "    stroke grestore\n"
            "} bind def\n" % self.size)
        fp.write(
            "\n/tabstar { %% usage x n tabstar - asterisque\n"
            "    -6 add -%d mul -%.1f add moveto\n"
            "    /Helvetica 21 selectfont (*) show\n"
            "} bind def\n" % (
                self.size, 0.5 * self.size
            ))
        fp.write(
            "\n/tabcross { %% usage x n tabcross - double cross\n"
            "    -6 add -%d mul -1 add moveto\n"
            "    /Helvetica 14 selectfont (#) show\n"
            "} bind def\n" % self.size)
        fp.write(
            "\n/taboline { %% usage x n taboline - oblique line\n"
            "    -5.5 add -%d mul moveto\n"
            "    gsave 1.2 setlinewidth\n"
            "    -5 -1.5 rmoveto 12 3 rlineto stroke grestore\n"
            "} bind def\n" % self.size)
        fp.write(
            "\n/tabstrup { %% x y tabstrup - strum up arrow\n"
            "    -12 add moveto gsave 1 setlinewidth\n"
            "    0 12 rlineto -3 -4 rmoveto 3 4 rlineto 3 -4 rlineto\n"
            "    stroke grestore\n"
            "} bind def\n"
        )
        fp.write(
            "\n/tabstrdn { %% x y tabstrdn - strum down arrow\n"
            "    moveto gsave 1 setlinewidth\n"
            "    0 -12 rlineto -3 4 rmoveto 3 -4 rlineto 3 4 rlineto\n"
            "    stroke grestore\n"
            "} bind def\n"
        )

        # right hand indications
        fp.write(
            "\n/tabi { %% x n tabi - index finger\n"
            "    -5.5 add -%d mul moveto\n"
            "    currentpoint 2 copy 1.2 0 360 arc fill\n"
            "} bind def\n" % self.size)
        fp.write(
            "\n/tabm { %% x n tabm - middle finger\n"
            "    -5.5 add -%d mul moveto -1.3 0 rmoveto\n"
            "    currentpoint 2 copy 1.2 0 360 arc\n"
            "    currentpoint fill moveto 2.6 0 rmoveto\n"
            "    currentpoint 2 copy 1.2 0 360 arc fill\n"
            "} bind def\n" % self.size)
        fp.write(
            "\n/taba { %% x n taba - ring finger\n"
            "    -5.5 add -%d mul moveto -2.5 0 rmoveto\n"
            "    currentpoint 2 copy 1.2 0 360 arc\n"
            "    currentpoint fill moveto 2.5 0 rmoveto\n"
            "    currentpoint 2 copy 1.2 0 360 arc\n"
            "    currentpoint fill moveto 2.5 0 rmoveto\n"
            "    currentpoint 2 copy 1.2 0 360 arc fill\n"
            "} bind def\n" % self.size)

        fp.write(
            "\n/tabp { %% x n tabp - thumb\n"
            "    -5.5 add -%d mul moveto\n"
            "    gsave 1 setlinewidth\n"
            "    0 2.5 rmoveto 0 -5 rlineto\n"
            "    stroke grestore\n"
            "} bind def\n" % self.size)

        fp.write(
            "\n/tabpguitar { %% x n tabpguitar - thumb (guitar style)\n"
            "    -5.5 add -%d mul moveto\n"
            "    gsave 1 setlinewidth\n"
            "    0 2.5 rmoveto 0 -5 rlineto\n"
            "    -2.5 2.5 rmoveto 5 0 rlineto\n"
            "    stroke grestore\n"
            "} bind def\n" % self.size)

        fp.write("\n/tabten { %% x1 y1 x2 y2 tenuto stroke\n"
                 "    gsave 0.4 setlinewidth 4 2 roll moveto lineto stroke grestore\n"
                 "} bind def\n")


def is_tab_line(line):
    """
    decide whether an input line is tablature
    Returns true, if the line contains a v specifier [V:...]
    corresponding to a tablature v or if the current v
    is tablature by default

    :param line:
    :return:
    """
    voice_spec, line = util.get_field_value('V', line)
    # There is a problem here, these parameter are not used.
    if tab_key.is_tab_key(voice.switch_voice(voice_spec).key):
        return True
    else:
        # check default current v
        if tab_key.is_tab_key(voice.key):
            return True
    return False

#     def german_tabcode(self, de_course, fret):
#         """
#         computes code number from german font
#
#         :param de_course:
#         :param fret:
#         :return:
#         """
#         # codes for courses 1-5
#         # first index = fret, second = (5 - course)
#         gcode = [[32, 33, 34, 35, 36], [37, 38, 39, 40, 41],
#                  [42, 43, 44, 45, 46], [47, 48, 49, 50, 51],
#                  [52, 53, 54, 55, 56], [57, 58, 59, 60, 61],
#                  [62, 63, 64, 65, 66], [67, 68, 69, 70, 71],
#                  [72, 73, 74, 75, 76], [77, 78, 79, 80, 81],
#                  [82, 83, 84, 85, 86]]
#
#         if fret > ord('i'):
#             fret -= 1  # 'j' is not used
#         fret -= 97  # french frets start at 'a' == 97
#         if fret > 10 or de_course > 6:
#             return 0
#         if de_course < 6:
#             return gcode[fret][5 - de_course]
#         else:  # course == 6
#             if self.brummer == constants.BRUMMER_1AB:
#                 return 144 + fret
#             elif self.brummer == constants.BRUMMER_123:
#                 return 160 + fret
#             else:  # default: BRUMMER_ABC
#                 return 128 + fret
#
