# Copyright 2019 Curtis Penner

"""
The purpose of this module is to have a common place to keep global
variable. I know it is not elegant but for now this is how I will work
this.
"""
from constants import (S_TITLE, VERBOSE0, DEBUG_LV)
from format import Format
from parse import Key
cfmt = Format()


bagpipe = False
bposy = 0.0
buf = ''   # output buffer.. should hold one tune

# choose_outname = args.outf
do_music = False
do_output = False
do_mode = 0
do_this_tune = False

epsf = False

file_initialized = False
file_open = False
output = 'out.ps'
fp = open(output, 'a')

in_page = False
in_file = list()
index_initialized = False
is_epsf = False
istab = False

key = Key()

ln_num = 0   # number of lines in buffer
ln_pos = list()   # vertical positions of buffered lines float
ln_buf = list()   # buffer location of buffered lines int

nbuf = 0   # number of bytes buffered
notab = Tr

maxSyms = 800

nepsf = 0
nsym0 = 0   # nsym at start of parsing a line

page_init = ''
pagenum = 0
posx = 0.0
posy = 0.0

search_field0 = S_TITLE

text = list()  # pool for history, words, etc. lines char
text_type = list()   # type of each text line int NTEXT
tunenum = 0
tnum1 = 0
tnum2 = 0

use_buffer = False   # 1 if lines are being accumulated

vb = 0
verbose = 0
vg = VERBOSE0
voices = list()

within_block = False

within_tune = False
writenum = 0   # calls to write_buffer for each one tune


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

db = DEBUG_LV   # debug control



# information fields
# info = Field()
# default_info = Field()

# string from last V: line
last_voice_id = ''
lvoiceid = ""

# number of voices defd, nonempty
# number_voice
# number_nonempty_voice
nvoice = 0
mvoice = 0
ivc = None   # current v
ivc0 = 0   # top nonempty v 
# int ixpfree                      # first free element in xp array
#                           # things to alloc: 
# int            *nsym_st
#
# int halftones                    # number of halftones to transpose by 
#
# float f0p,f5p,f1p,f0x,f5x,f1x            #   mapping fct 
# float lnnp,bnnp,fnnp,lnnx,bnnx,fnnx      #   note-note spacing 
# float lbnp,bbnp,rbnp,lbnx,bbnx,rbnx      #   bar-note spacing 
# float lnbp,bnbp,rnbp,lnbx,bnbx,rnbx      #   note-bar spacing 
#
#

wpool = ''   # pool for vocal strings, NWPOOL
nwpool = 0   # globals to handle wpool
nwline = 0   # globals to handle wpool

#
# char fontnames[50][STRLFMT]           # list of needed fonts 
# int  nfontnames
#
# //char txt[MAXNTEXT][MAXWLEN]           # for output of text 
# //int  ntxt
words_of_text = ''           # for output of text
#
#
# char mbf[501]                 # mini-buffer for one line 
# char buf[BUFFSZ]              # output buffer.. should hold one tune 
# float bposy                   # current position in buffered data

# float ln_pos[BUFFLN]          # vertical positions of buffered lines 
# int   ln_buf[BUFFLN]          # buffer location of buffered lines 
# char text [NTEXT][STRLINFO]   # pool for history, words, etc. lines
# int text_type[NTEXT]          # type of each text line 
# int ntext                     # number of text lines 
# char page_init[201]           # initialization string after page break 
escseq = ''               # escape sequence string
linenum = 0                  # current line number in input file
# int tunenum                   # number of current tune 
# int tnum1,tnum2
# int numtitle                  # how many titles were read 
# int mline                     # number music lines in current tune 
# int nsym                      # number of symbols in line 
# int nsym0                     # nsym at start of parsing a line 
# int pagenum                   # current page in output file 
# int xrefnum                   # xref number of current tune
# int do_meter, do_indent       # how to start next block 
#
# int index_pagenum             # for index file 
# float index_posx, index_posy
# int index_initialized
#
GchordList = list()   # prep_gchlst          # guitar chords for preparsing
# Deco prep_deco                  # decorations for preparsing 
# int bagpipe                     # switch for HP mode 
# int within_tune, within_block   # where we are in the file 
# int do_this_tune                # are we typesetting the current one ? 
# float posx,posy                 # overall scale, position on page 
# int barinit                     # carryover bar number between parts 
#
# char *p, *p0                    # global pointers for parsing music line 
#
word = False
slur = False                   # variables used for parsing...

last_note = 0
last_real_note = 0
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
# int write_history                 # write history and notes ? 
help_me = 0   # need help ?
select_all = False    # select all tunes?
# int epsf                          # for EPSF postscript output 
# int choose_outname                # 1 names outfile w. title/fnam 
# int break_continues               # ignore continuations ? 
# int search_field0                 # default search field 
# int pretty                        # for pretty but sprawling layout 
# int bars_per_line                 # bars for auto linebreaking 
# int continue_lines                # flag to continue all lines 
# int landscape                     # flag for landscape output 
# int barnums                       # interval for bar numbers 
make_index = False   # write index file
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
number_input_files = 0   # number of input file names
# FILE *fin                       # for input file 
#
# char outf[STRLFILE]             # output file name 
# char outfnam[STRLFILE]          # internal file name for open/close 
# char styf[STRLFILE]             # layout style file name 
# char styd[STRLFILE]             # layout style directory 
# char infostr[STRLFILE]          # title string in PS file 
#
# int  file_open                  # for output file 
# int  file_initialized           # for output file 
# FILE *fout,*findex              # for output file 
# int nepsf                       # counter for epsf output files 
#
# char sel_str[MAXINF][STRLFILE]  # list of selector strings 
# int  s_field[MAXINF]            # type of selection for each file 
# int  psel[MAXINF]               # pointers from files to selectors 
#
# int temp_switch


def bskip(h):
    """
    translate down by h points in output buffer

    :param h:
    :return:
    """
    global bposy

    if (h*h>0.0001):
        fp.write("0 %.2f T\n", -h)
        bposy = bposy - h
