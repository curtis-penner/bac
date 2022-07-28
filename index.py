# Copyright (c) Curtis Penner

import datetime
import getpass
from typing import IO

from log import log
import cmdline
import pssubs
import syms
import parse
import util
import field
import common
import constants

args = cmdline.options()
info = field.Field()


def close_index_file(fp):
    log.debug(f'Close index file {fp.name}')
    close_index_page(fp)
    fp.close()


def close_index_page(fp) -> None:
    fp.write("\n%%PageTrailer\ngrestore\nshowpage\n")



class Index:
    def __init__(self):
        self.fp: IO = None
        self.make_index = args.make_index
        self.initialized = False
        self.do_index = False
        self.page_number = 0
        self.posx = 0.0
        self.posy = 0.0
        self.index_posy = 0.0

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

    def open_index_file(self, filename: str):
        log.debug(f'Open index file "{filename}"\n')
        try:
            self.fp = open(filename, 'w')
        except FileExistsError as fee:
            log.error(f'Cannot open index file: {fee}')
            exit(1)
        index.initialized = False

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
        log.debug(f'Write index entry: {self.page_number} <{info.titles.titles[0]}>')
        # Spacing determined here
        self.posy = self.posy - 1.2 * common.cfmt.indexfont.size

        if self.posy-common.cfmt.indexfont.size < common.cfmt.bot_margin:
            close_index_page(self.fp)
            self.init_index_page(self.fp)

        dx1 = 1.8*common.cfmt.indexfont.size
        dx2 = dx1 + common.cfmt.indexfont.size

        t = info.titles
        if not t.titles:
            t.titles.append('No title')
        self.fp.write(f'{self.posx+dx1:.2f} {self.posy:2f} '
                      f'M ({self.page_number}) lshow\n')
        self.fp.write(f'{self.posx+dx2:.2f} {self.posy:2f} '
                      f'M ({t.titles[0]}) S\n')
        if info.rhythm.line or info.origin.line:
            self.fp.write('(  (')
            if info.rhythm.line:
                self.fp.write(f'{info.rhythm.line}')
            if info.rhythm.line and info.origin.line:
                self.fp.write(', ')
            if info.origin.line:
                self.fp.write(f'{info.origin.line}')
            self.fp.write(')) S\n')

        if info.composer[0]:
            self.fp.write(f'(   - {info.composer[0]}) S\n')


def do_index(fp, xref_str: str, pat: list, select_all, search_field) -> None:
    for line in fp.readlines():
        if parse.is_comment(line):
            continue
        line = parse.decomment_line(line)
        if field.is_field(line):
            f_type = info(line)
            if isinstance(f_type, field.XRef):
                info.xref(line)
                if common.within_block:
                    log.warning(f"+++ Tune {info.xref.xref} not closed properly\n")
                common.within_tune = False
                common.within_block = True
                continue
            elif isinstance(f_type, field.Key):
                if not common.within_block:
                    break
                if not common.within_tune:
                    common.tnum2 += 1
                    if parse.is_selected(xref_str, pat, select_all, search_field):
                        log.debug(f"  {info.xref.xref:-4d} {info.key.key_type:-5s}"
                                 f" {info.meter.meter_str:-4s}")
                        if search_field == constants.S_SOURCE:
                            log.debug(f"  {info.source.line:-15s}")
                        elif search_field == constants.S_RHYTHM:
                            log.debug(f"  {info.rhythm.line:-8s}")
                        elif search_field == constants.S_COMPOSER:
                            log.debug(f"  {info.composer.composers[0]:-15s}")
                        if info.titles.titles:
                            log.debug(f"  {info.titles.titles[0]} - "
                                     f"{info.titles.titles[1]} - "
                                     f"{info.titles.titles[2]}")
                        common.tnum1 += 1
                    common.within_tune = True
                break

            if util.isblankstr(line):
                if common.within_block and not common.within_tune:
                    log.debug(f"+++ Header not closed in tune {info.xref.xref}")
                common.within_tune = False
                common.within_block = False

    if common.within_block and not common.within_tune:
        log.debug(f"+++ Header not closed in tune {info.xref.xref}")


index = Index()

