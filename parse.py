import subs
import log

log = log.log()


def rehash_selectors(sel_str: list[str]) -> tuple:
    """
    split selectors into patterns and xrefs

    todo: find the meaning and structure of sel_str
    """
    xref_str = ''
    pat = list()
    for value in sel_str:
        if not value or value.startswith('-'):   # skip any flags
            pass
        elif subs.is_xrefstr(value):
            xref_str = value
        else:  # pattern with * or +
            if '*' in value or '+' in value:
                pat.append(value)
            else:   # simple pattern
                pat.append("*" + value + '*')

    return pat, xref_str


def do_index(fin, xref_str, pat, select_all, search_field):
    print(f"def do_index({fin}, {xref_str}, {pat}, {select_all}, {search_field})")
