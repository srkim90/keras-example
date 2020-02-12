#!/bin/env python
# -*- coding: utf-8 -*-

'''
  Author   : Kim, Seongrae
  Filename : imdb.py
  Release  : 1
  Date     : 2020-02-06
 
  Description : Stock Simulator Main module
 
  Notes :
  ===================
  History
  ===================
  2020/02/06  created by Kim, Seongrae
'''


# common package import
import os
import json
import numpy as np
from time import *

# keras package import
#from keras import models
#from keras import layers
#from keras.utils import to_categorical
#from keras.datasets import imdb
#from keras import optimizers
from keras.preprocessing.text import Tokenizer

def main():
    samples = ['The cat sat on the mat.', 'The dog ate my homework.']

    # 가장 빈도가 높은 1,000개의 단어만 선택하도록 Tokenizer 객체를 만듭니다.
    tokenizer = Tokenizer(num_words=1000)
    # 단어 인덱스를 구축합니다.
    tokenizer.fit_on_texts(samples)

    # 문자열을 정수 인덱스의 리스트로 변환합니다.
    sequences = tokenizer.texts_to_sequences(samples)

    # 직접 원-핫 이진 벡터 표현을 얻을 수 있습니다.
    # 원-핫 인코딩 외에 다른 벡터화 방법들도 제공합니다!
    one_hot_results = tokenizer.texts_to_matrix(samples, mode='binary')

    # 계산된 단어 인덱스를 구합니다.
    word_index = tokenizer.word_index
    print('Found %s unique tokens.' % len(word_index))

    test_text = "sat on the mat"
    sequences = tokenizer.texts_to_sequences([test_text])[0]
    print("sequences : ",sequences)                 
    print("word_index : ",tokenizer.word_index)     # 단어 집합(vocabulary) 출력
    return

if __name__ == "__main__":
    main()
