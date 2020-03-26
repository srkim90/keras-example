# -*- coding: utf-8 -*-

'''
  Author   : Kim, Seongrae
  Filename : mmc_parse.py
  Release  : 1
  Date     : 2018-07-02
 
  Description : mmc module for python
 
  Notes :
  ===================
  History
  ===================
  2018/07/02  created by Kim, Seongrae
'''
import re
import os
import sys    
import time
import copy
import json
import termios
import fcntl
from abc import *
from time import sleep
from singleton import *
from config import * 

#class mmc(metaclass=ABCMeta):
#    @abstractmethod
class mmc():
    def run(command):
        pass
'''
class __mmc_quit(mmc):
    def run(command):
        os.system('stty echo')
        mmc_print("__mmc_quit")
        quit()

class __mmc_request_manual(mmc):
    def run(command):
        mmc_print("__mmc_request_manual")

__mmc = np.array([
                  ["quit",            0, "quit"                              , __mmc_quit                    ], 
                  ["send",            0, "send"                              , None                          ], 
                  ["request",         1, "send-request"                      , None                          ], 
                  ["manual",          2, "send-request-manual"               , None                          ], 
                  [":method",         3, "send-request-manual-S"             , None                          ], 
                  [":path",           4, "send-request-manual-S-S"           , None                          ], 
                  ["JSON-File",       5, "send-request-manual-S-S-S"         , __mmc_request_manual          ],
                 ])
'''

if sys.version_info[0] == 2:
    from py2_util import *
else:
    from py3_util import *

def print_list(list_entry, tab=0):
    if list_entry == []:
        return

    str_tab = ""
    for i in range (tab):
        str_tab+="    "

    for item in list_entry:
        if type(item) == list:
            print_list(item, tab + 1)
        else:
            mmc_print("%s%s" % (str_tab, item))
    return

class mmc_parse(singleton_instance):
    isClose                 = False
    command                 = ""
    mmc_history             = []
    mmc_history_reference   = 0


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

    C_LINE_TYPE_A = '─'
    C_LINE_TYPE_B = '└'
    C_LINE_TYPE_C = '│'
    C_LINE_TYPE_D = '┬'
    C_LINE_TYPE_E = '├'

    def __init__(self, __mmc, index, name):
        self.name               = name
        self.index              = index
        self.mmc                = __mmc
        self.__call_count       = 0
        self.key_sequence       = 0
        self.last_fn_sequence   = -100
        self.org_command        = 0
        self.last_prompt_strlen = 0
        self.last_prompt_time   = 0
        os.system('stty -echo')

