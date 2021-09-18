import common

in_page = False
nbuf = 0


def clear_buffer():
    global nbuf, ln_num

    nbuf = 0
    common.bposy = 0.0
    ln_num = 0

"""
# ----- write_buffer: write buffer contents, break at full pages ----
def write_buffer(fp):
    
    if not nbuf:
        return

    writenum += 1
    
    if ((writenum==1) && make_index) write_index_entry();

    nb=0;
    for (l=0;l<ln_num;l++) {
        b1=0;
        p1=0;
        if (l>0) {
            b1=ln_buf[l-1];
            p1=ln_pos[l-1];
        }
        b2=ln_buf[l];
        dp=ln_pos[l]-p1;
        if ((posy+dp<cfmt.botmargin) && (!epsf)) {
            write_pagebreak (fp);
        }
        for (i=b1;i<b2;i++) putc(buf[i],fp);
        posy=posy+dp;
        nb=ln_buf[l];
    }

    if (nb<nbuf) {
        for (i=nb;i<nbuf;i++) putc(buf[i],fp);
    }
    
    clear_buffer();
    return;

# ----- buffer_eob: handle completed block in buffer ------- 
# if the added stuff does not fit on current page, write it out after page break and change buffer handling mode to pass though 
def buffer_eob(fp):
    int do_break;

    if (ln_num>=BUFFLN) 
        rx("max number off buffer lines exceeded"," -- check BUFFLN");
    
    ln_buf[ln_num]=nbuf;
    ln_pos[ln_num]=bposy;
    ln_num++;
    
    if (!use_buffer) {
        write_buffer (fp);
        return;
    }

    do_break=0;
    if (posy+bposy<cfmt.botmargin) do_break=1;
    if (cfmt.one_per_page) do_break=1;
    
    if (do_break && (!epsf)) {
        if (tunenum != 1) write_pagebreak (fp);
        write_buffer (fp);
        use_buffer=0;
    }

    return;
}

# ----- check_buffer: dump buffer if less than nb bytes avilable --- 
def check_buffer(fp, nb: int):
{
    char mm[81];

    if (nbuf+nb>BUFFSZ) {
        sprintf (mm, "BUFFSZ exceeded at line %d", ln_num);
        std::cerr << "possibly bad page breaks, " <<    mm << std::endl;
        write_buffer (fp);
        use_buffer=0;
    }
}

"""