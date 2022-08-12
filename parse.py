import re

import abctab2ps
from log import log
from constants import (S_SOURCE, S_RHYTHM, S_COMPOSER)
from constants import (NWPOOL, NTEXT)
from common import voices, ivc
import common
import symbol

sym = symbol.Symbol()


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


def add_text(s: str, t_type: int) -> None:
    if not common.do_output:
        return
    if len(common.text) >= NTEXT:
        log.warning(f"No more room for text line < {s}")
        return
    common.text.append(s)
    common.text_type.append(t_type)


def is_end_line(s: str) -> bool:
    """ identify eof """
    if len(s) < 3:
        return False
    if s.startswith('END'):
        return True
    return False



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

    # if not common.within_block:
    #     inf = info.Field()
    info = field.Field()

    if field.is_field(s):
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
        info.key(s)
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
        info.transcription_note(s)
    elif s.startswith( 'Q'):
        info.tempo(s)
    elif s.startswith( 'E'):
        info.layout_parameter(s)
    else:
        return False
    return True


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



def parse_uint(p) -> int:
    """ parse for unsigned integer """
    if not p.isdigit():
        number  = 0
    else:
        number = int(p)
    log.debug(f"    parsed unsigned int {number}")
    return number


# # ----- parse_bar: parse for some kind of bar ----
def parse_bar() -> bool:
    return False
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
                fac = parse_uint(line[p])
                if not fac:
                    fac = 1
                n_len *= fac

        if line[p] == '/':   # divide note length
            while line[p] == '/':
                p += 1
                if line[p].isdigit():
                    fac = parse_uint(line[p])
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


def parse_music_line(line: str) -> int:
    NotImplementedError()
    return 0
#     """ parse a music line into symbols """
#     # int num,nbr,n,itype,i
#     # char msg[81]
#
#     if ivc >= len(voices):
#         log.critical(f"Trying to parse undefined voice {True}")
#         exit(1)
#
#     common.nwline = 0
#     s_type = 0
#     nsym0 = len(voices[ivc].syms)
#
#     nbr = 0
#     p = 0
#
#     while p < len(line):
#         if p > len(line):
#             break   # emergency exit
#         s_type = parse_sym()
#         n = (voices[ivc].syms)
#         i = n-1
#         if common.db > 4 and s_type:
#             print(f"     sym[{n-1}] code ({voices[ivc].syms[n-1].type},{voices[ivc].syms[n-1].u}")
#
#         if s_type == NEWLINE:
#             if n > 0 and not cfmt.continueall and not cfmt.barsperstaff:
#                 voices[ivc].syms[i].eoln=1
#                 if common.word:
#                     voices[ivc].syms[common.last_note].word_end = True
#                     common.word = False
#
#         if s_type == ESCSEQ:
#             if db > 3:
#                 print(f"Handle escape sequence <{escseq}>")
#             itype = info_field(escseq)
#             handle_inside_field(itype)
#
#         if s_type == REST:
#             if pplet:   # n-plet can start on rest
#                 voices[ivc].syms[i].p_plet = pplet
#                 voices[ivc].syms[i].q_plet = qplet
#                 voices[ivc].syms[i].r_plet = rplet
#                 pplet=0
#             common.last_note = i     # need this so > and < work
#             p1 = p
#
#         if s_type == NOTE:
#             if not common.word:
#                 voices[ivc].syms[i].word_st = True
#                 word = True
#             if nbr and cfmt.slurisligatura:
#                 voices[ivc].syms[i].lig1 += nbr
#             else:
#                 voices[ivc].syms[i].slur_st += nbr
#             nbr=0
#             if voices[ivc].end_slur:
#                 voices[ivc].syms[i].slur_end += 1
#             voices[ivc].end_slur = 0
#
#             if pplet:                                    # start of n-plet
#                 voices[ivc].syms[i].p_plet = pplet
#                 voices[ivc].syms[i].q_plet = qplet
#                 voices[ivc].syms[i].r_plet = rplet
#                 pplet=0
#             last_note = last_real_note = i
#             p1 = p
#
#         if common.word and s_type == BAR or s_type == SPACE:
#             if last_real_note >= 0:
#                 voices[ivc].syms[last_real_note].word_end = True
#                 common.word = False
#
#         if not s_type:
#             if p == '-':   # a-b tie
#                 voices[ivc].syms[common.last_note].slur_st += 1
#                 voices[ivc].end_slur=1
#                 p += 1
#
#             elif p == '(':
#                 p += 1
#                 if p.isdigit():
#                     pplet = char_delta(line[p],'0')
#                     qplet = 0
#                     rplet = pplet
#                     p += 1
#                     if p == ':':
#                         p += 1
#                         if p.isdigit():
#                             qplet = char_delta(line[p],'0')
#                             p += 1
#                         if p == ':':
#                             p += 1
#                             if p.isdigit():
#                                 rplet = char_delta(line[p],'0')
#                                 p += 1
#                 else:
#                     nbr += 1
#             elif *p == ')':
#                 if common.last_note > 0:
#                     if cfmt.slurisligatura:
#                         voices[ivc].syms[common.last_note].lig2 += 1
#                     else:
#                         voices[ivc].syms[common.last_note].slur_end += 1
#                 else:
#                     SyntaxError(f"Unexpected symbol {p}")
#                 p += 1
#             elif *p == '>':
#                 num=1
#                 p += 1
#                 while *p == '>':
#                     num += 1
#                     p += 1
#                 if last_note < 0:
#                     SyntaxError("No note before > sign", p)
#                 else:
#                     double_note(last_note, num, 1, p1)
#             elif *p == '<':
#                     num = 1
#                     p += 1
#                     while *p == '<':
#                         num += 1
#                         p += 1
#                     if last_note < 0:
#                             SyntaxError("No note before < sign", p)
#                     else:
#                             double_note (last_note, num, -1, p1)
#             elif *p == '*':      # ignore stars for now
#                 p += 1
#             elif *p == '!':      # ditto for '!'
#                 p += 1
#             else:
#                 if *p != '\0':
#                     msg = f"Unexpected symbol '{line[p]}'"
#                 else:
#                     msg = f"Unexpected end of line"
#                 SyntaxError(msg, line[p])
#                 p += 1
#
#     # maybe set end-of-line marker, if symbols were added
#     n = len(voices[ivc].syms)
#
#     if n > nsym0:
#         if s_type == CONTINUE or cfmt.barsperstaff or cfmt.continueall:
#             voices[ivc].syms[n-1].eoln = False
#         else:
#             # add invisible bar, if last symbol no bar
#             if voices[ivc].syms[n-1].s_type != BAR:
#                 i = add_sym(BAR)
#                 voices[ivc].syms[i].u = B_INVIS
#                 n = i+1
#             }
#             voices[ivc].syms[n-1].eoln=1
#
#     # break words at end of line
#     if common.word and voices[ivc].syms[n-1].eoln:
#         voices[ivc].syms[common.last_note].word_end = True
#         common.word = False
#
#     return TO_BE_CONTINUED
#


