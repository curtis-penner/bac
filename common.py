# Copyright 2019 Curtis Penner

"""
The purpose of this module is to have a common place to keep global
variable. I know it is not elegant but for now this is how I will work
this.
"""
import constants
import info
from format import Format

cfmt: Format = Format()

bagpipe: bool = False
buf: str = ''   # output buffer.. should hold one tune

do_music: bool = False
do_output: bool = True
do_mode: int = 0

epsf: bool = False

output: str = 'out.ps'

in_page: bool = False
in_file: list = list()
index_initialized: bool = False
is_epsf: bool = False
istab: bool = False

ln_num: int = 0   # number of lines in buffer
ln_pos: list = list()   # vertical positions of buffered lines float
ln_buf: list = list()   # buffer location of buffered lines int

nbuf: int = 0   # number of bytes buffered
notab: bool = False   # ???

maxSyms: int = 800

nsym0: int = 0   # nsym at start of parsing a line

search_field0 = constants.S_TITLE

text: list = list()  # pool for history, words, etc. lines char
text_type: list = list()   # type of each text line int NTEXT

use_buffer: bool = False   # 1 if lines are being accumulated

voices: list[info.Voice] = list()

within_block: bool = False
do_this_tune: bool = False
within_tune: bool = False
write_num: int = 0   # calls to write_buffer for each one tune


class XPOS:            # struct for a horizontal position
    def __init__(self):
        self.type = 0                   # type of symbols here 
        self.next = 0
        self.prec = 0              # pointers for linked list  
        self.eoln = 0                   # flag for line break 
        self.p = list()                     # pointers to associated syms 
        self.time = 0.0
        self.dur = 0.0              # start time, duration 
        self.wl = 0.0
        self.wr = 0.0                 # right and left widths 
        self.space = 0.0
        self.shrink = 0.0
        self.stretch = 0.0  # glue before this position 
        self.tfac = 0.0                  # factor to tune spacings 
        self.x = 0.0                     # final horizontal position 


xp: list[XPOS] = []


# definitions of global variables

# information fields
# info = Field()
# default_info = Field()

# string from last V: line
last_voice_id: str = ''
lvoiceid: str = ""

# number of voices defd, nonempty
# number_voice
# number_nonempty_voice
nvoice: int = 0
mvoice: int = 0
ivc: int = 0   # current v
ivc0: int = 0   # top nonempty v
# int ixpfree                      # first free element in xp array
#                           # things to alloc: 
# int            *nsym_st
#
halftones: int = 0                    # number of halftones to transpose by
#
# float f0p,f5p,f1p,f0x,f5x,f1x            #   mapping fct 
# float lnnp,bnnp,fnnp,lnnx,bnnx,fnnx      #   note-note spacing 
# float lbnp,bbnp,rbnp,lbnx,bbnx,rbnx      #   bar-note spacing 
# float lnbp,bnbp,rnbp,lnbx,bnbx,rnbx      #   note-bar spacing

wpool: str = ''   # pool for vocal strings, NWPOOL
nwpool: int = 0   # globals to handle wpool
nwline: int = 0   # globals to handle wpool

#
# char fontnames[50][STRLFMT]           # list of needed fonts 
# int  nfontnames
#
# //char txt[MAXNTEXT][MAXWLEN]           # for output of text 
# //int  ntxt
words_of_text: str = ''           # for output of text
#
#
# char mbf[501]                 # mini-buffer for one line 
# char buf[BUFFSZ]              # output buffer.. should hold one tune 
bposy: float = 0.0                  # current position in buffered data

