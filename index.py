# Copyright (c) Curtis Penner

import datetime
import getpass

from log import log
import cmdline
import pssubs
import syms
import parse
import info
import common
import constants

args = cmdline.options()
info = info.Field()


class Index:
    def __init__(self):
        self.make_index = args.make_index
        self.initialized = False
        self.do_index = False
        self.page_number = 0
        self.fp = None
        self.posx = 0.0
        self.posy = 0.0
        self.index_posy = 0.

    def __del__(self):
        self.close_index_file()

    def open_index_file(self, filename):
        log.info(f'Open index file "{filename}"\n')
        try:
            self.fp = open(filename, 'w')
        except FileExistsError as fee:
            log.error(f'Cannot open index file: {fee}')
            exit(1)
        self.initialized = False

    def close_index_file(self):
        log.info(f'Close index file {self.fp.name}')
        close_index_page(self.fp)
        self.fp.close()

    def init_index_file(self, findex):
        findex.write("%!PS-Adobe-3.0\n")
        findex.write("%%Title: abctab2ps index\n")

        # CreationDate
        now = datetime.datetime.now()
        findex.write('%Creator: abctab2ps '
                     f'{constants.VERSION}.{constants.REVISION}\n')
        findex.write(f'%CreationDate: {now}\n')
        findex.write(f"%%Creator: "
                     f"abctab2ps {constants.VERSION}.{constants.REVISION}\n")
        findex.write(f"%%CreationDate: {now}\n")

        # Author
        if not args.noauthor:
            findex.write(f'%For: {getpass.getuser()}\n')
        if pssubs.PS_LEVEL == 2:
            findex.write("%%LanguageLevel: 2\n")

        findex.write("%%EndComments\n\n")

        findex.write("%%BeginSetup\n")
        if pssubs.PS_LEVEL < 2:
            pssubs.level1_fix(findex)

        syms.define_font(findex, common.cfmt.indexfont.name, 1)
        findex.write("\n/T {translate} bind def\n/M {moveto} bind def\n")
        findex.write("/S {show} bind def\n")
        syms.def_misc(findex)
        findex.write("%%EndSetup\n\n")

        common.page_number = 0
        self.init_index_page(findex)

        common.index_initialized = True

    def init_index_page(self, fp) -> None:
        common.page_number += 1

        fp.write(f"\n% --- page {common.page_number}\n"
                 f"%%Page: {common.page_number} {common.page_number}\n"
                 "%%BeginPageSetup\n")

        if common.cfmt.landscape:
            fp.write("%%PageOrientation: Landscape\n")
        fp.write("gsave\n")
        if common.cfmt.landscape:
            fp.write(f"90 rotate 0 {-common.cfmt.page_height:.1f} translate ")
        fp.write("%%EndPageSetup\n\n")

        index_posx = common.cfmt.left_margin
        index_posy = common.cfmt.page_height - common.cfmt.top_margin
        # extra space at top..
        index_posy = index_posy - 2 * common.cfmt.indexfont.size

        # write heading
        if common.page_number == 1:
            hsize = 1.5 * common.cfmt.indexfont.size
            index_posy = index_posy - hsize
            fp.write(f"{hsize:.1f} {common.cfmt.indexfont.box} F1 \n")
            fp.write(f"{index_posx:.2f} {index_posy:.2f} M (Contents) S\n")
            self.index_posy = self.index_posy - common.cfmt.indexfont.size

        fp.write(f"{common.cfmt.indexfont.size:.1f} {common.cfmt.indexfont.box} F1 \n", )

    def do_index(self, fp, xref_str: str, pat: list, selct_all, search_field0) -> None:
        field = info.Field()
        for line in fp.readlines():
            if parse.is_comment(line):
                continue
            line = parse.decomment_line(line)
            if info.is_field(line):
                f_type = field(line)
            if isinstance(f_type, field.XRef):
                if common.within_block:
                    log.warning(f"+++ Tune {field.XRef.xref} not closed properly\n")
                numtitle = 0
                within_tune = False
                within_block = True
                ntext = 0
                continue
            elif f_type == constants.KEY:
                pass

    def write_index_entry(self) -> None:
        if not self.initialized:
            self.init_index_file(self.fp)
        log.info(f'Write index entry: {self.page_number} <{info.title}>')
        # Spacing determined here
        self.posy = self.posy - 1.2 * common.cfmt.indexfont.size

        if self.posy-common.cfmt.indexfont.size < common.cfmt.bot_margin:
            close_index_page(self.fp)
            self.init_index_page(self.fp)

        dx1 = 1.8*common.cfmt.indexfont.size
        dx2 = dx1 + common.cfmt.indexfont.size

        t = info.Titles()
        if not t.titles:
            t.titles.append('No title')
        self.fp.write(f'{self.posx+dx1:.2f} {self.posy:2f} '
                      f'M ({self.page_number}) lshow\n')
        self.fp.write(f'{self.posx+dx2:.2f} {self.posy:2f} '
                      f'M ({t.titles[0]}) S\n')
        if info.rhyth or info.orig:
            self.fp.write('(  (')
            if info.rhyth:
                self.fp.write(f'{info.rhyth}')
            if info.rhyth and info.orig:
                self.fp.write(', ')
            if info.orig:
                self.fp.write(f'{info.orig}')
            self.fp.write(')) S\n')

        if info.composer[0]:
            self.fp.write(f'(   - {info.composer[0]}) S\n')


def close_index_page(fp) -> None:
    fp.write("\n%%PageTrailer\ngrestore\nshowpage\n")


"""

/* ----- do_index: print index of abc file ------ */
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
          printf ("  %-4d %-5s %-4s", xrefnum, info.key, info.meter);
          if      (search_field==S_SOURCE)   printf ("  %-15s", info.src);
          else if (search_field==S_RHYTHM)   printf ("  %-8s",  info.rhyth);
          else if (search_field==S_COMPOSER) printf ("  %-15s", info.comp[0]);
          if (numtitle==3)
            printf ("  %s - %s - %s", info.title,info.title2,info.title3);
          if (numtitle==2) printf ("  %s - %s", info.title, info.title2);
          if (numtitle==1) printf ("  %s", info.title);

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


if __name__ == '__main__':
    ind = Index()
