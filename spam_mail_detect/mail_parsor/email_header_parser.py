#!/bin/env python
# -*- coding: utf-8 -*-

'''
  Filename : email_header_parser.py at mail_parsor
  Release  : 1
  Date     : 2020-02-23
   
  Description : mime extractor of spam detect module
  
  Notes :
  ===================
  History
  ===================
  2020/02/23 created 
'''

# common package import
import re
import os
import sys
import time
import json
import quopri
import base64
import codecs
import chardet
import traceback

'''
{
    # 동일한 header가 2개 이상 일 경우, value를 list로 한다.
    "received"      : [ (from, ["110.9.209.145", "110.9.209.142,"... ]), (by, [...]), (with, [...]), (for, [...]), (date, []) ]
    "content-type"  : [ (None, "text/plain"), ("name", "aaa.png") ]
}
'''

class emailHeaderParser:
    def __init__(self, header_list, check_list=None):
        # header_list : [(key1, values), (key2, values), ..]
        # e.g.        : [, .., ("Content-Type", "text/plain; charset=utf-8; format=flowed; DelSp=Yes"), ..]
        #print(header_list)
        self.check_list  = check_list
        self.header_list = header_list
        self.result_dict = None
        self.header_dict = {
            "content-type"  : self.__handle_content_type,   # tags: None, name, ...
            "received"      : self.__handle_received,       # tags: from, by, with, for, date
            "subject"       : self.__handle_subject,        # tags: None
        }
        self.__do_value_parsing()

    def get_values(self):
        return self.result_dict

    def get_value_from_header_name(self, header, tag=None, pos=None):
        if self.result_dict == None:
            return None
        lower_header = header.lower()
        #print(": %s" % lower_header)
        if lower_header not in self.result_dict.keys():
            return None
        if tag != None:
            for tag_at in self.result_dict[lower_header]:
                __tag     = tag_at[0]
                __value   = tag_at[1]
                if __tag == None:
                    continue
                if tag.lower() == __tag.lower():
                    return __value
            return None
        if pos != None:
            tag_list = self.result_dict[lower_header]
            if len(tag_list) <= pos:
                return None
            return tag_list[pos][1]
        return self.result_dict[lower_header]

    def __parser_tag_vaule(self, str_value):
        result_list = []
        str_value = str_value.replace("\r", " ")
        str_value = str_value.replace("\n", " ")
        str_value = str_value.replace("\t", " ")
        str_value = str_value.strip()
        str_value = str_value.split(";")
        for item in str_value:
            item = item.strip()
            if item.count('=') == 1:
                item  = item.split("=")
                tag   = item[0].strip().lower()
                value = item[1]
            else:
                tag   = None
                value = item
            value = value.strip()
            value = value.replace("\"", "")
            value = value.replace("'", "")
            result_list.append((tag, value))
        return result_list

    def __handle_subject(self, header, str_value):
        header = header.lower()
        self.result_dict[header] = [(None, str_value)]

    def __handle_content_type(self, header, str_value):
        header      = header.lower()
        result_list = self.__parser_tag_vaule(str_value)
        if result_list != None:
            self.result_dict[header] = result_list

    def __handle_received(self, header, str_value):
        def __parser_received_addrs(str_line):
            result_list = []
            if '[' not in str_line or ']' not in ']':
                if '(' in str_line and ')' in str_line:
                    str_line = str_line.replace("(", "[")
                    str_line = str_line.replace(")", "]")
                else:
                    return None
            str_line = str_line.split("[")
            for str_st in str_line:
                ipaddr = str_st.split("]")[0].strip()
                result_list.append(ipaddr)

            return result_list
        header      = header.lower()
        result_list = self.__parser_tag_vaule(str_value)
        if result_list == None:
            return
        separators = ["from",] #, "by", "with", "for"]
        parsed_dict = self.__split_as_items(result_list[0][1], separators)
        #print(parsed_dict)
        #parsed_dict = {'from': 'KEIT-DDEI (unknown [127.0.0.1])', 'by': 'DDEI (Postfix)', 'with': 'SMTP id 130051B65852', 'for': '<parkorea@keit.re.kr>'}

        result_dict = {}
        for key in separators:
            value = None
            if key not in parsed_dict.keys():
                result_dict[key] = None
                continue
            if key == "from":
                value = __parser_received_addrs(parsed_dict[key])
                if value != None:
                    value = value[-1]
            elif key == "by":
                pass
            elif key == "with":
                pass
            elif key == "for":
                pass
            else:
                pass
            result_dict[key] = value
        if header not in self.result_dict.keys():
            result_hdr = []
            for key in separators:
                result_hdr.append((key, [result_dict[key],]))
            self.result_dict[header] = result_hdr
        else:
            for idx, key in enumerate(separators):
                self.result_dict[header][idx][1].append(result_dict[separators[idx]])
        return

    def __handle_defaule(self, header, str_value):
        pass
    
    def __split_as_items(self, string, separators):
        # [input]
        #   string      : from SN6PR08MB4287.com ([fe80::c07c:52f2:dc36:42a7]) by SN6PR7.namprd08.com ([fe80::c07c:52f2:dc36:42a7%4]) with mapi id 15.20.2474.022
        #   separators  : ["from", "by", "with", "for"]
        # [output]
        #   {
        #        from    : 'SN6PR08MB4287.com ([fe80::c07c:52f2:dc36:42a7])',
        #        by      : 'SN6PR7.namprd08.com ([fe80::c07c:52f2:dc36:42a7%4])',
        #        with    : 'mapi id 15.20.2474.022',
        #   }
        result_dict = {}
        for separ_at in separators:
            if "%s " % separ_at not in string:
                continue
            string_at = " %s" % string
            string_at = string_at.split("%s " % separ_at)[1]
            for separ_in in separators:
                if separ_in == separ_at:
                    continue
                if separ_in in string_at:
                    string_at = string_at.split("%s " % separ_in)[0]
            string_at = string_at.strip()
            result_dict[separ_at] = string_at
        return result_dict


    def __do_value_parsing(self):
        self.result_dict = {}
        for header_set in self.header_list:
            header, str_value = header_set
            header_lower = header.lower()
            handle_fn = self.__handle_defaule
            #print("%s %s" % (header_lower, type(str_value)))
            if self.check_list != None:
                if header_lower not in self.check_list:
                    continue
            if header_lower in self.header_dict.keys():
                handle_fn = self.header_dict[header_lower] 
            handle_fn(header, str_value)
        
        return self.result_dict









