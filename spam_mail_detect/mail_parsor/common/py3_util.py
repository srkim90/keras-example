# -*- coding: utf-8 -*-

'''
  Author   : Kim, Seongrae
  Filename : py3_util.py
  Release  : 1
  Date     : 2018-09-11
 
  Description : utility for python3
 
  Notes :
  ===================
  History
  ===================
  2018/09/11  created by Kim, Seongrae
'''
import struct

def mmc_print(string, end=None, flush=False):
    __mmc_print=print
    __mmc_print(string, end=end, flush=flush)


def get_mail_size(email_path):
    if email_path[-3:].lower() == ".gz":
        return getuncompressedsize(email_path)
    else:
        return os.path.getsize(email_path)

def getuncompressedsize(filename):
    with open(filename, 'rb') as f:
        f.seek(-4, 2)
        return int(struct.unpack('I', f.read(4))[0])

