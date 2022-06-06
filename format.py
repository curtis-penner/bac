# Copyright 2019 Curtis Penner

import os

from log import log
import cmdline
import common
from constants import (CM, PT, IN, DEFAULT_FDIR)

args = cmdline.options()


class Font:
    names: list = list()

    def __init__(self):
        self.name = 'Times-Roman'
        self.size = 14.0
        self.box = False

    def __call__(self, name='Times-Roman', size=14.0, box=False):
        self.name = name
        self.size = size
        self.box = box
        self._add_font()

    def _add_font(self):
        """ checks font list, adds font if new font """
        log.info("Adding fonts from format..")
        if self.name in Font.names:
            log.info(f"Font {self.name} "
                     f"exists at index {Font.names.index(self.name)}")
        else:
            Font.names.append(self.name)
            log.info(f"Adding new font {self.name}")

    def __str__(self):
        if self.box:
            return f"{self.name} {self.size:.1f} box"
        else:
            return f"{self.name} {self.size:.1f}"

    def set_font(self, add_bracket: bool =False) -> None:
        if self.name not in Font.names:
            font_index = Font.names.index(self.name)

        else:
            font_index = 0
            log.error(
                f'+++ Font "{self.name}" not predefined; "'
                'using first in list')

        if add_bracket:
            line = f"{self.size:.1f} {self.box:d} F{font_index}("
        else:
            line = f"{self.size:.1f} {self.box:d} F{font_index}"
        with open('out.ps', 'w') as fp:
            fp.write(line)

    def set_font_str(self, page_init):
        """
        subs.py 893  cfmt.textfont.set_font_str(page_init)

        subs.py 1001 set_font_str(page_init,cfmt.wordsfont)
        subs.py 1080 set_font_str(page_init,cfmt.textfont)

        :param boot page_init:
        """
        if not page_init:
            return
        font_index = 0
        if self.name in Font.names:
            font_index = Font.names.index(self.name)
        log.debug(f"{self.size:.1f} {self.box:d} F{font_index}")


class Papersize:
    # name: [page width, page height, left margin, staff width]
    papersizes = {
        "a4": [21.0 * CM, 29.7 * CM, 1.8 * CM, 17.4 * CM],
        "letter": [21.6 * CM, 27.9 * CM, 1.8 * CM, 18.0 * CM],
        "a5": [14.8 * CM, 21.0 * CM, 1.4 * CM, 12.0 * CM],
        "folio": [21.6 * CM, 33.0 * CM, 1.8 * CM, 18.0 * CM],
        "quarto": [21.5 * CM, 27.5 * CM, 1.8 * CM, 17.9 * CM],
        "legal": [21.6 * CM, 35.6 * CM, 1.8 * CM, 18.0 * CM],
        "executive": [19.0 * CM, 25.4 * CM, 1.5 * CM, 16.0 * CM],
        "tabloid": [27.9 * CM, 43.2 * CM, 2.0 * CM, 23.9 * CM]}

    def __init__(self, name='letter'):
        """ Default papaersize name is 'letter' """
        self.name = name.lower()
        self.page_width = Papersize.papersizes[self.name][0]
        self.page_height = Papersize.papersizes[self.name][1]
        self.left_margin = Papersize.papersizes[self.name][2]
        self.staff_width = Papersize.papersizes[self.name][3]


