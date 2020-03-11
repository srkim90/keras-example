# -*- coding: utf-8 -*-

'''
  Filename : mime_extractor.py
  Release  : 1
  Date     : 2019-11-26
 
  Description : mime extractor of spam detect module
  
  Notes :
  ===================
  History
  ===================
  2019/11/26 created 
'''
# common package import
import re
import os
import sys
import time
import codecs
import chardet
from numba import jit

min_word_len      = 3
max_word_len      = 12
remove_char       = ['\r', '\n']
split_char        = ['\t']
split_char_inc    = ['.', ',', '"', '\'', '[', ']', '<', '>', '*', '(', ')', ';'] # split char include separator
delete_if_include = [ '<tr>', '</tr>', '<td>', '</td>', '<table', '</table', '/p>', '<p>', '=",' ] # delete if include
special_char      = ['~', '!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '_', '+', ',', '.', '?', '`', '=', '/', '\\']

#@jit
def listup_urls(decoded_body):
    url_skip    = ['\r', '\n']
    url_stop    = [',', '"', '\'', ' ', '\t', '>', ')', ']']
    url_schemes = ["http://", "https://", "mailto:", "ftp://", "sftp://", ]
    decoded_low = decoded_body.lower()
    len_body    = len(decoded_body)

    url_listup = []
    url_listup_org = []
    domain_listup = []

    for scheme in url_schemes:
        start_idxs = [m.start() for m in re.finditer(scheme, decoded_low)]
        for start_idx in start_idxs:
            for idx in range(start_idx,len_body):
                char_at = decoded_body[idx]
                if char_at in url_skip:
                    continue
                if char_at in url_stop:
                    break
                if ord(char_at) < 32 or ord(char_at) > 126:
                    break # ASCII 이외 제거
            url_text = decoded_body[start_idx:idx]
            #print(url_text)
            #url_text = url_text.split('?')[0] # 파라미터 제거
            url_listup_org.append(url_text)
            for skip_at in url_skip:
                url_text = url_text.replace(skip_at,"")
            try:
                doamin_text = url_text.split(scheme)[1]
                doamin_text = doamin_text.replace(':', ' ')
                doamin_text = doamin_text.replace('/', ' ')
                doamin_text = doamin_text.split(' ')[0]
                doamin_text = doamin_text.split('@')[-1]
                domain_listup.append(doamin_text)
            except:
                pass
            url_listup.append(url_text)
    #print(decoded_body)
    for url_at in url_listup_org:
        #print("!! %s" % url_at)
        decoded_body = decoded_body.replace(url_at, ' ')

    return decoded_body, url_listup, domain_listup

#@jit
def do_word_split(decoded_body):
    re_hangule  = re.compile("^[\u3131-\u318E\uAC00-\uD7A3]*$")
    re_alphabet = re.compile("^[a-zA-Z]*$")
    re_number   = re.compile("^[0-9]*$")
    re_bar      = re.compile("^[-_]*$")

    re_must     = [re_hangule, re_alphabet, re_number]
    re_list     = [re_hangule, re_alphabet, re_number, re_bar]
    re_language = [{"language": "hangule", "data" : re_hangule}, {"language" : "alphabet", "data" : re_alphabet}]

    result_list = []

    # 1. URL 분리
    decoded_body, url_listup, domain_listup = listup_urls(decoded_body)
    
    #print(decoded_body)

    # 2. 개행 제거
    for char in remove_char:
        decoded_body = decoded_body.replace(char, '')

    # 3. 텝 치환
    for char in split_char:
        decoded_body = decoded_body.replace(char, ' ')

    # 4. 구분자 치환
    for char in split_char_inc:
        decoded_body = decoded_body.replace(char, char + ' ')
 
    # 5. 문자열 토큰화
    decoded_body = decoded_body.split(' ')
    for word in decoded_body:
        if word in delete_if_include:
            continue
        ln_special = 0
        # 5.1 특수문자로만 이루어져있으면 skip
        for special_at in special_char:
            if special_at in word:
                ln_special += 1
        if len(word) == ln_special:
            continue
    
        # 5.2 너무 잛은 문자 재외
        if len(word) < min_word_len:
            continue

        # 5.3 알파뱃, 한글, 숫자가 아닌것 기준으로 split
        f_skip        = False
        sub_text      = ""
        sub_text_list = []
        for idx, char in enumerate(word):
            n_checked = 0
            for re_item in re_list:
                if re_item.match(char) != None:
                    n_checked += 1
            if n_checked == 0:
                f_skip = True
            if f_skip == False:
                sub_text += char
            if f_skip == True or idx + 1 == len(word):
                f_skip = False
                if len(sub_text) != 0:    
                    #print("word: %s , sub_text: %s" % (word, sub_text))
                    if len(sub_text) >= min_word_len and len(sub_text) <= max_word_len:
                        #result_list.append(sub_text)
                        sub_text_list.append(sub_text)
                    sub_text = ""

        # 5.4 언어별로 분리 한다.
        sub_text       = ""
        old_language   = None
        sub_text_list2 = []
        for word in sub_text_list:
            sub_text     = ""
            old_language = None
            #print("-------------------")
            for idx, char in enumerate(word):
                for language_dict in re_language:
                    language = language_dict["language"]
                    re_item = language_dict["data"]
                    #print("idx=%d char=%s %s %s" % (idx, char, language, re_item.match(char)))
                    if re_item.match(char) != None:
                        if old_language != language and idx != 0:
                            #print(sub_text)
                            if len(sub_text) >= min_word_len and len(sub_text) <= max_word_len:
                                sub_text_list2.append(sub_text)
                            sub_text = ""
                            old_language = language
                            break
                        elif idx == 0:
                            old_language = language
                sub_text += char
        if sub_text != "":
            if re_bar.match(sub_text) == None:
                if len(sub_text) >= min_word_len and len(sub_text) <= max_word_len:
                    sub_text_list2.append(sub_text)

        result_list += sub_text_list2

    return result_list, url_listup, domain_listup
