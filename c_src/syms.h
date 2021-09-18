#ifndef _symsH
#define _symsH

/*  
 *  This file is part of abctab2ps, 
 *  See file abctab2ps.cpp for details.
 */

#include <stdio.h>
 
/*  subroutines to define postscript macros which draw symbols  */

#define STEM_XOFF 3.5
#define STEM_YOFF 1.0

void def_misc (FILE *fp);
void def_typeset(FILE *fp);
void define_font (FILE *fp, char name[], int num);
void def_tsig (FILE *fp);
void _add_cv (FILE *fp, float f1, float f2, float p[][2], int i0, int ncv);
void _add_sg (FILE *fp, float f1, float f2, float p[][2], int i0, int ncv);
void _add_mv (FILE *fp, float f1, float f2, float p[][2], int i0);
void def_stems (FILE *fp);
void def_dot (FILE *fp);
void def_deco (FILE *fp);
void def_deco1 (FILE *fp);
void def_hl (FILE *fp);
void def_beam (FILE *fp);
void def_flags1 (FILE *fp);
void def_flags2 (FILE *fp);
void def_xflags (FILE *fp);
void def_acc (FILE *fp);
void def_rests (FILE *fp);
void def_bars (FILE *fp);
void def_ends (FILE *fp);
void def_gchord (FILE *fp);
void def_sl (FILE *fp);
void def_hd1 (FILE *fp);
void def_hd2 (FILE *fp);
void def_hd3 (FILE *fp);
void def_gnote (FILE *fp);
void def_csg (FILE *fp);
void def_gclef (FILE *fp);
void def_t8clef (FILE *fp);
void def_fclef (FILE *fp);
void def_cclef (FILE *fp);
void def_brace (FILE *fp);
void def_staff (FILE *fp);
void def_sep (FILE *fp);

/* write postscript macros to file ------ */
void define_symbols (FILE *fp);

#endif // _symsH
