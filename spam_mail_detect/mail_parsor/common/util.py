# -*- coding: utf-8 -*-

'''
  Author   : Kim, Seongrae
  Filename : util.py
  Release  : 1
  Date     : 2018-08-28
 
  Description : utility for python
 
  Notes :
  ===================
  History
  ===================
  2018/08/28  created by Kim, Seongrae
'''
import os
import re
import sys
import pytz
import timeit
import datetime 
#from log import *
from time import sleep

C_END     = "\033[0m"
C_BOLD    = "\033[1m"
C_INVERSE = "\033[7m"
C_ITALIC  = "\033[3m"
C_UNDERLN = "\033[4m"
 
C_BLACK  = "\033[30m"
C_RED    = "\033[31m"
C_GREEN  = "\033[32m"
C_YELLOW = "\033[33m"
C_BLUE   = "\033[34m"
C_PURPLE = "\033[35m"
C_CYAN   = "\033[36m"
C_WHITE  = "\033[37m"
 

def echo_print(dummy_str):
    print("[%s]" % dummy_str)

def get_old_time(n_day):
    now = datetime.datetime.now(tz=pytz.timezone("Asia/Seoul"))
    old = now - datetime.timedelta(n_day)
    #print("%s-%02d-%02d %02d:%02d:%02d" % (old.year, old.month, old.day, old.hour, old.minute, old.second ))
    str_day = "%s-%02d-%02d" % (old.year, old.month, old.day)
    return old#str_day, old.weekday()

def get_yyyymmdd_time(yyyy, mm, dd):
    #print("%s %s %s" % (yyyy, mm, dd))
    return datetime.datetime(int(yyyy), int(mm), int(dd), 12, 0, 0, 0)

def memory_unit(n_size):
    if n_size < 1024:
        return "%-4d B" % (n_size)
    if n_size < 1024 * 1024:
        n_unit_byte = (float(n_size) / 1024.0)
        if n_unit_byte > 10.0:
            n_unit_byte = int(n_unit_byte)
            return "%-4d %s%sKB%s" % (n_unit_byte, C_BOLD,C_RED,C_END)
        return "%0.2f %s%sKB%s" % (n_unit_byte, C_BOLD,C_RED,C_END)
    if n_size < 1024 * 1024 * 1024:
        n_unit_byte = (float(n_size) / (1024.0 * 1024.0))
        if n_unit_byte > 10.0:
            n_unit_byte = int(n_unit_byte)
            return "%-4d %s%sMB%s" % (n_unit_byte, C_BOLD,C_YELLOW,C_END)
        return "%0.2f %s%sMB%s" % (n_unit_byte, C_BOLD,C_YELLOW,C_END)
    n_unit_byte = (float(n_size) / (1024.0 * 1024.0 * 1024.0))
    if n_unit_byte > 10.0:
        n_unit_byte = int(n_unit_byte)
        return "-4%d %s%sGB%s" % (n_unit_byte, C_BOLD,C_GREEN,C_END)
    return "0.2%f %s%sGB%s" % (n_unit_byte, C_BOLD,C_GREEN,C_END)

def get_now_time(format_string="%Y-%m-%d", yyyymmdd=None):
    if yyyymmdd != None:
        dd   = yyyymmdd[6:8]
        mm   = yyyymmdd[4:6]
        yyyy = yyyymmdd[0:4]
        now  = get_yyyymmdd_time(yyyy, mm, dd)
    else:
        now = datetime.datetime.now(tz=pytz.timezone("Asia/Seoul"))
    #old = now - datetime.timedelta(n_day)
    #print("%s-%02d-%02d %02d:%02d:%02d" % (old.year, old.month, old.day, old.hour, old.minute, old.second, old.milliseconds ))
    #yyyy:mm:dd:hh:MM:ss
    
    #  get_now_time("%Y-%m-%d %H:%M:%S %f")

    '''
    %Y  Year                        2013, 2014,     ... , 9999
    %y  Year                        17, 18,         ... , 99  
    %m  Month                       01, 02,         ... , 12
    %d  Day                         01, 02,         ... , 31
    %H  Hour (24-hour clock)        00, 01,         ... , 23
    %M  Minute                      00, 01,         ... , 59
    %S  Second                      00, 01,         ... , 59
    %f  Microsecond                 000000, 000001, ... , 999999
    '''

    #if format_string == "yyyy:mm:dd":
    #    str_day = "%s-%02d-%02d" % (old.year, old.month, old.day)
    return now.strftime(format_string)

#def get_old_time_list()

