# Copyright 2019 Curtis Penner

"""
abctab2ps: a program to typeset tunes in abc format using PostScript
 Copyright (C) 1996 - 1998    Michael Methfessel
 Copyright (C) 1999 - 2004    Christoph Dalitz
 
 This program is free software. You can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 2 of the License, or
 (at your option) any later version.
 
 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY, without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.    See the
 GNU General Public License for more details.
 
 You should have received a copy of the GNU General Public License
 along with this program, if not, write to the Free Software
 Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
 
 The author can be contacted as follows:
 
 Christoph Dalitz
 <christoph (dot) dalitz (at) hs-niederrhein (dot) de>
"""

import signal
import os

import common

import subs
from log import log, console
import cmdline
import util
import format
import index
import info
import music

args = cmdline.options()
cfmt = format.Format()
index = index.Index()
X = info.XRef


def signal_handler():
    """ signal handler for premature termination """
    subs.close_output_file(args.outfile)
    log.critical('could not install signal handler for SIGTERM and SIGINT')
    exit(130)


def process(s):
    """
    Strip the leading, following spaces

    :param s:
    :return:
    """
    s = s.strip()
    if not info.do_this_tune and s.startswith('X:'):
        info.parse_info(s)
    elif info.is_field(s):
        info.parse_info(s)
    else:
        music.parse_music(s)


def main():
    # char ext[41];
    # char xref_str[STRLFILE], pat[30][STRLFILE];
    # int isel,j,npat,search_field,retcode,rc;

    # cleanup on premature termination
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # ----- set the page format -----
    if args.help_me == 2:
        print(cfmt)
        exit(0)
    
    # ----- help printout    -----
    if args.help_me:
        cmdline.write_help()
        exit(0)

    # if len(args.filenames):
    #     i_select = pointer_select[len(args.filenames)-1]
    # else:
    #     i_select = pointer_select[0]
    # search_field0 = s_field[i_select]  # default for interactive mode
    if args.epsf:
        epsf_name, _ = util.cut_ext(common.output)
    
    # ----- initialize -----
    # zero_sym()
    common.pagenum = 0
    common.tunenum = 0
    common.file_initialized = False
    # nepsf = 0
    # bposy = 0
    # posx = cfmt.leftmargin
    # posy = cfmt.pageheight-cfmt.topmargin
    # page_init = False

    if args.make_index:
        subs.open_index_file('Ind.ps')

    # ----- loop over files in list ----
    if not args.filenames:
        console.error('++++ No input files')
        exit(1)


    for tune_number, filename in enumerate(args.filenames):
        ext = os.path.splitext(filename)[1]
        # skip .ps and .eps files
        if ext == '.ps' and ext == '.eps':
            continue
        if not ext:
            if not os.path.isfile(filename):
                if os.path.isfile(filename + '.abc'):
                    '.'.join([filename, 'abc'])
                else:
                    continue

        search_field = args.s_field[isel]
        pat = rehash_selectors(sel_str, args.xref_str)

        if args.make_index:
            log.warning(f'{filename}')
            index.do_index(filename, args.xref_str, len(pat), pat,
                args.select_all, search_field)
        else:
            if not common.epsf:
                outf = util.strext(outf, "ps", True)
                if choose_outname: 
                    strext (outf, filename, "ps", True)
                open_output_file(outf, filename)
            print("%s: " % filename) 
            process_file(filename, fout, args.xref_str, len(pat), pat,
                         args.select_all, search_field)

        log.info(f"Selected {tune_number} titles of {len(args.filenames)}")
    
    if args.make_index:
        subs.close_index_file()
    rc = close_output_file ()

    if rc:
        return True
    else:
        return False

