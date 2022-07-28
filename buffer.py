import logging

# import index
import common
from log import log
from constants import BUFFLN, BUFFSZ
from pssubs import write_pagebreak



def clear_buffer() -> None:
    common.nbuf = 0
    common.bposy = 0.0
    common.ln_num = 0


def write_buffer(fp) -> None:
    """ write buffer contents, break at full pages """
    if not common.nbuf:
        return

    common.write_num = True

    if common.write_num and common.make_index:
        index.write_index_entry()

    nb = 0
    for i in range(common.ln_num):
        b1 = 0
        p1 = 0
        if i > 0:
            b1 = common.ln_buf[i-1]
            p1 = common.ln_pos[i-1]

        b2 = common.ln_buf[i]
        dp = common.ln_pos[i]-p1
        if common.posy+dp < common.cfmt.bot_margin and not common.epsf:
            write_pagebreak(fp)

        fp.write(common.buf[b1:b2])
        common.posy += dp
        nb = common.ln_buf[i]

    if nb < common.nbuf:
        fp.write(common.buf[nb:common.nbuf])

    clear_buffer()


def buffer_eob(fp) -> None:
    """
    handle completed block in buffer

    if the added stuff does not fit on current page,
    write it out after page break and change buffer
    handling mode to pass though

    :param fp:
    :return:
    """
    if common.ln_num >= BUFFLN:
        logging.warning("max number off buffer lines exceeded",
                        " -- check BUFFLN")

    common.ln_buf[common.ln_num] = common.nbuf
    common.ln_pos[common.ln_num] = common.bposy
    common.ln_num += 1

    if not common.use_buffer:
        write_buffer(fp)
        return

    do_break = False
    if common.posy+common.bposy < common.cfmt.botmarginDD:
        do_break = True
    if common.cfmt.one_per_page:
        do_break = True

    if do_break and not common.epsf:
        if common.tunenum != 1:
            write_pagebreak(fp)
        write_buffer(fp)
        common.use_buffer = False


def check_buffer(fp, nb: int) -> None:
    """ dump buffer if less than nb bytes available """
    if common.nbuf+nb > BUFFSZ:
        mm = f"BUFFSZ exceeded at line {common.ln_num}"
        log.error(f"possibly bad page breaks, {mm}")
        write_buffer(fp)
        common.use_buffer = False
