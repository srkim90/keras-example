#!/bin/env pypy
# -*- coding: utf-8 -*-
'''
  Filename : main.py
  Release  : 1
  Date     : 2019-11-26
 
  Description : main of spam detect module
  
  Notes :
  ===================
  History
  ===================
  2019/11/26 created 
'''
# common package import
from mime_extractor import *

C_END    = "\033[0m"
C_RED    = "\033[31m"
C_GREEN  = "\033[32m"

C_END    = ""
C_RED    = ""
C_GREEN  = ""

def merge_dict(org_dict, new_dict):
    if len(org_dict.keys()) == 0:
        org_dict = new_dict
        return org_dict
    new_keys = new_dict.keys()
    org_keys = org_dict.keys()
    ln_new   = len(new_keys)
    for idx,word in enumerate(new_keys):
        count_array = new_dict[word]
        ham_cnt     = count_array[0]
        spam_cnt    = count_array[1]
        ham_file    = count_array[2]
        spam_file   = count_array[3]
        try:
            org_dict[word][0] += ham_cnt
            org_dict[word][1] += spam_cnt
            org_dict[word][2] += ham_file
            org_dict[word][3] += spam_file
        except:
            org_dict[word] = count_array
    return org_dict

def dict_to_list(word_dict, min_count=50, min_file=5):
    report_list = []
    for word in word_dict.keys():
        count_array = word_dict[word]
        ham_cnt     = count_array[0]
        spam_cnt    = count_array[1]
        ham_file    = count_array[2]
        spam_file   = count_array[3]

        if ham_cnt + spam_cnt < min_count or ham_file + spam_file < min_file:
            continue
        
        if len(word) < 5:
            continue

        try:
            deleta = abs(spam_cnt - ham_cnt)
        except TypeError as e:
            print("<%s>:%s, <%s>:%s" % (type(spam_cnt), spam_cnt, type(ham_cnt), ham_cnt))
            continue

        rate = (float(max([spam_cnt, ham_cnt])) / float(spam_cnt + ham_cnt)) - 0.5

        if rate < 0.25:
            continue

        rate += float(deleta * 0.01) + float(len(word) * 0.075)

        report_at = {
            "judgment"      : "%s[spam]%s" % (C_RED, C_END) if spam_cnt > ham_cnt else "%s[ham] %s" % (C_GREEN, C_END),
            "word"          : word,
            "ham_cnt"       : ham_cnt,
            "spam_cnt"      : spam_cnt,
            "ham_file"      : ham_file,
            "spam_file"     : spam_file,
            "rate"          : rate,
        }
        report_list.append(report_at)

    report_list = sorted(report_list, key=itemgetter("rate"), reverse=True)

    return report_list

MAX_WORD_EMBEDDING = (128 * 128)

def main():
    base_dir  = "/srkim/mnt/hdd250G/maildata/word_dict"
    word_dict = {}
    json_list = []
    file_list = os.listdir(base_dir)
    for item in file_list:
        if ".json" not in item or ".dat" not in item:
            continue
        json_list.append("%s/%s" % (base_dir, item))

    for idx,file_name in enumerate(json_list):
        print("[%d/%d] Try file: %s (total words:%s)" % (idx+1, len(json_list), file_name, len(word_dict.keys())))
        try:
            with codecs.open("%s" % file_name , 'r', 'utf-8') as fd:
                json_data = fd.read()
            new_dict  = json.loads(json_data)
            word_dict = merge_dict(word_dict, new_dict)
        except Exception as e:
            print("Error. %s" % (e,))
            continue

    report_list = dict_to_list(word_dict)
    report_file = "%s/report.txt" % (base_dir,)

    with codecs.open(report_file, 'wb') as fd:
        for item in report_list:
            hem_report  = "ham_cnt=%d(%d)"  % (item["ham_cnt"], item["ham_file"],)
            spam_report = "spam_cnt=%d(%d)" % (item["spam_cnt"], item["spam_file"],)
            report_str  = "%s %-20s %-20s : %s" % (item["judgment"], hem_report, spam_report, item["word"])
            try:
                report_str = "%s\n" % (report_str,)
                fd.write(report_str.encode('utf-8'))
            except:
                print("Error : %s" % str_out)
    print("report file : %s" % (report_file,))

    word_embedding_dict = {}
    for idx, item in enumerate(report_list):
        if idx > MAX_WORD_EMBEDDING:
            break
        word_embedding_dict[idx] = item["word"]

    json_word_embedding = json.dumps(word_embedding_dict)
    
    report_file = "%s/word_embedding.json" % (base_dir,)
    with codecs.open(report_file, 'w') as fd:
        try:
            report_str = "%s\n" % (report_str,)
            fd.write(json_word_embedding.encode('utf-8'))
        except:
            print("Error : %s" % str_out)
    print("report json : %s" % (report_file,))

    return True

if __name__ == "__main__":
    main()
else:
    print("result_parser.py: Invalid bootstrapping")

