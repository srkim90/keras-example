#!/bin/env python
# -*- coding: utf-8 -*-

'''
  Filename : email_parser.py at mail_parsor
  Release  : 1
  Date     : 2020-02-19
   
  Description : mime extractor of spam detect module
  
  Notes :
  ===================
  History
  ===================
  2020/02/19 created 
'''

# common package import
import re
import os
import sys
import time
import gzip
import copy
import json
import traceback
import datetime 

# local package import
from email_parser import *
from email_search import *


def main():
    base_dir        = "/srkim/mnt/hdd250G/maildata"
    start_yyyymmdd  = None
    end_yyyymmdd    = None

    if len(sys.argv) >= 3:
        if len(sys.argv[1]) == 8 and len(sys.argv[2]) == 8:
            start_yyyymmdd  = sys.argv[1]
            end_yyyymmdd    = sys.argv[2]

    search          = emailSearch(base_dir, start_yyyymmdd, end_yyyymmdd)
    search_result   = search.list_files()
    for idx, eml_pair in enumerate(search_result):
        eml_file = eml_pair[0]
        yyyymmdd = eml_pair[1]
        print("[%d/%d] : %s %s" % (idx, len(search_result), yyyymmdd, eml_file))
        e = emailParser(eml_file)
        e.load_all()
        report = e.mk_mail_report()
        e.save_parsed_mail_info('%s/parsed_mails' % base_dir, report, do_gzip=True) 
    return
        
if __name__ == "__main__":
    main()
