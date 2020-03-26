#!/bin/env python
# -*- coding: utf-8 -*-

'''
  Filename : mk_element_hash.py
  Release  : 1
  Date     : 2020-03-24
 
  Description : mime extractor of spam detect module
  
  Notes :
  ===================
  History
  ===================
  2020/03/24 created 
'''
# common package import
import re
import os
import sys
import time
import json
import copy
import random
import datetime

# local package import
from email_search import *
from word_embedding import *

EL_SAVE_FILE_NAME = "element_hash"

class emlHashManager:
    def __init__(self, home_dir):
        self.home_dir       = home_dir
        self.eml_hash       = None
        self.ln_eml         = None
        self.sz_embedding   = None
        '''
        hash = {
            "그래핀"     : {'2020-02-05-15:13:03:353843', '2020-02-05-15:12:23:282084', ...}
            "공개적으로" : {'2020-02-05-15:12:55:683407', ...}
            ...
        }
        '''

    def check_email_have_element(self, embedding_name, element):
        try:
            _hash = self.eml_hash[embedding_name]
        except:
            print("[check_email_have_element] Error. Not exist embedding name : %s" % (embedding_name,))
            return None
        
        try:
            list_of_have_element = _hash[element]
        except:
            return None
        return list_of_have_element

    def make_hash(self, end_yyyymmdd=None):
        self.word_hash   = dict()
        self.domain_hash = dict()
        eml_list  = self.__listup_eml(end_yyyymmdd)
        word_dict = self.__load_word_dict()
        ln_eml = len(eml_list)
        self.ln_eml = ln_eml

        self.eml_hash = {
            "Word-List"     : self.word_hash,
            "Domin-List"    : self.domain_hash,
            "ln_eml"        : self.ln_eml,
        }
        self.sz_embedding = len(self.word_hash.keys())
        for idx, emlFullPath in enumerate(eml_list):
            if ".gz" == emlFullPath[-3:]:
                fd = gzip.open(emlFullPath, 'rb')
            else:
                fd = open(emlFullPath, 'rb')

            emlFile = emlFullPath.split('/')[-1].split('.')[0]

            jDumps = fd.read()
            fd.close()

            emlDict = json.loads(jDumps)

            for item in emlDict["body-items"]:
                nCategory   = item["Category"]
                ContentType = item["Content-Type"]
                data        = item["Data"]

                if nCategory != CONTENT_CAT_TEXT:
                    continue
                word_list   = data["Word-List"]
                domain_list = data["Domin-List"]
                
                check_pair = [(word_list, self.word_hash), (domain_list, self.domain_hash)]

                for pair in check_pair:
                    _list = pair[0]
                    _hash = pair[1]
                    for _at in _list:
                        try:
                            _set = _hash[_at]
                        except: # hash에 단어가 없다
                            continue
                        _set.add(emlFile)
            print("[%d/%d] " % (idx, ln_eml))
        return self.eml_hash

    def get_mailinfo_by_name(self, eml_name):
        #input : "2020-03-16-09:20:46:928388"
        #${HOME}/terracespamadm/20200313/1510/2020-03-13-15:11:48:842109.qs.gz
        #${HOME}/parsed_mails/terracespamadm/20200313/1510/2020-03-13-15:11:48:842109.json.gz
        
        yyyymmdd = eml_name[:10]
        hhmmss   = eml_name[11:19]
        YYYY     = yyyymmdd.split("-")[0]
        mm       = yyyymmdd.split("-")[1]
        dd       = yyyymmdd.split("-")[2]
        HH       = hhmmss.split(":")[0]
        MM       = hhmmss.split(":")[1]
        SS       = hhmmss.split(":")[2]

        common    = "terracespamadm/%s%s%s/%s%s0/%s" % (YYYY, mm, dd, HH, MM[0], eml_name)
        eml_path  = "%s/%s.qs" % (self.home_dir, common)
        json_path = "%s/parsed_mails/%s.json" % (self.home_dir, common)

        if os.path.exists(eml_path) == False:
            eml_path += ".gz"

        if os.path.exists(json_path) == False:
            json_path += ".gz"

        if os.path.exists(eml_path) == False or os.path.exists(json_path) == False:
            #print("Not exist %s" % (eml_path))
            #print("Not exist %s" % (json_path))
            return None

        if ".gz" == json_path[-3:]:
            fd = gzip.open(json_path, 'rb')
        else:
            fd = open(json_path, 'rb')
        jDumps = fd.read()
        fd.close()
        jsonData = json.loads(jDumps)

        subject = None
        if "subject" in jsonData["head-items"]:
            subject_list = jsonData["head-items"]["subject"][0]
            for item in subject_list:
                if item != None:
                    subject = item
                    break

        result_dict = {
            "subject"       : subject,
            "email-path"    : eml_path,
            "json-data"     : jsonData,
        }

        return result_dict


    def __load_word_dict(self):
        mgr = wordEmbeddingManager(embedding_size=2 ** 18,saved_embedding_path="data_package") # [embedding_size == 262,144]
        domainEmbedding = mgr.get_embedding_by_name("Domin-List")
        wordEmbedding   = mgr.get_embedding_by_name("Word-List")

        word_list   = wordEmbedding.get_word_list()
        domain_list = domainEmbedding.get_word_list()

        for word in word_list:
            self.word_hash[word] = set()

        for domain in domain_list:
            self.domain_hash[word] = set()
        return

    def __listup_eml(self, end_yyyymmdd):
        if end_yyyymmdd == None:
            end_yyyymmdd = "20190801"
        result_list = []
        start_yyyymmdd = datetime.date.today().strftime("%Y%m%d")
        print("%s ~ %s" % (start_yyyymmdd, end_yyyymmdd))
        search = emailSearch(self.home_dir + "/parsed_mails", end_yyyymmdd, start_yyyymmdd)
        search_days = search.list_days()
        for yyyymmdd in search_days:
            search_result = search.list_files(param_yyyymmdd=yyyymmdd)
            for emlPair in search_result:
                emlFile, yyyymmdd = emlPair
                if "terracespamadm" not in emlFile:
                    continue
                #print(emlFile)
                result_list.append(emlFile)
        return result_list

    def save_hash(self, _hash=None):
        save_path = "%s/word_dict/%s" % (self.home_dir, EL_SAVE_FILE_NAME)
        if _hash == None:
            _hash = self.eml_hash
        if _hash == None:
            return None
        if os.path.exists(save_path) == False:
            try:
                os.makedirs(save_path)
            except Exception as e:
                print(e)
                return False
        now_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = "%s_%s_eml_%d_embedding_%d" % (EL_SAVE_FILE_NAME, now_time, self.ln_eml, self.sz_embedding)
        full_name = "%s/%s.dat.gz" % (save_path, file_name)
        with gzip.open(full_name, "wb") as fd:
            pickle.dump(_hash, fd)
        link_name = "%s/%s.dat.gz" % (save_path, EL_SAVE_FILE_NAME)
        if os.path.exists(link_name) == True:
            os.remove(link_name)
        os.symlink(full_name, link_name)
        return full_name

    def load_hash(self):
        save_path = "%s/word_dict/%s" % (self.home_dir, EL_SAVE_FILE_NAME)
        link_name = "%s/%s.dat.gz" % (save_path, EL_SAVE_FILE_NAME)
        if os.path.exists(link_name) == False:
            print("[load_hash] Error. Fail to load hash : path=%s" % (link_name,))
            return None

        with gzip.open(link_name, "rb") as fd:
            self.eml_hash = pickle.load(fd)
        self.ln_eml       = self.eml_hash["ln_eml"]
        self.sz_embedding = len(self.eml_hash['Word-List'].keys())
        return self.eml_hash

def main():
    start_yyyymmdd = None # "20200301"
    base_dir = "/srkim/mnt/hdd250G/maildata"
    e = emlHashManager(base_dir)
    hash_data = e.make_hash(start_yyyymmdd)
    e.save_hash(hash_data)
    e.load_hash()

if __name__ == "__main__":
    main()


