# Copyright 2018 Curtis Penner

import sys

# import constants
import log
import format

log = log.log()

cfmt = format.Format()

class Meter:
    """ data to specify the meter """
    Body = True

    Header = True
    Base = 196
    Whole = Base
    Half = Base // 2
    Quarter = Base // 4
    Eighth = Base // 8
    Sixteenth = Base // 16

    def __init__(self):
        self.meter1 = 4
        self.meter2 = 4   # numerator, denominator*/
        self.mflag = 1   # mflag: 1=C, 2=C|, 3=numerator only, otherwise 0
        self.top = ''
        self.meter_display = dict()
        self.display = 1   # 0 for M:none, 1 for real meter,
                           # 2 for differing display
        self.meter1 = 4
        self.meter2 = 4
        self.dlen = Meter.Eighth
        self.meter_str = None

    def __call__(self, meter_str, header=False):
        self.meter_str = meter_str
        if meter_str == 'C|':
            self.meter1 = 2
            self.meter2 = 4
        elif meter_str == 'C':
            self.meter1 = 4
            self.meter2 = 4
        elif '/' in meter_str:
            meters = meter_str.split('/', 2)
            if meters[0].isdigit():
                self.meter1 = int(meters[0])
            else:
                self.meter1 = 4
            if meters[1].isdigit():
                self.meter2 = int(meters[1])
            else:
                self.meter2 = 4
        else:
            if meter_str.isdigit():
                self.meter1 = int(meter_str)
                self.meter2 = 4
            else:
                log.critical(f'Failed meter value: {meter_str}')

    def parse_meter_token(self, s):
        self.meter_top = ''
        self.meter1 = 4
        self.meter2 = 4
        self.mflag = 1
        self.dlen = self.Eighth

        s = s.strip()
        if s[0] == 'C':
            if s[1] == '|':
                self.meter1 = 4
                self.meter2 = 2
                self.dlen = self.Eighth
                self.mflag = 2
                self.meter_top = 'C'
            else:
                self.meter1 = 4
                self.meter2 = 4
                self.dlen = self.Eighth
                self.mflag = 2
                self.meter_top = 'C'

        elif '/' not in s and s.isdigit():
            self.meter1 = int(s)
            self.meter2 = 4
            self.dlen = self.Eighth
            self.mflag = 3
            self.meter_top = s
        else:
            if '/' in s:
                self.meter_top, meter_bottom = s.split('/', 1)
            else:
                log.error(f"Cannot identify meter, missing /: {s}")
                return
            if '+' in self.meter_top:
                m = self.meter_top.split('+')
                m1 = sum(m)
            else:
                m = self.meter_top.split()
                m1 = m[0]
                if m[1] > m1:
                    m1 = m[1]
                if m[2] > m1:
                    m1 = m[2]
                if m1 > 30:
                    m[0] = m1//100
                    m[2] = m1 - 100*m[0]
                    m[1] = m[2]//10
                    m[2] = m[2] - 10*m[1]
                    m1 = m[0]
                    if m[1] > m1:
                        m1 = m[1]
                    if m[2] > m1:
                        m1 = m[2]
            if not meter_bottom.isdigit():
                log.error(f'meter bottom is not a number: {s}')
                sys.exit(1)
            m2 = int(meter_bottom)
            if m1*m2 == 0:
                log.error(f"Cannot identify meter: {s}")
                sys.exit(1)
            d = Meter.Base/m2
            if d*m2 != Meter.Base:
                log.error(f'Meter not recognized: {s}')
                sys.exit(1)
            self.meter1 = m1
            self.meter2 = m2
            self.dlen = Meter.Eighth
            if 4*self.meter1 < 3*self.meter2:
                self.dlen = Meter.Sixteenth
            self.mflag = 0

    def set_meter(self, mtrstr):   # def __call__(mtrstr):
        """ interpret meter string, store in struct """
        if not mtrstr:
            log.error("Empty meter string")
            return

        # if no meter, set invisible 4/4 (for default length)
        if mtrstr == "none":
            mtrstring = "4/4"
            self.display = 0
        else:
            mtrstring = mtrstr
            self.display = 1

        # if global meterdisplay option, add "display=..." string accordingly
        # (this is ugly and not extensible for more keywords, but works for now)
        if not self.meter_display and 'display=' in mtrstring:
            dismeter = self.display_meter(mtrstring)
            before, after = mtrstring.split('display=')
            dismeter(after)

        else:
            self.parse_meter_token(mtrstring)
            log.inf0(f'Meter <{mtrstr}> is {self.meter1} '
                     f'over {self.meter2} with default '
                     f'length 1/{Meter.Base/self.dlen}')


            # if (display == 2)
            #     printf(
            # else if (display == 0)
            #     printf("Meter <%s> will display as <none>\n", mtrstr);

        # # store parsed data in struct
        # meter->meter1 = meter1;
        # meter->meter2 = meter2;
        # meter->mflag = mflag;
        # if (!meter->dlen)
        #     meter->dlen = dlen;
        # strcpy(meter->top, meter_top);
        # meter->display = display;
        # if (display == 2)
        # {
        #     meter->dismeter1 = dismeter1;
        #     meter->dismeter2 = dismeter2;
        #     meter->dismflag = dismflag;
        #     strcpy(meter->distop, meter_distop);
        # else:
        #     self.dismeter1 = 0;
        #     meter->dismeter2 = 0;
        #     meter->dismflag = 0;
        #     strcpy(meter->distop, "");

    def display_meter(self, mtrstr):
        if not mtrstr:
            self.dismeter1 = 4
            self.dismeter2 = 4
            self.mflag = 0
            self.distop = ''
        elif mtrstr == 'none':
            self.display = 0
        print("Meter <%s> will display as %d over %d\n" %
              (mtrstr, self.dismeter1, self.dismeter2))


