#!/bin/env python
# -*- coding: utf-8 -*-

'''
  Filename : email_parser.py at mail_parsor
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

# email package import
import email

# local package import
from word_split import *
from email_header_parser import *
from email_content_parser import *
'''
{
    file-name  : "2020-02-06-16:09:10:557574.qs.gz"
    body-items : [
        {
            "Category"          : CONTENT_CAT_TEXT,
            "Sub-Category"      : CONTENT_SUBCAT_TEXT_HTML,
            "Content-Type"      : "text/plain" or "text/html", ...
            "Data"              : {
                "Word-List"     : ['Secure', 'your', 'web', 'assets', 'with', ... ]
                "URL-List"      : ['https://gallery.mailchimp.com/79cb120fb8178d/images/3a5cdd8832de85.png', ...]
                "Domin-List"    : ['www.acunetix.com', 'www.acunetix.com', ...]
            }
        }, ...
    ]
}
'''
class emailParser:
    def __init__(self, ps_path):
        self.ps_path    = ps_path
        self.email_obj  = None

    def load_all(self):
        try:
            nRet = self.__load_text()
            if nRet == None:
                return None
        except Exception as e:
            traceback.print_exc()
            return None
        return nRet

    def __load_text(self):
        f_start = False
        fd = None
        if self.ps_path[-3:].lower() == ".gz":
            fd = gzip.open(self.ps_path , 'rb')
        else:
            fd = open(self.ps_path , 'rb')

        rawAll = fd.read()
        fd.close()

        # .qs 파일일 경우, 메타데이터 제거
        if ".qs" in self.ps_path:
            for idx, at in enumerate(rawAll):
                if at == ord('\n'):
                    if b'%trqfile2%' in rawAll[:idx]:
                        rawAll = rawAll[idx+1:]
                    break
                elif idx == 1000:
                    break
            for idx in range(100, 1024 * 4):
                subline = rawAll[idx * -1:]
                if b"^^^^^^^^+_~!spacelee@$%^&!@#)_,$^^^^^^^^^^" in subline:
                    rawAll = rawAll[:idx * -1]
                    break

        self.email_obj = email.message_from_bytes(rawAll, policy=email.policy.SMTP)

        return True

    def __get_body_content(self):
        def __get_content_type_value(part):
            for head_key in part.keys():
                lower_key = ("%s" % head_key).lower()
                if lower_key == "content-type":
                    return part[head_key]
            return None
        parser = emailContentParser()

        result_list = []
        for idx,part in enumerate(self.email_obj.walk()):
            if part.is_multipart() == True:
                continue
            
            #parsed = parser.detect_content_category(__get_content_type_value(part))
            parsed = parser.detect_content_category(part.items())
            #print("%s %s" % (parsed,part.items()))
            if parsed == None:
                continue
            CATEGORY, SUB_CATEGORY, ContentType, ContentName = parsed

            headers = list(part.keys())
            try:
                body = part.get_content()
            except LookupError as e:
                print("Error. LookupError while get content e=%s" % (e,))
                continue

            parsedBody = parser.do_content_parser(headers, body, CATEGORY, SUB_CATEGORY, ContentType, ContentName)

            result_list.append(parsedBody)

        return result_list

    def __get_header_item(self):
        headers = self.email_obj.items()
        parsed = emailHeaderParser(headers)
        if parsed == None:
            return None
        return parsed.get_values()

    def mk_mail_report(self):
        report_dict = {
                "file-name"     : self.ps_path,
                "head-items"    : self.__get_header_item(),
                "body-items"    : self.__get_body_content(),
            }
        return report_dict

    def save_parsed_mail_info(self, base_path, report, do_gzip=False):
        spam_type = None
        yyyymmdd  = None
        hhmm      = None
        for item in self.ps_path.split("/"):
            if "terracespamadm" == item or "terracehamadm" == item:
                spam_type = item
            elif spam_type != None and len(item) == 8 and yyyymmdd == None:
                yyyymmdd = item
            elif yyyymmdd != None and hhmm == None and len(item) == 4:
                hhmm = item
        if spam_type == None or yyyymmdd == None or hhmm == None:
            return False

        path = "%s/%s/%s/%s" % (base_path, spam_type, yyyymmdd, hhmm)

        path_at = ""
        path_split = path.split("/")
        try:
            jDumps = json.dumps(report, indent=4, ensure_ascii=False)
        except Exception as e:
            print("[save_parsed_mail_info] Fail to dump to json report : Exception=%s" % (e,))

        for item in path_split:
            if item == '':
                continue
            path_at += "/%s" % (item,)
            if not os.path.exists(path_at):
                try:
                    os.makedirs(path_at)
                except Exception as e:
                    print("[save_parsed_mail_info] Fail to make dir : Exception=%s" % (e,))
                    return False
        new_name = self.ps_path.split("/")[-1].split('.')[0]
        full_name = "%s/%s.json" % (path_at, new_name)
 
        try:
            if do_gzip == True:
                full_name += ".gz"
                fd = gzip.open(full_name, "wb")
                jDumps = jDumps.encode('utf-8')
            else:
                fd = open(full_name, "w")
            fd.write(jDumps)
            fd.close()
        except Exception as e:
            print("[save_parsed_mail_info] Fail to save json data : Exception=%s" % (e,))
            return False

        #print("mail report saved st : %s" % (full_name,))

        return True       

def load_mail_report(report_path):
    report_dict = None
    try:
        if ".gz" in report_path:
            fd = gzip.open(report_path, "rb")
        else:
            fd = open(report_path, "rb")
        json_data = fd.read()
        fd.close()
        report_dict = json.loads(json_data)
    except Exception as e:
        print("Error in load_mail_report : %s" % (e,))
        traceback.print_exc()
    return report_dict

def main():
    ps_path = '/srkim/mnt/hdd250G/maildata/terracespamadm/20190902/0850/2019-09-02-08:50:04:525452.qs.gz'
    #ps_path = '/srkim/mnt/hdd250G/maildata/terracespamadm/20190902/0850/2019-09-02-08:59:56:300168.qs.gz'
    ps_path = '/srkim/mnt/hdd250G/maildata/terracespamadm/20190902/0850/2019-09-02-08:55:40:961260.qs.gz'
    ps_path = '/srkim/mnt/hdd250G/maildata/terracespamadm/20190902/0850/2019-09-02-08:50:53:180569.qs.gz'

    for ps_path in sys.argv[1:]:
        e = emailParser(ps_path)
        e.load_all()
        report = e.mk_mail_report()
        e.save_parsed_mail_info('/srkim/mnt/hdd250G/maildata/parsed_mails', report, do_gzip=True)
        #jDumps = json.dumps(report, indent=4, ensure_ascii=False)
        #print(jDumps)

if __name__ == "__main__":
    main()


