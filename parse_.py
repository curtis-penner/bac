import log
import constants
import common
import key
import format

log = log.log()
key = key.Key()
cfmt = format.Format()

voices = list()

def init_parse_params():
    """
    initialize variables for parsing
    
    :return: 
    """
    slur = 0
    nwpool = nwline = 0
    ntinext = 0


    # for continuation after output: reset nsym, switch to first v
    for voice in voices:
        voice.sym = list()
        # this would suppress tie/repeat carryover from previous page:
        voice.insert_btype = 0
        voice.end_slur = 0

    ivc = 0
    word = False
    carryover = False
    last_note = last_real_note = -1
    pplet = qplet = rplet = 0
    num_ending = 0
    mes1 = mes2 = 0
    prep_gchlst = list()
    prep_deco = list()


def add_text(line, f_type):
    """

    :param line:
    :param f_type:
    """
    if common.do_mode != constants.DO_OUTPUT:
        return
    if ntext >= constants.NTEXT:
        log.error(f"No more room for text line {line}")
        return
    text[ntext] = line
    text_type[ntext] = f_type
    ntext += 1




def is_end_line(line):
    """ identify eof """
    line = line.strip()
    return len(line) == 3 and line.startswith('END')


def is_pseudocomment(line):
    return line.startswith('%%')


def is_comment(line):
    return line.startswith('%') or line.startswith('\\')


def is_cmdline(line):
    return len(line) > 2 and line.strip().startswith('%!')