def str_time_to_int(str_time):
    #2019-02-07 09:17:00
    p = re.compile("20[0-9][0-9]-[0-1][0-9]-[0-3][0-9] [0-9][0-9]:[0-9][0-9]:[0-9][0-9]")
    if p.match(str_time) != None:
        str_tok = str_time.split(" ")[1].split(":")
        hh = int(str_tok[0])
        mm = int(str_tok[1])
        ss = int(str_tok[2])
        return hh * 10000 + mm * 100 + ss
        #return hh * 3600 + mm * 60 + ss

    #2019-02-07_09:17:00
    p = re.compile("20[0-9][0-9]-[0-1][0-9]-[0-3][0-9]_[0-9][0-9]:[0-9][0-9]:[0-9][0-9]")
    if p.match(str_time) != None:
        str_tok = str_time.split(" ")[1].split(":")
        hh = int(str_tok[0])
        mm = int(str_tok[1])
        ss = int(str_tok[2])
        return hh * 10000 + mm * 100 + ss
        #return hh * 3600 + mm * 60 + ss

    #09:17:00
    p = re.compile("[0-9][0-9]:[0-9][0-9]:[0-9][0-9]")
    if p.match(str_time) != None:
        str_tok = str_time.split(":")
        hh = int(str_tok[0])
        mm = int(str_tok[1])
        ss = int(str_tok[2])
        #return hh * 3600 + mm * 60 + ss
        # 120000 + 001100 + 000011
        return hh * 10000 + mm * 100 + ss

    #09:17
    p = re.compile("[0-9][0-9]:[0-9][0-9]")
    if p.match(str_time) != None:
        str_tok = str_time.split(":")
        hh = int(str_tok[0])
        mm = int(str_tok[1])
        return hh * 10000 + mm * 100
        #return hh * 3600 + mm * 60

    #09.17.00
    p = re.compile("[0-9][0-9].[0-9][0-9].[0-9][0-9]")
    if p.match(str_time) != None:
        str_tok = str_time.split(".")
        hh = int(str_tok[0])
        mm = int(str_tok[1])
        ss = int(str_tok[2])
        #return hh * 3600 + mm * 60 + ss
        # 120000 + 001100 + 000011
        return hh * 10000 + mm * 100 + ss



    return None


PYTHON_TYPE_CPYTHON = 0
PYTHON_TYPE_PYPY    = 1
g_python_type       =-1

def get_python_runtime():

    global g_python_type
    if g_python_type != -1:
        return g_python_type

    from subprocess import Popen, PIPE
    for line in Popen(['ps', 'aux'], shell=False, stdout=PIPE).stdout:
        if line.find("%s" % os.getpid()) == -1:
            continue
        line = line.split(' ')
        for item in line:
            if item.find('pypy') != -1:
                g_python_type = PYTHON_TYPE_PYPY
                return g_python_type
            elif item.find('python') != -1:
                g_python_type = PYTHON_TYPE_CPYTHON
                return g_python_type
            else:
                continue

    return g_python_type

g_timeit = {}
def SET_TIMEIT(l_timeit=None, description=""):
    if l_timeit == None:
        l_timeit = {}
    
    now_idx    = len(l_timeit.keys())
    timeit_key = "%02d %s" % ( now_idx, get_now_time("%H:%M:%S_%f")) + description
    l_timeit[timeit_key] = timeit.default_timer()

    global g_timeit
    g_timeit = l_timeit

    return l_timeit

def PRINT_TIMEIT(l_timeit=None):
    global g_timeit    
    if l_timeit == None:
        l_timeit = g_timeit

    item_list  = sorted(l_timeit.keys())
    old_timeit = None
    for idx, key in enumerate(item_list):
        prev_timeit = l_timeit[key]
        next_timeit = l_timeit[item_list[idx+1]] if idx+1 < len(item_list) else timeit.default_timer()
        print("%s : %s" % (key, next_timeit - prev_timeit))

    g_timeit = {}

OS_TYPE_LINUX   = 1
OS_TYPE_WINDOW  = 2
OS_TYPE_OTHERS  = 3

def get_os_type():
    if os.name.find("nt") != -1 or os.name.find("indow") != -1 or os.name.find("NT") != -1 or os.name.find("INDOW") != -1:
        return OS_TYPE_WINDOW
    else:
        return OS_TYPE_LINUX

def getConfigPath(stock_home=None, dir_delimiter=None):
    if "CONFIG_HOME" in os.environ:
        return os.environ["CONFIG_HOME"]
    else:
        if dir_delimiter == None:
            dir_delimiter = DIR_DELIMITER
        if stock_home == None:
            stock_home == STOCK_HOME
        if get_os_type() == OS_TYPE_WINDOW:
            return stock_home + "%ssrc%scfg" % (dir_delimiter, dir_delimiter)
        else: # LINUX
            return stock_home + "%scfg" % (dir_delimiter)

def do_demonize():
    pid = os.fork()
    if pid != 0:
        sleep(1)
        quit()
    iam_deamon = True
    return iam_deamon


def calc_rate(base_price, now_price):
    if base_price == 0 or base_price == 0.0:
        return 0.0
    return float((float(now_price) / float(base_price)) * 100.0) - 100.0



def funcname():
    return sys._getframe(1).f_code.co_name + "()"

def callname():
    return sys._getframe(2).f_code.co_name + "()"

