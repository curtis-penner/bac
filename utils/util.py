# Copyright (c) 2019 Curtis Penner

import os
import re
import random

from utils.log import log
import utils.cmdline
from utils import common

args = utils.cmdline.options()


# ----- bskip(h):  ----
def bskip(h):
    """
    translate down by h points in output buffer

    :param h:
    """
    global bposy

    if h*h > 0.0001:
        put(f'0 {-h:.2f} T\n')
        bposy = bposy - h



def put(line, fp=common.fp):
    """ This appends a line to filename. """
    fp.write(line)


def get_field_value(c, line):
    s = f'[{c}:'
    if s in line:
        n = line.find(s)
        if ']' in line[n+3]:
            p = line[n+3:].find(']')
            return line[n + 3:n + 3 + p].strip(), line[n+3+p+1:]
        else:
            log.error('Reached end of line')
    return line


def maximum(a, b):
    """ return the maximum of two arguments

    :param a:
    :param b:
    :return:  maximmu
    """
    if a > b:
        return a
    return b


def minimum(a, b):
    """
    return the minimum of two arguments

    :param a:
    :param b:
    :return:  maximmu
    """
    if a < b:
        return a
    return b


def rx(msg0, msg1):
    """
    error exit

    :param msg0:
    :param msg1:
    """
    log.error(f'\n+++ {msg0}{msg1}')
    print('+++ Fatal error: see log')
    exit(1)


def bug(msg, fatal):
    """
    print message for internal error and maybe stop
    
    :param str msg: 
    :param bool fatal: 
    """
    print("\n\nThis cannot happen!")
    if msg:
        log.critical(f"\nInternal error: {msg}.")
        print(f"\nInternal error: {msg}.")
    if fatal:
        print("Emergency stop.")
        exit(1)
    else:
        print("Trying to continue...")


def ranf(x1, x2):
    """
    return random float between x1 and x2

    :param float x1:
    :param float x2:
    :return float:
    """
    return random.uniform(x1, x2)


def chartoi(c):
    """
    convert a single character to an integer

    :param str c:
    :return int:
    """
    if len(c) == 1 and c.isdigit():
        return int(c)
    return 0


def getline(fp):
    """
    Reads a line from fp into string s, and trims away any trailing whitespace
    This function works with \r and \n and \r\n and even \n\r as EOL
    (the latter occurs on MacOs 8/9, because MPW swaps \r and \n)
    RC: 1 = line successfully read; 0 = EOF or error

    :param file fp:
    :return str:
    """
    s = fp.readline()
    if s:
        return s.strip(), True
    return '', False


def nwords(s):
    """
    count words in string
    
    :param str s:
    :return int:
    """
    return len(s.split())


# ----- getword:  ----
def getword(iw, line):
    """
    return n-th word from string

    :param iw:
    :param str line:
    :return str:
    """
    words = line.split()
    if iw < len(words):
        return words[iw]
    else:
        return ''


# ----- abbrev:  -----
def abbrev(line, ab, nchar):
    """
    check for valid abbreviation
    """
    # int i,nc;
    if len(line) > len(ab):
        return 0
    nc = len(line)
    if nc < nchar:
        nc = nchar
    for i in range(nc):
        if line[i] != ab[i]:
            return False
    return True


def str_ext(filename, ext, force):
    """
    set extension on a file identifier -----
    force=1 forces change even if fid already has an extension
    force=0 does not change the extension if there already is one

    :param filename:
    :param ext: "
    :param force:
    :return:
    """

    name, c_ext = os.path.splitext(filename)
    if force:
        if ext.startswith('.'):
            return name + ext
        else:
            return '.'.join([name, ext])
    else:
        if not c_ext:
            return name + c_ext
        else:
            if ext.startswith('.'):
                return name + ext
            else:
                return '.'.join([name, ext])


def cut_ext(filename):
    """
    Split the name of the

    :param filename:
    :return tuple: name, extension
    """
    return os.path.splitext(filename)


