# -*- coding: utf-8 -*-

'''
  Author   : Kim, Seongrae
  Filename : py2_util.py
  Release  : 1
  Date     : 2018-09-11
 
  Description : utility for python2
 
  Notes :
  ===================
  History
  ===================
  2018/09/11  created by Kim, Seongrae
'''
import sys

def mmc_print(string, end=None, flush=False):
    if end == '':
        print string,
    else:
        print (string)

    if flush == True:
        sys.stdout.flush()


