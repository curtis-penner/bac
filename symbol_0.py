# Copyright (c) 2019 Curtis Penner

import constants
from key import Key
import log
from util import put
import grace
import gchord
import deco

console = log.console
log = log.log

"""

/* ----- zero_sym: init global zero SYMBOL struct ----- */
void zero_sym (void)
{
  int j;
  zsym.type      = 0;
  for (j=0;j<MAXHD;j++) {
    zsym.pits[j]=zsym.lens[j]=zsym.accs[j]=0;
    zsym.sl1[j]=zsym.sl2[j]=0;
    zsym.ti1[j]=zsym.ti2[j]=0;
    zsym.ten1[j]=zsym.ten2[j]=0;
    zsym.shhd[j]=zsym.shac[j]=0;
  }
  zsym.lig1 = zsym.lig2 = 0;
  zsym.npitch    = 0;
  zsym.len       = 0;
  zsym.fullmes   = 0;
  zsym.word_st   = 0;
  zsym.word_end  = 0;
  zsym.slur_st   = 0;
  zsym.slur_end  = 0;
  zsym.ten_st    = 0;
  zsym.ten_end   = 0;
  zsym.yadd      = 0;
  zsym.x=zsym.y  = 0.0;
  zsym.ymn       = 0;
  zsym.ymx       = 0;
  zsym.yav       = 0;
  zsym.ylo       = 12;
  zsym.yhi       = 12;
  zsym.xmn=zsym.xmx = 0;
  zsym.stem      = 0;
  zsym.flags     = 0;
  zsym.dots      = 0;
  zsym.head      = 0;
  zsym.eoln      = 0;
  zsym.grcpit    = 0;
  zsym.gr.n      = 0;
  zsym.dc.clear();
  zsym.xs        = 0;
  zsym.ys        = 0;
  zsym.u         = 0;
  zsym.v         = 0;
  zsym.w         = 0;
  zsym.t         = 0;
  zsym.q         = 0;
  zsym.invis     = 0;
  zsym.wl=zsym.wr= 0;
  zsym.pl=zsym.pr = 0;
  zsym.xl=zsym.xr = 0;
  zsym.p_plet=zsym.q_plet=zsym.r_plet = 0;
  zsym.gchy      = 0;
  strcpy (zsym.text, "");
  zsym.gchords = NULL;
  zsym.wlines = 0;
  for (j=0;j<NWLINE;j++) zsym.wordp[j] = 0;
  zsym.p         = -1;
  zsym.time=0;
  for (j=0;j<MAXHD;j++) {
    zsym.tabdeco[j]=0;
  }
}
"""

max_syms = 800
XP_START = 0
P_END = max_syms-1