class Format:
    def __init__(self):
        name = 'letter'
        ppsz = Papersize(name)

        self.name = "standard"
        self.page_height = ppsz.page_height
        self.staff_width = ppsz.staff_width
        self.left_margin = ppsz.left_margin
        self.top_margin = 1.0 * CM
        self.bot_margin = 1.0 * CM
        self.topspace = 0.8*CM
        self.titlespace = 0.2*CM
        self.subtitlespace = 0.1*CM
        self.composerspace = 0.2*CM
        self.musicspace = 0.2*CM
        self.partsspace = 0.3*CM
        self.staffsep = 46.0*PT
        self.sysstaffsep = 40.0*PT
        self.systemsep = 55.0*PT
        self.stafflinethickness = 0.75
        self.vocalspace = 23.0*PT
        self.textspace = 0.5*CM
        self.wordsspace = 0.0*CM
        self.gchordspace = 14.0*PT
        self.scale = 0.70
        self.maxshrink = 0.65
        self.landscape = False
        self.titleleft = False
        self.stretchstaff = 1
        self.stretchlast = 1
        self.continueall = False
        self.breakall = 0
        self.writehistory = 0
        self.withxrefs = 0   # include_xrefs
        self.one_per_page = 0
        self.titlecaps = 0
        self.barsperstaff = 0
        self.barnums = False
        self.barinit = 1
        self.squarebrevis = 0
        self.endingdots = 0
        self.slurisligatura = 0
        self.historicstyle = 0
        self.nobeams = 0
        self.nogracestroke = 0
        self.printmetronome = 1
        self.nostems = 0
        self.lineskipfac = 1.1
        self.parskipfac = 0.4
        self.strict1 = 0.5
        self.strict2 = 0.8
        self.indent = 0.0
        self.titlefont = Font("Times-Roman", 15.0, False)
        self.subtitlefont = Font("Times-Roman", 12.0, False)
        self.composerfont = Font("Times-Italic", 11.0, False)
        self.partsfont = Font("Times-Roman", 11.0, False)
        self.tempofont = Font("Times-Bold", 10.0, False)
        self.vocalfont = Font("Times-Roman", 14.0, False)
        self.textfont = Font("Times-Roman", 12.0, False)
        self.wordsfont = Font("Times-Roman", 12.0, False)
        self.gchordfont = Font("Helvetica", 12.0, False)
        self.voicefont = Font("Times-Roman", 12.0, False)
        self.barnumfont = Font("Times-Italic", 12.0, False)
        self.barlabelfont = Font("Times-Bold", 18.0, False)
        self.indexfont = Font("Times-Roman", 11.0, False)

    def set_pretty_format(self):
        self.name = "pretty"
        self.titlespace = 0.4*CM
        self.composerspace = 0.25*CM
        self.musicspace = 0.25*CM
        self.partsspace = 0.3*CM
        self.staffsep = 50.0*PT
        self.sysstaffsep = 45.0*PT
        self.systemsep = 55.0*PT
        self.stafflinethickness = 0.75
        self.scale = 0.75
        self.maxshrink = 0.55
        self.parskipfac = 0.1
        self.titlefont = Font("Times-Roman", 18.0, False)
        self.subtitlefont = Font("Times-Roman", 15.0, False)
        self.composerfont = Font("Times-Italic", 12.0, False)
        self.partsfont = Font('Times-Roman', 12.0, False)
        self.tempofont = Font('Times-Bold', 10.0, False)
        self.vocalfont = Font('Times-Roman', 14.0, False)
        self.textfont = Font("Times-Roman", 10.0, False)
        self.wordsfont = Font("Times-Roman", 10.0, False)
        self.gchordfont = Font("Helvetica", 12.0, False)
        self.voicefont = Font("Times-Roman", 12.0, False)

    def set_pretty2_format(self):
        self.name = 'pretty2'
        self.titlespace = 0.4*CM
        self.composerspace = 0.3*CM
        self.musicspace = 0.25*CM
        self.partsspace = 0.2*CM
        self.staffsep = 55.0*PT
        self.sysstaffsep = 45.0*PT
        self.systemsep = 55.0*PT
        self.stafflinethickness = 0.75
        self.textspace = 0.2*CM
        self.scale = 0.70
        self.maxshrink = 0.55
        self.titleleft = 1
        self.parskipfac = 0.1
        self.titlefont = Font("Helvetica-Bold", 16.0, False)
        self.subtitlefont = Font("Helvetica-Bold", 13.0, False)
        self.composerfont = Font("Helvetica", 10.0, False)
        self.partsfont = Font("Times-Roman", 12.0, False)
        self.tempofont = Font("Times-Bold", 10.0, False)
        self.vocalfont = Font("Times-Roman", 14.0, False)
        self.textfont = Font("Times-Roman", 10.0, False)
        self.wordsfont = Font("Times-Roman", 10.0, False)
        self.gchordfont = Font("Helvetica", 12.0, False)
        self.voicefont = Font("Times-Roman", 12.0, False)
        self.barnumfont = Font("Times-Roman", 11.0, True)
        self.barlabelfont = Font("Times-Bold", 18.0, True)

    def set_page_format(self) -> None:
        """ The intent here is to create a page format from the option
        taken from the commandline for from a file. """
        if DEFAULT_FDIR or args.styf != 'fonts.fmt':
            self.read_fmt_file(args.styf, args.styd)
        if args.pretty == 1:
            self.set_pretty_format()
        elif args.pretty == 2:
            self.set_pretty2_format()
        self.ops_into_fmt()
        log.warning(f'used format file: {args.styf}')
        log.debug(f'Format file is {args.styf}')

    def read_fmt_file(self, filename, dirname):
        """
        Read format information from format file (default fonts.fmt)
        """
        if not os.path.isfile(filename):
            new_filename = os.path.join(dirname, filename)
            if os.path.isfile(new_filename):
                setattr(args, 'styf', new_filename)
            else:
                return
        with open(args.styf) as fp:
            log.info(f"Reading format file: {filename}\n")
            for line in fp:
                self.interpret_format_line(line)
            return

    def ops_into_fmt(self):
        dstaffsep = float(args.dstaffsep.removesuffix('cm'))
        self.staffsep = self.staffsep + dstaffsep
        self.sysstaffsep = self.sysstaffsep + dstaffsep

    def __str__(self):
        return f'''Format: {self.name}
    pageheight         {self.page_height / CM:.2f}cm
    staffwidth         {self.staff_width / CM:.2f}cm
    topmargin          {self.top_margin / CM:.2f}cm
    botmargin          {self.bot_margin / CM:.2f}cm
    leftmargin         {self.left_margin / CM:.2f}cm
    topspace           {self.topspace/CM:.2f}cm
    titlespace         {self.titlespace/CM:.2f}cm
    subtitlespace      {self.subtitlespace/CM:.2f}cm
    composerspace      {self.composerspace/CM:.2f}cm
    musicspace         {self.musicspace/CM:.2f}cm
    partsspace         {self.partsspace/CM:.2f}cm
    wordsspace         {self.wordsspace/CM:.2f}cm
    textspace          {self.textspace/CM:.2f}cm
    vocalspace         {self.vocalspace:.1f}pt
    gchordspace        {self.gchordspace:.1f}pt
    staffsep           {self.staffsep:.1f}pt
    sysstaffsep        {self.sysstaffsep:.1f}pt
    systemsep          {self.systemsep:.1f}pt
    stafflinethickness {self.stafflinethickness:.2f}
    scale              {self.scale:.2f}
    maxshrink          {self.maxshrink:.2f}
    strictness1        {self.strict1:.2f}
    strictness2        {self.strict2:.2f}
    indent             {self.indent:.1f}pt

    titlefont          {self.titlefont}
    subtitlefont       {self.subtitlefont}
    composerfont       {self.composerfont}
    partsfont          {self.partsfont}
    tempofont          {self.tempofont}
    vocalfont          {self.vocalfont}
    gchordfont         {self.gchordfont}
    textfont           {self.textfont}
    wordsfont          {self.wordsfont}
    voicefont          {self.voicefont}
    barnumberfont      {self.barnumfont}
    barlabelfont       {self.barlabelfont}
    indexfont          {self.indexfont}

    lineskipfac        {self.lineskipfac:.1f}
    parskipfac         {self.parskipfac:.1f}
    barsperstaff       {self.barsperstaff:d}
    barnumbers         {self.barnums:d}
    barnumberfirst     {self.barinit:d}
    landscape          {self.landscape}
    titleleft          {self.titleleft}
    titlecaps          {self.titlecaps}
    stretchstaff       {self.stretchstaff}
    stretchlast        {self.stretchlast}
    writehistory       {self.writehistory}
    continueall        {self.continueall}
    breakall           {self.breakall}
    one_per_page       {self.one_per_page}
    withxrefs          {self.withxrefs}
    squarebrevis       {self.squarebrevis}
    endingdots         {self.endingdots}
    slurisligatura     {self.slurisligatura}
    historicstyle      {self.historicstyle}
    nobeams            {self.nobeams}
    nogracestroke      {self.nogracestroke}
    printmetronome     {self.printmetronome}
    nostems            {self.nostems}
'''
        # tablature specific stuff
        # tabfmt.print_tab_format()

    def interpret_g_unum(self, key, value):
        if key not in ['pageheight',
                       'staffwidth',
                       'topmargin',
                       'botmargin',
                       "leftmargin",
                       "topspace",
                       "wordsspace",
                       "titlespace",
                       "subtitlespace",
                       "composerspace",
                       "musicspace",
                       "partsspace",
                       "staffsep",
                       "sysstaffsep",
                       "systemsep",
                       "vocalspace",
                       "textspace",
                       "gchordspace",
                       'indent']:
            return
        setattr(self, key, g_unum(value))

    def interpret_g_fltv(self, key, value):
        if key not in ["scale",
                       "stafflinethickness",
                       "maxshrink",
                       "lineskipfac",
                       "parskipfac",
                       "barsperstaff",
                       "strictness1",
                       "strictness2",
                       "strictness"]:
            return
        setattr(self, key, g_fspc(value))
        if key == 'strictness':
            self.strict2 = self.strict1

    def interpret_g_intv(self, key, value):
        if key not in ["barnumbers",
                       "barnumberfirst"]:
            return
        setattr(self, key, g_intv(value))

    def interpret_g_logv(self, key, value):
        if key not in ["titleleft",
                       "titlecaps",
                       "landscape",
                       "stretchstaff",
                       "stretchlast"
                       "continueall",
                       "breakall",
                       "writehistory",
                       "withxrefs",
                       "one_per_page",
                       "squarebrevis",
                       "endingdots",
                       "slurisligatura",
                       "historicstyle",
                       "nobeams",
                       "nogracestroke",
                       "printmetronome",
                       "nostems"]:
            return
        setattr(self, key, g_logv(value))

    def interpret_g_fspc(self, key, value):
        if key not in ["titlefont",
                       "subtitlefont",
                       "vocalfont",
                       "partsfont",
                       "tempofont",
                       "textfont",
                       "composerfont",
                       "wordsfont",
                       "gchordfont",
                       "voicefont",
                       "barnumberfont",
                       "barlabelfont",
                       "indexfont"]:
            return
        setattr(self, key, g_fspc(value))

    def interpret_format_line(self, line):
        """
        Read the line with a format directive to reset a format value

        :param line:
        """
        if line.startswith('%'):
            return False
        log.info(f"Interpret format line: {line}")
        if line == "end":
            return True
        key, value = line.split(' ', 1)
        self.interpret_g_unum(key, value)
        self.interpret_g_fltv(key, value)
        self.interpret_g_intv(key, value)
        self.interpret_g_logv(key, value)
        self.interpret_g_fspc(key, value)
        #
        # if key == "font":
        #     p, q = value.split()
        #     if p not in Font.names:
        #         if common.file_initialized:
        #             log.error(f"+++ Cannot predefine when output "
        #                       "file open: {line}")
        #             exit(3)
        #         if not q:
        #             q = 12.0
        #         setattr(Format, 'tempfont', Font(p, q))
        #
        # elif key == "meterdisplay":
        #     if '=' in
        # #     string str = s;
        # #     string key, value;
        # #     if ((pos=str.find('=': != string::
        # #         npos) {
        # #         key = str.substr(0, pos);
        # #     strip( & key);
        # #     value = str.substr(pos + 1, str.length());
        # #     strip( & value);
        # #     self.meterdisplay[key] = value;
        # #     } else {
        # #         printf("missing '=' in meterdisplay:%s\n", s);
        # #     }
        # return 0

    def init_pdims(self) -> None:
        """
        initialize page dimensions

        :return:
        """
        if common.in_page:
            return
        common.posx = self.left_margin
        common.posy = self.page_height - self.top_margin


