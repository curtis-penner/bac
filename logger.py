# Copyright (c) 2019 Curtis Penner

import logging


formatter = ('%(asctime)s [%(levelname)s %(filename)s::'
             '%(funcName)s::%(lineno)s]'
             ' %(message)s')
simple_formatter = '%(message)s'

logging.basicConfig(format=formatter)
log = logging.getLogger(__name__)
log.setLevel(logging.WARNING)
