#!/bin/env python
# -*- coding: utf-8 -*-

'''
  Filename : check_similar_email.py
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
from operator import itemgetter

# local package import
from common import *
from do_make_element_hash import *

class emlChecker:
    def __init__(self, home_dir):
        self.home_dir = home_dir
        self.hash_mgr = emlHashManager(base_dir)
        self.hash_mgr.load_hash()
        self.embeddingMgr = wordEmbeddingManager(saved_embedding_path="data_package")

    def __open_mail(self, mail_path):
        if os.path.exists(mail_path) == False: 
            return None
        if ".qs" in mail_path.lower() or ".eml" in mail_path.lower():
            mail_obj = emailParser(mail_path)
            mail_obj.load_all()
            emlDict = mail_obj.mk_mail_report()
        elif ".json" in mail_path.lower():
            if mail_path[-3:].lower() == "gz":
                fd = gzip.open(mail_path, 'rb')
            else:
                fd = gzip.open(mail_path, 'rb')
            jDumps = fd.read()
            emlDict = json.loads(jDumps)
        else:
            return None
        return emlDict

    def check_mail(self, mail_path):
        emlDict = self.__open_mail(mail_path)
        if emlDict == None:
            print("[check_mail] Error. Not exist mail file : %s" % (mail_path,))
            return None

        ln_total_element = 0
        ln_embedding_element = 0
        similar_email_dict = dict()

        #TODO : 하나의 메일 안에 body는여러개일 수 있다. 우린 그 중 Text인 것 들만 조사한다.
        for item in emlDict["body-items"]:
            nCategory   = item["Category"]
            ContentType = item["Content-Type"]
            data        = item["Data"]

            if nCategory != CONTENT_CAT_TEXT:
                continue
            word_list   = data["Word-List"]
            domain_list = data["Domin-List"]

            check_pair = [(word_list, "Word-List"), (domain_list, "Domin-List")]
            
            for pair in check_pair:
                _hash_list = pair[0]
                _name_list = pair[1]
                _ln_list   = len(_hash_list)
                ln_total_element += _ln_list
                embedding = self.embeddingMgr.get_embedding_by_name(_name_list)
                for item in _hash_list:
                    if embedding.word_to_index(item, EMBEDDING_INTEGER) == None:
                        continue
                    ln_embedding_element += 1
                    list_of_have_element = self.hash_mgr.check_email_have_element(_name_list, item) # 각 element가 포함된 스펨메일 열거
                    if list_of_have_element == None:
                        continue
                    ln_have_element      = len(list_of_have_element)
                    #print("%d : %s" % (ln_have_element, item))
                    for other_eml in list_of_have_element:
                        try:
                            similar_email_dict[other_eml]["ln_checked_element"] += 1
                        except:
                            similar_email_dict[other_eml]  = {"ln_checked_element" : 1, "element_dict" : {}}
                        try:
                            similar_email_dict[other_eml]["element_dict"][_name_list].add(item)
                        except:
                            similar_email_dict[other_eml]["element_dict"][_name_list] = set(item)



        similar_email_list = []
        for other_eml in similar_email_dict.keys():
            #TODO: ln_embedding_element     : 검채의 element 중, pre-defined element에 포함 된 element에 개수
            #      ln_checked_element       : 유사하다고 판정 된 메일에서 검채의 element 와 일치 한 개수
            #       similar_rate            : 유사도; ln_checked_element/ln_embedding_element, (0.00 ~ 1.0)
            ln_checked_element  = similar_email_dict[other_eml]["ln_checked_element"]    # 해당 이메일에서, 검사하는 메일의 단어가 포함 된 개수
            element_dict        = similar_email_dict[other_eml]["element_dict"]
            similar_rate = float(ln_checked_element) / float(ln_embedding_element)      # 유사도 비율
            if similar_rate < 0.2:
                continue
            eml_info = self.hash_mgr.get_mailinfo_by_name(other_eml) # 유사하다고 판단 된 메일의 정보를 가져온다
            if eml_info == None:
                continue
            email_path  = eml_info["email-path"]
            json_data   = eml_info["json-data"]
            subject     = eml_info["subject"]
            mail_size   = get_mail_size(email_path)
            info_str    = "[%d/%d] %0.2f : %s %dKB <%s>" % (ln_checked_element, ln_embedding_element, similar_rate, email_path, int(mail_size/1024), subject)
            analyze_report = {
                "subject"               : subject,
                "email_path"            : email_path,
                "similar_rate"          : similar_rate,
                "ln_embedding_element"  : ln_embedding_element,
                "ln_checked_element"    : ln_checked_element,
                "json_data"             : json_data,
                "info_str"              : info_str,
                "element_dict"          : element_dict,
                "mail_size"             : mail_size,
            }
            if self.judge_report(analyze_report) == False:
                continue
            similar_email_list.append(analyze_report)

        if(len(similar_email_list) < 2):
            PRINT("유사한 메일 없음")
            return

        similar_email_list = sorted(similar_email_list, key=itemgetter('similar_rate', 'ln_checked_element'), reverse=True) # 정렬: similar_rate

        tot_element_dict = {} # 선별 된 유사 메일 리스트에서 검출 된 element의 참조 횟수를 취합한다.
        print("%s[유사도]%s[메일 경로]%s[Size]%s[Subject]" % (" "*2, " "*5, " "*80, " "*8))
        for report in similar_email_list:
            similar_rate    = report["similar_rate"]
            subject         = report["subject"]
            info_str        = report["info_str"]
            element_dict    = report["element_dict"]
            for embedding_name in element_dict:
                element_set = element_dict[embedding_name]
                if embedding_name not in tot_element_dict.keys():
                    tot_element_dict[embedding_name] = {}
                for element in element_set:
                    try:
                        tot_element_dict[embedding_name][element] += 1
                    except:
                        tot_element_dict[embedding_name][element]  = 1
            print(info_str)

        max_refernce_cnt = None
        common_keywords  = {}
        for embedding_name in tot_element_dict.keys():
            for element in tot_element_dict[embedding_name]:
                refernce_cnt = tot_element_dict[embedding_name][element]
                if max_refernce_cnt == None or refernce_cnt > max_refernce_cnt:
                    max_refernce_cnt = refernce_cnt
        for embedding_name in tot_element_dict.keys():
            for element in tot_element_dict[embedding_name]:
                refernce_cnt = tot_element_dict[embedding_name][element]
                #if refernce_cnt < max_refernce_cnt:
                #    continue
                appear_rate = refernce_cnt / float(max_refernce_cnt)
                if appear_rate < 0.4: # 출연빈도 낮은 element 는 Skip!
                    continue
                try:
                    common_kw_list = common_keywords[embedding_name]
                except:
                    common_keywords[embedding_name] = []
                    common_kw_list = common_keywords[embedding_name]
                common_kw_list.append((element, appear_rate))

        print("")
        print("[공통 등장 단어]")

        black_kw_string = ""
        for embedding_name in common_keywords.keys():
            common_kw_list = common_keywords[embedding_name]
            common_kw_list = sorted(common_kw_list, key = lambda x : (x[1],), reverse=True)
            for element_pair in common_kw_list:
                element     = element_pair[0]
                appear_rate = element_pair[1]
                black_kw_string += "\"(%s:%0.2f)\", " % (element, appear_rate)
        print(black_kw_string)


    def judge_report(self, report):
        #subject                 = report["subject"]
        #email_path              = report["email_path"]
        similar_rate            = report["similar_rate"]
        ln_embedding_element    = report["ln_embedding_element"]
        ln_checked_element      = report["ln_checked_element"]
        json_data               = report["json_data"]
        if similar_rate < 0.5:
            return False
        if ln_checked_element < 15:
            return False

        return True

###########################################################
# START Test code
###########################################################

class __mmc_quit(mmc):
    @staticmethod
    def run(command):
        exit_handler()

class __mmc_help(mmc):
    @staticmethod
    def run(command):
        PRINT("check similar_mail ./issue/TMSE-4231_1.eml")
        PRINT("check similar_mail ./issue/TMSE-4231_2.eml")
        PRINT("check similar_mail ./issue/TMSE-4232_1.eml")
        PRINT("check similar_mail /srkim/mnt/hdd250G/maildata/terracespamadm/20200224/1840/2020-02-24-18:47:15:753529.qs.gz")
        PRINT("check similar_mail /srkim/mnt/hdd250G/maildata/terracespamadm/20200224/1840/2020-02-24-18:44:57:780349.qs.gz")


class __mmc_check_similar_mail(mmc):
    @staticmethod
    def run(command):
        input_mail = command[-1]
        if os.path.exists(input_mail) == False: 
            PRINT("Error. Not exist mail file : '%s'" % input_mail)
            return
        g_checker.check_mail(input_mail)
        return 

__mmc = [ 
          ["quit",                0, "quit"                                  , __mmc_quit                    ],  
          ["check",               0, "check"                                 , None                          ],
          ["help",                0, "help"                                  , __mmc_help                    ],
          ["similar_mail",        1, "check-similar_mail"                    , None                          ],
          ["mail_path",           2, "check-similar_mail-S"                  , __mmc_check_similar_mail      ],
        ]

def mmc_run(index, name):
    mmc_parse.instance(__mmc, index, name)
    e = mmc_parse.getinstance()    
    sa_get_log_object().set_check_pos_fn(e.check_pos)
    return e.run()

def main():
    global g_checker
    base_dir = "/srkim/mnt/hdd250G/maildata" 
    e = emlChecker(base_dir)
    g_checker = e
    
    input_maillist = sys.argv[1:]

    if len(input_maillist) == 0:
        log_index = 0
        log_name  = "check_similar_email"
        sa_initlog(log_name, log_index)
        return mmc_run(log_index, log_name)
    else:
        for ps_path in input_maillist:
            e.check_mail(ps_path)

if __name__ == "__main__":
    main()


