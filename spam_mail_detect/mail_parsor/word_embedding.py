#!/bin/env python
# -*- coding: utf-8 -*-

'''
  Filename : mk_word_embedding.py
  Release  : 1
  Date     : 2020-02-24
 
  Description : mime extractor of spam detect module
  
  Notes :
  ===================
  History
  ===================
  2020/02/24 created 
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
import numpy as np
import pandas as pd

# local package import
from email_parser import *
from do_make_word_embedding import *

EMBEDDING_ONEHOT    = 0
EMBEDDING_INTEGER   = 1

EMAIL_TYPE_SPAM     = 0
EMAIL_TYPE_HAM      = 1

USAGE_TYPE_TEST     = 0
USAGE_TYPE_TRAIN    = 1

data_set_prefix     = "data_set"
word_embedding_package   = "data_package"
word_embedding_file_name = "data_set.dat"

# word_to_index : word를 입력하면 index를 반환, coding 을 통해 출력 형식int, onehot 선택 가능하다.
class wordEmbedding:
    def __init__(self, raw_list, embedding_name):
        self.raw_list       = raw_list
        dict_result         = self.__make_index()
        self.word_dict      = dict_result[0] # word to index
        self.count_dict     = dict_result[1] # word to count
        self.index_dict     = dict_result[2] # index to word
        self.sz_embedding   = len(raw_list)
        self.embedding_name = embedding_name

    def word_to_index(self, word, coding=EMBEDDING_ONEHOT):
        try:
            index = self.word_dict[word]
        except:
            return None

        if coding == EMBEDDING_INTEGER:
            return index
        elif coding == EMBEDDING_ONEHOT:
            return self.index_to_onehot(index)
        else:
            return None

    def index_to_word(self, index):
        if hasattr(index,'__iter__') == True:
            index = np.where(index==1.0)[0][0]
        return self.index_dict[index]

    def index_to_onehot(self, index):
        onehot = np.zeros(self.sz_embedding)
        onehot[index] = 1.0
        return onehot

    def onehot_to_index(self, onehot_vector):
        pass

    def __make_index(self):
        word_dict  = {} # word to index
        count_dict = {} # word to count
        index_dict = {} # index to word
        for idx, word_pair in enumerate(self.raw_list):
            word  = word_pair[0]
            count = word_pair[1]
            word_dict[word] = idx
            count_dict[word] = count
            index_dict[idx] = word
        return word_dict, count_dict, index_dict

    def convert_file_to_embedding(self, file_name, coding=EMBEDDING_ONEHOT):
        if os.path.exists(file_name) == False:
            return None
        if ".eml" in file_name.lower() or ".qs" in file_name.lower():
            e = emailParser(file_name)
            e.load_all()
            report = e.mk_mail_report()
        elif ".dat" in file_name.lower() or ".json" in file_name.lower():
            report = load_mail_report(file_name)
        else:
            return None
    
        embedding_list = []
        for body_item in report['body-items']:
            data = body_item['Data']
            for embedding_name in data.keys():
                #print(self.embedding_name)
                if embedding_name != self.embedding_name:
                    continue
                word_list = data[embedding_name]
                for word in word_list:
                    embedding_index = self.word_to_index(word, coding)
                    if type(embedding_index) == type(None):
                        continue
                    embedding_list.append(embedding_index)
        #embedding_list = np.array(embedding_list).reshape(-1,1)
        if len(embedding_list) == 0:
            return None
        return embedding_list

class wordEmbeddingManager:
    def __init__(self, embedding_size = 2 ** 16, coding=EMBEDDING_INTEGER, saved_embedding_path=None, max_size=None):
        e = makeWordEmbedding(None)
        self.objEmbedding = e.load()
        self.embedding_set  = {}
        self.data_set       = {}
        self.coding         = coding
        for embedding_name in embedding_name_list:
            self.embedding_set[embedding_name]  = self.__setup_embedding(embedding_name, embedding_size)
            self.data_set[embedding_name]       = { # embedding_name 별 임베딩 데이터 set 리스트 초기화
                "train_data"     : [],    # 학습 데이터
                "train_labels"   : [],    # 학습 라벨
                "test_data"      : [],    # 테스트 데이터
                "test_labels"    : [],    # 테스트 라벨
            }
        if saved_embedding_path != None:
            self.__load_data(saved_embedding_path, max_size)

    def shuffle_data_set(self):
        data_set = self.data_set
        for embedding_name in data_set.keys():
            embedding_set = data_set[embedding_name]
            #for label_name in embedding_set.keys():
            #    label_data = []
            #    save_info = embedding_set[label_name]
            train_data   = embedding_set["train_data"]
            train_labels = embedding_set["train_labels"]
            test_data    = embedding_set["test_data"]
            test_labels  = embedding_set["test_labels"]

            test_sequence   = [i for i in range(len(test_data))]
            train_sequence  = [i for i in range(len(train_data))]
            random.shuffle(test_sequence)
            random.shuffle(train_sequence)
            
            embedding_set["train_data"]     = [None,] * len(train_data)
            embedding_set["train_labels"]   = [None,] * len(train_data)
            embedding_set["test_data"]      = [None,] * len(test_data)
            embedding_set["test_labels"]    = [None,] * len(test_data)
        
            for idx,jdx in enumerate(train_sequence):
                embedding_set["train_data"][idx]    = train_data[jdx]
                embedding_set["train_labels"][idx]  = train_labels[jdx]

            for idx,jdx in enumerate(test_sequence):
                embedding_set["test_data"][idx]     = test_data[jdx]
                embedding_set["test_labels"][idx]   = test_labels[jdx]


    def __setup_embedding(self, embedding_name, embedding_size):
        if embedding_name not in self.objEmbedding.keys():
            return None
        embedding = self.objEmbedding[embedding_name]
        if len(embedding) < embedding_size:
            print("Insuffisant data of embedding : org=%d, input=%d" % (len(embedding), embedding_size))
            return None
        embedding = embedding[0:embedding_size]
        return wordEmbedding(embedding, embedding_name)

    def get_embedding_by_name(self, embedding_name):
        if embedding_name not in self.embedding_set.keys():
            return None
        return self.embedding_set[embedding_name]

    def get_data(self, embedding_name):
        if embedding_name not in self.data_set.keys():
            return (None,) * 4
        a_data_set = self.data_set[embedding_name]
        return a_data_set["train_data"], a_data_set["train_labels"], a_data_set["test_data"], a_data_set["test_labels"]

    def __load_data(self, data_file_name=None, max_size=None):
        def load_subdata(file_name):
            if ".gz" == file_name[-3:].lower():
                fd = gzip.open(file_name, "rb")
            else:
                fd = open(file_name, "rb")
            data_set = pickle.load(fd)
            fd.close()
            return data_set

        if data_file_name == None:
            data_file_name = word_embedding_package
        pickle_package_dir = "%s/%s/%s" % (word_dict_dir, data_set_prefix, data_file_name)
        pickle_file_name   = "%s/%s" % (pickle_package_dir, word_embedding_file_name)
        try:
            if ".gz" == pickle_file_name[-3:].lower():
                fd = gzip.open(pickle_file_name, "rb")
            else:
                fd = open(pickle_file_name, "rb")
            data_set = pickle.load(fd)
            fd.close()
        except Exception as e:
            print("Error. Fail to load data : %s" % e)
            return False
        for embedding_name in data_set.keys():
            embedding_set = data_set[embedding_name]
            for label_name in embedding_set.keys():
                label_data = []
                save_info = embedding_set[label_name]
                for partial_file in save_info:
                    if max_size != None:
                        if len(label_data) >= max_size:
                            continue
                    label_data += load_subdata(partial_file)
                    if max_size != None:
                        if len(label_data) > max_size:
                            label_data = label_data[0:max_size]
                embedding_set[label_name] = label_data
        self.data_set = data_set
        return True

    def __load_data2(self, data_file_name=None):
        pickle_file_name = data_file_name
        if data_file_name == None:
            data_file_name = word_embedding_file_name
            pickle_file_name = "%s/%s/%s" % (word_dict_dir, data_set_prefix, data_file_name)
        try:
            if ".gz" == pickle_file_name[-3:].lower():
                fd = gzip.open(pickle_file_name, "rb")
            else:
                fd = open(pickle_file_name, "rb")
            data_set = pickle.load(fd)
            fd.close()
        except Exception as e:
            print("Error. Fail to load data : %s" % e)
            return False
        self.data_set = data_set
        return True

    def save_data(self, data_file_name=None, save_a_file_max=10000, do_gzip=False): # save_a_file_max 을 넘기면 다음파일에..
        def save_subdata(label_data, pickle_package_dir, embedding_name, label_name, save_a_file_max, do_gzip=False):
            save_info = []
            ln_split  = int(len(label_data) / save_a_file_max)
            ln_remain = int(len(label_data) % save_a_file_max)
            for idx in range(ln_split+1):
                s_idx = (idx + 0) * save_a_file_max
                e_idx = (idx + 1) * save_a_file_max
                if ln_split == idx and ln_remain == 0:
                    continue
                elif ln_split == idx:
                    e_idx = s_idx+ln_remain
                #print("%d ~ %d" % (s_idx, e_idx))
                splited_data = label_data[s_idx:e_idx]
                save_name = "%s/splited_data_%s_%s_%d.dat" % (pickle_package_dir, embedding_name, label_name, idx)
                if do_gzip == True:
                    save_name += ".gz"
                    fd = gzip.open(save_name, "wb")
                else:
                    fd = open(save_name, "wb")
                pickle.dump(splited_data, fd)
                fd.close()
                save_info.append(save_name)
            return save_info
        if data_file_name == None:
            data_file_name = word_embedding_package
        data_set = copy.deepcopy(self.data_set)
        if self.coding != EMBEDDING_INTEGER:
            for embedding_name in embedding_name_list: # onehot 일 경우, INT으로 바꾼다.
                pass
        pickle_package_dir = "%s/%s/%s" % (word_dict_dir, data_set_prefix, data_file_name)
        if os.path.exists(pickle_package_dir) == False:
            try:
                os.makedirs(pickle_package_dir)
            except Exception as e:
                print(e)
                return False
        for embedding_name in data_set.keys():
            embedding_set = data_set[embedding_name]
            for label_name in embedding_set.keys():
                label_data = embedding_set[label_name]
                save_info = save_subdata(label_data, pickle_package_dir, embedding_name, label_name, save_a_file_max, do_gzip)
                embedding_set[label_name] = save_info
        pickle_file_name = "%s/%s" % (pickle_package_dir, word_embedding_file_name)

        if do_gzip == True:
            pickle_file_name += ".gz"
            fd = gzip.open(pickle_file_name, "wb")
        else:
            fd = open(pickle_file_name, "wb")
        pickle.dump(data_set, fd)
        fd.close()
        return True

    def add_training_data_from_file(self, file_name, label, usage=USAGE_TYPE_TRAIN): # 이메일 파일을 입력하면, dataset으로 변환
        for embedding_name in embedding_name_list:
            embedding = self.embedding_set[embedding_name]
            embedding_vector = embedding.convert_file_to_embedding(file_name, self.coding)
            if usage == USAGE_TYPE_TRAIN:
                data_name  = "train_data"
                label_name = "train_labels"
            else:
                data_name  = "test_data"
                label_name = "test_labels"
            self.data_set[embedding_name][data_name].append(embedding_vector)
            self.data_set[embedding_name][label_name].append(label)
        return True

def main():
    file_name = "./terracespamadm/20191215/2050/2019-12-15-20:56:27:537400.qs.gz"
    file_name2 = "/srkim/mnt/hdd250G/maildata/parsed_mails/terracehamadm/20190903/1220/2019-09-03-12:28:29:056506.json.gz"
    file_name3 = "./terracespamadm/20191215/2050/2019-12-15-20:56:25:639698.qs.gz"

    coding = EMBEDDING_INTEGER
    #coding = EMBEDDING_ONEHOT
    #mgr = wordEmbeddingManager(embedding_size = 2 ** 16, coding=coding) # 65536
    #mgr.add_training_data_from_file(file_name, EMAIL_TYPE_SPAM)
    #mgr.add_training_data_from_file(file_name2, EMAIL_TYPE_HAM)
    #mgr.add_training_data_from_file(file_name3, EMAIL_TYPE_HAM)
    #mgr.save_data()
    #return
    
    data_path = "data_package"
    mgr2 = wordEmbeddingManager(saved_embedding_path=data_path, max_size=50100)
    mgr2.shuffle_data_set()
    train_data, train_labels, test_data, test_labels = mgr2.get_data("Word-List")
    print("%s" % len(train_labels))

    #for embedding_name in embedding_name_list:
    #    embedding = mgr.get_embedding_by_name(embedding_name)
    #    onehot    = embedding.word_to_index('anemail')
    #    word      = embedding.index_to_word(1111)
    #    embedding_list = embedding.convert_file_to_embedding(file_name, EMBEDDING_INTEGER)
    #    print("%s : %s" % (embedding_name, embedding_list))
        
if __name__ == "__main__":
    main()
