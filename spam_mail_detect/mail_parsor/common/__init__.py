# -*- coding: utf-8 -*-

'''
  Author   : Kim, Seongrae
  Filename : __init__.py
  Release  : 1
  Date     : 2020-03-26
 
  Description : common module entry
 
  Notes :
  ===================
  History
  ===================
  2020/03/26  created by Kim, Seongrae
'''

# common package import
import re
import os
import sys
import pytz
import json
import redis
import timeit
import threading
import inspect
from time import *
from datetime import *

# custom package import
from .util import *
from .singleton import *
from .mmc_parse import *
from .signal_handler import *

OS_TYPE = get_os_type()
#if "STOCK_HOME" in os.environ:
#    STOCK_HOME=os.environ["STOCK_HOME"]
#elif OS_TYPE == OS_TYPE_WINDOW:
#    STOCK_HOME="C:\\stock"
#else: # LINUX
#    STOCK_HOME="/home/seongrae/stock"

if OS_TYPE == OS_TYPE_WINDOW:
    DIR_DELIMITER="\\"
else: # LINUX
    DIR_DELIMITER="/"

PYTHON2 = True
PYTHON3 = False
if sys.version_info[0] == 3:
    PYTHON2 = False
    PYTHON3 = True

if OS_TYPE == OS_TYPE_LINUX and PYTHON2 == True:
    from .linux_http_server import *

# init custom package
init_signal()