def g_unum(s):
    """
    read a number with a unit

    :param str s:
    :return float: number
    """
    try:
        if s[-2:] in ['pt', 'cm', 'in', 'mm']:
            unit = s[-2:]
            num = float(s[:-2])
            if unit == 'cm':
                return num*CM
            elif unit == 'mm':
                return num*CM*0.1
            elif unit == 'in':
                return num*IN
            elif unit == 'pt':
                return num*PT
            else:
                raise TypeError
    except TypeError as te:
        log.error(te)
        log.error('+++ Unknown unit line: %s' % te)
        exit(3)


def g_logv(s):
    """read a logical variable

    :param str s:
    :return bool:
    """
    return s == '1' or s.lower() == 'yes' or s.lower() == 'true'


def g_fltv(s):
    """read a float variable, no units

    :param s:
    :return float:
    """
    try:
        return float(s)
    except ValueError as te:
        log.error(te)
        return 0.0


def g_intv(s):
    """read an int variable, no units

    :param s:
    :return int:
    """
    try:
        return int(s)
    except ValueError as te:
        log.error(te)
        return 0


def g_fspc(font_spec):
    """Read a font specifier. Can use * as a filler.

    :param font_spec:
    :return:
    """
    size = 14.0
    box = False
    fns = font_spec.split()
    if not len(fns):
        fns = list('***')
    if fns[0] == '*':
        name = 'Times-Roman'
    else:
        name = fns[0]
    if len(fns) > 1:
        if fns[1] == '*':
            size = 14.0
        else:
            size = g_fltv(fns[1])
    if len(fns) > 2:
        if fns[2] == '*':
            box = False
        else:
            box = False if 'box' != fns[2] else True
    return Font(name, size, box)


cfmt = Format()
font = Font()


if __name__ == '__main__':
    assert g_logv('true')
    assert g_logv('YES')
    assert not g_logv('hey')
    assert g_logv('1')
    assert g_logv('yes')

    assert g_fltv('1.43') == 1.43
    assert g_fltv('3') == 3
    assert g_fltv('1.a') == 0.0

    assert g_intv('3') == 3
    assert g_intv('2.1') == 0

    f = g_fspc('')
    assert f.name == 'Times-Roman'
    assert f.size == 14.0
    assert not f.box
    del f
    f = g_fspc('george')
    assert f.name == 'george'
    assert f.size == 14.0
    assert not f.box
    del f
    f = g_fspc('george 12.0 box')
    assert f.name == 'george'
    assert f.size == 12.0
    assert f.box
    del f