"""
# ----- switch_voice: read spec for a v, return v number ----- 
int switch_voice (char *str)
{
        int j,np,newv;
        char *r,*q;
        char t1[STRLINFO],t2[STRLINFO];

        if (!do_this_tune) return 0;

        j=-1;

        # start loop over v options: parse t1=t2 
        r=str;
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

                # interpret the parsed option. First case is identifier. 
                if (np==1) {
                        j=find_voice (t1,&newv);
                }

                else:         # interpret option
                        if j < 0:
                            bug("j invalid in switch_voice", True)
                        if            (!strcmp(t1,"name")        || !strcmp(t1,"nm"))     
                                strcpy(v[j].name,    t2);

                        elif (!strcmp(t1,"sname")     || !strcmp(t1,"snm"))    
                                strcpy(v[j].sname, t2);

                        elif (!strcmp(t1,"staves")    || !strcmp(t1,"stv"))    
                                v[j].staves    = atoi(t2);

                        elif (!strcmp(t1,"brace")     || !strcmp(t1,"brc")) 
                                v[j].brace     = atoi(t2);

                        elif (!strcmp(t1,"bracket") || !strcmp(t1,"brk")) 
                                v[j].bracket = atoi(t2);

                        elif (!strcmp(t1,"gchords") || !strcmp(t1,"gch"))
                                g_logv (str,t2,&v[j].do_gch);

                        # for sspace: add 2000 as flag if not incremental    
                        elif (!strcmp(t1,"space")     || !strcmp(t1,"spc")) {    
                                g_unum (str,t2,&v[j].sep);
                                if (t2[0]!='+' && t2[0]!='-') v[j].sep += 2000.0;
                        }

                        elif (!strcmp(t1,"clef")        || !strcmp(t1,"cl")) {
                                if (!set_clef(t2,&v[j].key))
                                        std::cerr << "Unknown clef in v spec: " << t2 << std::endl;
                        }
                        elif (!strcmp(t1,"stems") || !strcmp(t1,"stm")) {
                                if            (!strcmp(t2,"up"))        v[j].stems=1;
                                elif (!strcmp(t2,"down"))    v[j].stems=-1;
                                elif (!strcmp(t2,"free"))    v[j].stems=0;
                                else std::cerr << "Unknown stem setting in v spec: " << t2 << std::endl;
                        }
                        elif (!strcmp(t1,"octave")) {
                                ; # ignore abc2midi parameter for compatibility 
                        }
                        else std::cerr << "Unknown option in v spec: " << t1 << std::endl;
                }

        }

        # if new v was initialized, save settings im meter0, key0 
        if (newv) {
                v[j].meter0 = v[j].meter;
                v[j].key0     = v[j].key;
        }

        if (verbose>7) 
                printf ("Switch to v %d    <%s> <%s> <%s>    clef=%d\n", 
                                j,v[j].id,v[j].name,v[j].sname, 
                                v[j].key.ktype); 

        nsym0=v[j].nsym;    # set nsym0 to decide about eoln later.. ugly 
        return j;

} 


# ----- info_field: identify info line, store in proper place    ---- 
# switch within_block: either goes to default_info or info.
# Only xref ALWAYS goes to info.
def info_field(line):
    inf = constants.ISTRUCT

    if constants.within_block:
        inf = info;
    else:
        inf = default_info;

    if (strlen(str)<2) return 0;
    if (str[1]!=':')     return 0;
    if (str[0]=='|')     return 0;     # |: at start of music line

    for (i=0;i<strlen(str);i++) if (str[i]=='%') str[i]='\0';

    # info fields must not be longer than STRLINFO characters
    s = util.strnzcpy(line, constants.STRLINFO)

    if (s[0]=='X') {
            strip (info.xref,     &s[2]);
            xrefnum=get_xref(info.xref);
            return XREF;
    }

    elif (s[0]=='A') strip (inf->area,     &s[2]);
    elif (s[0]=='B') strip (inf->book,     &s[2]);
    elif (s[0]=='C') {
            if (inf->ncomp>=NCOMP)
                    std::cerr << "Too many composer lines\n";
            else {
                    strip (inf->comp[inf->ncomp],&s[2]);
                    inf->ncomp++;
            }
    }
    elif (s[0]=='D') {
            strip (inf->disc,     &s[2]);
            add_text (&s[2], TEXT_D);
    }

    elif (s[0]=='F') strip (inf->file,     &s[2]);
    elif (s[0]=='G') strip (inf->group,    &s[2]);
    elif (s[0]=='H') {
            strip (inf->hist,     &s[2]);
            add_text (&s[2], TEXT_H);
            return HISTORY;
    }
    elif (s[0]=='W') {
            add_text (&s[2], TEXT_W);
            return WORDS;
    }
    elif (s[0]=='I') strip (inf->info,     &s[2]);
    elif (s[0]=='K') {
            strip (inf->key,        &s[2]);
            return KEY;
    }
    elif (s[0]=='L') {
            strip (inf->len,        &s[2]);
            return DLEN;
    }
    elif (s[0]=='M') {
            strip (inf->meter,    &s[2]);
            return METER;
    }
    elif (s[0]=='N') {
            strip (inf->notes,    &s[2]);
            add_text (&s[2], TEXT_N);
    }
    elif (s[0]=='O') strip (inf->orig,     &s[2]);
    elif (s[0]=='R') strip (inf->rhyth,    &s[2]);
    elif (s[0]=='P') {
            strip (inf->parts,    &s[2]);
            return PARTS;
    }
    elif (s[0]=='S') strip (inf->src,        &s[2]);
    elif (s[0]=='T') {
            //strip (t, &s[2]);
            numtitle++;
            if (numtitle>3) numtitle=3;
            if (numtitle==1)            strip (inf->title,    &s[2]);
            elif (numtitle==2) strip (inf->title2, &s[2]);
            elif (numtitle==3) strip (inf->title3, &s[2]);
            return TITLE;
    }
    elif (s[0]=='V') {
            strip (lvoiceid,    &s[2]);
            if (!*lvoiceid) {
                    syntax("missing v specifier",p);
                    return 0;
            }
            return VOICE;
    }
    elif (s[0]=='Z') {
            strip (inf->trans,    &s[2]);
            add_text (&s[2], TEXT_Z);
    }
    elif (s[0]=='Q') {
            strip (inf->tempo,    &s[2]);
            return TEMPO;
    }

    elif (s[0]=='E') ;

    else {
            return 0;
    }

    return INFO;


# ----- append_meter: add meter to list of music -------- 
#
# * Warning: only called for inline fields
# * normal meter music are added in set_initsyms
 
void append_meter (const struct METERSTR* meter)
{
        int kk;

        //must not be ignored because we need meter for counting bars!
        //if (meter->display==0) return;

        kk=add_sym(TIMESIG);
        symv[ivc][kk]=zsym;
        symv[ivc][kk].gchords= new GchordList();
        symv[ivc][kk].type = TIMESIG;
        if (meter->display==2) {
                symv[ivc][kk].u        = meter->dismeter1;
                symv[ivc][kk].v        = meter->dismeter2;
                symv[ivc][kk].w        = meter->dismflag;
                strcpy(symv[ivc][kk].text,meter->distop);
        } else {
                symv[ivc][kk].u        = meter->meter1;
                symv[ivc][kk].v        = meter->meter2;
                symv[ivc][kk].w        = meter->mflag;
                strcpy(symv[ivc][kk].text,meter->top);
        }
        if (meter->display==0) symv[ivc][kk].invis=1;
}

# ----- append_key_change: append change of key to sym list ------ 
void append_key_change(struct KEYSTR oldkey, struct KEYSTR newkey)
{
        int n1,n2,t1,t2,kk;

        n1=oldkey.sf;        
        t1=A_SH;
        if (n1<0) { n1=-n1; t1=A_FT; }
        n2=newkey.sf;        
        t2=A_SH;                                        

        if (newkey.ktype != oldkey.ktype) {            # clef change 
                kk=add_sym(CLEF);
                symv[ivc][kk].u=newkey.ktype;
                symv[ivc][kk].v=1;
        }

        if (n2<0) { n2=-n2; t2=A_FT; }
        if (t1==t2) {                            # here if old and new have same type 
                if (n2>n1) {                                 # more new music ..
                        kk=add_sym(KEYSIG);                # draw all of them 
                        symv[ivc][kk].u=1;
                        symv[ivc][kk].v=n2;
                        symv[ivc][kk].w=100;
                        symv[ivc][kk].t=t1;
                }
                elif (n2<n1) {                        # less new music .. 
                        kk=add_sym(KEYSIG);                    # draw all new music and neutrals 
                        symv[ivc][kk].u=1;
                        symv[ivc][kk].v=n1;
                        symv[ivc][kk].w=n2+1;
                        symv[ivc][kk].t=t2;
                }
                else return;
        }
        else {                                         # here for change s->f or f->s 
                kk=add_sym(KEYSIG);                    # neutralize all old music 
                symv[ivc][kk].u=1;
                symv[ivc][kk].v=n1;
                symv[ivc][kk].w=1;
                symv[ivc][kk].t=t1;
                kk=add_sym(KEYSIG);                    # add all new music 
                symv[ivc][kk].u=1;
                symv[ivc][kk].v=n2;
                symv[ivc][kk].w=100;
                symv[ivc][kk].t=t2;
        }

}



# ----- numeric_pitch ------ 
# adapted from abc2mtex by Chris Walshaw 
int numeric_pitch(char note)
{

        if (note=='z') 
                return 14;
        if (note >= 'C' && note <= 'G')
                return(note-'C'+16+v[ivc].key.add_pitch);
        elif (note >= 'A' && note <= 'B')
                return(note-'A'+21+v[ivc].key.add_pitch);
        elif (note >= 'c' && note <= 'g')
                return(note-'c'+23+v[ivc].key.add_pitch);
        elif (note >= 'a' && note <= 'b')
                return(note-'a'+28+v[ivc].key.add_pitch);
        printf ("numeric_pitch: cannot identify <%c>\n", note);
        return(0);
}

# ----- symbolic_pitch: translate numeric pitch back to symbol ------ 
int symbolic_pitch(int pit, char *str)
{
        int    p,r,s;
        char ltab1[7] = {'C','D','E','F','G','A','B'};
        char ltab2[7] = {'c','d','e','f','g','a','b'};

        p=pit-16;
        r=(p+700)%7;
        s=(p-r)/7;

        if (p<7) {
                sprintf (str,"%c,,,,,",ltab1[r]);
                str[1-s]='\0';
        }
        else {
                sprintf (str,"%c'''''",ltab2[r]);
                str[s]='\0';
        }
        return 0;
}

# ----- handle_inside_field: act on info field inside body of tune --- 
void handle_inside_field(int type)
{
        struct KEYSTR oldkey;
        int rc;

        if (type==METER) {
                if (nvoice==0) ivc=switch_voice (DEFVOICE);
                set_meter (info.meter,&v[ivc].meter);
                append_meter (&(v[ivc].meter));
        }

        elif (type==DLEN) {
                if (nvoice==0) ivc=switch_voice (DEFVOICE);
                set_dlen (info.len,    &v[ivc].meter);
        }

        elif (type==KEY) {
                if (nvoice==0) ivc=switch_voice (DEFVOICE);
                oldkey=v[ivc].key;
                rc=set_keysig(info.key,&v[ivc].key,0);
                if (rc) set_transtab (halftones,&v[ivc].key);
                append_key_change(oldkey,v[ivc].key);
        }

        elif (type==VOICE) {
                ivc=switch_voice (lvoiceid);
        }

}



# ----- parse_uint: parse for unsigned integer ----- 
int parse_uint (void)
{
        int number,ndig;
        char num[21];

        if (!isdigit(*p)) return 0;
        ndig=0;
        while (isdigit(*p)) {                                
                num[ndig]=*p; 
                ndig++; 
                num[ndig]=0;
                p++;
        }
        sscanf (num, "%d", &number);
        if (db>3) printf ("    parsed unsigned int %d\n", number);
        return number;

}

# ----- parse_bar: parse for some kind of bar ---- 
int parse_bar (void)
{
        int j;
        GchordList::iterator ii;

        # special cases: [1 or [2 without a preceeding bar, [| 
        if (*p=='[') {
                if (strchr("123456789",*(p+1))) {
                        j=add_sym (BAR);
                        symv[ivc][j].u=B_INVIS;
                        symv[ivc][j].v=chartoi(*(p+1));
                        p=p+2;
                        return 1;
                }
        }

        # identify valid standard bar types 
        if (*p == '|') {
                p++;
                if (*p == '|') { 
                        j=add_sym (BAR);
                        symv[ivc][j].u=B_DBL;
                        p++;
                }
                elif (*p == ':') { 
                        j=add_sym(BAR);
                        symv[ivc][j].u=B_LREP;
                        p++; 
                }
                elif (*p==']') {                                    # code |] for fat end bar 
                        j=add_sym(BAR);
                        symv[ivc][j].u=B_FAT2;
                        p=p+1;
                }
                else {
                        j=add_sym(BAR);
                        symv[ivc][j].u=B_SNGL;
                }
        }
        elif (*p == ':') {
                if (*(p+1) == '|') { 
                        j=add_sym(BAR);
                        symv[ivc][j].u=B_RREP;
                        p+=2;
                }
                elif (*(p+1) == ':') {
                        j=add_sym(BAR);
                        symv[ivc][j].u=B_DREP;
                        p+=2; }
                else {
                        # ':' is decoration in tablature
                         *syntax ("Syntax error parsing bar", p-1);
                         
                        return 0;
                }
        }

        elif ((*p=='[') && (*(p+1)=='|') && (*(p+2)==']')) {    # code [|] invis 
                j=add_sym(BAR);
                symv[ivc][j].u=B_INVIS;
                p=p+3;
        }

        elif ((*p=='[') && (*(p+1)=='|')) {        # code [| for thick-thin bar 
                j=add_sym(BAR);
                symv[ivc][j].u=B_FAT1;
                p=p+2;
        }

        else return 0;

        # copy over preparsed stuff (gchords, decos) 
        strcpy(symv[ivc][j].text,"");
        if (!prep_gchlst.empty()) {
                for (ii=prep_gchlst.begin(); ii!=prep_gchlst.end(); ii++) {
                        symv[ivc][j].gchords->push_back(*ii);
                }
                prep_gchlst.clear();
        }
        if (prep_deco.n) {
                for (int i=0; i<prep_deco.n; i++) {
                        int deco=prep_deco.t[i];
                        if ((deco!=D_STACC) && (deco!=D_SLIDE))
                                symv[ivc][j].dc.add(deco);
                }
                prep_deco.clear();
        }

        # see if valid bar is followed by specifier for first or second ending 
        if (strchr("123456789",*p)) {
                symv[ivc][j].v=chartoi(*p); p++;
        } elif ((*p=='[') && (strchr("123456789",*(p+1)))) {
                symv[ivc][j].v=chartoi(*(p+1)); p=p+2;
        } elif ((*p==' ') && (*(p+1)=='[') && (strchr("123456789",*(p+2)))) {
                symv[ivc][j].v=chartoi(*(p+2)); p=p+3;
        }

        return 1;
}

# ----- parse_space: parse for whitespace ---- 
int parse_space (void)
{
        int rc;

        rc=0;
        while ((*p==' ')||(*p=='\t')) {
                rc=1;
                p++;
        }
        if (db>3) if (rc) printf ("    parsed whitespace\n"); 
        return rc;
}

# ----- parse_esc: parse for escape sequence ----- 
int parse_esc (void)
{

        int nseq;
        char *pp;

        if (*p == '\\') {                                         # try for \...\ sequence 
                p++;
                nseq=0;
                while ((*p!='\\') && (*p!=0)) {
                        escseq[nseq]=*p;
                        nseq++;
                        p++;
                }
                if (*p == '\\') {
                        p++;
                        escseq[nseq]=0;
                        if (db>3) printf ("    parsed esc sequence <%s>\n", escseq);    
                        return ESCSEQ;
                }
                else {
                        if (cfmt.breakall) return DUMMY;
                        if (db>3) printf ("    parsed esc to EOL.. continuation\n");    
                }
                return CONTINUE;
        }

        # next, try for [..] sequence 
        if ((*p=='[') && (*(p+1)>='A') && (*(p+1)<='Z') && (*(p+2)==':')) {    
                pp=p;
                p++;
                nseq=0;
                while ((*p!=']') && (*p!=0)) {
                        escseq[nseq]=*p;
                        nseq++;
                        p++;
                }                     
                if (*p == ']') {
                        p++;
                        escseq[nseq]=0;
                        if (db>3) printf ("    parsed esc sequence <%s>\n", escseq);    
                        return ESCSEQ;
                }
                syntax ("Escape sequence [..] not closed", pp);
                return ESCSEQ;
        }
        return 0;
}
"""