"""

/* ----- is_end_line: identify eof ----- */
int is_end_line (const char *str)
{
  if (strlen(str)<3) return 0;
  if (str[0]=='E' && str[1]=='N' && str[2]=='D') return 1;
  return 0;
}

/* ----- is_pseudocomment ----- */
int is_pseudocomment (const char *str)
{
  if (strlen(str)<2) return 0;
  if ((str[0]=='%')&&(str[1]=='%'))  return 1;
  return 0;
}

/* ----- is_comment ----- */
int is_comment (const char *str)
{
  if (strlen(str)<1) return 0;
  if (str[0]=='%')  return 1;
  if (str[0]=='\\') return 1;
  return 0;
}

/* ----- is_cmdline: command line ----- */
int is_cmdline (const char *str)
{
  if (strlen(str)<2) return 0;
  if (str[0]=='%' && str[1]=='!')  return 1;
  return 0;
}


/* ----- parse_music_line: parse a music line into music ----- */
int parse_music_line (char *line)
{
    int type,num,nbr,n,itype,i;
    char msg[81];
    char *p1,*pmx;

    if (ivc>=nvoice) { bug("Trying to parse undefined voice", true); }

    nwline=0;
    type=0;
    nsym0=voice[ivc].nsym;

    nbr=0;
    p1=p=p0=line;
    pmx=p+strlen(p);

    while (*p != 0) {
        if (p>pmx) break;                /* emergency exit */
        type=parse_sym();
        n=voice[ivc].nsym;
        i=n-1;
        if ((db>4) && type)
            printf ("   sym[%d] code (%d,%d)\n",
                    n-1,symv[ivc][n-1].type,symv[ivc][n-1].u);

        if (type==NEWLINE) {
            if ((n>0) && !cfmt.continueall && !cfmt.barsperstaff) {
                symv[ivc][i].eoln=1;
                if (word) {
                    symv[ivc][last_note].word_end=1;
                    word=0;
                }
            }
        }

        if (type==ESCSEQ) {
            if (db>3)
                printf ("Handle escape sequence <%s>\n", escseq);
            itype=info_field (escseq);
            handle_inside_field (itype);
        }

        if (type==REST) {
            if (pplet) {                   /* n-plet can start on rest */
                symv[ivc][i].p_plet=pplet;
                symv[ivc][i].q_plet=qplet;
                symv[ivc][i].r_plet=rplet;
                pplet=0;
            }
            last_note=i;                 /* need this so > and < work */
            p1=p;
        }

        if (type==NOTE) {
            if (!word) {
                symv[ivc][i].word_st=1;
                word=1;
            }
            if (nbr && cfmt.slurisligatura)
                symv[ivc][i].lig1 += nbr;
            else
                symv[ivc][i].slur_st += nbr;
            nbr=0;
            if (voice[ivc].end_slur) symv[ivc][i].slur_end++;
            voice[ivc].end_slur=0;

            if (pplet) {                   /* start of n-plet */
                symv[ivc][i].p_plet=pplet;
                symv[ivc][i].q_plet=qplet;
                symv[ivc][i].r_plet=rplet;
                pplet=0;
            }
            last_note=last_real_note=i;
            p1=p;
        }

        if (word && ((type==BAR)||(type==SPACE))) {
            if (last_real_note>=0) symv[ivc][last_real_note].word_end=1;
            word=0;
        }

        if (!type) {

            if (*p == '-') {                  /* a-b tie */
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
                        if (isdigit(*p)) { qplet=*p-'0';  p++; }
                        if (*p == ':') {
                            p++;
                            if (isdigit(*p)) { rplet=*p-'0';  p++; }
                        }
                    }
                }
                else {
                    nbr++;
                }
            }
            else if (*p == ')') {
                if (last_note>0)
                    if (cfmt.slurisligatura)
                        symv[ivc][last_note].lig2++;
                    else
                        symv[ivc][last_note].slur_end++;
                else
                    syntax ("Unexpected symbol",p);
                p++;
            }
            else if (*p == '>') {
                num=1;
                p++;
                while (*p == '>') { num++; p++; }
                if (last_note<0)
                    syntax ("No note before > sign", p);
                else
                    double_note (last_note, num, 1, p1);
            }
            else if (*p == '<') {
                num=1;
                p++;
                while (*p == '<') { num++; p++; }
                if (last_note<0)
                    syntax ("No note before < sign", p);
                else
                    double_note (last_note, num, -1, p1);
            }
            else if (*p == '*')     /* ignore stars for now  */
                p++;
            else if (*p == '!')     /* ditto for '!' */
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

    /* maybe set end-of-line marker, if music were added */
    n=voice[ivc].nsym;

    if (n>nsym0) {
        if (type==CONTINUE || cfmt.barsperstaff || cfmt.continueall) {
            symv[ivc][n-1].eoln=0;
        } else {
            /* add invisible bar, if last symbol no bar */
            if (symv[ivc][n-1].type != BAR) {
                i=add_sym(BAR);
                symv[ivc][i].u=B_INVIS;
                n=i+1;
            }
            symv[ivc][n-1].eoln=1;
        }
    }



    /* break words at end of line */
    if (word && (symv[ivc][n-1].eoln==1)) {
        symv[ivc][last_note].word_end=1;
        word=0;
    }

    return TO_BE_CONTINUED;

}

/* ----- is_selected: check selection for current info fields ---- */
int is_selected (char *xref_str, int npat, char (*pat)[STRLFILE], int select_all, int search_field)
{
    int i,j,a,b,m;

    /* true if select_all or if no selectors given */
    if (select_all) return 1;
    if (isblankstr(xref_str) && (npat==0)) return 1;

    m=0;
    for (i=0;i<npat;i++) {             /*patterns */
        if (search_field==S_COMPOSER) {
            for (j=0;j<info.ncomp;j++) {
                if (!m) m=match(info.comp[j],pat[i]);
            }
        }
        else if (search_field==S_SOURCE)
            m=match(info.src,pat[i]);
        else if (search_field==S_RHYTHM)
            m=match(info.rhyth,pat[i]);
        else {
            m=match(info.title,pat[i]);
            if ((!m) && (numtitle>=2)) m=match(info.title2,pat[i]);
            if ((!m) && (numtitle>=3)) m=match(info.title3,pat[i]);
        }
        if (m) return 1;
    }

    /* check xref against string of numbers */
    p=xref_str;
    while (*p != 0) {
        parse_space();
        a=parse_uint();
        if (!a) return 0;          /* can happen if invalid chars in string */
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
"""


