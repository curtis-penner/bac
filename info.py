

from log import log
from parse import Meter, DefaultLength
from key import Key
from voice import Voice
from common import (within_block)


def is_field(s: str) -> bool:
    """ Validate a field type """
    return len(s) > 2 and s[1] == ':' and s[0] in 'ABCDEFGHKLMNOPQRSTVWwXZ'


def end_of_file(filename) -> None:
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
        else:
            log.warning("Too many composer lines")

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

    def get_xref(self, line: str) -> int:
        """ get xref from string """
        if not line:
            log.error("xref string is empty")
            return 0

        if not line.isdigit():
            log.error(f"xref string has invalid symbols: {line}")
            return 0
        self.xref = int(line)


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
    def __init__(self, appendable=False):
        self.appendable = appendable
        self.line = ''

    def __call__(self, line):
        if self.appendable:
            self.line = ' '.join([self.line, line])
        else:
            self.line = line


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


class Field:
    header = False
    body = False

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

        if is_field(key) and Field.header:
            if not within_block:
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

    def get_default_info(self):
        """ set info to default, except xref field """
        savestr = self.xref
        # default_info = default_info.Field()
        self.xref = savestr

def process_line(self, fp, type, xref_str, pat, sel_all, search_field):
    pass
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
#