# float ln_pos[BUFFLN]          # vertical positions of buffered lines 
# int   ln_buf[BUFFLN]          # buffer location of buffered lines 
# char text [NTEXT][STRLINFO]   # pool for history, words, etc. lines
# int text_type[NTEXT]          # type of each text line 
ntext: int = 0                     # number of text lines
page_init: str = ''   # initialization string after page break
escseq: str = ''               # escape sequence string
linenum: int = 0                  # current line number in input file
tunenum: int = 0                  # number of current tune
tnum1: int = 0
tnum2: int = 0
number_of_titles: int = 0                  # how many titles were read
number_of_music_lines: int = 0                     # number music lines in current tune
# int nsym                      # number of symbols in line 
# int nsym0                     # nsym at start of parsing a line 
page_number: int = 0                   # current page in output file
# int xrefnum                   # xref number of current tune
# int do_meter, do_indent       # how to start next block 
#
# int index_pagenum             # for index file 
# float index_posx, index_posy
# int index_initialized
#
GchordList: list = list()   # prep_gchlst          # guitar chords for preparsing
# Deco prep_deco                  # decorations for preparsing 
# int bagpipe                     # switch for HP mode 
# int within_tune, within_block   # where we are in the file 
# int do_this_tune                # are we typesetting the current one ? 
posx: float = cfmt.left_margin
posy: float = cfmt.page_height - cfmt.top_margin   # overall scale, position on page
# int barinit                     # carryover bar number between parts 
#
# char *p, *p0                    # global pointers for parsing music line 
#
word = False
slur = False                   # variables used for parsing...

last_note: int = 0
last_real_note: int = 0
# int pplet,qplet,rplet
# int carryover                   # for interpreting > and < chars 
# int ntinext,tinext[MAXHD]       # for chord ties 
#
# struct ENDINGS ending[20]       # where to draw endings 
# int num_ending                  # number of endings to draw 
# int mes1,mes2                   # to count measures in an ending 
#
# int slur1[20],slur2[20]         # needed for drawing slurs 
# int overfull                    # flag if staff overfull 
# int do_words                    # flag if staff has words under it 
#
# int vb, verbose                 # verbosity, global and within tune 
# int in_page=0
#
#                                  # switches modified by flags: 
# int gmode                         # switch for glue treatment 
# int include_xrefs                 # to include xref numbers in title 
# int one_per_page                  # new page for each tune ? 
# int pagenumbers                   # write page numbers ? 
write_history: bool = False                 # write history and notes ?
help_me: bool = False   # need help ?
select_all = False    # select all tunes?
# int epsf                          # for EPSF postscript output 
choose_outname: bool = False                # 1 names outfile w. title/fnam
# int break_continues               # ignore continuations ? 
# int search_field0                 # default search field 
# int pretty                        # for pretty but sprawling layout 
# int bars_per_line                 # bars for auto linebreaking 
# int continue_lines                # flag to continue all lines 
# int landscape                     # flag for landscape output 
# int barnums                       # interval for bar numbers 
make_index: bool = False   # write index file
# int notab                         # do not process tablature 
# int transposegchords              # transpose gchords 
# float alfa_c                      # max compression allowed 
# float scalefac                    # scale factor for symbol size 
# float lmargin                     # left margin 
# float swidth                      # staff width 
# float staffsep,dstaffsep        # staff separation 
# float strict1,strict2           # 1stave, mstave strictness 
# char transpose[21]              # target key for transposition 
# struct PAPERSIZE* paper         # paper size (a4, letter) 
# int noauthor                    # suppress PS author tag (%%For) 
#
#
# float alfa_last,beta_last       # for last short short line.. 
#
# char in_file[MAXINF][STRLFILE]  # list of input file names 
number_input_files: int = 0   # number of input file names
# FILE *fin                       # for input file 
#
# char outf[STRLFILE]             # output file name 
# char outfnam[STRLFILE]          # internal file name for open/close 
# char styf[STRLFILE]             # layout style file name 
# char styd[STRLFILE]             # layout style directory 
# char infostr[STRLFILE]          # title string in PS file 
#
file_open: bool = False                  # for output file
file_initialized: bool = False           # for output file
# FILE *fout,*findex              # for output file 
nepsf: int = 0                       # counter for epsf output files
#
# char sel_str[MAXINF][STRLFILE]  # list of selector strings 
# int  s_field[MAXINF]            # type of selection for each file 
# int  psel[MAXINF]               # pointers from files to selectors 
#
# int temp_switch

# most likely will not need these but just safe keeping
# allocVc: int = 800
# allocSyms: int = 800
# maxVc: int = 3
# maxSymx: int = 3


def bskip(fp, h: float) -> None:
    """ translate down by h points in output buffer """
    global bposy

    if h*h > 0.0001:
        fp.write(f'0 {-h:.2f} T\n')
        bposy = bposy - h
