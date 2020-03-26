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

# email package import

'''
{
    yyyymmdd : {
        terracespamadm : ["aaa.eml", "bbb.eml", ...]
        terracehamadm  : ["ccc.eml", "ddd.eml", ...]
    }
}
'''

class emailSearch:
    def __init__(self, base_dir, start_yyyymmdd=None, end_yyyymmdd=None):
        self.base_dir   = base_dir

        if start_yyyymmdd == None:
            start_date  = (datetime.datetime.now() - datetime.timedelta(2)).date()
        else:
            yyyy = int(start_yyyymmdd[0:4])
            mm   = int(start_yyyymmdd[4:6])
            dd   = int(start_yyyymmdd[6:8])
            start_date      = datetime.date(yyyy, mm, dd) # 20190818
            start_date      = (start_date - datetime.timedelta(1))
        if end_yyyymmdd == None:
            end_date    = (datetime.datetime.now() - datetime.timedelta(1)).date()
        else:
            yyyy = int(end_yyyymmdd[0:4])
            mm   = int(end_yyyymmdd[4:6])
            dd   = int(end_yyyymmdd[6:8])
            end_date    = datetime.date(yyyy, mm, dd) # 20190818
        self.date_list  = [(end_date - datetime.timedelta(days=x)).strftime("%Y%m%d") for x in range((end_date - start_date).days)] 
        #print(self.date_list)
        self.search_result = self.search()
         
    def list_files(self, check_type=None, param_yyyymmdd=None): # spam_type : terracespamadm or terracehamadm
        total_list = []
        for yyyymmdd in self.search_result.keys():
            if param_yyyymmdd != None and param_yyyymmdd != yyyymmdd:
                continue
            in_dict = self.search_result[yyyymmdd]
            for spam_type in in_dict.keys():
                if check_type != None and check_type != spam_type:
                    continue
                for file_name in in_dict[spam_type]:
                    total_list.append((file_name, yyyymmdd))
        return total_list

    def list_days(self):
        return list(self.search_result.keys())

    def search(self):
        eml_dict    = {}
        check_list  = ["terracespamadm", "terracehamadm"]
        for yyyymmdd in self.date_list:
            in_dict = {}
            ln_file = 0
            for item in check_list:
                try:
                    eml_list = []
                    base_dir = "%s/%s/%s" % (self.base_dir, item, yyyymmdd)
                    in_dict[item] = self.__search(base_dir, eml_list)
                    ln_file += len(eml_list)
                except Exception as e:
                    #print("Error. %s" % (e,))
                    continue
            #print("%s: %d files" % (yyyymmdd, ln_file))
            eml_dict[yyyymmdd] = in_dict
        return eml_dict

    def __search(self, base_dir, eml_list):
        filenames = os.listdir(base_dir)
        for filename in filenames:
            full_filename = os.path.join(base_dir, filename)
            if os.path.isdir(full_filename) == True:
                self.__search(full_filename, eml_list)
            elif ".qs" in filename or ".json" in filename:
                ext = filename[-3:].lower()
                if ext == ".qs" or ext == ".gz" or ext == "son":
                    eml_list.append(full_filename)
        return eml_list


def main():
    #base_dir = "/srkim/mnt/hdd250G/maildata/parsed_mails"
    base_dir = "/srkim/mnt/hdd250G/maildata"
    e = emailSearch(base_dir, start_yyyymmdd=None, end_yyyymmdd=None)
    for eml_file in e.list_files():
        print(eml_file)
    #print("result : %s" % result)
    return


        
if __name__ == "__main__":
    main()
