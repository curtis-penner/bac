# Copyright 2019 Curtis Penner

"""
The purpose of this module is to have a common place to keep global
variable. I know it is not elegant but for now this is how I will work
this.
"""

import utils.cmdline

output = 'out.ps'
filename = ''

do_mode = 0

within_block = False
do_tune = False

file_initialized = False
index_initialized = False

pagenum = 0
tunenum = 0
in_page = False
page_init = ''

is_epsf = False

posy = 0.0

voices = list()

fp = open(output, 'a')

# ----- definitions of global variables ----- */
#
# int db=DEBUG_LV;                  /* debug control */
# int maxSyms,maxVc;                /* for malloc */
# int allocSyms,allocVc;
# struct ISTRUCT info,default_info; /* information fields */
# char lvoiceid[STRLINFO];          /* string from last V: line */
# int  nvoice,mvoice;               /* number of voices defd, nonempty */
# int  ivc;                         /* current voice */
# int  ivc0;                        /* top nonempty voice */
# int ixpfree;                      /* first free element in xp array */
# struct METERSTR default_meter;    /* data to specify the meter */
# struct KEYSTR default_key;        /* data to specify the key */
#                           /* things to alloc: */
# struct SYMBOL  *sym;              /* symbol list */
# struct SYMBOL  **symv;            /* symbols for voices */
# struct XPOS    *xp;               /* shared horizontal positions */
# struct VCESPEC *voice;            /* characteristics of a voice */
# struct SYMBOL  **sym_st;          /* symbols a staff start */
# int            *nsym_st;
#
# int halftones;                    /* number of halftones to transpose by */
#
# float f0p,f5p,f1p,f0x,f5x,f1x;            /*   mapping fct */
# float lnnp,bnnp,fnnp,lnnx,bnnx,fnnx;      /*   note-note spacing */
# float lbnp,bbnp,rbnp,lbnx,bbnx,rbnx;      /*   bar-note spacing */
# float lnbp,bnbp,rnbp,lnbx,bnbx,rnbx;      /*   note-bar spacing */
#
#
# char wpool[NWPOOL];            /* pool for vocal strings */
# int nwpool,nwline;             /* globals to handle wpool */
#
# struct SYMBOL zsym;            /* symbol containing zeros */
#
# struct FORMAT sfmt;                    /* format after initialization */
# struct FORMAT dfmt;                    /* format at start of tune */
# struct FORMAT cfmt;                    /* current format for output */
#
# char fontnames[50][STRLFMT];           /* list of needed fonts */
# int  nfontnames;
#
# //char txt[MAXNTEXT][MAXWLEN];           /* for output of text */
# //int  ntxt;
# StringVector words_of_text;            /* for output of text */
#
#
# char vcselstr[STRLFILE];          /* string for voice selection */
# char mbf[501];                 /* mini-buffer for one line */
# char buf[BUFFSZ];              /* output buffer.. should hold one tune */
# int nbuf;                      /* number of bytes buffered */
# float bposy;                   /* current position in buffered data */
# int   ln_num;                  /* number of lines in buffer */
# float ln_pos[BUFFLN];          /* vertical positions of buffered lines */
# int   ln_buf[BUFFLN];          /* buffer location of buffered lines */
# int   use_buffer;              /* 1 if lines are being accumulated */
#
# char text [NTEXT][STRLINFO];   /* pool for history, words, etc. lines */
# int text_type[NTEXT];          /* type of each text line */
# int ntext;                     /* number of text lines */
# char page_init[201];           /* initialization string after page break */
# bool do_output;                // do index (false) or output (true)
# char escseq[81];               /* escape sequence string */
# int linenum;                   /* current line number in input file */
# int tunenum;                   /* number of current tune */
# int tnum1,tnum2;
# int numtitle;                  /* how many titles were read */
# int mline;                     /* number music lines in current tune */
# int nsym;                      /* number of symbols in line */
# int nsym0;                     /* nsym at start of parsing a line */
# int pagenum;                   /* current page in output file */
# int writenum;                  /* calls to write_buffer for each one tune */
# int xrefnum;                   /* xref number of current tune */
# int do_meter, do_indent;       /* how to start next block */
#
# int index_pagenum;             /* for index file */
# float index_posx, index_posy;
# int index_initialized;
#
# GchordList prep_gchlst;          /* guitar chords for preparsing */
# Deco prep_deco;                  /* decorations for preparsing */
# int bagpipe;                     /* switch for HP mode */
# int within_tune, within_block;   /* where we are in the file */
# int do_this_tune;                /* are we typesetting the current one ? */
# float posx,posy;                 /* overall scale, position on page */
# int barinit;                     /* carryover bar number between parts */
#
# char *p, *p0;                    /* global pointers for parsing music line */
#
# int word,slur;                   /* variables used for parsing... */
# int last_note,last_real_note;
# int pplet,qplet,rplet;
# int carryover;                   /* for interpreting > and < chars */
# int ntinext,tinext[MAXHD];       /* for chord ties */
#
# struct ENDINGS ending[20];       /* where to draw endings */
# int num_ending;                  /* number of endings to draw */
# int mes1,mes2;                   /* to count measures in an ending */
#
# int slur1[20],slur2[20];         /* needed for drawing slurs */
# int overfull;                    /* flag if staff overfull */
# int do_words;                    /* flag if staff has words under it */
#
# int vb, verbose;                 /* verbosity, global and within tune */
# int in_page=0;
#
#                                  /* switches modified by flags: */
# int gmode;                         /* switch for glue treatment */
# int include_xrefs;                 /* to include xref numbers in title */
# int one_per_page;                  /* new page for each tune ? */
# int pagenumbers;                   /* write page numbers ? */
# int write_history;                 /* write history and notes ? */
# int help_me;                       /* need help ? */
# int select_all;                    /* select all tunes ? */
# int epsf;                          /* for EPSF postscript output */
# int choose_outname;                /* 1 names outfile w. title/fnam */
# int break_continues;               /* ignore continuations ? */
# int search_field0;                 /* default search field */
# int pretty;                        /* for pretty but sprawling layout */
# int bars_per_line;                 /* bars for auto linebreaking */
# int continue_lines;                /* flag to continue all lines */
# int landscape;                     /* flag for landscape output */
# int barnums;                       /* interval for bar numbers */
# bool make_index;                   // write index file
# int notab;                         /* do not process tablature */
# int transposegchords;              /* transpose gchords */
# float alfa_c;                      /* max compression allowed */
# float scalefac;                    /* scale factor for symbol size */
# float lmargin;                     /* left margin */
# float swidth;                      /* staff width */
# float staffsep,dstaffsep;        /* staff separation */
# float strict1,strict2;           /* 1stave, mstave strictness */
# char transpose[21];              /* target key for transposition */
# struct PAPERSIZE* paper;         /* paper size (a4, letter) */
# int noauthor;                    /* suppress PS author tag (%%For) */
#
#
# float alfa_last,beta_last;       /* for last short short line.. */
#
# char in_file[MAXINF][STRLFILE];  /* list of input file names */
# signed int  number_input_files;  /* number of input file names */
# FILE *fin;                       /* for input file */
#
# char outf[STRLFILE];             /* output file name */
# char outfnam[STRLFILE];          /* internal file name for open/close */
# char styf[STRLFILE];             /* layout style file name */
# char styd[STRLFILE];             /* layout style directory */
# char infostr[STRLFILE];          /* title string in PS file */
#
# int  file_open;                  /* for output file */
# int  file_initialized;           /* for output file */
# FILE *fout,*findex;              /* for output file */
# int nepsf;                       /* counter for epsf output files */
#
# char sel_str[MAXINF][STRLFILE];  /* list of selector strings */
# int  s_field[MAXINF];            /* type of selection for each file */
# int  psel[MAXINF];               /* pointers from files to selectors */
#
# int temp_switch;