class Symbol:
    """
    init global zero SYMBOL struct
    """
    MAXHD = 10  # max heads on one stem
    NWLINE = 16  # max number of vocal lines per staff

    def __init__(self):
        self.type = 0

        self.pits = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]  # pitch for notes
        self.lens = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.accs = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.sl1 = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.sl2 = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.ti1 = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.ti2 = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.ten1 = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.ten2 = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.shhd = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.shac = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

        self.lig1 = 0
        self.lig2 = 0
        self.npitch = 0  # number of note heads
        self.len = 0
        self.fullmes = 0
        self.word_st = 0  # 1 if word starts here
        self.word_end = 0  # 1 if word ends here
        self.slur_st = 0
        self.slur_end = 0
        self.ten_st = 0
        self.ten_end = 0
        self.yadd = 0
        self.x = 0.0
        self.y = 0.0
        self.ymn = 0  # min h-pos of a head rel to top
        self.ymx = 0  # max h-pos of a head rel to top
        self.yav = 0
        self.ylo = 12
        self.yhi = 12
        self.xmn = 0
        self.xmx = 0
        self.stem = 0
        self.flags = 0
        self.dots = 0  # number of dots
        self.head = 0
        self.eoln = 0
        self.grcpit = 0  # pitch to wheich grace notes apply
        self.gr = grace.Grace()
        self.dc = deco.Deco()
        self.xs = 0
        self.ys = 0
        self.u = 0
        self.v = 0
        self.w = 0
        self.t = 0
        self.q = 0
        self.invis = 0
        self.wl = 0  # left min width
        self.wr = 0  # right min width
        self.pl = 0
        self.pr = 0
        self.xl = 0
        self.xr = 0
        self.p_plet = 0
        self.q_plet = 0
        self.r_plet = 0
        self.gchy = 0
        self.text = ''
        self.gchords = list()  # guitar chords above symbol
        self.wlines = 0
        self.wordp = list()  # limit NWLINE
        self.p = -1
        self.time = 0
        self.tabdeco = list()
        self.tabdeco = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    def parse_sym(self, line):
        """
        parse a symbol and return its type

        :param line:
        :return str:
        """
        new_line = gchord.Gchord.parse_gchord(line)
        if line != new_line:
            line = new_line
            return line
        # if (parse_deco())     return DECO;
        # if (parse_bar())      return BAR;
        # if (parse_space())    return SPACE;
        # if (parse_nl())       return NEWLINE;
        # if ((i=parse_esc())) return i;
        # if ((i=parse_note())) return i;
        #
        # return line

    def symbolic_pitch(self, pit, line):
        if not self.npitch:
            log.warning(f'symbolic_pitch({pit}, {line}')

    def print_syms(self, voice):
        """
        show sym properties set by parser
        This might be best in the Voice class

        Need to convert this to __repr__ or __str__, meaning everything needs
        to be a return.

        :param voice:
        :return int:
        """
        dsym = [' ', '~', '.', 'J', 'M', 'H', 'u', 'v', 'R', 'T', 'K']
        # bsym = ['-', '1', '2', '3', '4', '5', '6', '7', '8', '9']

        console.info("\n---------- Symbol list ----------")
        console.info("word    slur    eol    num    description")

        for i, sym in enumerate(voice.syms):
            local_str = ''
            line = ''
            line += (f' {sym.word_st} {sym.word_end}     '
                     f'{sym.slur_st} {sym.slur_end}     {sym.eoln}')
            line += f'{i:4d}    '
            t = sym.type
            if t == constants.NOTE or t == constants.REST or t == constants.BREST:
                if t == constants.NOTE:
                    line += "NOTE "
                if t == constants.REST:
                    line += "REST "
                if t == constants.BREST:
                    line += "BREST "
                if sym.npitch > 1:
                    line += " ["
                for j in range(sym.npitch):
                    line += " "
                    if sym.accs[j] == Key.A_SH:
                        line += "^"
                    if sym.accs[j] == Key.A_NT:
                        line += "="
                    if sym.accs[j] == Key.A_FT:
                        line += "_"
                    if sym.accs[j] == Key.A_DS:
                        line += "^^"
                    if sym.accs[j] == Key.A_DF:
                        line += "__"
                    # y = 3 * (sym.pits[j] - 18) + sym.yadd
                    local_str = "z"
                    if t == constants.NOTE:
                        self.symbolic_pitch(sym.pits[j], local_str)
                    line += f'{local_str}({sym.lens[j]})'
                if sym.npitch > 1:
                    line += " ]"
                if sym.p_plet:
                    line += ("    (%d:%d:%d" % (sym.p_plet, sym.q_plet,
                                             sym.r_plet))
                if not sym.gchords.empty():
                    line += "    "
                    for gchi in sym.gchords:
                        line += f'"{gchi.text}"'
                if sym.dc.n > 0:
                    line += "    deco "
                    for j in range(sym.dc.n):
                        line += dsym[sym.dc.t[j]]
                if sym.gr.n > 0:
                    line += "    grace "
                    for j in range(sym.gr.n):
                        if j > 0:
                            line += "-"
                        if sym.gr.a[j] == Key.A_SH:
                            line += "^"
                        if sym.gr.a[j] == Key.A_NT:
                            line += "="
                        if sym.gr.a[j] == Key.A_FT:
                            line += "_"
                        self.symbolic_pitch(sym.gr.p[j], local_str)
                        line += local_str
                continue

            elif t == constants.BAR:
                line += "BAR    ======= "
                if sym.u == constants.B_SNGL:
                    line += "single"
                if sym.u == constants.B_DBL:
                    line += "double"
                if sym.u == constants.B_LREP:
                    line += "left repeat"
                if sym.u == constants.B_RREP:
                    line += "right repeat"
                if sym.u == constants.B_DREP:
                    line += "double repeat"
                if sym.u == constants.B_FAT1:
                    line += "thick-thin"
                if sym.u == constants.B_FAT2:
                    line += "thin-thick"
                if sym.u == constants.B_INVIS:
                    line += "invisible"
                if sym.v:
                    line += f', ending {sym.v}'
                if not sym.gchords.empty():
                    line += f', label "{sym.gchords.text}"'
                continue

            elif t == constants.CLEF:
                if sym.u == constants.TREBLE:
                    line += "CLEF    treble"
                if sym.u == constants.TREBLE8:
                    line += "CLEF    treble8"
                if sym.u == constants.TREBLE8UP:
                    line += "CLEF    treble8up"
                if sym.u == constants.BASS:
                    line += "CLEF    bass"
                if sym.u == constants.ALTO:
                    line += "CLEF    alto"
                if sym.u == constants.TENOR:
                    line += "CLEF    tenor"
                if sym.u == constants.SOPRANO:
                    line += "CLEF    soprano"
                if sym.u == constants.MEZZOSOPRANO:
                    line += "CLEF    mezzosoprano"
                if sym.u == constants.BARITONE:
                    line += "CLEF    baritone"
                if sym.u == constants.VARBARITONE:
                    line += "CLEF    varbaritone"
                if sym.u == constants.SUBBASS:
                    line += "CLEF    subbass"
                if sym.u == constants.FRENCHVIOLIN:
                    line += "CLEF    frenchviolin"
                continue

            elif t == constants.TIMESIG:
                line += 'TIMESIG    '
                if sym.w == 1:
                    line += "C"
                elif sym.w == 2:
                    line += "C|"
                else:
                    line += f'{sym.u}/{sym.v}'
                continue

            elif t == constants.KEYSIG:
                line += "KEYSIG     "
                if sym.t == Key.A_SH:
                    line += "sharps "
                if sym.t == Key.A_FT:
                    line += "flats "
                line += f"{sym.u} to {sym.v}"
                if sym.w <= sym.v:
                    line += f', neutrals from {sym.w}'
                continue

            elif t == constants.INVISIBLE:
                line += "INVIS     "
                continue

            else:
                line += "UNKNOWN "

            line += "\n"
            console.info(line)

class Note(Symbol):
    def __init__(self):
        super().__init__()
        self.ymn = 0  # min note head height (used in gracenotes, draw_decorations, draw_note)
        self.ymx = 0  # max note head height (used in gracenotes, draw_decorations, draw_note)
        self.gr = grace.Grace()

    def _draw_basic_note(self, x, w, d, m):
        """
        draw m-th head with accidentals and dots

        :param float x:
        :param float w:
        :param float d:
        :param int m
        """
        # int y,i,yy
        # float dotx,doty,xx,dx,avail,add,fac
        # char historic

        if cfmt.historicstyle:
            historic = 'h'
        else:
            historic = ''

        y = 3 * (self.pits[m] - 18) + self.yadd  # height on staff
        xx = x + self.shhd[m]  # draw head
        put(f"{xx:.1f} {y}")

        if self.lens[0] >= constants.LONGA:
            put(f' longa{historic}')
        elif self.lens[0] >= constants.BREVIS:
            if cfmt.historicstyle:
                put(" brevish")
            elif cfmt.squarebrevis:
                put(" brevis")
            else:
                put(" HDD")
        else:
            if self.head == constants.H_OVAL:
                if cfmt.historicstyle:
                    put(" Hdh")
                else:
                    put(" HD")
            elif self.head == constants.H_EMPTY:
                put(f" Hd{historic}")
            elif self.head == constants.H_FULL:
                put(f" hd{historic}")

        if self.shhd[m]:
            yy = 0
            if y >= 30:
                yy = y
                if yy % 6:
                    yy = yy - 3
            if y <= -6:
                yy = y
                if yy % 6:
                    yy = yy + 3
            if yy:
                put(f" {yy} hl")

        if self.dots:  # add dots
            if y % 6:
                dotx = 8
                doty = 0
            else:
                dotx = 8
                doty = 3
            if self.stem == -1:
                dotx = dotx + self.xmx - self.shhd[m]
            else:
                dotx = dotx + self.xmx - self.shhd[m]
            if self.dots and self.flags and (self.stem == 1) and not y % 6:
                if self.word_st == 1 and self.word_end == 1 and self.npitch == 1:
                    dotx = dotx + constants.DOTSHIFT
            if self.head == constants.H_EMPTY:
                dotx += 1
            if self.head == constants.H_OVAL:
                dotx += 2
            for i in range(self.dots):
                put(f" {dotx:.1f} {doty:.1f} dt")
                dotx += 3.5

        if self.accs[m]:  # add accidentals
            fac = 1.0
            avail = d - w - 3
            add = 0.3 * avail
            fac = 1 + add / self.wl
            if fac < 1:
                fac = 1
            if fac > 1.2:
                fac = 1.2
            dx = fac * self.shac[m]
            if self.accs[m] == constants.A_SH:
                put(f" {dx:.1f} sh", dx)
            if self.accs[m] == constants.A_NT:
                put(f" {dx:.1f} nt", dx)
            if self.accs[m] == constants.A_FT:
                put(f" {dx:.1f} ft", dx)
            if self.accs[m] == constants.A_DS:
                put(f" {dx:.1f} dsh", dx)
            if self.accs[m] == constants.A_DF:
                put(f" {dx:.1f} dft", dx)

    def draw_decorations(self, x):
        """
        This is used in draw_note, draw_bar, and draw_rest .
        This might move to Decoration

        :param float x:
        :return: float this, tp
        """
        # int y,sig,k,deco,m;
        # float yc,xc,y1,top,top1,dx,dy;
        # struct SYMBOL *nextsym;


