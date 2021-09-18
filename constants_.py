


# -------------- general macros -------------

VERSION = "1.8"   # version 
REVISION = "11"   # revison 
VDATE = "Apr 26 2011"   # version date 
VERBOSE0 = 2   # default verbosity 
DEBUG_LV = 0   # debug output level 
OUTPUTFILE = "Out.ps"   # standard output file 
INDEXFILE = "Ind.ps"   # output file for index 
PS_LEVEL = 2   # PS laguage level: must be 1 or 2

TABFONTDIRS = "/usr/share/abctab2ps;/usr/local/share/abctab2ps;fonts"

# default directory to search for format files 
DEFAULT_FDIR = ""

# ----- macros controlling music typesetting ----- 
BASEWIDTH = 0.8   # width for lines drawn within music 
SLURWIDTH = 0.8   # width for lines for slurs 
STEM_YOFF = 1.0   # offset stem from note center 
STEM_XOFF = 3.5
STEM = 20   # standard stem length 
STEM_MIN = 16   # min stem length under beams 
STEM_MIN2 = 12   # ... for notes with two beams 
STEM_MIN3 = 10   # ... for notes with three beams 
STEM_MIN4 = 10   # ... for notes with four beams 
STEM_CH = 16   # standard stem length for chord 
STEM_CH_MIN = 12   # min stem length for chords under beams 
STEM_CH_MIN2 = 8   # ... for notes with two beams 
STEM_CH_MIN3 = 7   # ... for notes with three beams 
STEM_CH_MIN4 = 7   # ... for notes with four beams 
BEAM_DEPTH = 2.6   # width of a beam stroke 
BEAM_OFFSET = 0.25   # pos of flat beam relative to staff line 
BEAM_SHIFT = 5.3   # shift of second and third beams 
#  To align the 4th beam as the 1st: shift=6-(depth-2*offset)/3  
BEAM_FLATFAC = 0.6   # factor to decrease slope of long beams 
BEAM_THRESH = 0.06   # flat beam if slope below this threshold 
BEAM_SLOPE = 0.5   # max slope of a beam 
BEAM_STUB = 6.0   # length of stub for flag under beam  
SLUR_SLOPE = 1.0   # max slope of a slur 
DOTSHIFT = 5   # shift dot when up flag on note 
GSTEM = 10.0   # grace note stem length 
GSTEM_XOFF = 2.0   # x offset for grace note stem 
GSPACE0 = 10.0   # space from grace note to big note 
GSPACE = 7.0   # space between grace notes 
WIDTH_MIN = 1.0   # minimal left,right width for xp list 
RANFAC = 0.05   # max random shift = RANFAC * spacing 
RANCUT = 1.50   # cutoff for random shift 
BNUMHT = 32.0   # height for bar numbers 

BETA_C = 0.1   # max expansion for flag -c 
ALFA_X = 1.0   # max compression before complaining 
BETA_X = 1.2   # max expansion before complaining 

VOCPRE = 0.4   # portion of vocals word before note 
GCHPRE = 0.4   # portion of guitar chord before note 

DEFVOICE = "1"   # default name for first v


# ----- macros for program internals ----- 

CM = 28.35   # factor to transform cm to pt 
PT = 1.00   # factor to transform pt to pt 
IN = 72.00   # factor to transform inch to pt 

STRLINFO = 301   # string length in info fields 
STRLFILE = 101   # string length for file names and selection patterns 
MAXSYMST = 11   # max symbols in start piece 
MAXHD = 10   # max heads on one stem 
NTEXT = 100   # max history lines for output 
MAXINF = 100   # max number of input files 
BUFFSZ = 50000   # size of output buffer 
BUFFSZ1 = 3000   # buffer reserved for one staff 
BUFFLN = 100   # max number of lines in output buffer 
NWPOOL = 4000   # char pool for vocals 
NWLINE = 16   # max number of vocal lines per staff 
MAXGCHLINES = 8   # max number of lines in guitar chords 
MAXGRACE = 30   # max number of grace notes 

BASE = 192   # base for durations    
LONGA = 768   # quadruple note (longa) 
BREVIS = 384   # double note (brevis) 
WHOLE = 192   # whole note 
HALF = 96   # half note 
QUARTER = 48   # quarter note 
EIGHTH = 24   # 1/8 note 
SIXTEENTH = 12   # 1/16 note 
THIRTYSECOND = 6   # 1/32 note 
SIXTYFOURTH = 3   # 1/64 note 