# ----- parse_nl: parse for newline ----- 
def parse_nl(line):
    """
    :param str line:
    :return str:
    """
    if line.startswith('\\\\'):
        return line[2:]
    else:
        return line

"""
# ----- parse_gchord: parse guitar chord, add to global prep_gchlst ----- 
int parse_gchord ()
{
        char *q;
        int n=0;
        Gchord gchnew;

        if (*p != '"') return 0;

        q=p;
        p++;
        //n=strlen(gch);
        //if (n > 0) syntax ("Overwrite unused guitar chord", q);

        while ((*p != '"') && (*p != 0)) {
                gchnew.text += *p;
                n++;
                if (n >= 200) {
                        syntax ("String for guitar chord too long", q);
                        return 1;
                }
                p++;
        }
        if (*p == 0) {
                syntax ("EOL reached while parsing guitar chord", q);
                return 1;
        }
        p++;
        if (db>3) printf("    parse guitar chord <%s>\n", gchnew.text.c_str());
        gch_transpose(&gchnew.text, v[ivc].key);
        prep_gchlst.push_back(gchnew);

        #|     gch_transpose (v[ivc].key); |

        return 1;
}


# ----- parse_deco: parse for decoration, add to global prep_deco ----- 
int parse_deco ()
{
        int deco,n;
        # mapping abc code to decorations 
        # for no abbreviation, set abbrev=0; for no !..! set fullname="" 
        struct s_deconame { int index; char abbrev; char* fullname; };
        static struct s_deconame deconame[] = {
                {D_GRACE,     '~', "!grace!"},
                {D_STACC,     '.', "!staccato!"},
                {D_SLIDE,     'J', "!slide!"},
                {D_TENUTO,    'N', "!tenuto!"},
                {D_HOLD,        'H', "!fermata!"},
                {D_ROLL,        'R', "!roll!"},
                {D_TRILL,     'T', "!trill!"},
                {D_UPBOW,     'u', "!upbow!"},
                {D_DOWNBOW, 'v', "!downbow!"},
                {D_HAT,         'K', "!sforzando!"},
                {D_ATT,         'j', "!accent!"},
                {D_ATT,         'L', "!emphasis!"}, #for abc standard 1.7.6 compliance
                {D_SEGNO,     'S', "!segno!"},
                {D_CODA,        'O', "!coda!"},
                {D_PRALLER, 'P', "!pralltriller!"},
                {D_PRALLER, 'P', "!uppermordent!"}, #for abc standard 1.7.6 compliance
                {D_MORDENT, 'M', "!mordent!"},
                {D_MORDENT, 'M', "!lowermordent!"}, #for abc standard 1.7.6 compliance
                {D_TURN,         0,    "!turn!"},
                {D_PLUS,         0,    "!plus!"},
                {D_PLUS,         0,    "!+!"}, #for abc standard 1.7.6 compliance
                {D_CROSS,     'X', "!x!"},
                {D_DYN_PP,     0,    "!pp!"},
                {D_DYN_P,        0,    "!p!"},
                {D_DYN_MP,     0,    "!mp!"},
                {D_DYN_MF,     0,    "!mf!"},
                {D_DYN_F,        0,    "!f!"},
                {D_DYN_FF,     0,    "!ff!"},
                {D_DYN_SF,     0,    "!sf!"},
                {D_DYN_SFZ,    0,    "!sfz!"},
                {D_BREATH,     0,    "!breath!"},
                {D_WEDGE,        0,    "!wedge!" },
                {0, 0, ""} #end marker
        };
        struct s_deconame* dn;

        n=0;

        for (;;) {
                deco=0;

                #check for fullname deco
                if (*p == '!') {
                        int slen;
                        char* q;
                        q = strchr(p+1,'!');
                        if (!q) {
                                syntax ("Deco sign '!' not closed",p);
                                p++;
                                return n;
                        } else {
                                slen = q+1-p;
                                #lookup in table
                                for (dn=deconame; dn->index; dn++) {
                                        if (0 == strncmp(p,dn->fullname,slen)) {
                                                deco = dn->index;
                                                break;
                                        }
                                }
                                if (!deco) syntax("Unknown decoration",p+1);
                                p += slen;
                        }
                }
                #check for abbrev deco
                else {
                        for (dn=deconame; dn->index; dn++) {
                                if (dn->abbrev && (*p == dn->abbrev)) {
                                        deco = dn->index;
                                        p++;
                                        break;
                                }
                        }
                }

                if (deco) {
                        prep_deco.add(deco);
                        n++;
                }
                else 
                        break;
        }

        return n;
}


# ----- parse_length: parse length specifer for note or rest --- 
int parse_length (void)
{
        int len,fac;

        len=v[ivc].meter.dlen;                    # start with default length 

        if (len<=0) {
                syntax("got len<=0 from current v", p);
                printf("Cannot proceed without default length. Emergency stop.\n");
                exit(1);
        }

        if (isdigit(*p)) {                                 # multiply note length 
                fac=parse_uint ();
                if (fac==0) fac=1;
                len *= fac;
        }

        if (*p=='/') {                                     # divide note length 
                while (*p=='/') {
                        p++;
                        if (isdigit(*p)) 
                                fac=parse_uint();
                        else 
                                fac=2;
                        if (len%fac) {
                                syntax ("Bad length divisor", p-1);
                                return len; 
                        }
                        len=len/fac;
                }
        }

        return len;
}

# ----- parse_brestnum parses the number of measures on a brest 
int parse_brestnum (void)
{
        int fac,len;
        len=1;
        if (isdigit(*p)) {                                 # multiply note length 
                fac=parse_uint ();
                if (fac==0) fac=1;
                len *= fac;
        }
        return len;
}

# ----- parse_grace_sequence --------- 
#
 * result is stored in arguments
 * when no grace sequence => arguments are not altered
 
int parse_grace_sequence (int *pgr, int *agr, int* len)
{
        char *p0;
        int n;

        p0=p;
        if (*p != '{') return 0;
        p++;

        *len = 0;     # default is no length => accacciatura 
        n=0;
        while (*p != '}') {
                if (*p == '\0') {
                        syntax ("Unbalanced grace note sequence", p0);
                        return 0;
                }
                if (!isnote(*p)) {
                        syntax ("Unexpected symbol in grace note sequence", p);
                        p++;
                }
                if (n >= MAXGRACE) {
                        p++; continue;
                }
                agr[n]=0;    
                if (*p == '=') agr[n]=A_NT;
                if (*p == '^') {
                        if (*(p+1)=='^') { agr[n]=A_DS; p++; }
                        else agr[n]=A_SH;
                }
                if (*p == '_') {
                        if (*(p+1)=='_') { agr[n]=A_DF; p++; }
                        else agr[n]=A_FT;
                }
                if (agr[n]) p++;

                pgr[n] = numeric_pitch(*p);
                p++;
                while (*p == '\'') { pgr[n] += 7; p++; }
                while (*p == ',') {    pgr[n] -= 7; p++; }

                do_transpose (v[ivc].key, &pgr[n], &agr[n]);

                # parse_length() returns default length when no length specified 
                # => we may only call it when explicit length specified 
                if (*p == '/' || isdigit(*p))
                        *len=parse_length ();
                n++;
        }

        p++;
        return n;
}

# ----- identify_note: set head type, dots, flags for note --- 
void identify_note (struct SYMBOL *s, char *q)
{
        int head,base,len,flags,dots;

        if (s->len==0) s->len=s->lens[0];
        len=s->len;

        # set flag if duration equals (or gretaer) length of one measure 
        if (nvoice>0) {
                if (len>=(WHOLE*v[ivc].meter.meter1)/v[ivc].meter.meter2)
                        s->fullmes=1;
        }

        base=LONGA;
        if (len>=LONGA)                            base=LONGA;
        elif (len>=BREVIS)                base=BREVIS;
        elif (len>=WHOLE)                 base=WHOLE;
        elif (len>=HALF)                    base=HALF;
        elif (len>=QUARTER)             base=QUARTER;
        elif (len>=EIGHTH)                base=EIGHTH;
        elif (len>=SIXTEENTH)         base=SIXTEENTH;
        elif (len>=THIRTYSECOND)    base=THIRTYSECOND;
        elif (len>=SIXTYFOURTH)     base=SIXTYFOURTH;
        else syntax("Cannot identify head for note",q);

        if (base>=WHOLE)         head=H_OVAL;
        elif (base==HALF) head=H_EMPTY;
        else                                 head=H_FULL;

        if (base==SIXTYFOURTH)                flags=4;
        elif (base==THIRTYSECOND)    flags=3;
        elif (base==SIXTEENTH)         flags=2;
        elif (base==EIGHTH)                flags=1;
        else                                                    flags=0;

        dots=0;
        if (len==base)                        dots=0;
        elif (2*len==3*base)     dots=1;
        elif (4*len==7*base)     dots=2;
        elif (8*len==15*base)    dots=3;
        else syntax("Cannot handle note length for note",q);

        #    printf ("identify_note: length %d gives head %d, dots %d, flags %d\n",
                len,head,dots,flags);    

        s->head=head;
        s->dots=dots;
        s->flags=flags;
}


# ----- double_note: change note length for > or < char --- 
# Note: if symv[ivc][i] is a chord, the length shifted to the following
     note is taken from the first note head. Problem: the crazy syntax 
     permits different lengths within a chord. 
void double_note (int i, int num, int sign, char *q)
{
        int m,shift,j,len;

        if ((symv[ivc][i].type!=NOTE) && (symv[ivc][i].type!=REST)) 
                bug("sym is not NOTE or REST in double_note", True)

        shift=0;
        len=symv[ivc][i].lens[0];
        for (j=0;j<num;j++) {
                len=len/2;
                shift -= sign*len;
                symv[ivc][i].len += sign*len;
                for (m=0;m<symv[ivc][i].npitch;m++) symv[ivc][i].lens[m] += sign*len;
        }
        identify_note (&symv[ivc][i],q);
        carryover += shift;
}

# ----- parse_basic_note: parse note or rest with pitch and length --
int parse_basic_note (int *pitch, int *length, int *accidental)
{
        int pit,len,acc;

        acc=pit=0;                                             # look for accidental sign 
        if (*p == '=') acc=A_NT;
        if (*p == '^') {
                if (*(p+1)=='^') { acc=A_DS; p++; }
                else acc=A_SH;
        }
        if (*p == '_') {
                if (*(p+1)=='_') { acc=A_DF; p++; }
                else acc=A_FT;
        }

        if (acc) {
                p++;
                if (!strchr("CDEFGABcdefgab",*p)) {
                        syntax("Missing note after accidental", p-1);
                        return 0;
                }
        }
        if (!isnote(*p)) {
                syntax ("Expecting note", p);
                p++;
                return 0;
        }

        pit= numeric_pitch(*p);                         # basic pitch 
        p++;

        while (*p == '\'') {                                # eat up following ' chars 
                pit += 7;
                p++;
        }

        while (*p == ',') {                                 # eat up following , chars 
                pit -= 7;
                p++;
        }

        len=parse_length();

        do_transpose (v[ivc].key, &pit, &acc);

        *pitch=pit;
        *length=len;
        *accidental=acc;

        if (db>3) printf ("    parsed basic note,"
                        "length %d/%d = 1/%d, pitch %d\n", 
                        len,BASE,BASE/len,pit);

        return 1;

}


# ----- parse_note: parse for one note or rest with all trimmings --- 
int parse_note (void)
{
        int j,deco,i,chord,m,type,rc,sl1,sl2,j,n;
        int pitch,length,accidental,invis;
        char *q,*q0;
        GchordList::iterator ii;
        #grace sequence must be remembered in static variables,
        #because otherwise it is lost after slurs
        static int ngr = 0;
        static int pgr[MAXGRACE],agr[MAXGRACE],lgr;

        n=parse_grace_sequence(pgr,agr,&lgr);     # grace notes 
        if (n) ngr = n;

        parse_gchord();                             # permit chord after graces 

        deco=parse_deco();                            # decorations 

        parse_gchord();                             # permit chord after deco 

        chord=0;                                                         # determine if chord 
        q=p;
        if ((*p=='+') || (*p=='[')) { chord=1; p++; }

        type=invis=0;
        parse_deco(); # allow for decos within chord 
        if (isnote(*p)) type=NOTE;
        if (chord && (*p=='(')) type=NOTE;
        if (chord && (*p==')')) type=NOTE;     # this just for better error msg 
        if ((*p=='z')) type=REST;
        if ((*p=='Z')) type=BREST;
        if ((*p=='x')||(*p=='X')) {type=REST; invis=1; }
        if (!type) return 0;

        j=add_sym(type);                                         # add new symbol to list 


        symv[ivc][j].dc.n=prep_deco.n;             # copy over pre-parsed stuff 
        for (i=0;i<prep_deco.n;i++) 
                symv[ivc][j].dc.t[i]=prep_deco.t[i];
        prep_deco.clear();
        if (ngr) {
                symv[ivc][j].gr.n=ngr;
                symv[ivc][j].gr.len=lgr;
                for (i=0;i<ngr;i++) {
                        symv[ivc][j].gr.p[i]=pgr[i];
                        symv[ivc][j].gr.a[i]=agr[i];
                }
                ngr = 0;
        } else {
                symv[ivc][j].gr.n=0;
                symv[ivc][j].gr.len=0;
        }

        if (!prep_gchlst.empty()) {
                #gch_transpose (v[ivc].key);
                for (ii=prep_gchlst.begin(); ii!=prep_gchlst.end(); ii++) {
                        symv[ivc][j].gchords->push_back(*ii);
                }
                prep_gchlst.clear();
        }

        q0=p;
        if (type==REST) {
                p++;
                symv[ivc][j].lens[0] = parse_length();
                symv[ivc][j].npitch=1;
                symv[ivc][j].invis=invis;
                if (db>3) printf ("    parsed rest, length %d/%d = 1/%d\n", 
                                symv[ivc][j].lens[0],BASE,BASE/symv[ivc][j].lens[0]); 
        }
        elif (type==BREST) {
                p++;
                symv[ivc][j].lens[0] = (WHOLE*v[ivc].meter.meter1)/v[ivc].meter.meter2;
                symv[ivc][j].len = symv[ivc][j].lens[0];
                symv[ivc][j].fullmes = parse_brestnum();
                symv[ivc][j].npitch=1;
        }
        else {
                m=0;                                                                 # get pitch and length 
                sl1=sl2=0;
                for (;;) {
                        if (chord && (*p=='(')) {
                                sl1++;
                                symv[ivc][j].sl1[m]=sl1;
                                p++;
                        }
                        if (deco=parse_deco()) {         # for extra decorations within chord 
                                for (i=0;i<deco;i++) symv[ivc][j].dc.add(prep_deco.t[i]);
                                prep_deco.clear();
                        }

                        rc=parse_basic_note (&pitch,&length,&accidental);
                        if (rc==0) { v[ivc].nsym--; return 0; }
                        symv[ivc][j].pits[m] = pitch;
                        symv[ivc][j].lens[m] = length;
                        symv[ivc][j].accs[m] = accidental;
                        symv[ivc][j].ti1[m]    = symv[ivc][j].ti2[m] = 0;
                        for (j=0;j<ntinext;j++) 
                                if (tinext[j]==symv[ivc][j].pits[m]) symv[ivc][j].ti2[m]=1;

                        if (chord && (*p=='-')) {symv[ivc][j].ti1[m]=1; p++;}

                        if (chord && (*p==')')) {
                                sl2++;
                                symv[ivc][j].sl2[m]=sl2;
                                p++;
                        }

                        if (chord && (*p=='-')) {symv[ivc][j].ti1[m]=1; p++;}

                        m++;

                        if (!chord) break;
                        if ((*p=='+')||(*p==']')) {
                                p++;
                                break;
                        }
                        if (*p=='\0') {
                                if (chord) syntax ("Chord not closed", q); 
                                return type;
                        }
                }
                ntinext=0;
                for (j=0;j<m;j++)
                        if (symv[ivc][j].ti1[j]) {
                                tinext[ntinext]=symv[ivc][j].pits[j];
                                ntinext++;
                        }
                symv[ivc][j].npitch=m;
                if (m>0) {
                        symv[ivc][j].grcpit = symv[ivc][j].pits[0];
                }
        }

        for (m=0;m<symv[ivc][j].npitch;m++) {     # add carryover from > or < 
                if (symv[ivc][j].lens[m]+carryover<=0) {
                        syntax("> leads to zero or negative note length",q0);
                }
                else
                        symv[ivc][j].lens[m] += carryover;
        }
        carryover=0;

        if (db>3) printf ("    parsed note, decos %d, text <%s>\n",
                        symv[ivc][j].dc.n, symv[ivc][j].text);


        symv[ivc][j].yadd=0;
        if (v[ivc].key.ktype==BASS)                 symv[ivc][j].yadd=-6;
        if (v[ivc].key.ktype==ALTO)                 symv[ivc][j].yadd=-3;
        if (v[ivc].key.ktype==TENOR)                symv[ivc][j].yadd=+3;
        if (v[ivc].key.ktype==SOPRANO)            symv[ivc][j].yadd=+6;
        if (v[ivc].key.ktype==MEZZOSOPRANO) symv[ivc][j].yadd=-9;
        if (v[ivc].key.ktype==BARITONE)         symv[ivc][j].yadd=-12;
        if (v[ivc].key.ktype==VARBARITONE)    symv[ivc][j].yadd=-12;
        if (v[ivc].key.ktype==SUBBASS)            symv[ivc][j].yadd=0;
        if (v[ivc].key.ktype==FRENCHVIOLIN) symv[ivc][j].yadd=-6;

        if (type!=BREST)
                identify_note (&symv[ivc][j],q0); 
        return type;
}


# ----- parse_sym: parse a symbol and return its type -------- 
int parse_sym (void)
{
        int i;

        if (parse_gchord())     return GCHORD;
        if (parse_deco())         return DECO;
        if (parse_bar())            return BAR;
        if (parse_space())        return SPACE;
        line = parse_nl(line))             return NEWLINE;
        if ((i=parse_esc()))    return i;
        if ((i=parse_note())) return i;

        return 0;
}

# ----- add_wd ----- 
char *add_wd(char *str)
{
        char *rp;
        int l;

        l=strlen(str);
        if (l==0) return 0;
        if (nwpool+l+1>NWPOOL) 
                rx ("Overflow while parsing vocals; increase NWPOOL and recompile.","");

        strcpy(wpool+nwpool, str);
        rp=wpool+nwpool;
        nwpool=nwpool+l+1;
        return rp;
}

# ----- parse_vocals: parse words below a line of music ----- 
# Use '^' to mark a '-' between syllables - hope nobody needs '^' ! 
int parse_vocals (char *line)
{
        int isym;
        char *c,*c1,*w;
        char word[81];

        if ((line[0]!='w') || (line[1]!=':')) return 0;
        p0=line;

        # increase vocal line counter in first symbol of current line 
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

                # now word contains a word, possibly with trailing '^',
                     or one of the special characters * | _ -                             

                if (!strcmp(word,"|")) {                             # skip forward to next bar 
                        isym++;
                        while ((symv[ivc][isym].type!=BAR) && (isym<v[ivc].nsym)) isym++; 
                        if (isym>=v[ivc].nsym) 
                        { syntax("Not enough bar lines for |",c1); break; }
                } 

                else {                                                                 # store word in next note 
                        w=word;
                        while (*w!='\0') {                                     # replace * and ~ by space 
                                # cd: escaping with backslash possible 
                                # (does however not yet work for '*') 
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
# ----- parse_music_line: parse a music line into music -----
def parse_music_line(line, ivc):
    # int type,num,nbr,n,itype,i;
    # char msg[81];
    # char *p1,*pmx;


    if ivc >= len(voices):
        log.error("Trying to parse undefined v")
        exit(1)

    nwline = 0
    type = 0
    nsym0 = voices[ivc].nsym

    nbr = 0
    p = 0
    p0 = line;

    while p < len(line):   # {
        type = parse_sym()
        n = len(voices[ivc].sym)
        i = n-1;
        symv =voices[ivc].sym
        if type:
            log.info(f"     sym[{n-1}] code ({symv[ivc][n-1].type},"
                     f"{symv[ivc][n-1].u})")

        if type == constants.NEWLINE:
            if n > 0 and not cfmt.continueall and not cfmt.barsperstaff:
                symv[ivc][i].eoln = True
                if word:
                    symv[ivc][last_note].word_end = True
                    word = False

        if type == constants.ESCSEQ:
            log.info(f"Handle escape sequence <{escseq}>")
            itype = info_field(escseq)
            handle_inside_field(itype)

        if type == constants.REST:
            if pplet:       # n-plet can start on 
                # rest
                symv[ivc][i].p_plet = pplet
                symv[ivc][i].q_plet = qplet
                symv[ivc][i].r_plet = rplet
                pplet = 0
            last_note = i                                 # need this so > 
            # and < work
            p1 = p

        if type == constants.NOTE:
            if not word:
                symv[ivc][i].word_st = True
                word = True
            if nbr and cfmt.slurisligatura:
                symv[ivc][i].lig1 += nbr
            else:
                symv[ivc][i].slur_st += nbr
            nbr = 0
            if voices[ivc].end_slur:
                symv[ivc][i].slur_end += 1
            voices[ivc].end_slur = 0

            if pplet:                    # start of n-plet
                symv[ivc][i].p_plet = pplet
                symv[ivc][i].q_plet = qplet
                symv[ivc][i].r_plet = rplet
                pplet = 0
            last_note=last_real_note = i
            p1 = p

        if word and type == constants.BAR or type == constants.SPACE:
                if last_real_note >= 0: 
                    symv[ivc][last_real_note].word_end = 1
                word = 0

        if not type:
            if p.startswith('-'):                                  # a-b tie
                symv[ivc][last_note].slur_st += 1
                voices[ivc].end_slur = 1
                p += 1
            elif p.startswith('('):
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
            elif (*p == ')') {
                if (last_note>0)
                    if (cfmt.slurisligatura)
                            symv[ivc][last_note].lig2++;
                    else
                            symv[ivc][last_note].slur_end++;
                else:
                    syntax ("Unexpected symbol",p);
                p++;
            }
            elif (*p == '>') {
                num=1;
                p++;
                while (*p == '>') { num++; p++; }
                if (last_note<0)
                    syntax ("No note before > sign", p);
                else
                    double_note (last_note, num, 1, p1);
            }
            elif (*p == '<') {
                num=1;
                p++;
                while (*p == '<') { num++; p++; }
                if (last_note<0)
                    syntax ("No note before < sign", p);
                else:
                    double_note (last_note, num, -1, p1);
            }
            elif (*p == '*')         # ignore stars for now
                    p++;
            elif (*p == '!')         # ditto for '!'
                    p++;
            else {
                if (*p != '\0')
                    sprintf (msg, "Unexpected symbol \'%c\'", *p);
                else
                    sprintf (msg, "Unexpected end of line");
                syntax (msg, p);
                p++;
            }
        }
    }

    # maybe set end-of-line marker, if music were added
    n=voices[ivc].nsym;

    if (n>nsym0) {
        if (type==CONTINUE || cfmt.barsperstaff || cfmt.continueall) {
            symv[ivc][n-1].eoln=0;
        } else {
            # add invisible bar, if last symbol no bar
            if (symv[ivc][n-1].type != BAR) {
                i=add_sym(BAR);
                symv[ivc][i].u=B_INVIS;
                n=i+1;
            }
            symv[ivc][n-1].eoln=1;
        }
    }



    # break words at end of line
    if (word && (symv[ivc][n-1].eoln==1)) {
        symv[ivc][last_note].word_end=1;
        word=0;
    }

    return TO_BE_CONTINUED;

}


def is_selected (xref_str, pat, select_all, search_field):
    """
    check selection for current info fields

    :param xref_str:
    :param pat:
    :param select_all:
    :param search_field:
    :return:
    """

    i = j = a = b = m = 0

    # true if select_all or if no selectors given
    if select_all:
        return True
    if isblankstr(xref_str) and len(pat) ==0:
        return True

    m=0;
    for (i=0;i<npat;i++) {
    for i in pat:   #patterns 
        if search_field == S_COMPOSER:
                for j in info.ncomp:
                    if not m:
                        m = match(info.comp[j],pat[i]);
                }
        }
        elif (search_field==S_SOURCE)
                m=match(info.src,pat[i]);
        elif (search_field==S_RHYTHM)
                m=match(info.rhyth,pat[i]);
        else {
                m=match(info.title,pat[i]);
                if ((!m) && (numtitle>=2)) m=match(info.title2,pat[i]);
                if ((!m) && (numtitle>=3)) m=match(info.title3,pat[i]);
        }
        if (m) return 1;
    }

    # check xref against string of numbers
    p=xref_str;
    while (*p != 0) {
            parse_space();
            a=parse_uint();
            if (!a) return 0;                    # can happen if invalid chars in string
            parse_space();
            if (*p == '-') {
                    p++;
                    parse_space();
                    b=parse_uint();
                    if (!b) {
                            if (xrefnum>=a) return 1;
                    }
                    else
                            for (i=a;i<=b;i++) if (xrefnum==i) return 1;
            }
            else {
                    if (xrefnum==a) return 1;
            }
            if (*p == ',') p++;
    }

    return 0;

}


# ----- rehash_selectors: split selectors into patterns and xrefs -- 
def rehash_selectors(sel_str, xref_str, pat):
    """

    :param str sel_str:
    :param str xref_str:
    :param list pat:
    :return int:
    """
    # char *q;
    # char arg[501];
    # int i,npat;

    npat = 0
    xref_str = ""
    q = sel_str

    i=0;
    while (1) {
            if ((*q==' ') || (*q=='\0')) {
                    arg[i]='\0';
                    i=0;
                    if (!isblankstr(arg)) {
                            if (arg[0]=='-')                             # skip any flags
                                    ;
                            elif (is_xrefstr(arg)) {
                                    strcat(xref_str, arg);
                                    strcat(xref_str, " ");
                            }
                            else {                                                 # pattern with * or +
                                    if ((strchr(arg,'*')) || (strchr(arg,'+'))) {
                                            strcpy(pat[npat],arg);
                                    }
                                    else {                                             # simple pattern
                                            strcpy(pat[npat],"*");
                                            strcat(pat[npat],arg);
                                            strcat(pat[npat],"*");
                                    }
                                    npat++;
                            }
                    }
            }
            else {
                    arg[i]=*q;
                    i++;
            }
            if (*q=='\0') break;
            q++;
    }
    return npat;
    }


def decomment_line(ln):
    """
    cut off after %
    :param str ln:
    :return str:
    """
    c = list()
    in_quotes = False   # do not remove inside double quotes
    for p in ln:
        if p == '"':
            if in_quotes:
                in_quotes = False
            else:
                in_quotes = True
        if p == '%' and  not in_quotes:
            p = '\0'
        c.append(p)
    return ''.join(c)
"""