def rehash_selectors(sel_str, xref_str) -> int:
    """split selectors into patterns and xrefs

    :param sel_str:
    :param xref_str:
    :return pat: list
    """
    # char *q;
    # char arg[501];
    # int i,npat;
    pat = sel_str.split()
    return pat


"""
/* ----- get_line: read line, do first operations on it ----- */
int get_line (FILE *fp, string *ln)
{
    *ln = "";
    if (feof(fp)) return 0;

    getline(ln, fp);
    linenum++;
    if (is_end_line(ln->c_str()))  return 0;

    if ((verbose>=7) || (vb>=10) ) printf ("%3d  %s \n", linenum, ln->c_str());

    return 1;
}


/* ----- read_line: returns type of line scanned --- */
int read_line (FILE *fp, int do_music, string* linestr)
{
    int type,nsym0;
    static char* line = NULL;

    if (!get_line(fp,linestr)) return E_O_F;
    if (line) free(line);
    line = strdup(linestr->c_str());

    if ((linenum==1) && is_cmdline(line)) return CMDLINE;
    if (isblankstr(line))                 return BLANK;
    if (is_pseudocomment(line))           return PSCOMMENT;
    if (is_comment(line))                 return COMMENT;

    decomment_line (line);

    if ((type=info_field(line))) {
        /* skip after history field. Nightmarish syntax, that. */
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

    /* now parse a real line of music */
    if (nvoice==0) ivc=switch_voice (DEFVOICE);

    nsym0=voice[ivc].nsym;

    /* music or tablature? */
    if (is_tab_line(line)) {
        type=parse_tab_line (line);
    } else {
        type=parse_music_line (line);
    }

    if (db>1)
        printf ("  parsed music music %d to %d for voice %d\n",
                nsym0,voice[ivc].nsym-1,ivc);

    return type;
}

"""


if __name__ == '__main__':
    main()


