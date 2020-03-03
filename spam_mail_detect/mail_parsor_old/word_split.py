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

min_word_len      = 4
remove_char       = ['\r', '\n']
split_char        = ['\t']
split_char_inc    = ['.', ',', '"', '\'', '[', ']', '<', '>', '*', '(', ')', ';'] # split char include separator
delete_if_include = [ '<tr>', '</tr>', '<td>', '</td>', '<table', '</table', '/p>', '<p>', '=",' ] # delete if include
special_char      = ['~', '!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '_', '+', ',', '.', '?', '`', '=', '/', '\\']

def listup_urls(decoded_body):
    url_stop    = [',', '"', '\'', ' ', '\t', '>', ')', ']', '\r', '\n']
    url_schemes = ["http://", "https://", "mailto:", "ftp://", "sftp://", ]
    decoded_low = decoded_body.lower()
    len_body    = len(decoded_body)

    url_listup = []
    domain_listup = []

    for scheme in url_schemes:
        start_idxs = [m.start() for m in re.finditer(scheme, decoded_low)]
        for start_idx in start_idxs:
            for idx in range(start_idx,len_body):
                char_at = decoded_body[idx]
                if char_at in url_stop:
                    break
                if ord(char_at) < 32 or ord(char_at) > 126:
                    break # ASCII 이외 제거
            url_text = decoded_body[start_idx:idx]
            url_text = url_text.split('?')[0] # 파라미터 제거
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
    for url_at in url_listup:
        decoded_body = decoded_body.replace(url_at, ' ')

    return decoded_body, url_listup, domain_listup

def do_word_split(decoded_body):
    result_list = []

    # 1. URL 분리
    decoded_body, url_listup, domain_listup = listup_urls(decoded_body)
    
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

        result_list.append(word)
    return result_list, url_listup, domain_listup