# ----- get_line: read line, do first operations on it ----- 
int get_line (FILE *fp, string *ln)
{
        *ln = "";
        if (feof(fp)) return 0;

        getline(ln, fp);
        linenum++;
        if (is_end_line(ln->c_str()))    return 0;

        if ((verbose>=7) || (vb>=10) ) printf ("%3d    %s \n", linenum, ln->c_str());

        return 1;
}


# ----- read_line: returns type of line scanned --- 
int read_line (FILE *fp, int do_music, string* linestr)
{
        int type,nsym0;
        static char* line = NULL;

        if (!get_line(fp,linestr)) return E_O_F;
        if (line) free(line);
        line = strdup(linestr->c_str());

        if ((linenum==1) && is_cmdline(line)) return CMDLINE;
        if (isblankstr(line))                                 return BLANK;
        if (is_pseudocomment(line))                     return PSCOMMENT;
        if (is_comment(line))                                 return COMMENT;

        decomment_line (line);

        if ((type=info_field(line))) {
                # skip after history field. Nightmarish syntax, that. 
                if (type != HISTORY) 
                        return type;
                else {                    
                        for (;;) {
                                if (! get_line(fp,linestr)) return E_O_F;
                                if (isblankstr(linestr->c_str())) return BLANK;
                                if (line) free(line);
                                line = strdup(linestr->c_str());
                                if (is_info_field(line)) break;
                                add_text (line, TEXT_H);
                        }
                        type=info_field (line);
                        return type;
                }
        }

        if (!do_music) return COMMENT;
        if (parse_vocals(line)) return MWORDS;

        # now parse a real line of music 
        if (nvoice==0) ivc=switch_voice (DEFVOICE);

        nsym0=voices[ivc].nsym;

        # music or tablature? 
        if (is_tab_line(line)) {
                type=parse_tab_line (line);
        } else {
                type=parse_music_line (line);
        }

        if (db>1)    
                printf ("    parsed music music %d to %d for v %d\n", 
                                nsym0,v[ivc].nsym-1,ivc);

        return type;
}

