# Copyright (c) 2019 Curtis Penner

import logging


formatter = ('%(asctime)s [%(levelname)s %(filename)s::'
             '%(funcName)s::%(lineno)s]'
             ' %(message)s')
simple_formatter = '%(message)s'

logging.basicConfig(format=formatter)
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

# # create file handler
# fh = logging.FileHandler('bac.log')
# fh.setLevel(logging.DEBUG)
# fh.setFormatter(simple_formatter)
#
# # create console handler
# console = logging.StreamHandler()
# console.setLevel(logging.DEBUG)
# console.setFormatter(simple_formatter)

# # add the handlers
# log.addHandler(fh)
# log.addHandler(ch)


# This is replaced with the SyntaxError Exception
# /* ----- sytax: print message for syntax error -------- */
# void syntax (const char *msg, char *q)
# {
#   int i,n,len,m1,m2,pp,qq,maxcol=65;
#
#   if (verbose<=2) printf ("\n");
#   if (!q) {
#     printf ("+++ %s in line %d\n", msg, linenum);
#     return;
#   }
#   qq=q-p0+1;
#   if (qq<0) qq=0;
#   printf ("+++ %s in line %d.%d \n", msg, linenum, qq);
#   m1=0;
#   m2=len=strlen(p0);
#   n=q-p0;
#   if (m2>maxcol) {
#     if (n<maxcol)
#       m2=maxcol;
#     else {
#       m1=n-10;
#       m2=m1+maxcol;
#       if (m2>len) m2=len;
#     }
#   }
#
#   printf ("%4d ", linenum);
#   pp=5;
#   if (m1>0) { printf ("..."); pp+=3; }
#   for (i=m1;i<m2;i++) printf ("%c", p0[i]);
#   if (m2<len) printf ("...");
#   printf ("\n");
#
#   if (n>=0 && n<200) {
#     for (i=0;i<n+pp-m1;i++) printf(" ");
#     printf ("^\n");
#   }
# }