COMMENT = 1   # types of lines scanned 
MUSIC = 2   
TO_BE_CONTINUED = 3    
E_O_F = 4   
INFO = 5
TITLE = 6
METER = 7
PARTS = 8
KEY = 9
XREF = 10
DLEN = 11
HISTORY = 12
BLANK = 13
WORDS = 14
MWORDS = 15
PSCOMMENT = 16
TEMPO = 17
VOICE = 18
CMDLINE = 19

INVISIBLE = 1   # valid symbol types 
NOTE = 2         
REST = 3         
BAR = 4
CLEF = 5 
TIMESIG = 6 
KEYSIG = 7 
GCHORD = 8 
BREST = 9          
DECO = 10          

SPACE = 101   # additional parsable things 
E_O_L = 102
ESCSEQ = 103
CONTINUE = 104
NEWLINE = 105
DUMMY = 106


B_SNGL = 1   # codes for different types of bars 
B_DBL = 2   # ||   thin double bar 
B_LREP = 3   # |:   left repeat bar 
B_RREP = 4   # :|   right repeat bar 
B_DREP = 5   # ::   double repeat bar 
B_FAT1 = 6   # [|   thick at section start 
B_FAT2 = 7   # |]   thick at section end  
B_INVIS = 8   # invisible; for endings without bars 

A_SH = 1   # codes for accidentals 
A_NT = 2
A_FT = 3
A_DS = 4
A_DF = 5


# 
# Important: music deco numbers should be < 50 
# because values >= 50 are used for tablature (see tab.h)
 
D_GRACE = 1   # codes for decoration 
D_STACC = 2           
D_SLIDE = 3
D_TENUTO = 4           
D_HOLD = 5           
D_IHOLD = 6   # not yet used            
D_UPBOW = 7           
D_DOWNBOW = 8           
D_TRILL = 9           
D_HAT = 10           
D_ATT = 11           
D_SEGNO = 12           
D_CODA = 13           
D_PRALLER = 14
D_MORDENT = 15
D_TURN = 16
D_PLUS = 17
D_CROSS = 18
D_ROLL = 19           
D_DYN_PP = 20
D_DYN_P = 21
D_DYN_MP = 22
D_DYN_MF = 23
D_DYN_F = 24
D_DYN_FF = 25
D_DYN_SF = 26
D_DYN_SFZ = 27
D_BREATH = 28
D_WEDGE = 29


H_FULL = 1   # types of heads 
H_EMPTY = 2
H_OVAL = 3

# 
# Important: music clef numbers must be < 50 
# because values >= 50 are reserved for tablature (see tab.h)
 
TREBLE = 1   # types of clefs 
TREBLE8 = 2
BASS = 3
ALTO = 4
TENOR = 5
SOPRANO = 6
MEZZOSOPRANO = 7
BARITONE = 8
VARBARITONE = 9
SUBBASS = 10
FRENCHVIOLIN = 11
TREBLE8UP = 12
G_FILL = 1   # modes for glue 
G_SHRINK = 2 
G_SPACE = 3 
G_STRETCH = 4

S_TITLE = 1   # where to do pattern matching 
S_RHYTHM = 2
S_COMPOSER = 3
S_SOURCE = 4

TEXT_H = 1   # type of a text line 
TEXT_W = 2
TEXT_Z = 3
TEXT_N = 4
TEXT_D = 5

DO_INDEX = 1   # what program does 
DO_OUTPUT = 2

SWFAC = 0.50   # factor to estimate width of string 

DB_SW = 0   # debug switch 

MAXFORMATS = 10   # max number of defined page formats 
STRLFMT = 81   # string length in FORMAT struct 


MAXNTEXT = 400   # for text output 
MAXWLEN = 51
ALIGN = 1
RAGGED = 2
OBEYLINES = 3
OBEYCENTER = 4
OBEYRIGHT = 5
SKIP = 6

E_CLOSED = 1
E_OPEN = 2 


# ----- global variables ------- 

db = 0   # debug control 

maxSyms = 0
maxVc = 0  # for malloc 
allocSyms = 0
allocVc = 0

NCOMP = 5   # max number of composer lines 


class ISTRUCT:   # information fields
    def __init__(self):
        self.area = ''
        self.book = ''
        self.comp = list()
        # ncomp;
        self.disc = ''
        self.eskip = ''
        self.file = ''
        self.group = ''
        self.hist = ''
        self.info = ''
        self.key = ''
        self.len = ''
        self.meter = ''
        self.notes = ''
        self.orig = ''
        self.rhyth = ''
        self.src = ''
        self.title = list()
        self.parts = ''
        self.xref = ''
        self.trans = ''
        self.tempo = ''


info = ISTRUCT()
default_info = ISTRUCT()


