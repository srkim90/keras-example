#!/bin/env python
# -*- coding: utf-8 -*-

'''
  Filename : do_convert_mail_dataset.py at mail_parsor
  Release  : 1
  Date     : 2020-03-10
   
  Description : mail convert to data set for training
  
  Notes :
  ===================
  History
  ===================
  2020/03/10 created 
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
from email_search import *
from word_embedding import *


def main():
    base_dir        = "/srkim/mnt/hdd250G/maildata"
    start_yyyymmdd  = "20191001"
    end_yyyymmdd    = "20200301"
    coding          = EMBEDDING_INTEGER
    test_file_rate  = 25.0 # 15.0% 의 데이터가 Test용으로 사용 된다.

    mgr             = wordEmbeddingManager(embedding_size = 2 ** 16, coding=coding)
    search          = emailSearch(base_dir + "/parsed_mails", start_yyyymmdd, end_yyyymmdd)
    search_days     = search.list_days()
    #print(search_days)
    usage_type      = USAGE_TYPE_TEST
    for jdx,yyyymmdd in enumerate(search_days):
        search_result   = search.list_files(param_yyyymmdd=yyyymmdd)
        report_list     = []
        if (float(jdx) / float(len(search_days))) * 100.0 - test_file_rate > 0.0:
            usage_type = USAGE_TYPE_TRAIN
        for idx, eml_pair in enumerate(search_result):
            eml_file = eml_pair[0]
            is_spam  = 0 if "terracehamadm" in eml_file else 1
            mgr.add_training_data_from_file(eml_file, is_spam, usage=usage_type)
            print("[%d/%d] : %s %s usage_type=%d" % (idx, len(search_result), yyyymmdd, eml_file, usage_type))
    mgr.shuffle_data_set()
    mgr.save_data()
    return
        
if __name__ == "__main__":
    main()
