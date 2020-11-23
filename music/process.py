# Copyright 2019 Curtis Penner

import sys

import utils.cmdline
import fields.vcestr
import fields.info
from utils.common import within_block
from format import Format

cfmt = Format()


class Process:
    def __init__(self, log_obj):
        self.log = log_obj.log

    def cmdline(self, line):
        args_line = line[2:].strip()
        sys.argv.append(args_line)
        utils.cmdline.options()

    def process_pscomment(self, fpin, fp, line):
        """

        :param fpin:
        :param fp:
        :param line:
        :return:
        """
        # char w[81], fstr[81], unum1[41], unum2[41], unum3[41];
        # float h1, h2, len, lwidth;
        #
        # int i, nch, job;

        lwidth = cfmt.staffwidth
        line[0] = ' '
        line[1] = ' '
        for (i=0;i < strlen(line);i++) { if (line[i] == '%') line[i]='\0';}
        strcpy(w, " ");
        sscanf(line, "%s%n", w, & nch);

        if (!strcmp(w, "begintext")) {
            if (epsf & & !within_block)
                return;
            strcpy(fstr, "");
            sscanf(line, "%*s %s", fstr);
            if (isblankstr(fstr)) 
                strcpy(fstr, "obeylines");
            if (!strcmp(fstr, "obeylines")) 
                job=OBEYLINES;
            else if (!strcmp(fstr, "align"))         
                job=ALIGN;
            else if (!strcmp(fstr, "skip"))            
                job=SKIP;
            else if (!strcmp(fstr, "ragged"))        
                job=RAGGED;
            else {
                job = SKIP;
                rx("bad argument for begintext: ", fstr);
            }
            if (within_block & & !do_this_tune) 
                job=SKIP;
            process_textblock(fpin, fp, job);
            return;
        }

if (!strcmp(w, "text") | | !strcmp(w, "center") | | !strcmp(w, "right")) {
if (epsf & & !within_block) return;
if (within_block & & !do_this_tune) return;
output_music(fp);
set_font(fp, cfmt.textfont, 0);
words_of_text.clear();
if (*(line + nch))
    add_to_text_block(line + nch + 1, 1);
else
    add_to_text_block("", 1);
if (!strcmp(w, "text"))
write_text_block(fp, OBEYLINES);
else if (!strcmp(w, "right"))
write_text_block(fp, OBEYRIGHT);
else
write_text_block(fp, OBEYCENTER);
buffer_eob(fp);
}

else if (!strcmp(w, "sep")) {
if (within_block & & !do_this_tune) return;
output_music(fp);
strcpy(unum1, "");
strcpy(unum2, "");
strcpy(unum3, "");
sscanf(line, "%*s %s %s %s", unum1, unum2, unum3);
g_unum(unum1, unum1, & h1);
g_unum(unum2, unum1, & h2);
g_unum(unum3, unum1, & len);
if (h1 * h1 < 0.00001) h1=0.5 * CM;
if (h2 * h2 < 0.00001) h2=h1;
if (len * len < 0.0001) len=3.0 * CM;
bskip(h1);
PUT2("%.1f %.1f sep0\n", lwidth / 2 - len / 2, lwidth / 2 + len / 2);
bskip(h2);
buffer_eob(fp);
}

else if (!strcmp(w, "vskip")) {
if (within_block & & !do_this_tune) return;
output_music(fp);
strcpy(unum1, "");
sscanf(line, "%*s %s", unum1);
g_unum(unum1, unum1, & h1);
if (h1 * h1 < 0.00001) h1=0.5 * CM;
bskip(h1);
buffer_eob(fp);
}

else if (!strcmp(w, "newpage")) {
if (within_block & & !do_this_tune) return;
output_music(fp);
write_buffer(fp);
use_buffer = 0;
write_pagebreak(fp);
}

else {
if (within_block) {
interpret_format_line (line, & cfmt);
}
else {
interpret_format_line (line, & dfmt);
cfmt=dfmt;
}
}

}

    def line(self, fpout, line, xref_str,
             pat, sel_all, search_field):
        if within_block:
            self.log.info(f"process_line, type {line} ")
        else:
            return

        raise NotImplementedError

    def index(self, fpin, xref_str, pat, sellect_all, search_field):
        with open(fpin) as fp:
            lines = fp.readlines()

        if lines[0].startswith('%!'):
            self.cmdline(lines[0].rstrip())
            del lines[0]

        for line in lines:
            if not fields.info.is_field(line):
                continue



    def file(self, fpin, fpout, xref_str, pat, sel_all, search_field):
        """


        :param fpin: filename input
        :param fpout: filename output
        :param str xref_str: xref string to filter
        :param list pat: patterns to filter
        :param bool sel_all: filter
        :param bool search_field: filter
        """
        do_music = False
        voices = list()
        with open(fpin) as fp:
            lines = fp.readlines()

        if lines[0].startswith('%!'):
            self.cmdline(lines[0].rstrip())
            del lines[0]

        for line in lines:
            line = line.strip()
            if not line:
                do_music = False
                continue
            if line.startswith('%'):
                if line.startswith('%%'):
                    self.pscomment(fpin, fpout, line)
                    continue
                continue

            line = self.decomment(line)   # todo
            if not do_music:
                self.line(fpout, line, xref_str,
                          pat, sel_all, search_field)
                continue
            if not voices:
                voice = fields.vcestr.Voice()  # todo
                voice('1')

            if is_tab_line(line):
                parse_tab_line(line)
            else:
                parse_music_line(line)

        if not epsf:
            buffer_eob(fpout)
            write_buffer(fpout)


# ----- process_textblock -----
void process_textblock(FILE *fpin, FILE *fp, int job)
{
    char* w1;
    string ln;
    float lwidth,baseskip,parskip;
    int i,ll,add_final_nl;

    baseskip = cfmt.textfont.size * cfmt.lineskipfac;
    parskip    = cfmt.textfont.size * cfmt.parskipfac;
    add_final_nl=0;
    if (job==OBEYLINES) add_final_nl=1;
    lwidth=cfmt.staffwidth;
    output_music (fp);
    buffer_eob (fp);
    set_font (fp, cfmt.textfont, 0);
    words_of_text.clear();
    for (i=0;i<100;i++) {
        if (feof(fpin)) rx("EOF reached scanning text block","");
        getline(&ln, fpin);
        ll=ln.length();
        linenum++;
        if ((verbose>=5) || (vb>=10) ) printf ("%3d    %s \n", linenum, ln.c_str());
        if ((ln[0]=='%') && (ln[1]=='%')) {
            ln.erase(0,2);
        }

        w1 = (char*) malloc(sizeof(char)*(ln.length()+4));
        w1[0] = '\0';
        sscanf(ln.c_str(),"%s",w1);
        if (!strcmp(w1,"endtext")) break;
        free(w1);

        if (job!=SKIP) {
            if (isblankstr(ln.c_str())) {
                write_text_block (fp,job);
                words_of_text.clear();
            }
            else {
                add_to_text_block ((char*)ln.c_str(),add_final_nl);
            }
        }
    }
    if (job!=SKIP) write_text_block (fp,job);
}

