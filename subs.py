import sys
import os

import pssubs
import common
import util as util
from util import bskip, put
import log
import cmdline
import format
import info
import constants

args = cmdline.options()
log = log.log()
cfmt = format.Format()
info = info.Field()

maxSyms = 800
allocSyms = 800
maxVc = 3
allocVc = 3
   

def write_help():
    pass

def is_xrefstr(xrefstr):
    """
    check if string ok for xref selection

    :param xrefstr:
    :return bool:
    """
    return xrefstr.isdigit() and int(xrefstr) != 0

def ops_into_fmt(fmt):
    """

    :param Format fmt:
    """
    fmt.staffsep = fmt.staffsep + args.dstaffsep
    fmt.sysstaffsep = fmt.sysstaffsep + args.dstaffsep

def process_cmdline(line):
    """
    parse '%!'-line from input file

    :param line:
    :return Namespace: argparse
    """
    if line.startswith('%!'):
        line = line[2:].strip()
    else:
        line = line.strip()
    params = line.split()
    sys.argv.extend(params)
    return cmdline.options()


def tex_str(line):   # tex_str(const char *str, string *s, float *wid)
    """
    change string to take care of some tex-style codes

    Puts \ in front of ( and ) in case brackets are not balanced,
    interprets some TeX-type strings using ISOLatin1 encodings.
    Returns the length of the string as finally given out on paper.
    Also returns an estimate of the string width...

    :param line:
    :return tuple: s, w
    """
    s = list()
    n = 0
    w = 0
    c = 0
    while c < len(line):
        if line[c] == '(' or line[c] == ')':   #( ) becomes \( \)
            t = "\\" + line[c]
            s.append(t)
            w += util.cwid('(')
            n += 1

        elif line[c] == '\\':   # backslash
            # sequences
            c += 1
            if line[c] == '\0': break
            add = 0
            # accented vowels
            if line[c] == '`':
                add=1
            if line[c] == '\'':
                add=2
            if line[c] == '^':
                add=3
            if line[c] == '"':
                add=4
            if add:
                c += 1
                base = 0
                if line[c] == 'a':
                    base=340
                    if add == 4:
                        add=5
                if line[c] == 'e':
                    base=350
                if line[c] == 'i':
                    base=354
                if line[c] == 'o':
                    base=362
                    if add == 4:
                        add=5
                if line[c] == 'u':
                    base=371
                if line[c] == 'A':
                    base=300
                    if add == 4:
                        add=5
                if line[c] == 'E':
                    base=310
                if line[c] == 'I':
                    base=314
                if line[c] == 'O':
                    base=322
                    if add == 4:
                        add=5
                if line[c] == 'U':
                    base=331
                w += util.cwid(line[c])
                if base:
                    t = "\\%d" % (base+add-1)
                    s.append(t)
                    n += 1
                else:
                    t = "%c" % line[c]
                    s.append(t)
                    n += 1

            elif line[c] == '#':
                # sharp sign
                s.append("\201")
                w += util.cwid('\201')
                n += 1
            elif line[c] == 'b':
                # flat sign
                s.append("\202")
                w += util.cwid('\202')
                n += 1
            elif line[c] == '=':
                # natural sign
                s.append("\203")
                w += util.cwid('\203')
                n += 1
            elif line[c] == ' ':
                # \-space
                s.append(" ")
                w += util.cwid(' ')
                n += 1

            elif line[c] == 'O': # O-slash
                s.append("\\330")
                w += util.cwid('O')
                n += 1

            elif line[c] == 'o':  # o-slash
                s.append("\\370")
                w += util.cwid('O')
                n += 1

            elif line[c] == 's' and line[c+1] =='s':      # sz
                c += 1
                s.append("\\337")
                w += util.cwid('s')
                n += 1
            elif line[c] == 'a' and line[c+1] == 'a':     # a-ring
                c += 1
                s.append("\\345")
                w += util.cwid('a')
                n += 1
            elif line[c] == 'A' and line[c+1] == 'A':     # A-ring
                c += 1
                s.append("\\305")
                w += util.cwid('A')
                n += 1
            elif line[c] == 'a' and line[c+1] == 'e':      # ae
                c += 1
                s.append("\\346")
                w += 1.5 * util.cwid('a')
                n += 1
            elif line[c] == 'A' and line[c+1] =='E':      # AE
                c += 1
                s.append("\\306")
                w += 1.5 * util.cwid('A')
                n += 1
            elif line[c] == 'c':          # c-cedilla
                c += 1
                w += util.cwid(line[c])
                if line[c] == 'C':
                    s.append("\\307")
                n += 1
            elif line[c] == 'c':
                s.append("\\347")
                n += 1
            else:
                t = "%c" % line[c]
                s.append(t)
                n += 1

        elif line[c] == '~':
            # n-twiddle
            if line[c+1]:
                c += 1
                w += util.cwid(line[c])
                if line[c] == 'N':
                    s.append("\\321")
                    n += 1
                elif line[c] == 'n':
                    s.append("\\361")
                    n += 1
                else:
                    t = "~%c" % line[c]
                    s.append(t)
                    n += 1
            else:
                w += util.cwid('~')
                s.append("~")
                n += 1
        else:    #
            # \-something-else
            # pass through
            t = "\\%c" % line[c]
            s.append(t)
            w += util.cwid('A')
            n += 1
        if line[c] == '{':
            pass

        elif line[c] == '}':
            pass
        else:      # other
            # characters: pass though
            t = "%c" % line[c]
            s.append(t)
            n += 1
            w += util.cwid(line[c])
        c += 1
    return s, w