def is_selected(xref_str: str, pat: list, select_all: bool, search_field: int) -> bool:
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


def is_xrefstr(xrefstr: str) -> bool:
    """ check if string ok for xref selection
    This will end up in info.XRef class"""
    return xrefstr.isdigit() and int(xrefstr) != 0


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
        elif field.is_xrefstr(value):
            xref_str = value
        else:  # pattern with * or +
            if '*' in value or '+' in value:
                pat.append(value)
            else:   # simple pattern
                pat.append("*" + value + '*')

    return pat, xref_str


def decomment_line(ln: str) -> str:
    """ cut off after % """
    in_quotes = False   # do not remove inside double quotes
    for i, p in enumerate(list(ln)):
        if p == '"':
            if in_quotes:
                    in_quotes = False
            else:
                in_quotes = True
        if p == '%' and not in_quotes:
            return ln[0:i]
    return ln


def do_index(filename, xref_str: str, pat: list, select_all: bool, search_field: int) -> None:
    """ index of abc file """
    import constants
    import field

    common.within_tune = False
    common.within_block = False
    common.do_this_tune = False
    info = field.Field()

    with open(filename) as fp:
        lines = fp.readlines()
    for line in lines:
        if abctab2ps.is_comment(line):
            continue
        line = decomment_line(line)
        f_type = info.get_default_info()   # todo this right?
                
        if f_type == constants.XREF:
            if common.within_block:
                log.info(f"+++ Tune {info.xref.xref} not closed properly ")
            common.number_of_titles = 0
            common.within_tune = False
            common.within_block = True
            common.ntext = 0
            break
            
        elif f_type == constants.KEY:
            if not common.within_block:
                break
            if not common.within_tune:
                common.tnum2 += 1
                if is_selected(xref_str, pat, select_all, search_field):
                    log.info(f"    {info.xref.xref:-4d} {info.key.key_type:-5s} {info.meter:-4s}")
                    if search_field == S_SOURCE:
                        log.info(f"    {info.source:-15s}")

                    elif search_field == S_RHYTHM:
                        log.info(f"    {info.rhythm:-8s}")
                    elif search_field == S_COMPOSER:
                        log.info(f"    {info.composer[0]:-15s}")
                    if common.number_of_titles == 3:
                        log.info(f"    {info.titles[0]} - {info.titles[1]} - {info.titles[2]}")
                    if common.number_of_titles == 2:
                        log.info(f"    {info.titles[0]} - {info.titles[1]}")
                    if common.number_of_titles == 1:
                        log.info(f"    {info.titles[0]}")

                    common.tnum1 += 1
                common.within_tune=1
            break

        if not line:
            if common.within_block and not common.within_tune:
                log.info(f"+++ Header not closed in tune {info.xref.xref}")
            common.within_tune = False
            common.within_block = False
            info = info.Field()
    if common.within_block and not common.within_tune:
        log.info(f"+++ Header not closed in for tune {info.xref.xref}", )
