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
import datetime 
import numpy as np

#python -m pip install nltk
from do_make_word_embedding import *

EMBEDDING_ONEHOT    = 0
EMBEDDING_INTEGER   = 1

class wordEmbedding:
    def __init__(self, raw_list):
        self.raw_list       = raw_list
        dict_result         = self.__make_index()
        self.word_dict      = dict_result[0] # word to index
        self.count_dict     = dict_result[1] # word to count
        self.index_dict     = dict_result[2] # index to word
        self.sz_embedding   = len(raw_list)

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

class wordEmbeddingManager:
    def __init__(self):
        e = makeWordEmbedding(None)
        self.objEmbedding = e.load()    

    def get_embedding(self, embedding_name, max_size):
        if embedding_name not in self.objEmbedding.keys():
            return None
        embedding = self.objEmbedding[embedding_name]
        if len(embedding) < max_size:
            print("Insuffisant data of embedding : org=%d, input=%d" % (len(embedding), max_size))
            return None
        embedding = embedding[0:max_size]
        return wordEmbedding(embedding)

def main():
    mgr     = wordEmbeddingManager()
    e       = mgr.get_embedding("WordEmbedding", 2 ** 16) # 65536
    onehot  = e.word_to_index('anemail')
    word    = e.index_to_word(1111)
    print(word)
        
if __name__ == "__main__":
    main()