def put_str(line):
    """
    output a string in postscript

    :param line:
    """
    s = line.strip()
    print(f"{s}")



class Pos:
    def __init__(self):
        self.posx = 0.0
        self.posy = 0.0

    def check_margin(self, new_posx):
        """
        do horizontal shift if needed

        :param new_posx:
        """
        dif = new_posx-self.posx
        if dif*dif < 0.001:
            return
        with open(common.filename, 'a') as f:
            f.write(f"{dif:.2f} 0 T\n")
        self.posx = new_posx


def epsf_title(title):
    """

    :param title:
    :return:
    """
    title.replace(' ', '_')
    return title


def close_output_file(fp):
    """
    This should not have to exist with python.  Using context switches the
    output will always be closed, even with errors.

    RC: 0 = output file is kept
        1 = output file is removed(because it is empty)
    """
    if fp.closed:
        return True

    filename = fp.name
    pssubs.close_page(fp)
    pssubs.close_ps(fp)
    fp.close()

    common.file_open = False
    common.file_initialized = False

    if common.tunenum == 0:
        log.warning(f"No tunes written to output file. Removing {filename}")
        os.remove(filename)
        return True
    else:
        m = utils.util.get_file_size(common.output)
        print(f'Output written to {common.output} (pages: {common.pagenum}, '
              f'titles: {common.tunenum}, bytes: {m}')
        return False


def open_output_file(out_filename, in_filename):
    """
    Help.  Don't think this is correct.

    :param out_filename:
    :param in_filename:
    :return:
    """
    if not os.path.exists(out_filename):
        pass

    if out_filename == common.output:
        return

    if in_filename == out_filename:
        return

    try:
        open(out_filename, 'r+')
    except IOError as ioe:
        print(f'{out_filename} is already open')
        close_output_file(in_filename)

    status = os.access(out_filename, os.W_OK)
    if status:
       log.error(f'Cannot open output file {out_filename}')
    common.pagenum = 0
    common.tunenum = tnum1 = tnum2 = 0
    file_open = True
    file_initialized = False

# These are in ps/index.py
# def open_index_file(filename):
# def close_index_file(findex):

