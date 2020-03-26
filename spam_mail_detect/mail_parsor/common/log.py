# -*- coding: utf-8 -*-

'''
  Author   : Kim, Seongrae
  Filename : log.py
  Release  : 1
  Date     : 2018-07-02
 
  Description : sa_log module for python
 
  Notes :
  ===================
  History
  ===================
  2018/07/02  created by Kim, Seongrae
'''

#print(dir())
import re             
import os
import sys
import codecs
#import fcntl
#import termios
import traceback
import datetime
import threading
from time import sleep
from singleton import *
from os.path import expanduser
from util import *
import logging


LOG_NONE    = 0
LOG_CRT     = 1
LOG_MAJ     = 2
LOG_MIN     = 3
LOG_INF     = 4
LOG_DBG     = 5
LOG_TRC     = 6

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
 
C_BGBLACK  = "\033[40m"
C_BGRED    = "\033[41m"
C_BGGREEN  = "\033[42m"
C_BGYELLOW = "\033[43m"
C_BGBLUE   = "\033[44m"
C_BGPURPLE = "\033[45m"
C_BGCYAN   = "\033[46m"
C_BGWHITE  = "\033[47m"


line80="--------------------------------------------------------------------------------"
line90="------------------------------------------------------------------------------------------"
line100="----------------------------------------------------------------------------------------------------"
line110="--------------------------------------------------------------------------------------------------------------"
line120="------------------------------------------------------------------------------------------------------------------------"

LNE80="================================================================================"
LINE80=LNE80
LINE90="=========================================================================================="
LINE100="===================================================================================================="
LINE110="=============================================================================================================="
LINE120="========================================================================================================================"


DEBUG       = logging.DEBUG
INFO        = logging.INFO
WARNING     = logging.WARNING
ERROR       = logging.ERROR
CRITICAL    = logging.CRITICAL


class common_log(singleton_instance):
    def __init__(self, log_level=logging.INFO):
        self.logger = logging.getLogger("default")
        self.logger.setLevel(log_level)
        self.log_level = log_level

    def set_log_level(self,log_level):
        if lv != logging.DEBUG and lv != logging.INFO and lv != logging.WARNING and lv != logging.ERROR and lv != logging.CRITICAL:
            self.do_logging(logging.ERROR, "Error. Invalid loglevel=%s" % log_level)
            return False
        self.logger.setLevel(log_level)
        self.log_level = log_level
        return True
    
    def do_logging(self, log_level, mseeage):
        if log_level == logging.DEBUG:
            logging_fn = ogging.debug
        elif log_level == logging.INFO:
            logging_fn = ogging.info
        elif log_level == logging.WARNING:
            logging_fn = ogging.warning
        elif log_level == logging.ERROR:
            logging_fn = ogging.error
        elif log_level == logging.CRITICAL:
            logging_fn = ogging.critical
        else:
            return False
        logging_fn(mseeage)
        return True

    #def set_


