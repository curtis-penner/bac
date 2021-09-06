import time

# this is only used once in set_xpwid
WIDTH_MIN = 1.0
ixpfree = 0   # first element in xp array

XP_START = 0

class XPos(object):
    def __init__(self):
        self.type = None
        self.time = time.time()
        self.next = 0
        self.prev = 0
        self.dur = 0.0
        self.wl = 0.0
        self.wr = 0.0
        self.space = 0.0
        self.shrink = 0.0
        self.stretch = 0.0
        self.tune_fac = 0.0   # factor to tune spacing
        self.x = 0.0   # final horizontal position


xpos = dict(type=None,
            time=time.time(),
            dur=0.0,
            wl=0.0,
            wr=0.0,
            space=0.0,
            shrink=0.0,
            stretch=0.0,
            tune_fac=0.0,
            x=0.0)

xps = list()   # of XPos()

def set_xpwid(xp):
    """
    In every element xp set tune_fac = 1.0 and wl and wr to WIDTH_MIN
    For every voice that has syms:
        k1 is the first symbol
        k2 is the last symbol
        if k1.wl > xp[0].wl: xp[0].wl = k1.wl
        if k2.wl > xp[-1].wl: xp[-1].wl = k2.wl



    :return:
    """
