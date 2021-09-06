# Copyright 2019 Curtis Penner

import common
import info

info = info.Field()


class Process:
    def __init__(self, filename):
        self.filename = filename

    def process_file(self):
        with open(self.filename) as fp:
            lines = fp.readlines()

        if lines[0].startswith('%!'):
            self.process_cmdline(lines[0][2:]).strip()
            del lines[0]

        for line in lines:
            if is_field(line):
                info.process_field(line)
                continue
            if common.do_tune:
                self.process_line(line)

    def process_line(self, line):
        pass

    def process_cmdline(self, line):
        pass