class Words:
    def __init__(self):
        self.words_of_text = list()


    def add_to_text_block(self, ln, add_final_nl):
        """
        Used in:
            subs.put_text

        :param str ln:
        :param bool add_final_nl:
        :return ln, words_of_text:
        """
        # const char *c
        word = list()
        # int nl
        self.words_of_text = list()
        c = 0
        nl = 0

        while c < len(ln):
            while ln[c] == ' ':
                c += 1
            if c >= len(ln):
                break
            while ln[c] != ' ' and c >= len(ln) and ln[c] != '\n':
                nl=0
                if ln[c] == '\\' and ln[c+1] == '\\':
                    nl=1
                    c += 2
                    break
                word.append(ln[c])
                c += 1
            if word:
                self.words_of_text.append(word)
                word = list()
            if nl:
                self.words_of_text.append("$$NL$$")
                word = list()
        if add_final_nl:
            self.words_of_text.append("$$NL$$")


    def write_text_block(self, fp, job):
        """

        :param fp:
        :param job:
        """
        # size_t ntxt
        # int i,i1,i2,ntline,nc,mc,nbreak
        # float textwidth,ftline,ftline0,swfac,baseskip,parskip
        # float wwidth,wtot,spw
        # string str

        if not self.words_of_text:
            return

        baseskip = cfmt.textfont.size * cfmt.lineskipfac
        parskip = cfmt.textfont.size * cfmt.parskipfac
        cfmt.textfont.set_font_str(common.page_init)

        # estimate text widths.. ok for T-R, wild guess for other fonts
        swfac = 1.0
        if cfmt.textfont.name == "Times-Roman":
            swfac = 1.00
        if cfmt.textfont.name == "Times-Bold":
            swfac=1.05
        if cfmt.textfont.name == "Helvetica":
            swfac=1.10
        if cfmt.textfont.name == "Helvetica-Bold":
            swfac=1.15
        if cfmt.textfont.name == "Palatino":
            swfac=1.10

        # Now this is stupid. All that work to just set it to 1.0
        swfac = 1.0
        spw = utils.util.cwid(' ')
        put("/LF \{0 "
            f"{-baseskip:.1f}"
            " rmoveto} bind def\n")

        # output by pieces, separate at newline token
        ntxt = len(self.words_of_text)
        i1 = 0
        while i1 < ntxt:
            i2 = -1
            for i in range(i1, ntxt):
                if self.words_of_text[i] == '$$NL$$':
                    i2 = i
                    break
            if i2 == -1:
                i2 = ntxt
            bskip(baseskip)

            if job == constants.OBEYLINES:
                put("0 0 M(")
                for i in range(i1, i2):
                    line, wwidth = tex_str(self.words_of_text[i])
                    put(f"{line} ")
                put(") rshow\n")

            elif job == constants.OBEYCENTER:
                put(f"{cfmt.staffwidth/2:.1f} 0 M(")
                for i in range(i1, i2):
                    line, wwidth = tex_str(self.words_of_text[i])
                    put(f"{line}")
                    if i<i2-1:
                        put(" ")
                put(") cshow\n")

            elif job == constants.OBEYRIGHT:
                put(f"{cfmt.staffwidth:.1f} 0 M(")
                for i in range(i1, i2):
                    line, wwidth = tex_str(self.words_of_text[i])
                    put(f"{line}")
                    if i<i2-1:
                        put(" ")
                put(") lshow\n")

            else:
                put("0 0 M mark\n")
                nc = 0
                mc = -1
                wtot = -spw
                for(i=i2-1;i>=i1;i--) {
                for i in range(i2, i1, -1):
                    line, wwidth = tex_str(self.words_of_text[i])
                    mc += ?? + 1
                    wtot += wwidth+spw
                    nc += len(line)+2
                    if nc >= 72:
                        nc = 0
                        put("\n"); }
                    put(f"({line})")
                if(job==RAGGED)
                    PUT1(" %.1f P1\n",cfmt.staffwidth)
                else
                    PUT1(" %.1f P2\n",cfmt.staffwidth)
                        # first estimate:(total textwidth)/(available width)
                        textwidth=wtot*swfac*cfmt.textfont.size
                if(strstr(cfmt.textfont.name,"Courier"))
                    textwidth=0.60*mc*cfmt.textfont.size
                ftline0=textwidth/cfmt.staffwidth
                # revised estimate: assume some chars lost at each line end
                nbreak=(int)ftline0
                textwidth= textwidth + 5 * nbreak * util.cwid('a') * swfac * cfmt.textfont.size
                ftline=textwidth/cfmt.staffwidth
                ntline=(int)(ftline+1.0)
                if(vb>=10)
                    printf("first estimate %.2f, revised %.2f\n", ftline0,ftline)
                if(vb>=10)
                    printf("Output %d word%s, about %.2f lines(fac %.2f)\n",
                                 i2-i1, i2-i1==1?"":"s", ftline,swfac)
                bskip((ntline-1)*baseskip)
            }

            buffer_eob(fp);
            # next line to allow pagebreak after each text "line"
            # if(!epsf && !within_tune) write_buffer(fp);
            i1=i2+1
        }
        bskip(parskip)
        buffer_eob(fp);
        # next line to allow pagebreak after each paragraph
        if(!epsf && !within_tune) write_buffer(fp)
        strcpy(page_init,"")
        return
    }



    # ----- put_words -------
    void put_words(self, fp)
    {
        int i,nw,n
        char str[81]
        char *p,*q

        set_font(fp,cfmt.wordsfont, 0)
        cfmt.wordsfont.set_font_str(page_init)

        n=0
        for(i=0;i<ntext;i++) if(text_type[i]==TEXT_W) n++
        if(n==0) return

        bskip(cfmt.wordsspace)
        for(i=0;i<ntext;i++) {
            if(text_type[i]==TEXT_W) {
                bskip(cfmt.lineskipfac*cfmt.wordsfont.size)
                p=&text[i][0]
                q=&str[0]
                if(isdigit(text[i][0])) {
                    while(*p != '\0') {
                        *q=*p
                        q++
                        p++
                        if(*p==' ') break
                        if(*(p-1)==':') break
                        if(*(p-1)=='.') break
                    }
                    if(*p==' ') p++
                }
                *q='\0'

                # permit page break at empty lines or stanza start
                nw=nwords(text[i])
                if((nw==0) ||(strlen(str)>0)) buffer_eob(fp)

                if(nw>0) {
                    if(strlen(str)>0) {
                        PUT0("45 0 M(")
                        put_str(str)
                        PUT0(") lshow\n")
                    }
                    if(strlen(p)>0) {
                        PUT0("50 0 M(")
                        put_str(p)
                        PUT0(") rshow\n")
                    }
                }
            }
        }

        buffer_eob(fp)
        strcpy(page_init,"")

    }

    # ----- put_text -------
    void put_text(self, fp, int type, char *str)
    {
        int i,n
        float baseskip,parskip

        n=0
        for(i=0;i<ntext;i++) if(text_type[i]==type) n++
        if(n==0) return

        baseskip = cfmt.textfont.size * cfmt.lineskipfac
        parskip = cfmt.textfont.size * cfmt.parskipfac
        PUT0("0 0 M\n")
        self.words_of_text.clear()
        add_to_text_block(str,0)
        for(i=0;i<ntext;i++) {
            if(text_type[i]==type) add_to_text_block(text[i],1)
        }
        write_text_block(fp,RAGGED)
        buffer_eob(fp);

    }