"""
  top=-1000;
  for (k=s->dc.n-1;k>=0;k--) {                 /*  decos close to head */
    deco=s->dc.t[k];

/*  if ((deco==D_STACC)||(deco==D_TENUTO)) { */
    if (deco==D_STACC) {                           /* dot */
      sig=1; if (s->stem==1) sig=-1;
      y=(int)s->y+6*sig;
      if (y<top+3) y=(int)top+3;
      if (!(y%6) && (y>=0) && (y<=24)) y+=3*sig;
      if (top<y) top=y;
      PUT2(" %.1f %d stc",x, y);
    }

    if (deco==D_SLIDE) {                           /* slide */
      yc=s->ymn;
      xc=5;
      for (m=0;m<s->npitch;m++) {                       
        dx=5-s->shhd[m];
        if (s->head==H_OVAL) dx=dx+2.5; 
        if (s->accs[m]) dx=4-s->shhd[m]+s->shac[m];
        dy=3*(s->pits[m]-18)+s->yadd-yc;
        if ((dy<10) && (dx>xc)) xc=dx; 
      }
      yc=s->ymn;
      PUT2(" %.1f %.1f sld", yc, xc);
    }
  }

  top1=top;
  for (k=s->dc.n-1;k>=0;k--) {       /*  decos further away */
    deco=s->dc.t[k];
    switch (deco)
      {
      case D_TENUTO:                 /* tenuto sign */
        yc=s->ymx+6; 
        if (s->stem==1) yc=s->ys+4;
        if (yc<28) yc=28;
        if (yc<top+3) yc=top+3;
        if (top<yc+2) top=yc+2;
        PUT2(" %.1f %.2f emb", x, yc);
        break;

      case D_GRACE:                  /* gracing,hat,att */
      case D_HAT:
      case D_ATT:
        yc=s->ymx+9;
        if (s->stem==1) yc=s->ys+5;
        if (yc<30) yc=30;
        if (yc<top+4) yc=top+4;
        if (top<yc+2) top=yc+6;
        if      (deco==D_GRACE) PUT2(" %.1f %.2f grm", x, yc);
        else if (deco==D_HAT)   PUT2(" %.1f %.2f hat", x, yc);
        else                    PUT2(" %.1f %.2f att", x, yc);
        break;

      case D_ROLL:                    /* roll sign */
        y=(int)s->y;
        if (s->stem==1) {
          yc=s->y-5;
          if (yc>-2) yc=-2;
          PUT2(" %.1f %.2f cpd", x, yc);
        }
        else {
          yc=s->y+5;
          if (s->dots && (!(y%6))) yc=s->y+6;
          if (yc<26) yc=26;
          if (yc<top+1) yc=top+1;
          if (top<yc+8) top=yc+8;
          PUT2(" %.1f %.2f cpu", x, yc);
        }
        break;

       case D_HOLD:                   /* fermata */
        yc=27;
        if (s->stem==1) 
          y1=s->ys+4; 
        else 
          y1=s->ymx+6;
        if (yc<y1) yc=y1;
        if (yc<top+4) yc=top+4;
        if (top<yc+12) top=yc+12;
        PUT2(" %.1f %.1f hld", x, yc);
        break;

      case D_TRILL:                   /* trill sign */
        yc=30;
        if (s->stem==1) 
          y1=s->ys+5; 
        else 
          y1=s->ymx+7;
        if (yc<y1) yc=y1;
        if (yc<top+1) yc=top+1;
        if (top<yc+13) top=yc+13;
        PUT2(" %.1f %.1f trl", x, yc);
        break;

      case D_UPBOW:                   /* bowing signs */
      case D_DOWNBOW:
        yc=21;
        if (s->stem==1) 
          y1=s->ys+4; 
        else 
          y1=s->ymx+8;
        if (yc<y1) yc=y1;
        if (yc<top+4) yc=top+4;
        if (top<yc+10) top=yc+10;
        if (deco==D_UPBOW)   PUT2(" %.1f %.1f upb", x, yc);
        if (deco==D_DOWNBOW) PUT2(" %.1f %.1f dnb", x, yc);
        break;

      case D_SEGNO:                   /* segno sign */
        yc=27;
        if (s->stem==1) 
          y1=s->ys+4; 
        else 
          y1=s->ymx+6;
        if (yc<y1) yc=y1;
        if (yc<top+4) yc=top+4;
        if (top<yc+23) top=yc+23;
        PUT2(" %.1f %.1f sgno", x, yc);
        break;

      case D_CODA:                    /* coda sign */
        yc=27;
        if (s->stem==1) 
          y1=s->ys+4; 
        else 
          y1=s->ymx+6;
        if (yc<y1) yc=y1;
        if (yc<top+4) yc=top+4;
        if (top<yc+23) top=yc+23;
        PUT2(" %.1f %.1f coda", x, yc);
        break;

      case D_PRALLER:                 /* pralltriller */
        yc=27;
        if (s->stem==1) 
          y1=s->ys+4; 
        else 
          y1=s->ymx+6;
        if (yc<y1) yc=y1;
        if (yc<top+4) yc=top+4;
        if (top<yc+5) top=yc+5;
        PUT2(" %.1f %.1f umrd", x, yc);
        break;

      case D_MORDENT:                 /* mordent */
        yc=27;
        if (s->stem==1) 
          y1=s->ys+4; 
        else 
          y1=s->ymx+6;
        if (yc<y1) yc=y1;
        if (yc<top+4) yc=top+4;
        if (top<yc+5) top=yc+5;
        PUT2(" %.1f %.1f lmrd", x, yc);
        break;

      case D_TURN:                    /* doppelschlag */
        yc=27;
        if (s->stem==1) 
          y1=s->ys+4; 
        else 
          y1=s->ymx+6;
        if (yc<y1) yc=y1;
        if (yc<top+4) yc=top+4;
        if (top<yc+13) top=yc+13;
        PUT2(" %.1f %.1f turn", x, yc);
        break;

      case D_WEDGE:
        yc=27;
        if(s->stem==1)
          y1=s->ys+4;
        else
          y1=s->ymx+6;
        if(yc < y1) yc=y1;
        if(yc<top+4) yc=top+4;
        if(top<yc+13) top=yc+13;
        PUT2(" %.1f %.1f wedge", x ,yc); 
        break;

      case D_PLUS:                    /* plus sign */
        yc=27;
        if (s->stem==1) 
          y1=s->ys+4; 
        else 
          y1=s->ymx+6;
        if (yc<y1) yc=y1;
        if (yc<top+4) yc=top+4;
        if (top<yc+11) top=yc+11;
        PUT2(" %.1f %.1f plus", x, yc);
        break;

      case D_CROSS:                   /* x shaped cross */
        yc=27;
        if (s->stem==1) 
          y1=s->ys+4; 
        else 
          y1=s->ymx+6;
        if (yc<y1) yc=y1;
        if (yc<top+4) yc=top+4;
        if (top<yc+10) top=yc+10;
        PUT2(" %.1f %.1f cross", x, yc);
        break;

      case D_DYN_PP:                  /* dynamic marks */
      case D_DYN_P:
      case D_DYN_MP:
      case D_DYN_FF:
      case D_DYN_F:
      case D_DYN_MF:
      case D_DYN_SF:
      case D_DYN_SFZ:
        yc=27;
        if (s->stem==1) 
          y1=s->ys+4; 
        else 
          y1=s->ymx+6;
        if (yc<y1) yc=y1;
        if (yc<top+4) yc=top+4;
        if (top<yc+16) top=yc+16;
        if (deco==D_DYN_PP)
          PUT2(" (pp) %.1f %.1f dyn", x, yc);
        else if (deco==D_DYN_P)
          PUT2(" (p) %.1f %.1f dyn", x, yc);
        else if (deco==D_DYN_MP)
          PUT2(" (mp) %.1f %.1f dyn", x, yc);
        else if (deco==D_DYN_MF)
          PUT2(" (mf) %.1f %.1f dyn", x, yc);
        else if (deco==D_DYN_F)
          PUT2(" (f) %.1f %.1f dyn", x, yc);
        else if (deco==D_DYN_FF)
          PUT2(" (ff) %.1f %.1f dyn", x, yc);
        else if (deco==D_DYN_SF)
          PUT2(" (sf) %.1f %.1f dyn", x, yc);
        else if (deco==D_DYN_SFZ)
          PUT2(" (sfz) %.1f %.1f dyn", x, yc);
        break;

      case D_BREATH:                  /* breath mark */
        yc=STAFFHEIGHT;
        nextsym=s; nextsym++;
        /* default position: half way next note */
        /* when next symbol bar or shorter note: 2/3 way next note */
        dx = nextsym->x - s->x;
        if ((nextsym->type==BAR) || (nextsym->len < s->len))
          xc = s->x + 0.66*dx;
        else
          xc = s->x + 0.5*dx;
        PUT2(" %.1f %.1f brth", xc, yc);
        break;
      }
  }

  *tp=top;
  return top1;
}


print(self.npitch)
return x, 0.0


def draw_note(self, x, w, d, fl):
    """
    gchy: gchord y position

    :param float x:
    :param float w:
    :param float d:
    :param bool fl:
    :return float, float: top, ghcy
    """
    slen0 = constants.STEM
    gchy = constants.STAFFHEIGHT + cfmt.gchordspace

    self.draw_gracenotes(x, w, d)  # draw grace notes

    if cfmt.historicstyle:
        historic = 'h'
    else:
        historic = ''

    c = 'd'
    cc = 'u'
    if self.stem == 1:
        c = 'u'
        cc = 'd'
    stem_len = self.stem * (self.ys - self.y)

    # for (m=0;m<s->npitch;m++)
    for m in range(self.npitch):
        if m > 0:
            put(" ")
        # this needs to be looked at
        self._draw_basic_note(x, w, d, m)  # draw note heads
        xx = 3 * (self.pits[m] - 18) + self.yadd - self.y
        xx = xx * xx
        if not cfmt.nostems:  # stems can be suppressed
            if xx < 0.01:  # add stem
                if self.stem:
                    put(f' {stem_len:.1f} s{c}{historic}')
                if fl and self.flags > 0:  # add flags
                    put(f' {stem_len:.1f} f{self.flags}{c}{historic}')

            if m > 0 and self.pits[m] == self.pits[m - 1]:  # unions
                if self.stem:
                    put(f' {slen0:.2f} s{cc}{historic}')
                if self.flags > 0:
                    put(f' {slen0:.1f} f{self.flags}{cc}{historic}')

    top, top2 = self.draw_decorations(x)  # add decorations

    y = self.ymn  # lower ledger lines
    if y <= -6:
        for i in range(-6, y, -6):
            put(f' {i} hl')
        if self.len >= constants.BREVIS:
            put("2")
        elif self.head == constants.H_OVAL:
            put("1")

    y = self.ymx  # upper ledger lines
    if y >= 30:
        for i in range(30, y, 6):
            put(f" {i} hl")
        if self.len >= constants.BREVIS:
            put("2")
        elif self.head == constants.H_OVAL:
            put("1")

    if not self.gchords:  # position guitar chord
        yc = gchy
        if yc < y + 8:
            yc = y + 8
        if yc < self.ys + 4:
            yc = self.ys + 4
        if yc < top2:
            yc = top2
        gchy = yc
    put("\n")
    return top, gchy

"""



