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
import pickle
import traceback
import datetime 

# local package import
from email_parser import *
from email_search import *
from email_content_parser import *

base_dir                = "/srkim/mnt/hdd250G/maildata"
word_dict_dir           = base_dir + "/word_dict"
word_embedding_prefix   = "word_embedding"

class makeWordEmbedding:
    def __init__(self, eml_list, old_embedding=None):
        self.embedding   = old_embedding
        self.eml_list    = eml_list
        self.save_prefix = word_embedding_prefix
        if old_embedding == None:
            #self.embedding = {
            #    "Word-List"     : {},
            #    "Domin-List"    : {},
            #}
            self.embedding = {}
            for embedding_name in embedding_name_list:
                self.embedding[embedding_name] = {}

    def work(self):
        #WordEmbedding = self.embedding["Word-List"]
        #DomainEmbedding = self.embedding["Domin-List"]
        for idx, mail_path in enumerate(self.eml_list):
            #print("[%d/%d] %s (w:%d, d:%d)" % (idx, len(self.eml_list), mail_path, \
            #                                      len(WordEmbedding.keys()), len(DomainEmbedding.keys())))
            print("[%d/%d] %s" % (idx, len(self.eml_list), mail_path))

            report = load_mail_report(mail_path)

            if report == None:
                continue
            #print("%s" % report)
            for paragraph in report["body-items"]:
                category = paragraph["Category"]
                sub_Category = paragraph["Sub-Category"]
                data = paragraph["Data"]
                if category != CONTENT_CAT_TEXT:
                    continue
                for embedding_name in embedding_name_list:
                    for word in data[embedding_name]:
                        self.__add_embedding(self.embedding[embedding_name], word)
                #for word in data["Word-List"]:
                #    self.__add_embedding(WordEmbedding, word)
                #for domain in data["Domin-List"]:
                #    self.__add_embedding(DomainEmbedding, domain)
        return

    @classmethod
    def make_embedding_name(cls, yyyymmdd="", subdir=None):
        save_dir = word_dict_dir
        if subdir != None:
            save_dir = "%s/%s" % (word_dict_dir, subdir,)
            if os.path.exists(save_dir) == False:
                os.makedirs(save_dir)
        if yyyymmdd != "":
            yyyymmdd = "_%s" % (yyyymmdd,)
        json_file_name = "%s/%s%s.json.gz" % (save_dir, word_embedding_prefix, yyyymmdd)
        pickle_file_name = "%s/%s%s.dat.gz" % (save_dir, word_embedding_prefix, yyyymmdd)
        return json_file_name, pickle_file_name

    def save(self, save_dir, yyyymmdd="", subdir=None):
        #WordEmbedding = self.embedding["Word-List"]   
        #DomainEmbedding = self.embedding["Domin-List"]

        #WordEmbedding   = sorted(WordEmbedding.items(), key=lambda x: x[1], reverse=True)
        #DomainEmbedding = sorted(DomainEmbedding.items(), key=lambda x: x[1], reverse=True)

        #total_result = {
        #    "Word-List"    : WordEmbedding,
        #    "Domin-List"   : DomainEmbedding,
        #}

        total_result = {}
        for embedding_name in embedding_name_list:
            embedding = self.embedding[embedding_name]
            embedding = sorted(embedding.items(), key=lambda x: x[1], reverse=True)
            total_result[embedding_name] = embedding

        jDumps = json.dumps(total_result, indent=4, ensure_ascii=False)
        json_file_name, pickle_file_name = makeWordEmbedding.make_embedding_name(yyyymmdd, subdir)
        with gzip.open(json_file_name, "wb") as fd:
            fd.write(jDumps.encode("utf-8"))

        with gzip.open(pickle_file_name,"wb") as fd:
            pickle.dump(total_result, fd)

        return json_file_name, pickle_file_name

    def load(self, save_dir=None, yyyymmdd="", subdir=None):
        total_result = None
        if save_dir == None:
            save_dir = word_dict_dir
        #file_name = "%s/%s%s.json.gz" % (save_dir, self.save_prefix, yyyymmdd)
        json_file_name, pickle_file_name = makeWordEmbedding.make_embedding_name(yyyymmdd, subdir)
        pickle_non_gz = pickle_file_name[0:-3]
        if os.path.exists(pickle_non_gz) != False:
            with open(pickle_non_gz,"rb") as fd:
                total_result = pickle.load(fd)
        elif os.path.exists(pickle_file_name) != False:
            with gzip.open(pickle_file_name,"rb") as fd:
                total_result = pickle.load(fd)
        elif os.path.exists(json_file_name) != False:
            with gzip.open(json_file_name, "rb") as fd:
                jDumps = fd.read()
                total_result = json.loads(jDumps)
        return total_result

    def __add_embedding(self, embedding_dict, word):
        try:
            embedding_dict[word] += 1
        except KeyError as e:
            embedding_dict[word]  = 1

    def __merge(self, day_result, total_report = None):
        if total_report == None:
            total_report = copy.deepcopy(self.embedding)
        for category_key in day_result.keys():
            category = day_result[category_key]
            for item in category:
                name  = item[0]
                count = item[1]
                #print("%s %s" % (name, count))
                try:
                    total_report[category_key][name] += count
                except KeyError as e:
                    total_report[category_key][name] = count
        return total_report

    def merge_word_embedding(self, base_dir, start_yyyymmdd, n_day_before):
        if start_yyyymmdd == None:
            end_date    = (datetime.datetime.now() - datetime.timedelta(1)).date()
        else:
            yyyy = int(start_yyyymmdd[0:4])
            mm   = int(start_yyyymmdd[4:6])
            dd   = int(start_yyyymmdd[6:8])
            end_date   = datetime.date(yyyy, mm, dd)
        start_date = (datetime.datetime.now() - datetime.timedelta(n_day_before)).date() 
        date_list  = [(end_date - datetime.timedelta(days=x)).strftime("%Y%m%d") for x in range((end_date - start_date).days)] 

        total_report = None
        for yyyymmdd in date_list:
            print(yyyymmdd)
            day_result   = self.load(base_dir, yyyymmdd, subdir="day_embeddings")
            total_report = self.__merge(day_result, total_report)
        self.embedding = total_report
        return total_report

