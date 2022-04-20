

VERSION = "1.8"   # version
REVISION = "11"   # revison
VDATE = "Apr 26 2011"   # version date
VERBOSE0 = 2   # default verbosity

OUTPUTFILE = "Out.ps"   # standard output file
INDEXFILE: str = "Ind.ps"   # output file for index
PS_LEVEL = 2   # PS laguage level: must be 1 or 2
DEFAULT_FDIR = ""   # default directory to search for format files

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
MAXSYMST = 11   # max music in start piece
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

G_FILL = 'fill'   # modes for glue
G_SHRINK = 'shrink'
G_SPACE = 'space'
G_STRETCH = 'stretch'

S_TITLE = 1   # where to do pattern matching
S_RHYTHM = 2
S_COMPOSER = 3
S_SOURCE = 4

TEXT_H = 1   # type of a text line
TEXT_W = 2
TEXT_Z = 3
TEXT_N = 4
TEXT_D = 5


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

STAFFHEIGHT = 24   # height of music staves in pt

# 
# Important: tablature clef numbers must be >= 50 
# because values < 50 are reserved for music (see abctab2ps.h)

FRENCHTAB = 50   # types of tablature "clefs"
SPANISHTAB = 51
ITALIANTAB = 52
ITALIAN7TAB = 53
SPANISH5TAB = 54
SPANISH4TAB = 55
FRENCH5TAB = 56
FRENCH4TAB = 57
ITALIAN5TAB = 58
ITALIAN4TAB = 59
ITALIAN8TAB = 60
GERMANTAB = 61

# 
# Important: tablature deco numbers should be >= 50 
# because values < 50 are used for music (see abctab2ps.h)

D_INDEX = 50   # codes for decoration
D_MEDIUS = 51
D_ANNULARIUS = 52
D_POLLIX = 53
D_TABACC = 54
D_TABX = 55
D_TABU = 56
D_TABV = 57
D_TABTRILL = 58
D_TABSTAR = 59
D_TABCROSS = 60
D_TABOLINE = 61
D_STRUMUP = 62
D_STRUMDOWN = 63

NETTO = 0
BRUTTO = 1
ALMOSTBRUTTO = 2

TABFONTDIRS = "/usr/share/abctab2ps;/usr/local/share/abctab2ps;fonts"

RHSIMPLE = 1   # possible rhythm styles
RHMODERN = 2
RHDIAMOND = 3
RHNONE = 4
RHGRID = 5
RHMODERNBEAMS = 6

BRUMMER_ABC = 1   # possible styles for Brummer in germantab
BRUMMER_1AB = 2
BRUMMER_123 = 3
