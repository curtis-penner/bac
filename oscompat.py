# Copyright (c) 2019. Curtis Penner

import getpass

TABFONTDIRS = ['/usr/share/abctab2ps', '/usr/local/share/abctab2ps', 'fonts']

F_OK = 0   # file existence
X_OK = 1   # execute permission.
W_OK = 2   # write permission
R_OK = 4   # read permission


# get real user name info 
def get_real_user_name():
    return getpass.getuser()

