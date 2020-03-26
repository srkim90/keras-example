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
#from PIL import Image, ImageDraw
import PIL
from time import *
from PIL import ImageDraw
from tkinter import *

# keras package import
from keras import models
from keras import layers
from keras.utils import to_categorical
from keras.datasets import imdb
from keras import optimizers

sys.path.append('./mail_parsor')
sys.path.append('./3th')
from word_embedding import *

def vectorize_sequences(sequences, dimension):
    # 크기가 (len(sequences), dimension))이고 모든 원소가 0인 행렬을 만듭니다
    results = np.zeros((len(sequences), dimension))
    for i, sequence in enumerate(sequences):
        results[i, sequence] = 1.  # results[i]에서 특정 인덱스의 위치를 1로 만듭니다
        #sequence.sort()
        #print("%d:%s" % (i, sequence))
    return results


def main():
    embedding_size = 22000
    (train_data, train_labels), (test_data, test_labels) = imdb.load_data(num_words=embedding_size)
    mgr = wordEmbeddingManager(saved_embedding_path="data_package", max_size=250000)
    train_data, train_labels, test_data, test_labels = mgr.get_data("Domin-List")

    embedding_size = mgr.get_embedding_size()# + 1

    #for item in train_data:
    #    for idx, value in enumerate(item):
            

    print(train_data[0])

    #word_index = imdb.get_word_index()
    #reverse_word_index = dict([(value, key) for (key, value) in word_index.items()])

    #decoded_review = ' '.join([reverse_word_index.get(i - 3, '?') for i in train_data[0]])
    #print(decoded_review)

    x_train = vectorize_sequences(train_data, embedding_size)
    x_test = vectorize_sequences(test_data, embedding_size)

    y_train = np.asarray(train_labels).astype('float32')
    y_test = np.asarray(test_labels).astype('float32')

    model = models.Sequential()
    model.add(layers.Dense(16 * 4, activation='relu', input_shape=(embedding_size,)))
    model.add(layers.Dense(16 * 4, activation='relu'))
    model.add(layers.Dense(1, activation='sigmoid'))

    model.compile(optimizer=optimizers.RMSprop(lr=0.001),
              loss='binary_crossentropy',
              metrics=['accuracy'])

    x_val = x_train[:embedding_size]
    partial_x_train = x_train[embedding_size:]

    y_val = y_train[:embedding_size]
    partial_y_train = y_train[embedding_size:]

    history = model.fit(partial_x_train,
                    partial_y_train,
                    #epochs=20,
                    #batch_size=512,
                    epochs=20 ,
                    batch_size=512 * 8,
                    validation_data=(x_val, y_val))

    predictions = model.predict(x_test)

    fail_cnt = 0
    suss_cnt = 0
    for idx,predict in enumerate(predictions):
        actual_label = y_test[idx]
        if abs(actual_label - predict) > 0.35:
            fail_cnt += 1
        else:
            suss_cnt += 1
    print("fail_cnt=%d, suss_cnt=%d rate=%f" % (fail_cnt, suss_cnt, 100.0 - (float(fail_cnt)/float(suss_cnt)) * 100))

    print(predictions)

    return

if __name__ == "__main__":
    main()
