#ifndef _oscompatH
#define _oscompatH

/*
 *  This file is part of abctab2ps
 *  It is necessary for compatibility between 
 *  different operating systems
 */

#include <string>
using namespace std;

// directory separator
const static std::string DIRSEPCHAR = "/";

/* default tabfont search path */
#ifdef MACINTOSH
  const static std::string TABFONTDIRS = ":fonts";
#else
  const static std::string TABFONTDIRS = "/usr/share/abctab2ps;/usr/local/share/abctab2ps;fonts";
#endif


/* MPW on MacOs 8/9 lacks some Posix stuff */
#ifndef MACINTOSH
  #include <sys/stat.h>
#endif

/* MingW32 has alloca declared in malloc.h instead of stdlib.h */
#ifdef __MINGW32__
  #include <malloc.h>
#endif

/* get real user name info */
string get_real_user_name();

#endif // _oscompatH


