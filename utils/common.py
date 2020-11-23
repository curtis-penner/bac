# Copyright 2019 Curtis Penner

"""
The purpose of this module is to have a common place to keep global
variable. I know it is not elegant but for now this is how I will work
this.
"""

import utils.cmdline

output = 'out.ps'
filename = ''

do_mode = 0

within_block = False
do_tune = False

file_initialized = False
index_initialized = False

pagenum = 0
tunenum = 0
in_page = False
page_init = ''

is_epsf = False

posy = 0.0

voices = list()

fp = open(output, 'a')