class sa_log(singleton_instance):

    isClose            = False
    fn_check_pos       = None
    log_fd             = None
    is_visible_log     = True
    is_trace_log       = True
    print_list         = []

    def __init__(self, log_name, log_index, log_path=None, log_level=-1, log_max_size=-1, log_max_num_a_day=-1):
        ''' 1. set prameters '''
        self.todey              = None
        self.log_fd             = None
        self.log_path           = log_path
        self.log_home           = log_path
        self.log_name           = log_name
        self.log_level          = log_level
        self.log_index          = log_index
        self.log_max_size       = log_max_size
        self.log_max_num_a_day  = log_max_num_a_day
        self.now_log_file_name  = None
        self.os_type            = get_os_type() # check os type

        ''' 2. make log path '''
        if log_path == None:
            if ("LOG_HOME" in os.environ) == True:
                self.log_path = os.environ["LOG_HOME"]
                self.log_home = os.environ["LOG_HOME"]
            else:
                home = expanduser("~")
                if self.os_type == OS_TYPE_WINDOW:
                    self.log_path = "%s/log" % (home)
                    self.log_home = "%s/log" % (home)
                else:
                    self.log_path = "%s\\log" % (home)
                    self.log_home = "%s\\log" % (home)

        if self.os_type == OS_TYPE_WINDOW:
            self.log_path = ("%s\\%s" % (self.log_path, log_name))
        else:
            self.log_path = ("%s/%s" % (self.log_path, log_name))
        
        if os.path.exists(self.log_path) == False:
            os.makedirs( self.log_path )

        ''' 3. read config '''
        self._read_config_file(True if log_max_size      == -1 else False,
                               True if log_max_num_a_day == -1 else False,
                               True if log_level         == -1 else False )

        ''' 4. make lock '''
        self.log_lock = threading.Semaphore(1)

        ''' 5. file open'''
        self._check_log_move()

        ''' 6. run print thread'''
        #hThread = threading.Thread(target=self.run_salog)
        #hThread.daemon = True
        #hThread.start()

    def __del__(self):
        if self.log_fd != None:
            print("LOG: %s close!!" % (self.now_log_file_name))
            self.log_fd.close()
        self.log_fd = None
    
    def _get_today(self):
        now = datetime.datetime.now()
        return "%s%02d%02d" % ( now.year, now.month, now.day )

    def _get_log_time(self):
        now = datetime.datetime.now()
        #str_time = "%04d/%02d/%02 %02d:%02d%02d" % ( now.year, now.month, now.day, now.hour, now.minute, now.second )
        str_time = "%s/%02d/%02d_%02d:%02d:%02d" % ( now.year, int(now.month), int(now.day), int(now.hour), int(now.minute), int(now.second) )
        return str_time

    def get_call_stack(self, depth):
        str_callstack = ""
        start = 2
        if sys._getframe(2).f_code.co_name == "LOG" or sys._getframe(2).f_code.co_name == "PRINT":
            start += 1

        if sys._getframe(3).f_code.co_name == "LOG" or sys._getframe(3).f_code.co_name == "PRINT":
            start += 1

        for i in range(start, depth+start):
            try:
                frame = sys._getframe(i).f_code
                #print ("co_argcount=%s,\n co_cellvars=%s,\n co_code=%s,\n co_consts=%s,\n co_filename=%s,\n co_firstlineno=%s,\n co_flags=%s,\n co_freevars=%s,\n co_kwonlyargcount=%s,\n co_lnotab=%s,\n co_name=%s,\n co_names=%s,\n co_nlocals=%s,\n co_stacksize=%s,\n co_varnames=%s" % (frame.co_argcount, frame.co_cellvars, frame.co_code, frame.co_consts, frame.co_filename, frame.co_firstlineno, frame.co_flags, frame.co_freevars, frame.co_kwonlyargcount, frame.co_lnotab, frame.co_name, frame.co_names, frame.co_nlocals, frame.co_stacksize, frame.co_varnames))
                str_callstack += "%s:%s <%s>" % (frame.co_filename.split('/')[-1], frame.co_firstlineno, frame.co_name)
            except ValueError:
                print("ValueError")
                break

        return str_callstack

    def _read_config_file(self, f_size, f_cnt, f_level):
        fMylog = False
        if self.os_type == OS_TYPE_WINDOW:
            log_cfg = "%s\\salog.cfg" % (self.log_home)
        else:
            log_cfg = "%s/salog.cfg" % (self.log_home)

        cfg_fd  = open(log_cfg, 'r')
        for line in cfg_fd:
            line = line.rstrip('\r|\n|\t')
            if line.find("[%s]" % (self.log_name)) == 0:
                fMylog = True
                continue
            elif line.find("[") != -1 and line.find("]") != -1:
                fMylog = False
                continue
            elif line.find("max-file-size") != -1 and fMylog == True and f_size == True:
                value = line.split('=')[-1]
                self.log_max_size = int(value)
                #print (value)
                continue
            elif line.find("max-num-of-file-a-day") != -1 and fMylog == True and f_cnt == True:
                value = line.split('=')[-1]
                self.log_max_num_a_day = int(value)
                #print (value)
                continue
            elif line.find("log-level") != -1 and fMylog == True and f_level == True:
                value = line.split('=')[-1]
                self.log_level = int(value)
                #print (value)
                continue
        if self.log_max_size <= 0:
            self.log_max_size = 1024*1024*30
        if self.log_max_num_a_day <= 0:
            self.log_max_num_a_day = 1000
        if self.log_level <= LOG_NONE or self.log_level > LOG_TRC:
            self.log_level = LOG_DBG

    def _open_log_file(self):
        #self.log_lock.acquire()
        if self.log_fd == None:
            self.todey             = self._get_today()
            if self.os_type == OS_TYPE_WINDOW:
                self.now_log_file_name = "%s\\%s%d.%s.log" % (self.log_path, self.log_name, self.log_index, self.todey)
            else:
                self.now_log_file_name = "%s/%s%d.%s.log" % (self.log_path, self.log_name, self.log_index, self.todey)
            #self.log_fd = codecs.open(self.now_log_file_name, 'a', 'utf8')
            self.log_fd = open(self.now_log_file_name, 'a')
        #self.log_lock.release()

    def _move_log(self):
        count_top = 0
        filenames = os.listdir(self.log_path)
        for filename in filenames:
            full_filename = os.path.join(self.log_path, filename)
            if filename.find(self.log_name) == 0:
                str_log_num = filename.split('.')[-1]
                try:
                    log_num = int(str_log_num)
                except:
                    continue
                if count_top < log_num:
                    count_top = log_num

        if self.log_fd != None:
            print("LOG: %s close!!" % (self.now_log_file_name))
            self.log_fd.close()
            self.log_fd = None

        count_top += 1

        if self.log_max_num_a_day > count_top:
            try:
                shutil.move(self.now_log_file_name, "%s.%03d" % (self.now_log_file_name, count_top))
            except:
                pass
        else:
            os.remove(self.now_log_file_name)

    def _check_log_move(self):
        self.log_lock.acquire()
        if self.log_fd == None:
            #print("New open log file!!")
            self._open_log_file()
            self.log_lock.release()
            return

        log_size = self.log_fd.tell()

        if log_size > self.log_max_size:
            PRINT("log_size(%s) > max(%s), move file\n" % (log_size, self.log_max_size));
            self._move_log()
            self._open_log_file()
            self.log_lock.release()
            return

        if self.todey != self._get_today():
            PRINT("day changed : old=%s, now=%s\n" % (self.todey, self._get_today()));
            self._move_log()
            self._open_log_file()
            self.log_lock.release()
            return

        self.log_lock.release()

    def _log_lv_string(self, log_level):
        if log_level == LOG_NONE:
            return "NONE"
        elif log_level == LOG_CRT:
            return "CRT"
        elif log_level == LOG_MAJ:
            return "MAJ"
        elif log_level == LOG_MIN:
            return "MIN"
        elif log_level == LOG_INF:
            return "INF"
        elif log_level == LOG_DBG:
            return "DBG"
        elif log_level == LOG_TRC:
            return "TRC"
        else:
            return str(log_level)

    def C__LOG(self, log_level, log_string):
        if log_level > self.log_level:
            return
        self._check_log_move()
        pos = self.get_call_stack(1)
        full_log_ln = "%s [%s] %s : %s" % (self._get_log_time(), self._log_lv_string(log_level), pos, log_string)
        if self.os_type == OS_TYPE_WINDOW:
            full_log_ln += "\r\n"
        else:
            full_log_ln += "\n"

        self.log_lock.acquire()
        if self.log_fd == None:
            self.log_lock.release()
            return

        try:
            nErr = self.log_fd.write(full_log_ln)
        except UnicodeEncodeError as e:
            pass
            #nErr = self.log_fd.write(full_log_ln)
            
        if self.log_fd != None:
            self.log_fd.close()
        self.log_fd =None
        self.log_lock.release()
        #print("3")

    def disable_print_terminal(self):
        self.is_visible_log = False

    def enable_print_terminal(self):
        self.is_visible_log = True

    def C__PRINT(self, log_string):
        if self.is_visible_log == True:
            print("" + log_string)
            #self.print_list.append(log_string)
        self.C__LOG(LOG_CRT, log_string)

    def set_check_pos_fn(self, fn):
        self.fn_check_pos = fn

    def run_salog(self):
        while self.isClose == False:
            n_print = len(self.print_list)
            for i in range (n_print):
                log_string = self.print_list.pop(0)
                print(log_string)

            sleep(0.05)