class DefaultLength(Meter):
    Body = True

    def __init__(self):
        super().__init__()
        self.default_length = Meter.Eighth

    def __call__(self, length, header=True):
        if '/' in length:
            top, bottom = length.split('/')
            if not top.isdigit() and not bottom.isdigit():
                log.error(f'+++Error: Default Length {length}')
                exit(3)
            self.default_length = Meter.Base * int(top) // int(bottom)
        else:
            self.default_length = Meter.Eighth


class DLen(Meter):
    """ this is going away """
    def __init__(self):
        super().__init__()
        self.dlen = Meter.Eighth

    def set_dlen(self, line, header):
        """
        set default length for parsed notes

        :return:
        """
        print(line, header)
        l1 = ''
        l2 = ''
        if '/' in line:
            l1, l2 = line.split('/')

        if not l1:
            return   # empty string.. don't change default length
                     # else {d =  BASE / l2;
        d = Meter.Base // int(l2)
        if d*l2 != Meter.Base:
            log.error("Length incompatible with BASE, using 1/8: ")
            self.dlen = Meter.Base // 8
        else:
            self.dlen = d * l1
        log.info(
            f"Dlen    <{line}> sets default note length to {self.dlen}/"
            f"{Meter.Base} =  1/{Meter.Base // self.dlen}")