# ----- do_index: print index of abc file ------ 
void do_index(FILE *fp, char *xref_str, int npat, char (*pat)[STRLFILE], int select_all, int search_field)
{
        int type,within_tune;
        string linestr;
        static char* line = NULL;

        linenum=0;
        verbose=vb;
        numtitle=0;
        write_history=0;
        within_tune=within_block=do_this_tune=0;
        reset_info (&default_info);
        info=default_info;

    for (;;) {
        if (!get_line(fp,&linestr)) break;
        if (is_comment(linestr.c_str())) continue;
        if (line) free(line);
        line = strdup(linestr.c_str());
        decomment_line (line);
        type=info_field (line);

        switch (type) {
                
        case XREF:
            if (within_block) 
                printf ("+++ Tune %d not closed properly \n", xrefnum);
            numtitle=0;
            within_tune=0;
            within_block=1;
            ntext=0;
            break;
            
        case KEY:
            if (!within_block) break;
            if (!within_tune) {
                tnum2++;
                if (is_selected (xref_str,npat,pat,select_all,search_field)) {
                    printf ("    %-4d %-5s %-4s", xrefnum, info.key, info.meter);
                    if            (search_field==S_SOURCE)     printf ("    %-15s", info.src);
                    elif (search_field==S_RHYTHM)     printf ("    %-8s",    info.rhyth);
                    elif (search_field==S_COMPOSER) printf ("    %-15s", info.comp[0]);
                    if (numtitle==3) 
                        printf ("    %s - %s - %s", info.title,info.title2,info.title3);
                    if (numtitle==2) printf ("    %s - %s", info.title, info.title2);
                    if (numtitle==1) printf ("    %s", info.title);
                    
                    printf ("\n");
                    tnum1++;
                }
                within_tune=1;
            }    
            break;

        }
        
        if (isblankstr(line)) {
            if (within_block && !within_tune) 
                printf ("+++ Header not closed in tune %d\n", xrefnum);
            within_tune=0;
            within_block=0;
            info=default_info;
        }
    }
    if (within_block && !within_tune) 
        printf ("+++ Header not closed in for tune %d\n", xrefnum);

}
"""