######################################################################################
'''
    USE THIS FUNCTIONS
        - sa_initlog        : call when process init
        - sa_reinitlogcfg   : call when recv signal <SIGHUP>
        - LOG               : log
        - PRINT             : log + print to terminal
'''
g_old_pos = 0

def sa_initlog(log_name, log_index, log_path=None, log_level=-1, log_max_size=-1, log_max_num_a_day=-1, is_visible_log=True):
    sa_log.instance(log_name, log_index, log_path, log_level, log_max_size, log_max_num_a_day)
    sa_log.getinstance().is_visible_log = is_visible_log
    #sleep(1.0)

def sa_reinitlogcfg(log_level):
    log = sa_log.getinstance()
    log._read_config_file()

def sa_get_log_object():
    return sa_log.getinstance()

def LOG(log_level, log_string):
    log = sa_log.getinstance()
    log.C__LOG(log_level, log_string)

def CRT(log_string):
    LOG(LOG_CRT, log_string)

def MAJ(log_string):
    LOG(LOG_MAJ, log_string)

def MIN(log_string):
    LOG(LOG_MIN, log_string)

def INF(log_string):
    LOG(LOG_INF, log_string)

def DBG(log_string):
    LOG(LOG_DBG, log_string)

def STACK():
    lines = traceback.format_exc().strip().split('\n')
    rl = [lines[-1]]
    lines = lines[1:-1]
    lines.reverse()
    nstr = ''
    for i in range(len(lines)):
        line = lines[i].strip()
        if line.startswith('File "'):
            eles = lines[i].strip().split('"')
            basename = os.path.basename(eles[1])
            lastdir = os.path.basename(os.path.dirname(eles[1]))
            eles[1] = '%s/%s' % (lastdir,basename)
            rl.append('^\t%s %s' % (nstr,'"'.join(eles)))
            nstr = ''
        else:
            nstr += line
    tr_back = '\n'.join(rl)
    PRINT("%s" % tr_back)
    return tr_back