# ----- put_history ------- 
void put_history(FILE *fp)
{
    int i,ok
    float baseskip,parskip

    set_font(fp, cfmt.textfont,0)
    cfmt.textfont.set_font_str(page_init)
    baseskip = cfmt.textfont.size * cfmt.lineskipfac
    parskip = cfmt.textfont.size * cfmt.parskipfac

    bskip(cfmt.textspace)

    if(strlen(info.rhyth)>0) {
        bskip(baseskip); 
        PUT0("0 0 M(Rhythm: ")
        put_str(info.rhyth)
        PUT0(") show\n")
        bskip(parskip)
    }
    
    if(strlen(info.book)>0) {
        bskip(0.5*CM); 
        PUT0("0 0 M(Book: ")
        put_str(info.book)
        PUT0(") show\n")
        bskip(parskip)
    }

    if(strlen(info.src)>0) {
        bskip(0.5*CM); 
        PUT0("0 0 M(Source: ")
        put_str(info.src)
        PUT0(") show\n")
        bskip(parskip)
    }

    put_text(fp, TEXT_D, "Discography: ")
    put_text(fp, TEXT_N, "Notes: ")
    put_text(fp, TEXT_Z, "Transcription: ")
    
    ok=0
    for(i=0;i<ntext;i++) {
        if(text_type[i]==TEXT_H) {
            bskip(0.5*CM); 
            PUT0("0 0 M(")
            put_str(text[i])
            PUT0(") show\n")
            ok=1
        }
    }
    if(ok) bskip(parskip)
    buffer_eob(fp)
    strcpy(page_init,"")

}


# ----- write_inside_title    ----- 
void write_inside_title(FILE *fp)
{
    char t[201]

    if          (numtitle==1) strcpy(t,info.title)
    elifnumtitle==2) strcpy(t,info.title2)
    elifnumtitle==3) strcpy(t,info.title3)
    if(vb>15) print("write inside title <%s>\n", t)
    if(strlen(t)==0) return

    bskip(cfmt.subtitlefont.size+0.2*CM)
    set_font(fp, cfmt.subtitlefont, 0)

    if(cfmt.titlecaps) cap_str(t)
    PUT0("(")
    put_str(t)
    if(cfmt.titleleft) PUT0(") 0 0 M rshow\n")
    else PUT1(") %.1f 0 M cshow\n", cfmt.staffwidth/2)
    bskip(cfmt.musicspace+0.2*CM)

}    


# ----- write_tunetop ----- 
def write_tunetop(fp):
    put(f"\n\n%% --- tune {tunenum+1} {info.title}\n")
    if not common.epsf:
        bskip(cfmt.topspace)