class Grace:   # describes grace notes
    def __init__(self):
        self.n = 0   # number of grace notes
        self.length = 0   # note length
        # when zero (default), treated as accacciatura
        self.p = list()   # pitches
        self.a = list()   # accidentals


class Deco:   # describes decorations
    def __init__(self):
        self.n = 0   # number of decorations
        self.top = 0.0   # max height needed
        self.t = list()   # type of deco  (30)
        self.clear()

    def clear(self):
        self.n = 0
        self.top = 0.0
        self.t = list()

    def add(self, dtype):
        if self.n < 30:
            self.t.append(dtype)
            self.n += 1


# single guitar chord and list of guitar chords on a single note 
class Gchord:
    def __init__(self):
        self.text = ''   # gchord text
        self.x = 0.0


GchordList = list()   # list of Gchords


class SYMBOL:   # struct for a drawable symbol
    def __init__(self):
        self.type = 0   # type of symbol
        self.pits = list()   # pitches for notes
        self.lens = list()   # note lengths as multiple of BASE
        self.accs = list()   # code for accidentals
        self.sl1 = list()   # which slur start on this head
        self.sl2 = list()   # which slur ends on this head
        self.ti1 = list()   # flag to start tie here
        self.ti2 = list()   # flag to end tie here
        self.ten1 = list()   # flag to start tenuto here (only tab)
        self.ten2 = list()   # flag to end tenuto here (only tab)
        self.lig1 = 0   # ligatura starts here
        self.lig2 = 0   # ligatura ends here
        self.shhd = list()   # floats horizontal shift for heads
        self.shac = list()   # floats horizontal shift for
        # accidentals
        self.npitch = 0   # number of note heads
        self.len = 0   # basic note length
        self.fullmes = 0   # flag for full-measure rests
        self.word_st = 0   # 1 if word starts here
        self.word_end = 0   # 1 if word ends here
        self.slur_st = 0   # how many slurs starts here
        self.slur_end = 0   # how many slurs ends here
        self.ten_st = 0   # how many tenuto strokes start (only tab)
        self.ten_end = 0   # how many tenuto strokes end (only tab)
        self.yadd = 0   # shift for treble/bass etc clefs
        self.x = 0.0   # position
        self.y = 0.0   # position
        self.ymn = 0   # min,mav,avg note head height
        self.ymx = 0   # min,mav,avg note head height
        self.yav = 0   # min,mav,avg note head height
        self.yhi = 0.0   # bounds for this object
        self.ylo = 0.0   # bounds for this object
        self.xmn = 0.0   # min,max h-pos of a head rel to top
        self.xmx = 0.0   # min,max h-pos of a head rel to top
        self.stem = 0   # 0,1,-1 for no stem, up, down
        self.flags = 0   # number of flags or bars
        self.dots = 0   # number of dots
        self.head = 0   # type of head
        self.eoln = 0   # flag for last symbol in line
        self.grcpit = 0   # pitch to which grace notes apply
        self.gr = Grace()   # grace notes
        self.dc = Deco()   # decoration symbols
        self.xs = 0.0   # position of stem end
        self.ys = 0.0   # position of stem end
        self.u = 0   # auxillary information
        self.v = 0   # auxillary information
        self.w = 0   # auxillary information
        self.q = 0   # auxillary information
        self.invis = 0   # mark note as invisible
        self.wl = 0.0   # left,right min width
        self.wr = 0.0   # left,right min width
        self.pl = 0.0   # left,right preferred width
        self.pr = 0.0   # left,right preferred width
        self.xl = 0.0   # left,right expanded width
        self.xr = 0.0   # left,right expanded width
        self.p_plet = 0   # data for n-plets
        self.q_plet = 0   # data for n-plets
        self.r_plet = 0   # data for n-plets
        self.gchy = 0.0   # height of guitar chord
        self.text = ''   # for guitar chords (no longer) etc.
        self.GchordList = list()   # gchords; guitar chords above symbol
        # number of vocal lines (only stored in first symbol per line)
        self.wlines = 0
        self.wordp = ''   # pointers to wpool for vocals
        self.p = 0   # pointer to entry in posit table
        self.time = 0.0   # time for symbol start
        self.tabdeco = list()   # tablature decorations inside chord


lvoiceid = ''   # string from last V: line
nvoice = 0   # number of voices defd, nonempty
mvoice = 0   # number of voices defd, nonempty
ivc = 0   # current v
ivc0 = 0   # top nonempty v


