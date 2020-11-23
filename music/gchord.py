# Copyright (c) 2019. Curtis Penner


class Gchord:
    def __init__(self):
        self.text = ''
        self.x = 0

    def parse_gchord(self, line):
        if line.startswith('"'):
            if line[1:].find('"') != -1:
                self.text = line[1:line.find('"')]