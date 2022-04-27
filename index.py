# Copyright (c) Curtis Penner

import datetime
import getpass

from log import log
import cmdline
import pssubs
import syms
import parse
import util
import info
import common
import constants

args = cmdline.options()
field = info.Field()


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

    def init_index_file(self, fp):
        fp.write("%!PS-Adobe-3.0\n")
        fp.write("%%Title: abctab2ps index\n")

        # CreationDate
        now = datetime.datetime.now()
        fp.write('%Creator: abctab2ps '
                 f'{constants.VERSION}.{constants.REVISION}\n')
        fp.write(f'%CreationDate: {now}\n')
        fp.write(f"%%Creator: "
                 f"abctab2ps {constants.VERSION}.{constants.REVISION}\n")
        fp.write(f"%%CreationDate: {now}\n")

        # Author
        if not args.noauthor:
            fp.write(f'%For: {getpass.getuser()}\n')
        if pssubs.PS_LEVEL == 2:
            fp.write("%%LanguageLevel: 2\n")

        fp.write("%%EndComments\n\n")

        fp.write("%%BeginSetup\n")
        if pssubs.PS_LEVEL < 2:
            pssubs.level1_fix(fp)

        syms.define_font(fp, common.cfmt.indexfont.name, 1)
        fp.write("\n/T {translate} bind def\n/M {moveto} bind def\n")
        fp.write("/S {show} bind def\n")
        syms.def_misc(fp)
        fp.write("%%EndSetup\n\n")

        common.page_number = 0
        self.init_index_page(fp)

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
        # extra space at top
        index_posy = index_posy - 2 * common.cfmt.indexfont.size

        # write heading
        if common.page_number == 1:
            hsize = 1.5 * common.cfmt.indexfont.size
            index_posy = index_posy - hsize
            fp.write(f"{hsize:.1f} {common.cfmt.indexfont.box} F1 \n")
            fp.write(f"{index_posx:.2f} {index_posy:.2f} M (Contents) S\n")
            self.index_posy = self.index_posy - common.cfmt.indexfont.size

        fp.write(f"{common.cfmt.indexfont.size:.1f} {common.cfmt.indexfont.box} F1 \n", )

    def write_index_entry(self) -> None:
        if not self.initialized:
            self.init_index_file(self.fp)
        log.info(f'Write index entry: {self.page_number} <{field.titles.titles[0]}>')
        # Spacing determined here
        self.posy = self.posy - 1.2 * common.cfmt.indexfont.size

        if self.posy-common.cfmt.indexfont.size < common.cfmt.bot_margin:
            close_index_page(self.fp)
            self.init_index_page(self.fp)

        dx1 = 1.8*common.cfmt.indexfont.size
        dx2 = dx1 + common.cfmt.indexfont.size

        t = field.titles
        if not t.titles:
            t.titles.append('No title')
        self.fp.write(f'{self.posx+dx1:.2f} {self.posy:2f} '
                      f'M ({self.page_number}) lshow\n')
        self.fp.write(f'{self.posx+dx2:.2f} {self.posy:2f} '
                      f'M ({t.titles[0]}) S\n')
        if field.rhythm.line or field.origin.line:
            self.fp.write('(  (')
            if field.rhythm.line:
                self.fp.write(f'{field.rhythm.line}')
            if field.rhythm.line and field.origin.line:
                self.fp.write(', ')
            if field.origin.line:
                self.fp.write(f'{field.origin.line}')
            self.fp.write(')) S\n')

        if field.composer[0]:
            self.fp.write(f'(   - {field.composer[0]}) S\n')


def do_index(fp, xref_str: str, pat: list, select_all, search_field) -> None:
    global field
    for line in fp.readlines():
        if parse.is_comment(line):
            continue
        line = parse.decomment_line(line)
        if info.is_field(line):
            f_type = field(line)
            if isinstance(f_type, info.XRef):
                field.xref(line)
                if common.within_block:
                    log.warning(f"+++ Tune {field.xref.xref} not closed properly\n")
                common.within_tune = False
                common.within_block = True
                continue
            elif f_type == constants.KEY:
                if not common.within_block:
                    break
                if not common.within_tune:
                    common.tnum2 += 1
                    if parse.is_selected(xref_str, pat, select_all, search_field):
                        log.info(f"  {field.xref.xref:-4d} {field.key.key_type:-5s}"
                                 f" {field.meter.meter_str:-4s}")
                        if search_field == constants.S_SOURCE:
                            log.info(f"  {field.source.line:-15s}")
                        elif search_field == constants.S_RHYTHM:
                            log.info(f"  {field.rhythm.line:-8s}")
                        elif search_field == constants.S_COMPOSER:
                            log.info(f"  {field.composer.composers[0]:-15s}")
                        if field.titles.titles:
                            log.info(f"  {field.titles.titles[0]} - "
                                     f"{field.titles.titles[1]} - "
                                     f"{field.titles.titles[2]}")
                        common.tnum1 += 1
                    common.within_tune = True
                break

            if util.isblankstr(line):
                if common.within_block and not common.within_tune:
                    log.info(f"+++ Header not closed in tune {field.xref.xref}")
                common.within_tune = False
                common.within_block = False
                field = info.Field()

    if common.within_block and not common.within_tune:
        log.info(f"+++ Header not closed in tune {field.xref.xref}")


def close_index_page(fp) -> None:
    fp.write("\n%%PageTrailer\ngrestore\nshowpage\n")


if __name__ == '__main__':
    ind = Index()