"""

/* ----- set_meter: interpret meter string, store in struct ---- */
void set_meter (char *mtrstr, struct METERSTR *meter)
{
  int meter1,meter2,dlen,mflag;
  int dismeter1,dismeter2,dismflag;
  char meter_top[31], meter_distop[31], *mtrstrcopy;
  string mtrstring;
  int display;

  if (strlen(mtrstr)==0) { std::cerr << "Empty meter string" << std::endl; return; }

  /* if no meter, set invisible 4/4 (for default length) */
  if (!strcmp(mtrstr,"none")) {
    mtrstring = "4/4";
    display = 0;
  } else {
    mtrstring = mtrstr;
    display = 1;
  }

  /* if global meterdisplay option, add "display=..." string accordingly */
  /* (this is ugly and not extensible for more keywords, but works for now) */
  if (!cfmt.meterdisplay.empty() && (string::npos==mtrstring.find("display="))) {
    StringMap::iterator it = cfmt.meterdisplay.find(mtrstring);
    if (it != cfmt.meterdisplay.end())
      mtrstring += " display=" + it->second;
  }

  /* now we move to char* because there is no C++ equivalent to strtok */
  mtrstrcopy = (char*) alloca(sizeof(char)*(mtrstring.length()+1));
  strcpy(mtrstrcopy,mtrstring.c_str());

  /* loop over blank delimited fields */
  for (char* s=strtok(mtrstrcopy," \t"); s; s=strtok(NULL," \t")) {
    int rc, dummy;
    rc = 0;
    if (0==strcmp("display=none", s)) {
      display = 0;
    } else if (0==strncmp("display=", s, strlen("display="))) {
      rc = parse_meter_token(s + strlen("display="), &dismeter1, &dismeter2,
                             &dismflag, meter_distop, &dummy);
      display = 2;
    } else {
      rc = parse_meter_token(s, &meter1, &meter2,
                             &mflag, meter_top, &dlen);
    }
    if (rc) return;
  }

  if (verbose>=4) {
    printf ("Meter <%s> is %d over %d with default length 1/%d\n",
            mtrstr, meter1, meter2, BASE/dlen);
    if (display==2)
      printf ("Meter <%s> will display as %d over %d\n",
            mtrstr, dismeter1, dismeter2);
    else if (display==0)
      printf ("Meter <%s> will display as <none>\n", mtrstr);
  }

  /* store parsed data in struct */
  meter->meter1 = meter1;
  meter->meter2 = meter2;
  meter->mflag  = mflag;
  if (!meter->dlen)
    meter->dlen = dlen;
  strcpy(meter->top, meter_top);
  meter->display = display;
  if (display==2) {
    meter->dismeter1 = dismeter1;
    meter->dismeter2 = dismeter2;
    meter->dismflag  = dismflag;
    strcpy(meter->distop, meter_distop);
  } else {
    meter->dismeter1 = 0;
    meter->dismeter2 = 0;
    meter->dismflag  = 0;
    strcpy(meter->distop, "");
  }

}

/* ----- set_dlen: set default length for parsed notes ---- */
void set_dlen (char *str, struct METERSTR *meter)
{
  int l1,l2,d,dlen;

  l1=0;
  l2=1;
  sscanf(str,"%d/%d ", &l1, &l2);
  if (l1 == 0) return;       /* empty string.. don't change default length */
  else {
    d=BASE/l2;
    if (d*l2 != BASE) {
      std::cerr << "Length incompatible with BASE, using 1/8: " << str << std::endl;
      dlen=BASE/8;
    }
    else
      dlen = d*l1;
  }
  if (verbose>=4)
    printf ("Dlen  <%s> sets default note length to %d/%d = 1/%d\n",
            str, dlen, BASE, BASE/dlen);

  meter->dlen=dlen;

}


/* ----- append_meter: add meter to list of music -------- */
/*
 * Warning: only called for inline fields
 * normal meter music are added in set_initsyms
 */
void append_meter (const struct METERSTR* meter)
{
    int kk;

    //must not be ignored because we need meter for counting bars!
    //if (meter->display==0) return;

    kk=add_sym(TIMESIG);
    symv[ivc][kk]=zsym;
    symv[ivc][kk].gchords= new GchordList();
    symv[ivc][kk].type = TIMESIG;
    if (meter->display==2) {
        symv[ivc][kk].u    = meter->dismeter1;
        symv[ivc][kk].v    = meter->dismeter2;
        symv[ivc][kk].w    = meter->dismflag;
        strcpy(symv[ivc][kk].text,meter->distop);
    } else {
        symv[ivc][kk].u    = meter->meter1;
        symv[ivc][kk].v    = meter->meter2;
        symv[ivc][kk].w    = meter->mflag;
        strcpy(symv[ivc][kk].text,meter->top);
    }
    if (meter->display==0) symv[ivc][kk].invis=1;
}

"""