# ----- tempo_is_metronomemark ----- 
#
 * checks whether a tempostring is a metronome mark("1/4=100")
 * or a verbose text(eg. "Andante"). In abc, verbose tempo texts
 * must start with double quotes
 
int tempo_is_metronomemark(char* tempostr)
{
    char* p
    for(p=tempostr; *p; p++) {
        if(isspace(*p)) continue
        if(*p == '"')
            return 0
        else
            break
    }
    if(*p)
        return 1; # only when actually text found 
    else
        return 0
}

# ----- write_tempo ----- 
void write_tempo(FILE *fp, char *tempo, struct METERSTR meter)
{
    char *r, *q
    char text[STRLINFO]
    int top,bot,value,len,i,err,fac,dig,div
    struct SYMBOL s
    float stem,dotx,doty,sc,dx

    if(vb>15) print("write tempo <%s>\n", info.tempo)
    r=tempo
    set_font(fp,cfmt.tempofont,0)
    PUT0(" 18 0 M\n")

    for(;;) {
        while(*r==' ') r++;                                        # skip blanks 
        if(*r=='\0') break

        if(*r=='"') {                                                    # write string 
            r++
            q=text
            while(*r!='"' && *r!='\0') { *q=*r; r++; q++; }
            if(*r=='"') r++
            *q='\0'
            if(strlen(text)>0) {         
                PUT0("6 0 rmoveto(")
                put_str(text)
                PUT0(") rshow 12 0 \n")
            }
        }
        else {                                                                    # write tempo denotation 
            q=text
            while(*r!=' ' && *r!='\0') { *q=*r; r++; q++; }
            *q='\0'
            
            q=text
            len=QUARTER
            value=0
            err=0
            if(strchr(q,'=')) {
                if(*q=='C' || *q=='c') {
                    q++
                    len=meter.dlen;    
                    div=0
                    if(*q=='/') { div=1; q++; }
                    fac=0
                    while(isdigit(*q)) { dig=*q-'0'; fac=10*fac+dig; q++; }

                    if(div) {
                        if(fac==0) fac=2
                        if(len%fac) print("Bad length divisor in tempo: %s", text)
                        len=len/fac
                    }
                    else    
                        if(fac>0) len=len*fac
                    if(*q!='=') err=1
                    q++
                    if(!isdigit(*q)) err=1
                    sscanf(q,"%d", &value)
                }
                elifisdigit(*q)) {
                    sscanf(q,"%d/%d=%d", &top,&bot,&value)
                    len=(BASE*top)/bot
                }
                else err=1
            } 
            else {
                if(isdigit(*q))
                    sscanf(q,"%d", &value)
                else err=1
            }
            
            if(err)                                                            # draw note=value 
                printf("\n+++ invalid tempo specifier: %s\n", text)
            else {
                s.len=len
                identify_note(&s,r)
                sc=0.55*cfmt.tempofont.size/10.0
                PUT2("gsave %.2f %.2f scale 15 3 rmoveto currentpoint\n", sc,sc)
                if(s.head==H_OVAL)    PUT0("HD")
                if(s.head==H_EMPTY) PUT0("Hd")
                if(s.head==H_FULL)    PUT0("hd")
                dx=4.0
                if(s.dots) {            
                    dotx=8; doty=0
                    if(s.flags>0) dotx=dotx+4
                    if(s.head==H_EMPTY) dotx=dotx+1
                    if(s.head==H_OVAL)    dotx=dotx+2
                    for(i=0;i<s.dots;i++) {
                        PUT2(" %.1f %.1f dt", dotx, doty)
                        dx=dotx
                        dotx=dotx+3.5
                    }
                }
                stem=16.0
                if(s.flags>1) stem=stem+3*(s.flags-1)
                if(s.len<WHOLE) PUT1(" %.1f su",stem)
                if(s.flags>0) PUT2(" %.1f f%du",stem,s.flags)
                if((s.flags>0) &&(dx<6.0)) dx=6.0
                dx=(dx+18)*sc
                PUT2(" grestore %.2f 0 rmoveto( = %d) rshow\n", dx,value)
            }
        }
    }
}


# ----- write_inside_tempo    ----- 
void write_inside_tempo(FILE *fp)
{
    # print metronome marks only when wished 
    if(tempo_is_metronomemark(info.tempo) && !cfmt.printmetronome)
        return; 

    bskip(cfmt.partsfont.size)
    write_tempo(fp,info.tempo,voice[ivc].meter)
    bskip(0.1*CM)
}

