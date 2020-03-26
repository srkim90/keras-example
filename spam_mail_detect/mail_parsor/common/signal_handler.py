# -*- coding: utf-8 -*-

'''
  Author   : Kim, Seongrae
  Filename : main.py
  Release  : 1
  Date     : 2018-08-26
 
  Description : Stock HIS Main module
 
  Notes :
  ===================
  History
  ===================
  2018/08/26  created by Kim, Seongrae
'''

import os
import sys
import signal
import threading
from time import sleep
from singleton import *

_OS_TYPE_LINUX      = 1
_OS_TYPE_WINDOW     = 2

class signal_handler(singleton_instance):
    exit_handler        = None
    signal_recv_time    = 0

    def __init__(self):
        self.os_type = self._get_os_type()
        if self.os_type == _OS_TYPE_WINDOW:
            return
        self.signal_init()

    def _get_os_type(self):
        if os.name.find("nt") != -1 or os.name.find("indow") != -1 or os.name.find("NT") != -1 or os.name.find("INDOW") != -1:
            return _OS_TYPE_WINDOW
        else:
            return _OS_TYPE_LINUX

    def signal_init(self):
        signal.signal(signal.SIGINT  , self.signal_handler_SIGINT)
        #signal.signal(signal.SIGHUP  , self.signal_handler_SIGHUP) 
        #signal.signal(signal.SIGTERM , self.signal_handler_SIGTERM)
        #signal.signal(signal.SIGPIPE , self.signal_handler_SIGPIPE)
        #signal.signal(signal.SIGCHLD , self.signal_handler_SIGCHLD)

        hThread = threading.Thread(target=self.signal_wait)
        hThread.daemon = True
        hThread.start()

    def set_signal_handler(self, sig_type, callback_func):
        signal.signal(sig_type  , callback_func)

    def signal_wait(self):
        while True:
            signal.pause()
            sleep(0.01)

    def set_handler_SIGINT(self, proc):
        self.exit_handler = proc

    def signal_handler_SIGPIPE(self, signal, frame):
        pass

    def signal_handler_SIGCHLD(self, signal, frame):
        pass

    def signal_handler_SIGHUP(self, signal, frame):
        pass

    def signal_handler_SIGTERM(self, signal, frame):
        pass

    def signal_handler_SIGINT(self, signal, frame):
        #if time.time() - self.signal_recv_time > 1:
        #    print('\nYou pressed Ctrl+C!! Once again in 1 sec, will quit.')
        #    self.signal_recv_time = time.time()
        #    return
        if self.exit_handler != None:
            PRINT("Detect input Control+C; Terminate simulator!!")
            self.exit_handler()

        exit()

def exit_handler():
    os.system('stty echo')

    #ch = child.getinstance()
    #if ch.is_child == False:
    #    for pid in ch.pid_list:
    #        os.system("kill -9 %d" % (pid))
    #        os.system("kill -9 %d" % (pid))

    sleep(0.15)
    quit()

def init_signal():
    signal_handler.instance()

