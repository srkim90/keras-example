#!/bin/env python
# -*- coding: utf-8 -*-

'''
  Filename : email_content_parser.py at mail_parsor
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
import json
import quopri
import base64
import codecs
import chardet
import traceback

# email package import
import email
from email import policy
from email.header import decode_header

# 3th package import
sys.path.append("../3th")
import html2text
#from flanker import mime

# local package import
from word_split import *
from email_header_parser import *

# CATEGORY <같은 CATEGORY내에서는 출력 형식이 동일하다.>
CONTENT_CAT_TEXT                = 1000 # text/plain, text/html
CONTENT_CAT_IMAGE               = 2000 # image/jpeg, image/png
CONTENT_CAT_DOC                 = 3000 # application/msword, application/pdf ...
CONTENT_CAT_ARCHIVE             = 4000 # application/zip, application/x-rar-compressed

# SUB-CATEGORY
CONTENT_SUBCAT_TEXT_PLAIN       = CONTENT_CAT_TEXT      + 1  # text/plain
CONTENT_SUBCAT_TEXT_HTML        = CONTENT_CAT_TEXT      + 2  # text/html <Text만 추출 한다.>

CONTENT_SUBCAT_IMAGE_JPGE       = CONTENT_CAT_IMAGE     + 1  # *.jpeg, *.jpg
CONTENT_SUBCAT_IMAGE_PNG        = CONTENT_CAT_IMAGE     + 2  # *.png
CONTENT_SUBCAT_IMAGE_GIF        = CONTENT_CAT_IMAGE     + 3  # *.gif
CONTENT_SUBCAT_IMAGE_BMP        = CONTENT_CAT_IMAGE     + 4  # *.bmp
CONTENT_SUBCAT_IMAGE_ISO9660    = CONTENT_CAT_IMAGE     + 5  # *.img (?)

CONTENT_SUBCAT_DOC_MSWORD_COMP  = CONTENT_CAT_DOC       + 1  # *.doc  <MS Compound>
CONTENT_SUBCAT_DOC_MSWORD_ZIP   = CONTENT_CAT_DOC       + 2  # *.docx <ZIP>
CONTENT_SUBCAT_DOC_PDF          = CONTENT_CAT_DOC       + 3  # *.pdf

CONTENT_SUBCAT_ARCHIVE_ZIP      = CONTENT_CAT_ARCHIVE   + 1  # *.zip
CONTENT_SUBCAT_ARCHIVE_GZIP     = CONTENT_CAT_ARCHIVE   + 2  # *.gz
CONTENT_SUBCAT_ARCHIVE_RAR      = CONTENT_CAT_ARCHIVE   + 3  # *.rar

# Content Type parsing rule table
content_type_map = [
    # CATEGORY            # SUB-CATEGORY                   # type of mime header            # *.xxx
## Text
    ( CONTENT_CAT_TEXT,     CONTENT_SUBCAT_TEXT_PLAIN,      "text/plain"                    ,  None     ),
    ( CONTENT_CAT_TEXT,     CONTENT_SUBCAT_TEXT_HTML,       "text/html"                     ,  None     ),

## Images
    ( CONTENT_CAT_IMAGE,    CONTENT_SUBCAT_IMAGE_PNG,       "image/png"                     ,  None     ),
    ( CONTENT_CAT_IMAGE,    CONTENT_SUBCAT_IMAGE_JPGE,     ("image/jpg",\
                                                            "image/jpeg")                   ,  None     ),
    ( CONTENT_CAT_IMAGE,    CONTENT_SUBCAT_IMAGE_GIF,       "image/gif"                     ,  None     ),
    ( CONTENT_CAT_IMAGE,    CONTENT_SUBCAT_IMAGE_BMP,       "image/bmp"                     ,  None     ),
    ( CONTENT_CAT_IMAGE,    CONTENT_SUBCAT_IMAGE_ISO9660,   "application/x-iso9660-image"   ,  None     ),

## Documents
    ( CONTENT_CAT_DOC,      CONTENT_SUBCAT_DOC_MSWORD_COMP, "application/msword"            , "*.doc"   ),
    ( CONTENT_CAT_DOC,      CONTENT_SUBCAT_DOC_MSWORD_ZIP,  "application/msword"            , "*.docx"  ),
    ( CONTENT_CAT_DOC,      CONTENT_SUBCAT_DOC_PDF,         "application/pdf"               ,  None     ),

## Archives
    ( CONTENT_CAT_ARCHIVE,  CONTENT_SUBCAT_ARCHIVE_ZIP,     "application/zip"               ,  None     ),
    ( CONTENT_CAT_ARCHIVE,  CONTENT_SUBCAT_ARCHIVE_GZIP,    "application/x-gzip"            ,  None     ),
    ( CONTENT_CAT_ARCHIVE,  CONTENT_SUBCAT_ARCHIVE_RAR,    ("application/x-rar",\
                                                            "application/x-rar-compressed") ,  None     ),
]

embedding_name_list = [
    "Word-List" ,
    "URL-List"  ,
    "Domin-List",
]

class emailContentParser:
    def __init__(self):
        pass

    def detect_content_category(self, header_list):
        # header의 Text값을 보고 CATEGORY 를 찾는다.
        ContentName = None
        parsed      = emailHeaderParser(header_list)
        ContentType = parsed.get_value_from_header_name("Content-Type", pos=0)
        ContentName = parsed.get_value_from_header_name("Content-Type", tag="Name")

        #print("ContentType=%s, ContentName=%s" % (ContentType, ContentName))

        if ContentType == None:
            ContentType = "text/plain"
        for map_at in content_type_map:
            CATEGORY        = map_at[0]
            SUB_CATEGORY    = map_at[1]
            text_type       = map_at[2]
            if type(text_type) == str:
                text_type = (text_type,)
            for type_at in text_type:
                if type_at == ContentType:
                    return (CATEGORY, SUB_CATEGORY, type_at, ContentName)
        return None

    def __content_text_parser(self, body_block, sub_category):
        report_data = {}

        if sub_category == CONTENT_SUBCAT_TEXT_HTML:
            body_block = html2text.html2text(body_block)

        parsed = do_word_split(body_block)

        #report_data["Word-List" ] = parsed[0]
        #report_data["URL-List"  ] = parsed[1]
        #report_data["Domin-List"] = parsed[2]
        for idx, parsed_at in enumerate(parsed):
            report_data[embedding_name_list[idx]] = parsed_at

        return report_data

    def __content_image_parser(self, body_block, sub_category):
        report_data = {}

        return report_data

    def __content_doc_parser(self, body_block, sub_category):
        report_data = {}

        return report_data

    def __content_archive_parser(self, body_block, sub_category):
        report_data = {}

        return report_data

    def do_content_parser(self, headers, body_block, category, sub_category, content_type, content_name):
        report = {
            "Category"      : category,
            "Sub-Category"  : sub_category,
            "Content-Type"  : content_type,
            "Content-Name"  : content_name,
            "Data"          : None
        }

        if category == CONTENT_CAT_TEXT:
            data = self.__content_text_parser(body_block, sub_category)
        elif category == CONTENT_CAT_IMAGE:
            data = self.__content_image_parser(body_block, sub_category)
        elif category == CONTENT_CAT_DOC:
            data = self.__content_doc_parser(body_block, sub_category)
        elif category == CONTENT_CAT_ARCHIVE:
            data = self.__content_archive_parser(body_block, sub_category)
        else:
            data = None

        report["Data"] = data
        return report