# ----- write_heading    ----- 
def write_heading(fp):

    # float lwidth,down1,down2
    # int i,ncl
    # char t[STRLINFO]

    lwidth = cfmt.staffwidth

    # write the main title 
    util.bskip(cfmt.titlefont.size + cfmt.titlespace)
    set_font(fp,cfmt.titlefont,1)
    if cfmt.withxrefs:
        put(f"{xrefnum}. ")
    t = info.titles[0]
    if(cfmt.titlecaps) cap_str(t)
    put_str(t)
    if cfmt.titleleft:
        put(") 0 0 M rshow")
    else:
        put(f") {lwidth/2:.1f} 0 M cshow\n", )

    # write second title 
    if len(info.titles) >=2:
        util.bskip(cfmt.subtitlespace + cfmt.subtitlefont.size)
        set_font(fp,cfmt.subtitlefont,1)
        strcpy(t,info.title2)
        if(cfmt.titlecaps) cap_str(t)
        put_str(t)
        if(cfmt.titleleft) PUT0(") 0 0 M rshow\n")
        else PUT1(") %.1f 0 M cshow\n", lwidth/2)
    }

    # write third title 
    if(numtitle>=3) {
        bskip(cfmt.subtitlespace+cfmt.subtitlefont.size)
        set_font(fp,cfmt.subtitlefont,1)
        strcpy(t,info.title3)
        if(cfmt.titlecaps) cap_str(t)
        put_str(t)
        if(cfmt.titleleft) PUT0(") 0 0 M rshow\n")
        else PUT1(") %.1f 0 M cshow\n", lwidth/2)
    }

    # write composer, origin 
    if((info.ncomp>0) ||(strlen(info.orig)>0)) {
        set_font(fp,cfmt.composerfont,0)
        bskip(cfmt.composerspace)
        ncl=info.ncomp
        if((strlen(info.orig)>0) &&(ncl<1)) ncl=1
        for(i=0;i<ncl;i++) {
            bskip(cfmt.composerfont.size)
            PUT1("%.1f 0 M(", lwidth)
            put_str(info.comp[i])
            if((i==ncl-1)&&(strlen(info.orig)>0)) {
                put_str("(")
                put_str(info.orig)
                put_str(")")
            }
            PUT0(") lshow\n")
        }
        down1=cfmt.composerspace+cfmt.musicspace+ncl*cfmt.composerfont.size
    }
    else {
        bskip(cfmt.composerfont.size+cfmt.composerspace)
        down1=cfmt.composerspace+cfmt.musicspace+cfmt.composerfont.size
    }
    bskip(cfmt.musicspace)

    # decide whether we need extra shift for parts and tempo 
    down2=cfmt.composerspace+cfmt.musicspace
    if(strlen(info.parts)>0) down2=down2+cfmt.partsspace+cfmt.partsfont.size
    if(strlen(info.tempo)>0) down2=down2+cfmt.partsspace+cfmt.partsfont.size
    if(down2>down1) bskip(down2-down1)

    # write tempo and parts 
    if(strlen(info.parts)>0 || strlen(info.tempo)>0) {
        int printtempo =(strlen(info.tempo)>0)
        if(printtempo && 
                tempo_is_metronomemark(info.tempo) && !cfmt.printmetronome)
            printtempo = 0

        if(printtempo) {
            bskip(-0.2*CM)
            PUT1(" %.2f 0 T ", cfmt.indent*cfmt.scale)
            write_tempo(fp, info.tempo, default_meter)
            PUT1(" %.2f 0 T ", -cfmt.indent*cfmt.scale)
            bskip(-cfmt.tempofont.size)
        }
        
        if(strlen(info.parts)>0) {
            bskip(-cfmt.partsspace)
            set_font(fp,cfmt.partsfont,0)
            PUT0("0 0 M(")
            put_str(info.parts)
            PUT0(") rshow\n")
            bskip(cfmt.partsspace)
        }

        if(printtempo) bskip(cfmt.tempofont.size+0.3*CM)
        
    }
    

}

# ----- write_parts    ----- 
def write_parts(fp):
    """
    
    :param fp: file
    """
    if len(info.parts) > 0:
        util.bskip(cfmt.partsfont.size)
        set_font(fp, cfmt.partsfont,0)
        fp.write("0 0 M(")
        put_str(info.parts)
        fp.write(") rshow\n")
        bskip(cfmt.partsspace)


