#!/bin/env python
# -*- coding: utf-8 -*-

'''
  Author   : Kim, Seongrae
  Filename : boston_housing.py
  Release  : 1
  Date     : 2020-02-07
 
  Description : Stock Simulator Main module
 
  Notes :
  ===================
  History
  ===================
  2020/02/07  created by Kim, Seongrae
'''


# common package import
import os
import json
import numpy as np
from time import *

# keras package import
from keras import models
from keras import layers
from keras.datasets import boston_housing

def main():
    (train_data, train_targets), (test_data, test_targets) = boston_housing.load_data()   
    
    return

if __name__ == "__main__":
    main()