def is_note(c):
  """
  checks char for valid note symbol

  :param str c:
  :return:
  """
  return c in "CDEFGABcdefgab^=_"


class Note(object):
    def __init__(self, letters):
        self.letters = letters
        if self.letters.startwith('Z') or self.letters.startwith('z'):
            Rest(self.letters)
        else:
            print(f'Note: {self.letters}')


class Rest(object):
    def __init__(self, rests):
        self.rests = rests
        print(f'Rest: {self.rests}')


if __name__ == '__main__':
    m = '|:A2 AG ABc|~E2 DA DEG|A2 ~A2 Bcd|~e2 BA B'
    line_music = Symbol(m)
    line_music.parse()

"""

/* ----- init_parse_params: initialize variables for parsing --- */
void init_parse_params (void)
{
  int i;

  slur=0;
  nwpool=nwline=0;
  ntinext=0;

  /* for continuation after output: reset nsym, switch to first voice */
  for (i=0;i<nvoice;i++) {
    voice[i].nsym=0;
    /* this would suppress tie/repeat carryover from previous page: */
    /* voice[i].insert_btype=0; */
    /* voice[i].end_slur=0; */
  }

  ivc=0;

  word=0;
  carryover=0;
  last_note=last_real_note=-1;
  pplet=qplet=rplet=0;
  num_ending=0;
  mes1=mes2=0;
  prep_gchlst.clear();
  prep_deco.clear();
}


/* ----- numeric_pitch ------ */
/* adapted from abc2mtex by Chris Walshaw */
int numeric_pitch(char note)
{

    if (note=='z')
        return 14;
    if (note >= 'C' && note <= 'G')
        return(note-'C'+16+voice[ivc].key.add_pitch);
    else if (note >= 'A' && note <= 'B')
        return(note-'A'+21+voice[ivc].key.add_pitch);
    else if (note >= 'c' && note <= 'g')
        return(note-'c'+23+voice[ivc].key.add_pitch);
    else if (note >= 'a' && note <= 'b')
        return(note-'a'+28+voice[ivc].key.add_pitch);
    printf ("numeric_pitch: cannot identify <%c>\n", note);
    return(0);
}

/* ----- symbolic_pitch: translate numeric pitch back to symbol ------ */
int symbolic_pitch(int pit, char *str)
{
    int  p,r,s;
    char ltab1[7] = {'C','D','E','F','G','A','B'};
    char ltab2[7] = {'c','d','e','f','g','a','b'};

    p=pit-16;
    r=(p+700)%7;
    s=(p-r)/7;

    if (p<7) {
        sprintf (str,"%c,,,,,",ltab1[r]);
        str[1-s]='\0';
    }
    else {
        sprintf (str,"%c'''''",ltab2[r]);
        str[s]='\0';
    }
    return 0;
}


/* ----- parse_bar: parse for some kind of bar ---- */
int parse_bar (void)
{
    int k;
    GchordList::iterator ii;

    /* special cases: [1 or [2 without a preceeding bar, [| */
    if (*p=='[') {
        if (strchr("123456789",*(p+1))) {
            k=add_sym (BAR);
            symv[ivc][k].u=B_INVIS;
            symv[ivc][k].v=chartoi(*(p+1));
            p=p+2;
            return 1;
        }
    }

    /* identify valid standard bar types */
    if (*p == '|') {
        p++;
        if (*p == '|') {
            k=add_sym (BAR);
            symv[ivc][k].u=B_DBL;
            p++;
        }
        else if (*p == ':') {
            k=add_sym(BAR);
            symv[ivc][k].u=B_LREP;
            p++;
        }
        else if (*p==']') {                  /* code |] for fat end bar */
            k=add_sym(BAR);
            symv[ivc][k].u=B_FAT2;
            p=p+1;
        }
        else {
            k=add_sym(BAR);
            symv[ivc][k].u=B_SNGL;
        }
    }
    else if (*p == ':') {
        if (*(p+1) == '|') {
            k=add_sym(BAR);
            symv[ivc][k].u=B_RREP;
            p+=2;
        }
        else if (*(p+1) == ':') {
            k=add_sym(BAR);
            symv[ivc][k].u=B_DREP;
            p+=2; }
        else {
            /* ':' is decoration in tablature
             *syntax ("Syntax error parsing bar", p-1);
             */
            return 0;
        }
    }

    else if ((*p=='[') && (*(p+1)=='|') && (*(p+2)==']')) {  /* code [|] invis */
        k=add_sym(BAR);
        symv[ivc][k].u=B_INVIS;
        p=p+3;
    }

    else if ((*p=='[') && (*(p+1)=='|')) {    /* code [| for thick-thin bar */
        k=add_sym(BAR);
        symv[ivc][k].u=B_FAT1;
        p=p+2;
    }

    else return 0;

    /* copy over preparsed stuff (gchords, decos) */
    strcpy(symv[ivc][k].text,"");
    if (!prep_gchlst.empty()) {
        for (ii=prep_gchlst.begin(); ii!=prep_gchlst.end(); ii++) {
            symv[ivc][k].gchords->push_back(*ii);
        }
        prep_gchlst.clear();
    }
    if (prep_deco.n) {
        for (int i=0; i<prep_deco.n; i++) {
            int deco=prep_deco.t[i];
            if ((deco!=D_STACC) && (deco!=D_SLIDE))
                symv[ivc][k].dc.add(deco);
        }
        prep_deco.clear();
    }

    /* see if valid bar is followed by specifier for first or second ending */
    if (strchr("123456789",*p)) {
        symv[ivc][k].v=chartoi(*p); p++;
    } else if ((*p=='[') && (strchr("123456789",*(p+1)))) {
        symv[ivc][k].v=chartoi(*(p+1)); p=p+2;
    } else if ((*p==' ') && (*(p+1)=='[') && (strchr("123456789",*(p+2)))) {
        symv[ivc][k].v=chartoi(*(p+2)); p=p+3;
    }

    return 1;
}

/* ----- parse_space: parse for whitespace ---- */
int parse_space (void)
{
    int rc;

    rc=0;
    while ((*p==' ')||(*p=='\t')) {
        rc=1;
        p++;
    }
    if (db>3) if (rc) printf ("  parsed whitespace\n");
    return rc;
}

/* ----- parse_esc: parse for escape sequence ----- */
int parse_esc (void)
{

    int nseq;
    char *pp;

    if (*p == '\\') {                     /* try for \...\ sequence */
        p++;
        nseq=0;
        while ((*p!='\\') && (*p!=0)) {
            escseq[nseq]=*p;
            nseq++;
            p++;
        }
        if (*p == '\\') {
            p++;
            escseq[nseq]=0;
            if (db>3) printf ("  parsed esc sequence <%s>\n", escseq);
            return ESCSEQ;
        }
        else {
            if (cfmt.breakall) return DUMMY;
            if (db>3) printf ("  parsed esc to EOL.. continuation\n");
        }
        return CONTINUE;
    }

    /* next, try for [..] sequence */
    if ((*p=='[') && (*(p+1)>='A') && (*(p+1)<='Z') && (*(p+2)==':')) {
        pp=p;
        p++;
        nseq=0;
        while ((*p!=']') && (*p!=0)) {
            escseq[nseq]=*p;
            nseq++;
            p++;
        }
        if (*p == ']') {
            p++;
            escseq[nseq]=0;
            if (db>3) printf ("  parsed esc sequence <%s>\n", escseq);
            return ESCSEQ;
        }
        syntax ("Escape sequence [..] not closed", pp);
        return ESCSEQ;
    }
    return 0;
}


/* ----- parse_nl: parse for newline ----- */
int parse_nl (void)
{

    if ((*p == '\\')&&(*(p+1)=='\\')) {
        p+=2;
        return 1;
    }
    else
        return 0;
}

/* ----- parse_gchord: parse guitar chord, add to global prep_gchlst ----- */
int parse_gchord ()
{
    char *q;
    int n=0;
    Gchord gchnew;

    if (*p != '"') return 0;

    q=p;
    p++;
    //n=strlen(gch);
    //if (n > 0) syntax ("Overwrite unused guitar chord", q);

    while ((*p != '"') && (*p != 0)) {
        gchnew.text += *p;
        n++;
        if (n >= 200) {
            syntax ("String for guitar chord too long", q);
            return 1;
        }
        p++;
    }
    if (*p == 0) {
        syntax ("EOL reached while parsing guitar chord", q);
        return 1;
    }
    p++;
    if (db>3) printf("  parse guitar chord <%s>\n", gchnew.text.c_str());
    gch_transpose(&gchnew.text, voice[ivc].key);
    prep_gchlst.push_back(gchnew);

    /*|   gch_transpose (voice[ivc].key); |*/

    return 1;
}


/* ----- parse_deco: parse for decoration, add to global prep_deco ----- */
int parse_deco ()
{
    int deco,n;
    /* mapping abc code to decorations */
    /* for no abbreviation, set abbrev=0; for no !..! set fullname="" */
    struct s_deconame { int index; const char abbrev; const char* fullname; };
    static struct s_deconame deconame[] = {
        {D_GRACE,   '~', "!grace!"},
        {D_STACC,   '.', "!staccato!"},
        {D_SLIDE,   'J', "!slide!"},
        {D_TENUTO,  'N', "!tenuto!"},
        {D_HOLD,    'H', "!fermata!"},
        {D_ROLL,    'R', "!roll!"},
        {D_TRILL,   'T', "!trill!"},
        {D_UPBOW,   'u', "!upbow!"},
        {D_DOWNBOW, 'v', "!downbow!"},
        {D_HAT,     'K', "!sforzando!"},
        {D_ATT,     'k', "!accent!"},
        {D_ATT,     'L', "!emphasis!"}, /*for abc standard 1.7.6 compliance*/
        {D_SEGNO,   'S', "!segno!"},
        {D_CODA,    'O', "!coda!"},
        {D_PRALLER, 'P', "!pralltriller!"},
        {D_PRALLER, 'P', "!uppermordent!"}, /*for abc standard 1.7.6 compliance*/
        {D_MORDENT, 'M', "!mordent!"},
        {D_MORDENT, 'M', "!lowermordent!"}, /*for abc standard 1.7.6 compliance*/
        {D_TURN,     0,  "!turn!"},
        {D_PLUS,     0,  "!plus!"},
        {D_PLUS,     0,  "!+!"}, /*for abc standard 1.7.6 compliance*/
        {D_CROSS,   'X', "!x!"},
        {D_DYN_PP,   0,  "!pp!"},
        {D_DYN_P,    0,  "!p!"},
        {D_DYN_MP,   0,  "!mp!"},
        {D_DYN_MF,   0,  "!mf!"},
        {D_DYN_F,    0,  "!f!"},
        {D_DYN_FF,   0,  "!ff!"},
        {D_DYN_SF,   0,  "!sf!"},
        {D_DYN_SFZ,  0,  "!sfz!"},
        {D_BREATH,   0,  "!breath!"},
        {D_WEDGE,    0,  "!wedge!" },
        {0, 0, ""} /*end marker*/
    };
    struct s_deconame* dn;

    n=0;

    for (;;) {
        deco=0;

        /*check for fullname deco*/
        if (*p == '!') {
            int slen;
            char* q;
            q = strchr(p+1,'!');
            if (!q) {
                syntax ("Deco sign '!' not closed",p);
                p++;
                return n;
            } else {
                slen = q+1-p;
                /*lookup in table*/
                for (dn=deconame; dn->index; dn++) {
                    if (0 == strncmp(p,dn->fullname,slen)) {
                        deco = dn->index;
                        break;
                    }
                }
                if (!deco) syntax("Unknown decoration",p+1);
                p += slen;
            }
        }
        /*check for abbrev deco*/
        else {
            for (dn=deconame; dn->index; dn++) {
                if (dn->abbrev && (*p == dn->abbrev)) {
                    deco = dn->index;
                    p++;
                    break;
                }
            }
        }

        if (deco) {
            prep_deco.add(deco);
            n++;
        }
        else
            printf("There is no decorator\n");
            break;
    }

    return n;
}


/* ----- parse_length: parse length specifer for note or rest --- */
int parse_length (void)
{
    int len,fac;

    len=voice[ivc].meter.dlen;          /* start with default length */

    if (len<=0) {
        syntax("got len<=0 from current voice", p);
        printf("Cannot proceed without default length. Emergency stop.\n");
        exit(1);
    }

    if (isdigit(*p)) {                 /* multiply note length */
        fac=parse_uint ();
        if (fac==0) fac=1;
        len *= fac;
    }

    if (*p=='/') {                   /* divide note length */
        while (*p=='/') {
            p++;
            if (isdigit(*p))
                fac=parse_uint();
            else
                fac=2;
            if (len%fac) {
                syntax ("Bad length divisor", p-1);
                return len;
            }
            len=len/fac;
        }
    }

    return len;
}

/* ----- parse_brestnum parses the number of measures on a brest */
int parse_brestnum (void)
{
    int fac,len;
    len=1;
    if (isdigit(*p)) {                 /* multiply note length */
        fac=parse_uint ();
        if (fac==0) fac=1;
        len *= fac;
    }
    return len;
}

/* ----- parse_grace_sequence --------- */
/*
 * result is stored in arguments
 * when no grace sequence => arguments are not altered
 */
int parse_grace_sequence (int *pgr, int *agr, int* len)
{
    char *p0;
    int n;

    p0=p;
    if (*p != '{') return 0;
    p++;

    *len = 0;   /* default is no length => accacciatura */
    n=0;
    while (*p != '}') {
        if (*p == '\0') {
            syntax ("Unbalanced grace note sequence", p0);
            return 0;
        }
        if (!isnote(*p)) {
            syntax ("Unexpected symbol in grace note sequence", p);
            p++;
        }
        if (n >= MAXGRACE) {
            p++; continue;
        }
        agr[n]=0;
        if (*p == '=') agr[n]=A_NT;
        if (*p == '^') {
            if (*(p+1)=='^') { agr[n]=A_DS; p++; }
            else agr[n]=A_SH;
        }
        if (*p == '_') {
            if (*(p+1)=='_') { agr[n]=A_DF; p++; }
            else agr[n]=A_FT;
        }
        if (agr[n]) p++;

        pgr[n] = numeric_pitch(*p);
        p++;
        while (*p == '\'') { pgr[n] += 7; p++; }
        while (*p == ',') {  pgr[n] -= 7; p++; }

        do_transpose (voice[ivc].key, &pgr[n], &agr[n]);

        /* parse_length() returns default length when no length specified */
        /* => we may only call it when explicit length specified */
        if (*p == '/' || isdigit(*p))
            *len=parse_length ();
        n++;
    }

    p++;
    return n;
}

/* ----- identify_note: set head type, dots, flags for note --- */
void identify_note (struct SYMBOL *s, char *q)
{
    int head,base,len,flags,dots;

    if (s->len==0) s->len=s->lens[0];
    len=s->len;

    /* set flag if duration equals (or gretaer) length of one measure */
    if (nvoice>0) {
        if (len>=(WHOLE*voice[ivc].meter.meter1)/voice[ivc].meter.meter2)
            s->fullmes=1;
    }

    base=LONGA;
    if (len>=LONGA)              base=LONGA;
    else if (len>=BREVIS)        base=BREVIS;
    else if (len>=WHOLE)         base=WHOLE;
    else if (len>=HALF)          base=HALF;
    else if (len>=QUARTER)       base=QUARTER;
    else if (len>=EIGHTH)        base=EIGHTH;
    else if (len>=SIXTEENTH)     base=SIXTEENTH;
    else if (len>=THIRTYSECOND)  base=THIRTYSECOND;
    else if (len>=SIXTYFOURTH)   base=SIXTYFOURTH;
    else syntax("Cannot identify head for note",q);

    if (base>=WHOLE)     head=H_OVAL;
    else if (base==HALF) head=H_EMPTY;
    else                 head=H_FULL;

    if (base==SIXTYFOURTH)        flags=4;
    else if (base==THIRTYSECOND)  flags=3;
    else if (base==SIXTEENTH)     flags=2;
    else if (base==EIGHTH)        flags=1;
    else                          flags=0;

    dots=0;
    if (len==base)            dots=0;
    else if (2*len==3*base)   dots=1;
    else if (4*len==7*base)   dots=2;
    else if (8*len==15*base)  dots=3;
    else syntax("Cannot handle note length for note",q);

    /*  printf ("identify_note: length %d gives head %d, dots %d, flags %d\n",
        len,head,dots,flags);  */

    s->head=head;
    s->dots=dots;
    s->flags=flags;
}


/* ----- double_note: change note length for > or < char --- */
/* Note: if symv[ivc][i] is a chord, the length shifted to the following
   note is taken from the first note head. Problem: the crazy syntax
   permits different lengths within a chord. */
void double_note (int i, int num, int sign, char *q)
{
    int m,shift,j,len;

    if ((symv[ivc][i].type!=NOTE) && (symv[ivc][i].type!=REST))
        bug("sym is not NOTE or REST in double_note", true);

    shift=0;
    len=symv[ivc][i].lens[0];
    for (j=0;j<num;j++) {
        len=len/2;
        shift -= sign*len;
        symv[ivc][i].len += sign*len;
        for (m=0;m<symv[ivc][i].npitch;m++) symv[ivc][i].lens[m] += sign*len;
    }
    identify_note (&symv[ivc][i],q);
    carryover += shift;
}

/* ----- parse_basic_note: parse note or rest with pitch and length --*/
int parse_basic_note (int *pitch, int *length, int *accidental)
{
    int pit,len,acc;

    acc=pit=0;                       /* look for accidental sign */
    if (*p == '=') acc=A_NT;
    if (*p == '^') {
        if (*(p+1)=='^') { acc=A_DS; p++; }
        else acc=A_SH;
    }
    if (*p == '_') {
        if (*(p+1)=='_') { acc=A_DF; p++; }
        else acc=A_FT;
    }

    if (acc) {
        p++;
        if (!strchr("CDEFGABcdefgab",*p)) {
            syntax("Missing note after accidental", p-1);
            return 0;
        }
    }
    if (!isnote(*p)) {
        syntax ("Expecting note", p);
        p++;
        return 0;
    }

    pit= numeric_pitch(*p);             /* basic pitch */
    p++;

    while (*p == '\'') {                /* eat up following ' chars */
        pit += 7;
        p++;
    }

    while (*p == ',') {                 /* eat up following , chars */
        pit -= 7;
        p++;
    }

    len=parse_length();

    do_transpose (voice[ivc].key, &pit, &acc);

    *pitch=pit;
    *length=len;
    *accidental=acc;

    if (db>3) printf ("  parsed basic note,"
            "length %d/%d = 1/%d, pitch %d\n",
            len,BASE,BASE/len,pit);

    return 1;

}


/* ----- parse_note: parse for one note or rest with all trimmings --- */
int parse_note (void)
{
    int k,deco,i,chord,m,type,rc,sl1,sl2,j,n;
    int pitch,length,accidental,invis;
    char *q,*q0;
    GchordList::iterator ii;
    /*grace sequence must be remembered in static variables,*/
    /*because otherwise it is lost after slurs*/
    static int ngr = 0;
    static int pgr[MAXGRACE],agr[MAXGRACE],lgr;

    n=parse_grace_sequence(pgr,agr,&lgr);   /* grace notes */
    if (n) ngr = n;

    parse_gchord();               /* permit chord after graces */

    deco=parse_deco();              /* decorations */

    parse_gchord();               /* permit chord after deco */

    chord=0;                             /* determine if chord */
    q=p;
    if ((*p=='+') || (*p=='[')) { chord=1; p++; }

    type=invis=0;
    parse_deco(); /* allow for decos within chord */
    if (isnote(*p)) type=NOTE;
    if (chord && (*p=='(')) type=NOTE;
    if (chord && (*p==')')) type=NOTE;   /* this just for better error msg */
    if (*p=='z') type=REST;
    if (*p=='Z') type=BREST;
    if ((*p=='x')||(*p=='X')) {type=REST; invis=1; }
    if (!type) return 0;

    k=add_sym(type);                     /* add new symbol to list */


    symv[ivc][k].dc.n=prep_deco.n;       /* copy over pre-parsed stuff */
    for (i=0;i<prep_deco.n;i++)
        symv[ivc][k].dc.t[i]=prep_deco.t[i];
    prep_deco.clear();
    if (ngr) {
        symv[ivc][k].gr.n=ngr;
        symv[ivc][k].gr.len=lgr;
        for (i=0;i<ngr;i++) {
            symv[ivc][k].gr.p[i]=pgr[i];
            symv[ivc][k].gr.a[i]=agr[i];
        }
        ngr = 0;
    } else {
        symv[ivc][k].gr.n=0;
        symv[ivc][k].gr.len=0;
    }

    if (!prep_gchlst.empty()) {
        /*gch_transpose (voice[ivc].key);*/
        for (ii=prep_gchlst.begin(); ii!=prep_gchlst.end(); ii++) {
            symv[ivc][k].gchords->push_back(*ii);
        }
        prep_gchlst.clear();
    }

    q0=p;
    if (type==REST) {
        p++;
        symv[ivc][k].lens[0] = parse_length();
        symv[ivc][k].npitch=1;
        symv[ivc][k].invis=invis;
        if (db>3) printf ("  parsed rest, length %d/%d = 1/%d\n",
                symv[ivc][k].lens[0],BASE,BASE/symv[ivc][k].lens[0]);
    }
    else if (type==BREST) {
        p++;
        symv[ivc][k].lens[0] = (WHOLE*voice[ivc].meter.meter1)/voice[ivc].meter.meter2;
        symv[ivc][k].len = symv[ivc][k].lens[0];
        symv[ivc][k].fullmes = parse_brestnum();
        symv[ivc][k].npitch=1;
    }
    else {
        m=0;                                 /* get pitch and length */
        sl1=sl2=0;
        for (;;) {
            if (chord && (*p=='(')) {
                sl1++;
                symv[ivc][k].sl1[m]=sl1;
                p++;
            }
            if ((deco=parse_deco())) {     /* for extra decorations within chord */
                for (i=0;i<deco;i++) symv[ivc][k].dc.add(prep_deco.t[i]);
                prep_deco.clear();
            }

            rc=parse_basic_note (&pitch,&length,&accidental);
            if (rc==0) { voice[ivc].nsym--; return 0; }
            symv[ivc][k].pits[m] = pitch;
            symv[ivc][k].lens[m] = length;
            symv[ivc][k].accs[m] = accidental;
            symv[ivc][k].ti1[m]  = symv[ivc][k].ti2[m] = 0;
            for (j=0;j<ntinext;j++)
                if (tinext[j]==symv[ivc][k].pits[m]) symv[ivc][k].ti2[m]=1;

            if (chord && (*p=='-')) {symv[ivc][k].ti1[m]=1; p++;}

            if (chord && (*p==')')) {
                sl2++;
                symv[ivc][k].sl2[m]=sl2;
                p++;
            }

            if (chord && (*p=='-')) {symv[ivc][k].ti1[m]=1; p++;}

            m++;

            if (!chord) break;
            if ((*p=='+')||(*p==']')) {
                p++;
                break;
            }
            if (*p=='\0') {
                if (chord) syntax ("Chord not closed", q);
                return type;
            }
        }
        ntinext=0;
        for (j=0;j<m;j++)
            if (symv[ivc][k].ti1[j]) {
                tinext[ntinext]=symv[ivc][k].pits[j];
                ntinext++;
            }
        symv[ivc][k].npitch=m;
        if (m>0) {
            symv[ivc][k].grcpit = symv[ivc][k].pits[0];
        }
    }

    for (m=0;m<symv[ivc][k].npitch;m++) {   /* add carryover from > or < */
        if (symv[ivc][k].lens[m]+carryover<=0) {
            syntax("> leads to zero or negative note length",q0);
        }
        else
            symv[ivc][k].lens[m] += carryover;
    }
    carryover=0;

    if (db>3) printf ("  parsed note, decos %d, text <%s>\n",
            symv[ivc][k].dc.n, symv[ivc][k].text);


    symv[ivc][k].yadd=0;
    if (voice[ivc].key.ktype==BASS)         symv[ivc][k].yadd=-6;
    if (voice[ivc].key.ktype==ALTO)         symv[ivc][k].yadd=-3;
    if (voice[ivc].key.ktype==TENOR)        symv[ivc][k].yadd=+3;
    if (voice[ivc].key.ktype==SOPRANO)      symv[ivc][k].yadd=+6;
    if (voice[ivc].key.ktype==MEZZOSOPRANO) symv[ivc][k].yadd=-9;
    if (voice[ivc].key.ktype==BARITONE)     symv[ivc][k].yadd=-12;
    if (voice[ivc].key.ktype==VARBARITONE)  symv[ivc][k].yadd=-12;
    if (voice[ivc].key.ktype==SUBBASS)      symv[ivc][k].yadd=0;
    if (voice[ivc].key.ktype==FRENCHVIOLIN) symv[ivc][k].yadd=-6;

    if (type!=BREST)
        identify_note (&symv[ivc][k],q0);
    return type;
}


/* ----- add_wd ----- */
char *add_wd(char *str)
{
    char *rp;
    int l;

    l=strlen(str);
    if (l==0) return 0;
    if (nwpool+l+1>NWPOOL) {
        error("Overflow while parsing vocals; increase NWPOOL and recompile.","");
    }

    strcpy(wpool+nwpool, str);
    rp=wpool+nwpool;
    nwpool=nwpool+l+1;
    return rp;
}

"""