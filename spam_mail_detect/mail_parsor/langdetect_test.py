#!/bin/env python
# -*- coding: utf-8 -*-

'''
  Filename : langdetect_test.py
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
import quopri
import base64
import codecs
import chardet
import traceback
import langdetect

#need "python -m pip install langdetect"

def main():
    test_set = [
                "AAA1",
                "BBB2",
                "cCC3",
                "111hang",
                "김성래",
                "가나다라밤",
                "特殊文字のみ構成されている場合、",
            ]

    for item in test_set:
        print("%s : %s" % (langdetect.detect(item), item))

if __name__ == "__main__":
    main()