#    def __del__(self):
#        os.system('stty echo')


    def run(self):
        self._refresh_input()
        while self.isClose == False:
            char = self._getch()
            self._input_proc(char)
            if char == "":
                sleep(0.05)
            
    def show_mmc_tree(self):
        mmc_tree = self._get_mmc_child_list()
        self.old_dir = []
        self.mmc_tree_list = []
        self._mmc_dict_string(mmc_tree)

        try:
            mmc_print("%s%s,%s,%s,%s,%s%s\n" % (self.C_BLACK, self.C_LINE_TYPE_A, self.C_LINE_TYPE_B, self.C_LINE_TYPE_C, self.C_LINE_TYPE_D, self.C_LINE_TYPE_E, self.C_END))
        except:
            self.C_LINE_TYPE_A = "-"
            self.C_LINE_TYPE_B = "+"
            self.C_LINE_TYPE_C = "|"
            self.C_LINE_TYPE_D = "+"
            self.C_LINE_TYPE_E = "+"

        lv_len_list=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        for item in self.mmc_tree_list:
            for i in range(len(item)):
                if len(item[i]) > lv_len_list[i]:
                    lv_len_list[i] = len(item[i]) + 8
 
        print_list = []
        for item in self.mmc_tree_list:
            str_tmp=""
            str_line=""
            #old_mmc_len = 0
            for i in range(len(item)):
                padding = 0
                str_tmp = ""
                if len(item[i]) != 0:
                    padding = 2
                    #str_tmp = "%s[%s%s%s]%s" % (self.C_GREEN, self.C_END, item[i], self.C_GREEN, self.C_END)
                    str_tmp = "?%s?" % (item[i])
                #str_tmp += "%s" % (self.C_GREEN)
                f_underline = 0
                for j in range(lv_len_list[i] - len(item[i]) - padding):
                    if (len(item[i]) == 0 or i + 1 == len(item)):
                        str_tmp += ' '
                    else:
                        #if f_underline == 0 and i != 0:
                        f_underline = 1
                        str_tmp += self.C_LINE_TYPE_A
                if i < len(item) - 1:
                    if len(item[i+1]) != 0 and f_underline == 0:
                        str_tmp = str_tmp[0:-2]
                        str_tmp += self.C_LINE_TYPE_B
                        str_tmp += self.C_LINE_TYPE_A
                #str_tmp += "%s" % (self.C_END)
                str_line += str_tmp
                #old_mmc_len = len(item[i])

            #mmc_print ("%s%s" % ("    ",str_line))
            print_list.append("%s%s" % ("    ",str_line))

        for i in range(len(print_list) - 1, 1, -1):
            idx=print_list[i].find(self.C_LINE_TYPE_B)
            if idx == -1:
                continue
            for j in range(i-1, 0, -1):
                if len(print_list[j]) <= idx:
                    break
                if print_list[j][idx] == ' ':
                    len_org = len(print_list[j])
                    print_list[j] = "%s%s%s" % (print_list[j][0:idx], self.C_LINE_TYPE_C , print_list[j][idx+1:len_org])
                else:
                    break
        for m in range(10):
            for i in range(len(print_list) - 1, 1, -1):
                j = i - 1
                idx=print_list[i].find(self.C_LINE_TYPE_B)
                if idx == -1:
                    continue
                if len(print_list[j]) <= idx:
                    continue
                if print_list[j][idx] == self.C_LINE_TYPE_A:
                    len_org = len(print_list[j])
                    print_list[j] = "%s%s%s" % (print_list[j][0:idx], self.C_LINE_TYPE_D , print_list[j][idx+1:len_org])
                elif print_list[j][idx] == self.C_LINE_TYPE_B:
                    len_org = len(print_list[j])
                    print_list[j] = "%s%s%s" % (print_list[j][0:idx], self.C_LINE_TYPE_E , print_list[j][idx+1:len_org])
        for m in range(10):
            for i in range(len(print_list) - 1, 1, -1):
                j = i - 1
                idx=print_list[i].find(self.C_LINE_TYPE_E)
                if idx == -1:
                    continue
                if len(print_list[j]) <= idx:
                    continue
                if print_list[j][idx] == self.C_LINE_TYPE_A:
                    len_org = len(print_list[j])
                    print_list[j] = "%s%s%s" % (print_list[j][0:idx], self.C_LINE_TYPE_D , print_list[j][idx+1:len_org])
                elif print_list[j][idx] == self.C_LINE_TYPE_B:
                    len_org = len(print_list[j])
                    print_list[j] = "%s%s%s" % (print_list[j][0:idx], self.C_LINE_TYPE_E , print_list[j][idx+1:len_org])
        for m in range(10):
            for i in range(len(print_list) - 1, 1, -1):
                j = i - 1
                idx=print_list[i].find(self.C_LINE_TYPE_C)
                if idx == -1:
                    continue
                if len(print_list[j]) <= idx:
                    continue
                if print_list[j][idx] == self.C_LINE_TYPE_A:
                    len_org = len(print_list[j])
                    print_list[j] = "%s%s%s" % (print_list[j][0:idx], self.C_LINE_TYPE_D , print_list[j][idx+1:len_org])
                elif print_list[j][idx] == self.C_LINE_TYPE_B:
                    len_org = len(print_list[j])
                    print_list[j] = "%s%s%s" % (print_list[j][0:idx], self.C_LINE_TYPE_E , print_list[j][idx+1:len_org])

             
        for item in print_list:
            line = ""
            item_arr = item.split('?')
            for it in item_arr:
                it_len = len(it)
                if it_len < 2:
                    continue
                if it[0] == self.C_LINE_TYPE_A or it[0] == self.C_LINE_TYPE_B or it[0] == self.C_LINE_TYPE_C or it[0] == self.C_LINE_TYPE_D or it[0] == self.C_LINE_TYPE_E or it[0] == ' ':
                    line += "%s%s%s" % (self.C_GREEN, it, self.C_END)
                else:
                    str_command = it
                    if str_command[0] == "'":
                        str_split = str_command.split("'")
                        str_command = '<%s%s%s>=%s' % (self.C_YELLOW, str_split[1], self.C_END, str_split[3])
                    line += "%s[%s%s%s]%s" % (self.C_GREEN, self.C_WHITE, str_command, self.C_GREEN, self.C_END)
            mmc_print ("%s" % (line))
        return
    
    def _mmc_dict_string(self, mmc_dict, parent=[], level=0):

        for k in mmc_dict.keys():
            item = mmc_dict[k]
            my_dir = copy.deepcopy(parent)
            my_dir.append(k)
            if type(item) == dict:
                self._mmc_dict_string(item, my_dir, level+1)
            else:
                str_tree      = ""
                len_old_dir   = len(self.old_dir)
                mmc_tree      = []
                #self.mmc_tree_list.append([])
                f_underline = 0
                for i in range(len(my_dir)):
                    if len_old_dir > i:
                        if self.old_dir[i] == my_dir[i] and f_underline == 0:
                            str_tree = "%s" % ("")
                            mmc_tree.append(str_tree)
                            continue
                    f_underline = 1
                    str_tree = "%s" % (my_dir[i])
                    mmc_tree.append(str_tree)
                self.old_dir = copy.deepcopy(my_dir)
                self.mmc_tree_list.append(mmc_tree) 
                #str_tree = str_tree[0:-1]
                #mmc_print ("    %s" % (str_tree))

    def _get_mmc_child_list(self):
        h         = -1
        max_level =  0
        mmc_dict  =  {}

        mmc = copy.deepcopy(self.mmc)

        for item in mmc:
            h          += 1
            m           = -1
            name        = item[0]
            level       = item[1]
            mmc_tree    = item[2].split('-')
            mmc_func    = item[3]

            if mmc_func == None and (mmc_tree[-1] == 'S' or mmc_tree[-1] == 'N'):
                #mmc_print (mmc_tree)
                for i in mmc:
                    m          += 1
                    name2       = i[0]
                    level2      = i[1]
                    mmc_tree2   = i[2].split('-')
                    mmc_func2   = i[3]
                    f_continue  = 0
                    
                    if level2 < level or len(mmc_tree2) < len(mmc_tree):
                        continue

                    for j in range(len(mmc_tree)):
                        if mmc_tree2[j] != mmc_tree[j]:
                            f_continue = 1

                    if f_continue == 1:
                        continue

                    if mmc_tree2[level] == 'S':
                        mmc_tree2[level] = "'%s''String" % (name)
                    elif mmc_tree2[level] == 'N':
                        mmc_tree2[level] = "'%s''Number" % (name)
                    mmc_line = ""
                    for k in mmc_tree2:
                        mmc_line += "%s-" % (k)
                    mmc[m][2] = mmc_line[0:-1]
            elif mmc_func != None:
                mmc_tree[level] = "%s" % (name)
                mmc_line = ""
                for k in mmc_tree:
                    mmc_line += "%s-" % (k)
                mmc[h][2] = mmc_line[0:-1]
                   
        for item in mmc:
            #mmc_print (item)
            level       = item[1]
            if max_level < level:
                max_level = level
         
        for i in range (max_level + 1):
            f_err = 0
            for item in mmc:
                f_continue  = 0
                name        = item[0]
                level       = item[1]
                mmc_tree    = item[2].split('-')
                mmc_func    = item[3]

                if level != i:
                    continue
             
                f_err   = 0
                lv_dicc = mmc_dict   
                for j in range(i):
                    if mmc_tree[j] not in lv_dicc:
                        f_err = 1
                        break
                    lv_dicc = lv_dicc[mmc_tree[j]]

                if f_err == 1:
                    continue

                if mmc_tree[i] not in lv_dicc:
                    if mmc_func == None:
                        lv_dicc[mmc_tree[i]] = {}
                    else:
                        lv_dicc[mmc_tree[i]] = "<cr>"

        return mmc_dict

    def _check_prompt_down(self):
        now_time = time.time()
        if now_time - self.last_prompt_time > 1 and self.last_prompt_strlen == 0:
            mmc_print ("")
            self._prompt(True)


    @classmethod
    def _getch(self, n_timeout=0.25):
        fd = sys.stdin.fileno()
        oldterm = termios.tcgetattr(fd)
        newattr = termios.tcgetattr(fd)
        newattr[3] = newattr[3] & ~termios.ICANON 
        termios.tcsetattr(fd, termios.TCSANOW, newattr)

        oldflags = fcntl.fcntl(fd, fcntl.F_GETFL)
        fcntl.fcntl(fd, fcntl.F_SETFL, oldflags | os.O_NONBLOCK)
        sleep_time = 0.005
        n_tot_sleep = 0
        try:        
            while 1:            
                try:
                    #sleep(0.025)
                    c = sys.stdin.read(1)
                    break
                except IOError: 
                    sleep(sleep_time)
                    n_tot_sleep += sleep_time
                    if n_tot_sleep > n_timeout:
                        c = ""
                        break
        finally:
            termios.tcsetattr(fd, termios.TCSAFLUSH, oldterm)
            fcntl.fcntl(fd, fcntl.F_SETFL, oldflags)
        return c



    def _prompt(self, newLine):
        ssBlank=""
        for i in range(self.last_prompt_strlen + 8):
            ssBlank+=" "

        mmc_print("\r%s" % ssBlank, end='', flush=True)
        str_line  = "\r  %s%s%s-%d-%d %s#%s%s %s%s%s " % (self.C_BOLD, self.C_BLUE, self.name, self.index, self.__call_count, self.C_RED, self.C_WHITE, self.C_END, self.C_END ,self.command, self.C_END)
        self.last_prompt_strlen = len(str_line)
        self.last_prompt_time   = time.time()
        mmc_print("%s%s" % (str_line, chr(8)) , end='', flush=True)

    '''
        if newLine == True:
            mmc_print("\n  %s-%d-%d # " % (self.name, self.index, self.__call_count), end='')
            for item in self.command :
                mmc_print('%s' % item, end='', flush=True)
            mmc_print (" " , end='', flush=True)
            mmc_print ("%s" % (chr(8)) , end='', flush=True)
            self.last_prompt_strlen = 0
        else:
            ssBlank=""
            for i in range(self.last_prompt_strlen + 8):
                ssBlank+=" "

            mmc_print("\r%s" % ssBlank, end='', flush=True)
            str_line  = "\r  %s%s-%d-%d %s#%s %s " % (self.C_BLUE, self.name, self.index, self.__call_count, self.C_RED, self.C_WHITE, self.command)
            self.last_prompt_strlen = len(str_line)

            mmc_print("%s%s" % (str_line, chr(8)) , end='', flush=True)
    '''


    def _command_check(self, commands):
        #{root:udId}
        ckd_cmmand = []
        for item in commands:
            if item[0] == '{' and item[-1] == '}':
                __item = item
                item = item[1:-1]
                item = item.split(':')
                if len(item) != 2 and len(item) != 1:
                    PRINT("Error. Invalid config tocken : item = %s" % (__item))
                    sleep(0.5)
                    ckd_cmmand.append(__item)
                    continue
                if len(item) == 1:
                    item2 = ["root", item[0]]
                    item  = item2
                e = cfg_data.getinstance()
                e.read_data_file()
                item = e.search_data_cfg(item[1], item[0])
                if item == None:
                    PRINT("Error. Notfund config tocken : item = %s" % (__item))
                    sleep(0.5)
                    ckd_cmmand.append(__item)
                    continue
                ckd_cmmand.append(item)
                continue
            ckd_cmmand.append(item)
        return ckd_cmmand

    def run_command(self, command):
        return self._run_command(command, silence=True)

    def _run_command(self, command, silence=False):
        str_tab     = "          "
        mmc_ok      = None

        if command == "!!":
            sz_his = len(self.mmc_history)
            if sz_his == 0:
                mmc_print ("\n\n  MMC execute error at mmc history :\n          Not exist command history")
                return False
            else:
                return self._run_command(self.mmc_history[-1])

        if command == "history" or command == "his" :
            self._input_handle_fn("C")
            return True

        if silence == False:
            if len(self.mmc_history) == 0:
                self.mmc_history.append(command)
            elif self.mmc_history[-1] != command:
                self.mmc_history.append(command)

        input_list  = command.split(' ')
        for i in range(input_list.count('')):
            input_list.remove('')
          
        inupt_count = len(input_list)
        for mmc_item in self.mmc:
            if inupt_count != mmc_item[1] + 1:
                continue

            if mmc_item[3] == None:
                continue

            mmc_comm_set = mmc_item[2].split('-')
            mmc_count    = len(mmc_comm_set)

            #mmc_print ("%s : %s" % (mmc_comm_set, input_list))
            i = 0
            find_continue = 0
            #print ("dddddddddddvv")
            #print (self.command)
            #print (mmc_item)
            #print ("dddddddddddtt")
            for ch in input_list:
                if mmc_count <= i:
                    break
                #print ("i=%d" % i)
                #print ("-- %s, %s" % (mmc_comm_set[i], ch))
                if mmc_comm_set[i] == ch or mmc_comm_set[i] == 'N' or mmc_comm_set[i] == 'S' :
                    mmc_ok         = mmc_item
                    find_continue += 1
                i += 1
            #print ("find_continue:%d, inupt_count:%d" % (find_continue, inupt_count))
            if find_continue != inupt_count:
                continue

            self.__call_count += 1
            #PRINT("%s" % (input_list))
            input_list = self._command_check(input_list)
            #PRINT("%s" % (input_list))
            mmc_ok[3].run(input_list)
            return True
        if (silence==False):
            print ("\n\n  %s%sS%syntax error at mmc_token :\n%s%s" % (self.C_BOLD, self.C_RED, self.C_END, str_tab, command))
            print ("  %s%sNOTE:%s type %s%s'%shelp%s'%s or %s%s'%sshow mmc_tree%s'%s to %sshow%s %sMMC%s %scommands%s" % ( self.C_BOLD, self.C_GREEN, self.C_END, self.C_BOLD, self.C_YELLOW, self.C_RED, self.C_YELLOW, self.C_END, self.C_BOLD, self.C_YELLOW, self.C_RED, self.C_YELLOW, self.C_END, self.C_UNDERLN, self.C_END, self.C_UNDERLN, self.C_END, self.C_UNDERLN, self.C_END))

        return False     

    def _find_possible_command(self, flash=True):
        level                   = 0
        str_help                = "\n\n  %s%sA%s%svailable commands" % (self.C_BOLD, self.C_GREEN, self.C_END, self.C_WHITE)
        str_tab                 = "          "
        str_autocomplete        = ""
        str_possible_command    = ""
        autocomplete_list       = []
        possible_input_count    = 0
        possible_command_count  = 0

        input_list  = self.command.split(' ')
        for i in range(input_list.count('')):
            input_list.remove('')
          
        if len(input_list) != 0:
            if self.command[-1] == " ":
                input_list.append("")
        else:
            input_list.append("")

        inupt_count = len(input_list)

        #print ("inupt_count:%s" % inupt_count)

        for mmc_item in self.mmc:
            if inupt_count != mmc_item[1] + 1:
                continue
            mmc_comm_set = mmc_item[2].split('-')
            mmc_count    = len(mmc_comm_set)

            i = 0
            find_continue = 0
            #print ("dddddddddddvv")
            #print (self.command)
            #print (mmc_item)
            #print ("dddddddddddtt")
            for ch in input_list:
                if mmc_count <= i:
                    break
                #if ch == "":
                #    break
                #mmc_print("i=%d" % i)
                #print ("-- %s, %s" % (mmc_comm_set[i], ch))
                if mmc_comm_set[i] == ch or mmc_comm_set[i] == 'N' or mmc_comm_set[i] == 'S' :
                    find_continue += 1
                elif mmc_comm_set[i].find(ch) == 0 and i == mmc_count - 1:
                    level = i
                    autocomplete_list.append(mmc_comm_set[i])
                else:
                    break
                i += 1
            #print ("find_continue:%d, inupt_count:%d" % (find_continue, inupt_count))
            if find_continue != inupt_count:
                continue
        
            i = mmc_count - 1

            #print ("\n\n%s : %d" % (mmc_comm_set, i))
            #if mmc_item[1] != 0:
            if mmc_comm_set[i] == 'N'   :
                possible_input_count += 1
                #str_possible_command += "{%s'%s%s%s'%s=%sNumber%s} " % (mmc_item[0])
                str_possible_command += "{%s'%s%s%s%s'=%sNumber%s} " % (self.C_BOLD, self.C_GREEN, mmc_item[0], self.C_BOLD, self.C_END, self.C_UNDERLN, self.C_END)
            elif mmc_comm_set[i] == 'S' :
                possible_input_count += 1
                str_possible_command += "{%s'%s%s%s%s'=%sString%s} " % (self.C_BOLD, self.C_GREEN, mmc_item[0], self.C_BOLD, self.C_END, self.C_UNDERLN, self.C_END)
            else:
                str_possible_command += "%s " % (mmc_item[0])
                #str_possible_command += "%s%s%s%s%s " % (self.C_BOLD, self.C_GREEN, mmc_item[0][0], self.C_END, mmc_item[0][1:-1] )
                #pass
            possible_command_count += 1
        
        if possible_command_count   > 1 or possible_input_count > 0 :
            if flash == True:
                print ("%s%s\n" % (str_help, str_possible_command))
            if possible_input_count == 1 and self.command[-1] != ' ' :
                self.command += " "
        elif possible_command_count == 1 and possible_input_count == 0:
            self.command = ""
            for i in range(inupt_count - 1):
                self.command += "%s " % (input_list[i])
            self.command += "%s " % (str_possible_command)
            return
        elif len(autocomplete_list) == 1 :
            self.command = ""
            for i in range(inupt_count - 1):
                self.command += "%s " % (input_list[i])
            self.command += "%s " % (autocomplete_list[0])
            return
        elif len(autocomplete_list) > 0 :
            sz_newline = 0
            for auto_item in autocomplete_list:
                short_cut, others = self._get_prompt_shortcut_idx(auto_item, autocomplete_list)
                #tmp_autocomplete  = "%s%s[%s%s%s%s%s%s%s%s]%s " % (self.C_BOLD, self.C_RED, self.C_END, self.C_BOLD, self.C_UNDERLN, auto_item[0], self.C_END, auto_item[1:len(auto_item)], self.C_BOLD, self.C_RED, self.C_END )
                tmp_autocomplete  = "%s%s[%s%s%s%s%s%s%s%s]%s " % (self.C_BOLD, self.C_RED, self.C_END, self.C_BOLD, self.C_UNDERLN, short_cut, self.C_END, others, self.C_BOLD, self.C_RED, self.C_END )
                sz_newline       += len(auto_item) + 3

                if sz_newline > 60:
                    tmp_autocomplete += "\n          "
                    sz_newline = 0

                str_autocomplete += tmp_autocomplete
                #str_autocomplete += "%s " % (auto_item)
            if flash == True:
                print ("%s at level=%s%s%d%s\n%s%s\n" % (str_help, self.C_BOLD, self.C_RED, level, self.C_END, str_tab, str_autocomplete))
        else:
            if flash == True:
                print ("%s\n%s%s\n" % (str_help, str_tab, "<cr>"))

    def _refresh_input(self):
        self._prompt(False)

    def _input_proc(self, char):

        if char == '' or char == None:
            return False

        #print ("\n[%s:%d]" % (char, self.key_sequence))
        self.key_sequence += 1

        if char == '\t':
            return self._input_handle_tab(char)
        elif char == '\n':
            self._refresh_input()
            return self._input_handle_enter(char)
        elif char == chr(8): #''' back-space  '''
            return self._input_handle_backspase(char)
        elif (char == 'A' or char == 'B' or char == 'C' or char == 'D') and (self.last_fn_sequence == self.key_sequence - 1):
            return self._input_handle_fn(char)
        elif ord(char) >= 32 and ord(char) <= 126 and char != '[' and char != ']':
            return self._input_handle_char(char)
        elif char == '[':
            self.last_fn_sequence = self.key_sequence
        else:
            return False

    def _input_handle_tab(self, char):
        self._find_possible_command()
        self._refresh_input()
        return True

    def _input_handle_enter(self, char):
        self.org_command           = ""
        self.mmc_history_reference = 0
        if len(self.command) > 0:
            self._find_possible_command(flash=False)
            command = self.command
            self.command = ""
            mmc_print("")
            #self._refresh_input()
            self.last_prompt_strlen = 0
            self._run_command(command)
            mmc_print("")
        else:
            self.command = ""
            mmc_print("")
        self._refresh_input()
        return True

    def _input_handle_backspase(self, char):
        self.command = self.command[:-1]
        #mmc_print(self.command)
        self._refresh_input()
        return True

    def _input_handle_char(self, char):
        self.command+=char
        #mmc_print(self.command)
        self._refresh_input()
        return True

    def _input_handle_char(self, char):
        self.command+=char
        #mmc_print(self.command)
        self._refresh_input()
        return True

    def _input_handle_fn(self, char):
        cnt_history = len(self.mmc_history)

        if char == 'A':
            if cnt_history > self.mmc_history_reference:
                if self.mmc_history_reference == 0:
                    self.org_command = self.command
                    #print ("A: self.org_command:%s" % self.org_command)

                self.command = self.mmc_history[(self.mmc_history_reference * -1) -1 ]

                if self.mmc_history_reference + 1 != cnt_history:
                   self.mmc_history_reference+=1
                   #print ("self.mmc_history_reference:%d -> %d"% (self.mmc_history_reference - 1, self.mmc_history_reference))
            #else:
            #    print ("\n          %s" % "reached end of mmc history list\n")

        elif char == 'B':
            if self.mmc_history_reference >= 0:
                if self.mmc_history_reference >= 1:
                    self.mmc_history_reference-=1
                    self.command = self.mmc_history[(self.mmc_history_reference * -1) -1]
                    #print ("self.mmc_history_reference:%d -> %d"% (self.mmc_history_reference + 1, self.mmc_history_reference))
                else:
                    #print ("B: self.org_command:%s" % self.org_command)
                    self.command = self.org_command
            #else:
            #    print ("\n          %s" % "reached beginning of mmc history list\n")

        else:
            if cnt_history >= 0:
                mmc_print ("\n  %s:" % "simulator MMC history list")
                i = 0
                for cmd in reversed(self.mmc_history):
                    mmc_print ("   -- %02d : %s" % (i + 1, cmd))
                    i += 1
                    if i >= 50:
                        break
                mmc_print("")

        self._refresh_input()

    def check_pos(self):
        return self.last_prompt_strlen

    def _get_prompt_shortcut_idx(self, item, prompt_list):
        length=len(item)
        for i in range(length):
            s_cut = item[0:i+1]
            n_hit = 0
            for it in prompt_list:
                if it.find(s_cut) == 0:
                    n_hit += 1
            if n_hit <= 1:
                return item[0:i+1], item[i+1:length]
        return item, ""
         
#def mmn_run(index, name):
if __name__ == '__main__':
    mmc_parse.instance(__mmc, 1, "TEST1")
    e = mmc_parse.getinstance()
    e.run()