class XPOS:   # struct for a horizontal position
    def __init__(self):
        self.type = 0   # type of symbols here
        self.next = 0   # pointers for linked list
        self.prec = 0   # pointers for linked list
        self.eoln = 0   # flag for line break
        self.p = 0   # pointers to associated syms
        self.time = 0.0   # start time, duration
        self.dur = 0.0   # start time, duration
        self.wl = 0.0   # right and left widths
        self.wr = 0.0   # right and left widths
        self.space = 0.0  # glue before this position
        self.shrink = 0.0  # glue before this position
        self.stretch = 0.0  # glue before this position
        self.tfac = 0.0   # factor to tune spacings
        self.x = 0.0   # final horizontal position


ixpfree = 0   # first free element in xp array


class METERSTR:   # data to specify the meter
    def __init__(self):
        self.meter1 = 0   # numerator, denominator
        self.meter2 = 0   # numerator, denominator
        self.mflag = 0   # mflag: 1=C, 2=C|, 3=numerator only, otherwise 0
        self.top = ''   # limit 31
        self.dlen = 0
        self.display = 0   # 0 for M:none, 1 for real meter, 2 for differing
        # display
        # here follow the paramaters for a differing display value
        # (these are only set, when display == 2)
        self.dismeter1 = 0
        self.dismeter2 = 0
        self.dismflag = 0
        self.distop = ''   # limit 31


default_meter = METERSTR()


class KEYSTR:   # data to specify the key
    def __init__(self):
        self.ktype = 0
        self.sf = 0
        self.add_pitch = 0
        self.root_acc = 0
        self.root = 0
        self.add_transp = 0
        self.add_acc = list()   # int, limit 7


default_key = KEYSTR()
  

class VCESPEC:   # struct to characterize a v
    def __init__(self):
        self.id = ''   # identifier string, eg. a number, 33
        self.name = ''   # full name of this v; 81
        self.sname = ''   # short name; 81
        self.meter = METERSTR()   # meter
        self.meter0 = METERSTR()   # meter
        self.meter1 = METERSTR()   # meter
        self.key = KEYSTR()   # keysig
        self.key0 = KEYSTR()   # keysig
        self.key1 = KEYSTR()   # keysig
        self.stems = 0   # +1 or -1 to force stem direction
        self.staves = 0   # for deco over several voices
        self.brace = 0   # for deco over several voices
        self.bracket = 0   # for deco over several voices
        self.do_gch = 0   # 1 to output gchords for this v
        self.sep = 0.0   # for space to next v below
        self.nsym = 0   # number of symbols
        self.draw = 0   # flag if want to draw this v
        self.select = 0   # flag if selected for output
        self.insert_btype = 0  # to split bars over linebreaks
        self.insert_num = 0  # to split bars over linebreaks
        self.insert_bnum = 0   # same for bar number
        self.insert_space = 0.0   # space to insert after init syms
        self.end_slur = 0   # for a-b slurs
        self.insert_text = ''   # string over inserted barline; 81
        self.timeinit = 0.0   # carryover time between parts


# things to alloc:
sym = SYMBOL()   # symbol list
symv = list()   # symbols for voices
xp = XPOS()   # shared horizontal positions
voice = VCESPEC   # characteristics of a v
sym_st = SYMBOL()   # symbols a staff start
nsym_st = 0


halftones = 0   # number of halftones to transpose by

# style parameters:
# mapping fct
f0p = 0.0
f5p = 0.0   # mapping fct
f1p = 0.0   # mapping fct 
f0x = 0.0   # mapping fct
f5x = 0.0
f1x = 0.0   # mapping fct
# note-note spacing
lnnp = 0.0
bnnp = 0.0
fnnp = 0.0
lnnx = 0.0
bnnx = 0.0
fnnx = 0.0
# bar-note spacing
lbnp = 0.0
bbnp = 0.0
rbnp = 0.0
lbnx = 0.0
bbnx = 0.0
rbnx = 0.0
# note-bar spacing
lnbp = 0.0
bnbp = 0.0
rnbp = 0.0
lnbx = 0.0
bnbx = 0.0
rnbx = 0.0

wpool = ''   # pool for vocal strings, NWPOOL
nwpool = 0   # globals to handle wpool
nwline = 0   # globals to handle wpool

zsym = SYMBOL()   # symbol containing zeros


class BEAM:   # packages info about one beam 
    def __init__(self):
        self.i1 = 0
        self.i2 = 0            
        self.a = 0.0
        self.b = 0.0
        self.x = 0.0
        self.y = 0.0
        self.t = 0.0
        self.stem = 0




fontnames = list()
nfontnames = 0

words_of_text = list()   # for output of text StringVector 