def PRINT(log_string, tab=1):
    if type(log_string) != str:
        log_string = "%s" % log_string
    if log_string == "":
        print("")
        return
    str_ln = ""
    global g_old_pos
    log = sa_log.getinstance()
    if log == None:
        print(log_string)
        return
    if log.fn_check_pos != None:
        old_pos = log.fn_check_pos()
        if old_pos != 0 and old_pos != g_old_pos:
            str_ln = "\n"
        g_old_pos = old_pos

    str_tab=""
    for i in range(tab):
        str_tab+="    "
    if tab > 0:
        log.C__PRINT("%s%s%s->%s " % (str_ln, str_tab, C_YELLOW, C_END)  + log_string)
    else:
        log.C__PRINT("%s%s " % (str_ln, log_string))


def TRACE(log_string, tab=2):
    log = sa_log.getinstance()
    if log.is_trace_log != True or log.is_visible_log != True:
        return

    if log_string == "":
        print("")
        return
    str_ln = ""
    global g_old_pos
    if log.fn_check_pos != None:
        old_pos = log.fn_check_pos()
        if old_pos != 0 and old_pos != g_old_pos:
            str_ln = "\n"
        g_old_pos = old_pos

    str_tab=""
    for i in range(tab):
        str_tab+="    "
    if tab > 0:
        log.C__PRINT("%s%s%s;%s " % (str_ln, str_tab, C_YELLOW, C_END)  + log_string)
    else:
        log.C__PRINT("%s%s " % (str_ln, log_string))

    #log = sa_log.getinstance()
    #if log.is_trace_log == True and log.is_visible_log == True:
    #    log.PRINT(log_string)


def PRINT2(log_string):
    log = sa_log.getinstance()
    log.C__PRINT(log_string)

######################################################################################

def __fn_test():
    for i in range (1):
        LOG(LOG_CRT, "sdsaddasdsa")
        LOG(LOG_MAJ, "sdsaddasdsa11111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111")
        LOG(LOG_MIN, "sdsaddasdsa11111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111")


if __name__ == '__main__':
    sa_initlog("HCMD", 1)
    __fn_test()