def print_usage():
    print("Usage : ")
    print("    ./do_make_word_embedding.py [stary_yyyymmdd] [end_yyyymmdd]")
    print("    ./do_make_word_embedding.py -m [stary_yyyymmdd] [n_day_before]")
    print("    ./do_make_word_embedding.py --merge [stary_yyyymmdd] [n_day_before]")
    return None

def main():
    start_yyyymmdd  = None
    end_yyyymmdd    = None
    is_merge        = False
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "-m" or sys.argv[1] == "--merge":
            return main_merge(sys.argv[2:])
            #if len(sys.argv) >= 3:
            #    return main_merge(sys.argv[2:])
            #else:
            #    return print_usage()
        if sys.argv[1] == "-h" or sys.argv[1] == "--help":
            return print_usage()

    for idx,item in enumerate(sys.argv[1:]):
        if idx == 0 and len(item) == 8:
            start_yyyymmdd  = item
        elif idx == 1 and len(item) == 8:
            end_yyyymmdd    = item

    search          = emailSearch(base_dir + "/parsed_mails", start_yyyymmdd, end_yyyymmdd)
    search_days     = search.list_days()
    for yyyymmdd in search_days:
        search_result   = search.list_files(param_yyyymmdd=yyyymmdd)
        report_list     = []
        for idx, eml_pair in enumerate(search_result):
            eml_file = eml_pair[0]
            report_list.append(eml_file)
            #print("[%d/%d] : %s %s" % (idx, len(search_result), yyyymmdd, eml_file))
        e = makeWordEmbedding(report_list, None)
        e.work()
        e.save(word_dict_dir, yyyymmdd=yyyymmdd, subdir="day_embeddings")
    return

def main_merge(argv):
    start_yyyymmdd = None #argv[0]
    n_day_before = 10
    if len(argv) >= 2:
        n_day_before = int(argv[1])
    if len(argv) >= 1:
        start_yyyymmdd = argv[0]
    e = makeWordEmbedding(None, None)
    total_report = e.merge_word_embedding(word_dict_dir, start_yyyymmdd, n_day_before)
    json_file_name, pickle_file_name = e.save(word_dict_dir, yyyymmdd=start_yyyymmdd, subdir="merged_embeddings")
    if json_file_name != None:
        link_name = "%s/%s.json.gz" % (word_dict_dir, e.save_prefix)
        if os.path.exists(link_name) == True:
            os.remove(link_name)
        os.symlink(json_file_name, link_name)
    if pickle_file_name != None:
        link_name = "%s/%s.dat.gz" % (word_dict_dir, e.save_prefix)
        if os.path.exists(link_name) == True:
            os.remove(link_name)
        os.symlink(pickle_file_name, link_name)
        not_gz_file = link_name[0:-3]
        if os.path.exists(not_gz_file) == True:
            os.remove(not_gz_file)
        with gzip.open(pickle_file_name, "rb") as fd:
            picRow = fd.read()
        with open(not_gz_file, "wb") as fd:
            fd.write(picRow)

if __name__ == "__main__":
    main()
