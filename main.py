import argparse

import fields.info
import music.symbol


def blank_line():
    """
    This is to reset info and symbol
    :return:
    """
    field = fields.info.Field()
    sym = music.symbol.Symbol()
    return field, sym


def args():
    parser = argparse.ArgumentParser(description='Python version of abctab2ps')
    parser.add_argument('filenames',
                        nargs='+',
                        help='Make a list of one or more files')
    return parser.parse_args()


def main():
    filenames = args().filenames
    for filename in filenames:
        with open(filename) as f:
            lines = f.readlines()

        field = fields.info.Field()
        sym = music.symbol.Symbol()
        for line in lines:
            line = line.strip()
            if line.startswith("%%"):
                print(f'pseudo-command:{line}')
                continue
            elif line.startswith('%'):
                # do nothing, this is a comment
                continue
            elif not line:
                field, sym = blank_line()
                continue
            elif fields.info.is_field(line):
                field.parse_info(line)
                continue
            elif field.do_music:
                # sym.parse(line)
                pass


if __name__ == '__main__':
    main()
