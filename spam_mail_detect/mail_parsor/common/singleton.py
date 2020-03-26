# -*- coding: utf-8 -*-

'''
  Author   : Kim, Seongrae
  Filename : singleton.py
  Release  : 1
  Date     : 2018-07-02
 
  Description : singleton module for python
 
  Notes :
  ===================
  History
  ===================
  2018/07/02  created by Kim, Seongrae
'''
class singleton_instance:
    __instance = None

    @classmethod
    def getinstance(cls):
        return cls.__instance

    @classmethod
    def instance(cls, *args, **kargs):
        cls.__instance = cls(*args, **kargs)
        cls.instance = cls.getinstance
        return cls.__instance



