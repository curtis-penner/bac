bposy = 0.0   # current position in buffered data
posx = 0.0
posy = 0.0


class Grace(object):   # describes grace notes
    def __init__(self):
        self.n = 0   # number of grace notes
        self.len = 0   # note length when zero(default), treated as accacciatura
        self.p = list()   # MAXGRACE pitches
        self.a = list()   # MAXGRACE accidentals


class Deco(object):   # describes decorations
    def __init__(self):
        self.n = 0   # number of decorations
        self.top = 0.0   # max height needed
        self.t = list()   # type of deco 30

    def clear(self):
        self.n = 0
        self.top = 0.0
        self.t = list()

    def add(self, dtype):
        if len(self.t) < 30:
            self.t.append(dtype)


class Gchord(object):
    """
    single guitar chord and list of guitar chords on a single note
    """
    def __init__(self):
        self.text = ''
        self.x = 0.0


GchordList = list()

prep_gch_list = GchordList   # guitar chords for preparsing
prep_deco = Deco()   # decorations for preparsing

ixpfree = 0   # first free element in xp array

# things to alloc:
sym = Symbol()   # symbol list
symv = Symbol()   # music for voices
xp = XPos()   # shared horizontal positions

sym_st = Symbol()   # music a staff start
nsym_st = 0


class Beam(object):   # packages info about one beam
    def __init__(self):
        self.i1 = 0
        self.i2 = 0
        self.a = 0.0
        self.b = 0.0
        self.x = 0.0
        self.y = 0.0
        self.t = 0.0
        self.stem = 0


class Endings(object):   # where to draw endings
    def __init__(self):
        self.a = 0.0
        self.b = 0.0
        self.ai = 0
        self.bi = 0
        self.num = 0
        self.type = 0


class Symbol(object):   # struct for a drawable symbol
    def __init(self):
        self.type = 0   # type of symbol
        self.pits = list()   # pitches for notes
        self.lens = list()   # note lengths as multiple of BASE
        self.accs = list()   # code for accidentals
        self.sl1 = list()   # which slur start on this head
        self.sl2 = list()   # which slur ends on this head
        self.ti1 = list()   # flag to start tie here
        self.ti2 = list()   # flag to end tie here
        self.ten1 = list()   # flag to start tenuto here(only tab)
        self.ten2 = list()   # flag to end tenuto here(only tab)
        self.lig1 = 0   # ligatura starts here
        self.lig2 = 0   # ligatura ends here
        self.shhd = list()   # horizontal shift for heads
        self.shac = list()   # horizontal shift for accidentals
        self.npitch = 0   # number of note heads
        self.len = 0   # basic note length
        self.fullmes = 0   # flag for full-measure rests
        self.word_st = 0   # 1 if word starts here
        self.word_end = 0   # 1 if word ends here
        self.slur_st = 0   # how many slurs starts here
        self.slur_end = 0   # how many slurs ends here
        self.ten_st = 0   # how many tenuto strokes start(only tab)
        self.ten_end = 0   # how many tenuto strokes end(only tab)
        self.yadd = 0   # shift for treble/bass etc clefs
        self.x = 0
        self.y = 0   # position
        self.ymn = 0
        self.ymx = 0
        self.yav = 0   # min,mav,avg note head height
        self.ylo = 0
        self.yhi = 0   # bounds for this object
        self.xmn = 0
        self.xmx = 0   # min,max h-pos of a head rel to top
        self.stem = 0   # 0,1,-1 for no stem, up, down
        self.flags = 0   # number of flags or bars
        self.dots = 0   # number of dots
        self.head = 0   # type of head
        self.eoln = 0   # flag for last symbol in line
        self.grcpit = 0   # pitch to which grace notes apply
        self.gr = Grace()   # grace notes
        self.dc = Deco()   # decoration music
        self.xs = 0
        self.ys = 0   # position of stem end
        self.u = 0
        self.v = 0
        self.w = 0
        self.t = 0
        self.q = 0   # auxillary information
        self.invis = 0   # mark note as invisible
        self.wl = 0
        self.wr = 0   # left,right min width
        self.pl = 0
        self.pr = 0  # left,right preferred width
        self.xl = 0
        self.xr = 0   # left,right expanded width
        self.p_plet = 0
        self.q_plet = 0
        self.r_plet = 0   # data for n-plets
        self.gchy = 0   # height of guitar chord
        self.text = ''   # for guitar chords(no longer) etc.
        self.gchords = GchordList   # guitar chords above symbol
        # number of vocal lines(only stored in first symbol per line)
        self.wlines = 0   
        self.wordp = ''   # pointers to wpool for vocals
        self.p = 0   # pointer to entry in posit table
        self.time = 0   # time for symbol start
        self.tabdeco = list()   # tablature decorations inside chord


class XPos(object):       # struct for a horizontal position
    def __init__(self):
        self.type = 0   # type of music here
        self.next = 0   # pointers for linked list
        self.prec = 0
        self.elon = 0   # flag for line break
        self.p = None               # pointers to associated syms
        self.time = 0.0
        self.dur = 0.0              # start time, duration
        self.wl = 0.0
        self.wr = 0.0   # right and left widths
        self.space = 0.0
        self.shrink = 0.0
        self.stretch = 0.0   # glue before this position
        self.tfac = 0.0   # factor to tune spacings
        self.x = 0.0   # final horizontal position