def getext(filename):
    """
    get extension on a file identifier

    :param filename:
    :return:
    """
    _, ext = os.path.splitext(filename)
    return ext


def isblankstr(line):
    """
    check for blank string

    :param line:
    :return bool:
    """
    return len(line.strip()) == 0


def cap_str(line):
    """
    capitalize a string

    :param str line:
    :return str:
    """
    return line.upper()


def cwid(c):
    """"
    These are char widths for Times-Roman

    :param str c:
    :return float:
    """

    letters = {'a': 44.4,
               'b': 50.0,
               'c': 44.4,
               'd': 50.0,
               'e': 44.4,
               'f': 33.3,
               'g': 50.0,
               'h': 50.0,
               'i': 27.8,
               'j': 27.8,
               'k': 50.0,
               'l': 27.8,
               'm': 77.8,
               'n': 50.0,
               'o': 50.0,
               'p': 50.0,
               'q': 50.0,
               'r': 33.3,
               's': 38.9,
               't': 27.8,
               'u': 50.0,
               'v': 50.0,
               'w': 72.2,
               'x': 50.0,
               'y': 50.0,
               'z': 44.4,

               'A': 72.2,
               'B': 66.7,
               'C': 66.7,
               'D': 72.2,
               'E': 61.1,
               'F': 55.6,
               'G': 72.2,
               'H': 72.2,
               'I': 33.3,
               'J': 38.9,
               'K': 72.2,
               'L': 61.1,
               'M': 88.9,
               'N': 72.2,
               'O': 72.2,
               'P': 55.6,
               'Q': 72.2,
               'R': 66.7,
               'S': 55.6,
               'T': 61.1,
               'U': 72.2,
               'V': 72.2,
               'W': 94.4,
               'X': 72.2,
               'Y': 72.2,
               'Z': 61.1,

               '0': 50.0,
               '1': 50.0,
               '2': 50.0,
               '3': 50.0,
               '4': 50.0,
               '5': 50.0,
               '6': 50.0,
               '7': 50.0,
               '8': 50.0,
               '9': 50.0,

               '~': 54.1,
               '!': 33.3,
               '@': 92.1,
               '#': 50.0,
               '$': 50.0,
               '%': 83.3,
               '^': 46.9,
               '&': 77.8,
               '*': 50.0,
               '(': 33.3,
               ')': 33.3,
               # '-': 33.3,
               '-': 40.0,
               '_': 50.0,
               '+': 56.4,
               '=': 55.0,
               '[': 33.3,
               ']': 33.3,
               '{': 48.0,
               '}': 48.0,
               '|': 20.0,
               ':': 27.8,
               ',': 27.8,
               '.': 27.8,
               '\\': 27.8,
               "'": 33.3,
               '"': 40.8,
               '<': 56.4,
               '>': 56.4,
               '?': 44.4,
               '/': 27.8,
               '`': 33.3,
               ' ': 25.0,
               # sharp, flat, nat
               '\201': 50.0,
               '\202': 50.0,
               '\203': 50.0}

    w = letters.get(c, 50.0)
    return w/100.0


def get_file_size(fname):
    """
    version using standard function stat

    :param fname:
    :return int: file size
    """
    try:
        return os.path.getsize(fname)
    except OSError as ose:
        print(f'Unsuccessful call to stat for file {fname}')
        print(ose)
        return -1


def match(s, pat=''):
    return re.search(pat, s, re.I)


"""

/* ----- parse_uint: parse for unsigned integer ----- */
int parse_uint (void)
{
    int number,ndig;
    char num[21];

    if (!isdigit(*p)) return 0;
    ndig=0;
    while (isdigit(*p)) {
        num[ndig]=*p;
        ndig++;
        num[ndig]=0;
        p++;
    }
    sscanf (num, "%d", &number);
    if (db>3) printf ("  parsed unsigned int %d\n", number);
    return number;

}

"""