vcselstr = ''  # string for v selection
mbf = ''   # mini-buffer for one line 
buf = ''   # output buffer.. should hold one tune 
nbuf = 0   # number of bytes buffered 
bposy = 0.0   # current position in buffered data 
ln_num = 0   # number of lines in buffer 
ln_pos = list()   # vertical positions of buffered lines float
ln_buf = list()   # buffer location of buffered lines int 
use_buffer = False   # 1 if lines are being accumulated 

text = list()  # pool for history, words, etc. lines char
text_type = list()   # type of each text line int NTEXT
ntext = 0   # number of text lines 
page_init = ''   # initialization string after page break 
do_output = False   # control whether to do index or output
escseq = ''   # escape sequence string 
linenum = 0   # current line number in input file 
tunenum = 0   # number of current tune 
tnum1 = 0
tnum2 = 0
numtitle = 0   # how many titles were read 
mline = 0   # number music lines in current tune 
nsym = 0   # number of symbols in line 
nsym0 = 0   # nsym at start of parsing a line 
pagenum = 0   # current page in output file 
writenum = 0   # calls to write_buffer for each one tune 
xrefnum = 0   # xref number of current tune 
do_meter = 0 
do_indent = 0   # how to start next block 

index_pagenum = 0   # for index file 
index_posx = 0.0
index_posy = 0.0
index_initialized = 0

prep_gchlst = list()   # guitar chords for preparsing GchordList 
prep_deco = list()   # decorations for preparsing Deco
bagpipe = False   # switch for HP mode 
within_tune = False
within_block = False   # where we are in the file 
do_this_tune = False   # are we typesetting the current one ? 
posx = 0.0
posy = 0.0   # overall scale, position on page 
barinit = False   # carryover bar number between parts 

p = 0
p0 = 0   # global pointers for parsing music line 

word = False
slur = False   # variables used for parsing... 
last_note = False
last_real_note = False
pplet = 0
qplet = 0
rplet = 0
carryover = False   # for interpreting > and < chars 
ntinext = 0
tinext = list()   # for chord ties MAXHD


class ENDINGS:   # where to draw endings 
    def __init__(self):
        self.a = 0.0
        self.b = 0.0   # start and end position 
        self.i = 0
        self.bi = 0   # symbol index of start/end 
        # position 
        self.num = 0   # number of the ending 
        self.type = 0   # shape: open or closed at right 


ending = list()   # ENDINGS
num_ending = 0   # number of endings to draw 
mes1 = 0
mes2 = 0   # to count measures in an ending 

slur1 = list()
slur2 = list()   # needed for drawing slurs 
overfull = False   # flag if staff overfull 
do_words = False   # flag if staff has words under it 

vb = False
verbose = False   # verbosity, global and within tune 
in_page = False

# switches modified by flags: 
gmode = False   # switch for glue treatment 
include_xrefs = False   # to include xref numbers in title 
one_per_page = False   # new page for each tune ? 
pagenumbers = False   # write page numbers ? 
write_history = False   # write history and notes ? 
help_me = False   # need help ? 
select_all = False   # select all tunes ? 
epsf = False   # for EPSF postscript output 
choose_outname = False   # 1 names outfile w. title/fnam 
break_continues = False   # ignore continuations ? 
search_field0 = False   # default search field 
pretty = False   # for pretty but sprawling layout 
bars_per_line = False   # bars for auto linebreaking 
continue_lines = False   # flag to continue all lines 
landscape = False   # flag for landscape output 
barnums = False   # interval for bar numbers 
make_index = False   # write index file
notab = False   # do not process tablature 
transposegchords = False   # transpose gchords 
alfa_c = 0.0   # max compression allowed 
scalefac = 0.0   # scale factor for symbol size 
lmargin = 0.0   # left margin 
swidth = 0.0   # staff width 
staffsep = 0.0
dstaffsep = 0.0   # staff separation 
strict1 = 0.0
strict2 = 0.0   # 1stave, mstave strictness 
transpose = list()   # target key for transposition 
# paper = format.Papersize()   # paper size
noauthor = False   # suppress PS author tag (%%For) 

alfa_last = 0.0
beta_last = 0.0   # for last short short line.. 

in_file = list()   # list of input file names char
number_input_files = 0   # number of input file names 
fin = ''   # for input file 

outf = ''   # output file name 
outfnam = ''   # internal file name for open/close 
styf = ''   # layout style file name 
styd = ''   # layout style directory 
infostr = ''   # title string in PS file 

file_open = False   # for output file 
file_initialized = False   # for output file 
fout = ''
findex = ''   # for output file 
nepsf = 0   # counter for epsf output files 

sel_str = list()   # list of selector strings 
s_field = list()   # type of selection for each file 
psel = list()   # pointers from files to selectors 

temp_switch = False
