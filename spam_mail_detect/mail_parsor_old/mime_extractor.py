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
import codecs
import chardet
#from common import *
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import chardet  
import re
import gzip
import copy
import json
import base64
import html2text
import os
import sys
import pprint
from email import message_from_file
from email import message_from_string
import re
from operator import itemgetter
import time
import quopri
#reload(sys)
#sys.setdefaultencoding('utf-8')
from word_split import *
import traceback

handle_charset = ["utf-8",
                  "euc_kr",
                  "cp949",
                  "euc_jp",
                  "cp932",
                  "ascii",
                  "iso2022_jp_2",
                  "iso2022_kr",
                  "johab",
                  "euc_jis_2004",
                  "euc_jisx0213",
                  "iso2022_jp",
                  "iso2022_jp_1",
                  "iso2022_jp_2",
                  "iso2022_jp_2004",
                  "iso2022_jp_3",
                  "iso2022_jp_ext",
                  "shift_jis",
                  "shift_jis_2004",
                  "shift_jisx0213"]

EML_TYPE_SPAM = 0
EML_TYPE_HAM  = 1



class headerExtractor:
    def __init__(self, msg_txt):
        self.msg_txt   = copy.deepcopy(msg_txt)
        self.head_list = msg_txt["heads"]

        del self.msg_txt["binary_mime"]

        j_data = json.dumps(self.msg_txt)
        #print(j_data)

    def get_header_tlv(self):
        header_list = []
        for item in self.head_list:
            hdr  = item.split(":")[0]
            data = item[len(hdr)+1:]
            hdr  = hdr.replace(" ", "")
            hdr  = hdr.replace("\t", "")
            header_list.append((hdr, data))

        return header_list

    def __feature_head_Received(self):
        pass


def decode_inline_mime_encoding(line, final_coding="utf-8"):
    #=?utf-8?B?...something...?=
    #   ^    ^
    #   |    `--- The bytes are Base64 encoded
    #   `---- The string is UTF-8 encoded
    # ex>' To: =?UTF-8?B?7Zmp7IiY7JiB?= <hsy@dio.co.kr>'

    idx_start   = line.find("=?")
    idx_end     = line.find("?=")
    str_before  = line[:idx_start]
    str_after   = line[idx_end+2:]
    if idx_start == -1 or idx_end == -1:
        return line
 
    try:
        in_line         = line[idx_start+2:idx_end]
        string_coding   = in_line.split("?")[0]
        transfer_coding = in_line.split("?")[1]
        data            = in_line[len(string_coding)+len(transfer_coding)+2:]
    except Exception as e:
        #print("Error : e=%s" % (e,))
        return line

    '''
    print("in_line         ::%s::" % in_line)
    print("string_coding   ::%s::" % string_coding)
    print("transfer_coding ::%s::" % transfer_coding)
    print("data            ::%s::" % data)
    print("str_before      ::%s::" % str_before)
    print("str_after       ::%s::" % str_after)
    '''

    if transfer_coding.lower() == "b":
        try:
            line = base64.b64decode(data)
        except Exception as e:
            pass
    else:
        line = line

    if len(string_coding) > 3:
        try:
            line = line.decode(string_coding)
        except:
            line = ""
    
    final_string = ""
    for coding_at in [final_coding,]+handle_charset:
        try:
            final_string = "%s%s%s" % (str_before, line.encode(coding_at), str_after)
        except:
            continue
        break

    return final_string

class mimeExtractor:
    def __init__(self, ps_path, eml_type=EML_TYPE_SPAM):
        self.ps_path    = ps_path
        self.eml_type   = eml_type
        self.msg_txt    = {
            "heads"             : [],
            "heads-raw"         : [],
            "mime"              : [], # list of dict, dict item is
                                      # ['Child-Mime', 
                                      #  'Content-Transfer-Encoding', 
                                      #  '<body>', 
                                      #  '<decoded-body>', 
                                      #  'Sub-Boundary', 
                                      #  'Content-Type']
            "binary_mime"       : [],
            "root_boundary"     : None,
        }
        self.word_dict  = None

    def handle_mime_body(self, hdr_tr_encoding, hdr_content_type, raw_body):
        # Content-Type, Content-Transfer-Encoding 을고려해서 최종 문자열을 뽑는다.
        if hdr_content_type == None:
            hdr_content_type = "text/plain; charset=UTF-8"
        else:
            hdr_content_type = hdr_content_type.split(":")[-1]
        
        hdr_content_type = hdr_content_type.lower()
        charset = None
        content_transfer_encoding = None
        content_type = "text"
        if hdr_tr_encoding != None:
            hdr_tr_encoding = hdr_tr_encoding.lower()
            value = hdr_tr_encoding.split(":")[-1]
            if "base64" in value:
                content_transfer_encoding = "base64"
            elif "quoted-printable" in value:
                content_transfer_encoding = "quoted-printable"
        # Content-Type: text/plain; charset=utf-8
        if "html" in hdr_content_type:
            content_type = "html"
        if "charset=" in hdr_content_type:
            charset = hdr_content_type.split("charset=")[-1]

        if content_transfer_encoding == "base64":
            try:
                raw_body = base64.b64decode(raw_body)
            except:
                pass
        elif content_transfer_encoding == "quoted-printable":
            try:
                raw_body = quopri.decodestring(raw_body)
            except:
                pass

        if type(raw_body) == bytes:
            decoded_body = None
            if charset != None:
                # header 에 인코딩 정보가 있다.
                try:
                    decoded_body = raw_body.decode(charset, errors='ignore')
                except:
                    pass
            else:
                # header 에 인코딩 정보가 없다.
                result = chardet.detect(raw_body)
                charset = result['encoding']
                if charset != None:
                    decoded_body = raw_body.decode(charset, errors='ignore')
            if decoded_body == None:
                decoded_body = raw_body.decode("utf-8", errors='ignore')
        elif type(raw_body) == str:
            decoded_body = raw_body
        elif type(raw_body) == unicode:
            decoded_body = raw_body.encode('utf-8')
        else:
            print("Error!!!! fail to detect encoding")
            #print(raw_body)
            #print(type(raw_body))
            raise
        #print(type(decoded_body))

        if content_type == "html":
            decoded_body = self.__html_to_string(decoded_body)

        if type(decoded_body) != str:
            if type(decoded_body) == unicode:
                decoded_body = decoded_body.encode("utf-8")
        #print(type(decoded_body))

        return decoded_body

    def get_parsed_text_dict(self, str_type=None):
        return self.msg_txt

    def __detect_html(self, html_string):
        text_string = self.__html_to_string(html_string)
        return text_string

    def __html_to_string(self, html_string):
        try:
            text_string = html2text.html2text(html_string)
        except Exception as e:
            text_string = ""
        return text_string

    def __load_text(self):
        # 1. load email text from file
        is_text = None
        ln_content = 0
        fd = None
        if self.ps_path[-3:].lower() == ".gz":
            fd = gzip.open(self.ps_path , 'rb')
        else:
            fd = open(self.ps_path , 'rb')
        linebufs = []
        rawbufs  = []
        rawAll   = b""

        while True:
            line = fd.readline()
            if len(line) == 0:
                break
            rawAll += line
            rawbufs.append(line)
        fd.close()

        try:
            charset = chardet.detect(rawAll)['encoding']
            print("charset=%s" % charset)
            for line in rawbufs:
                line = line.decode(charset)
                if "%trqfile2%" in line:
                    continue
                if "^^^^^^^^+_~!spacelee@$%^&!@#)_,$^^^^^^^^^^" in line:
                    break

                if "Content-Type:" in line:
                    ln_content = 0
                    if "text" in line:
                        is_text = True
                    else:
                        is_text = False
                elif is_text != None:
                    ln_content += 1
                
                if len(linebufs) > 1024 * 4:
                    if (ln_content > 256 and is_text == False) or (ln_content > 1024 * 2 and is_text == True):
                        if ln_line > 70 and ln_line < 80 and ln_line == len(linebufs[-1]):
                            continue
                linebufs.append(line)
        except Exception as e:
            traceback.print_exc()
            linebufs = None


        '''
        for charset in handle_charset:
            try:
                is_text = None
                ln_content = 0
                fd = None
                #fd = codecs.open(self.ps_path , 'rb', charset)
                if self.ps_path[-3:].lower() == ".gz":
                    fd = gzip.open(self.ps_path , 'rb')
                else:
                    fd = open(self.ps_path , 'rb')
                linebufs = []
                while True:
                    line = fd.readline()
                    line = line.decode(charset)
                    ln_line = len(line)
                    if ln_line == 0:
                        break
                    if "%trqfile2%" in line:
                        continue
                    if "^^^^^^^^+_~!spacelee@$%^&!@#)_,$^^^^^^^^^^" in line:
                        break

                    if "Content-Type:" in line:
                        ln_content = 0
                        if "text" in line:
                            is_text = True
                        else:
                            is_text = False
                    elif is_text != None:
                        ln_content += 1
                    
                    if len(linebufs) > 1024 * 4:
                        if (ln_content > 256 and is_text == False) or (ln_content > 1024 * 2 and is_text == True):
                            if ln_line > 70 and ln_line < 80 and ln_line == len(linebufs[-1]):
                                continue
                    linebufs.append(line)
                fd.close()
                break
            except Exception as e:
            #except ArithmeticError as e:
                #print("charset=%s : None, e=%s" % (charset,e,))
                if fd != None:
                    fd.close()
                linebufs = None
                continue
        '''
        if linebufs == None:
            return None

        if charset != "utf-8": # utf-8 L ¾ƴР°瀬 º¯ȯ ȑ´׮
            #print("charset : %s" % charset)
            for idx, line in enumerate(linebufs):
                #print("%s" % (line.encode("hex"),))
                #print("%d : %s" % (idx, line))
                #linebufs[idx] = unicode(line,charset).encode('utf-8')
                continue
                line = unicode(line)
                #print(type(line))
                try:
                    linebufs[idx] = line.encode('utf-8')
                except Exception as e:
                    pass

        header_buf     = ""
        header_buf_raw = ""
        f_end_head = False
        body_row_txt = []
        # 2. parser eml headers
        for idx, line in enumerate(linebufs):
            if f_end_head == False:
                if line[0] != ' ' and line[0] != '\t':# and line[0] != '\r' and line[0] != '\n':
                    if len(header_buf) > 0:
                        self.msg_txt["heads"].append(header_buf)
                        self.msg_txt["heads-raw"].append(header_buf_raw)
                        header_lower = header_buf.lower()
                        #Content-Type: multipart/alternative; boundary=--boundary_3692462_058b50cf-e1b1-4ac9-8811-7b0036171f50
                        if 'content-type:' in header_lower and 'boundary=' in header_lower:
                            if 'boundary="' in header_buf.lower():
                                root_boundary = re.split('BOUNDARY="|Boundary="|boundary="',header_buf)[1].split('"')[0]
                            elif 'boundary=' in header_buf.lower():
                                root_boundary = re.split('BOUNDARY=|Boundary=|boundary=',header_buf)[1]
                                root_boundary = root_boundary.split(" ")[0]
                                root_boundary = root_boundary.split("\n")[0]
                                root_boundary = root_boundary.split("\t")[0]
                                root_boundary = root_boundary.split("\r")[0]
                            else:
                                #print(header_lower)
                                return None
                            self.msg_txt["root_boundary"] = root_boundary
                    header_buf_raw  = decode_inline_mime_encoding(line)
                    line            = line.replace("\r", "")
                    header_buf      = line.replace("\n", "")
                    if line[0] == '\r' or line[0] == '\n':
                        f_end_head = True    
                elif line[0] == ' ' or line[0] == '\t':
                    header_buf_raw  += decode_inline_mime_encoding(line)
                    line             = line.replace("\r", "")
                    line             = line.replace("\n", "")
                    header_buf      += " %s" % line.lstrip()
                else:
                    pass
            else:
                line = line.replace("\r", "")
                if self.msg_txt["root_boundary"] != None:
                    line = line.replace("\n", "")
                #self.msg_txt["body_row_txt"].append(line)
                body_row_txt.append(line)

        # 3. make mime tree leaf nodes
        if self.msg_txt["root_boundary"] == None:
            report_at = self.__make_mime_report(body_row_txt, None, None)[None][0]
            line_all = ""
            for line in report_at["<body>"]:
                line_all += line

            # check base64
            content_type = ""
            content_transfer_encoding=None
            for hdr_at in self.msg_txt['heads']:
                hdr_at = hdr_at.lower()
                hdr_at = hdr_at.replace(" ", "")
                hdr_vals = hdr_at.split(":")
                value = hdr_vals[-1]
                if "content-type" == hdr_vals[0]:
                    content_type = value
                elif "transfer-encoding" in hdr_vals[0]:
                    content_transfer_encoding = value

            report_at["<decoded-body>"]  = self.handle_mime_body(content_transfer_encoding, content_type, line_all)
            self.msg_txt["mime"].append(report_at)
            return True        

        f_start = False
        mime_line = []
        for line in body_row_txt:
            if f_start == False and "--%s" % root_boundary in line:
                f_start = True
                mime_line.append(line)
                continue
            if f_start == True:
                if "--%s--" % root_boundary in line:
                    f_start = False
                    break
                mime_line.append(line)
                
        if len(mime_line) != 0:
            leaf_node = []
            self.__make_mime_report(mime_line, root_boundary, leaf_node)
        else:
            return None
        for item in leaf_node:
            if item["Content-Type"] != None:
                hdr_content_type = item["Content-Type"].lower()
                if "text" in hdr_content_type:
                    self.msg_txt["mime"].append(item)
                else:
                    self.msg_txt["binary_mime"].append(item)
        #pprint.pprint(self.msg_txt["mime"])

        # 4. decode data
        for item in self.msg_txt["mime"]:
            line_all = ""
            for line in item["<body>"]:
                line_all += line

            hdr_content_type = item["Content-Type"]
            hdr_tr_encoding  = item["Content-Transfer-Encoding"]
            raw_body         = line_all
            item["<decoded-body>"] = self.handle_mime_body(hdr_tr_encoding, hdr_content_type, raw_body)

        return True

    def __mime_hdr_parser(self, hdr_line, report_at):
        if len(hdr_line) != 0:
            header_lower = hdr_line.lower()
            if "content-type:" in header_lower:
               ContentType = hdr_line.split(":")[1].split(";")[0].replace(" ","")
               report_at["Content-Type"] = ContentType
               if "multipart" in ContentType and "boundary" in hdr_line:
                    hdr_line_in = hdr_line.replace(" ", "")
                    hdr_line_in = hdr_line.replace("\r", "")
                    if 'boundary="' in hdr_line_in:
                        boundary = hdr_line_in.split('boundary="')[1].split('"')[0]
                    else:
                        boundary = hdr_line_in.split('boundary=')[1]
                    report_at["Sub-Boundary"] = boundary
            if "content-transfer-encoding:" in header_lower:
               report_at["Content-Transfer-Encoding"] = hdr_line.split(":")[1].split(";")[0].replace(" ","")

    def __make_mime_report(self, lines, boundary, leaf_node):
        report_at = None
        f_body    = False
        f_head    = False
        mime_list = []
        for idx, line in enumerate(lines):
            #print("[%s] %d %s" % (idx, len(line), line))
            if "--%s" % boundary in line or (idx == 0 and boundary == None):
                f_body    = False
                f_head    = True
                hdr_buffer = ""
                if report_at != None:
                    report_at["<body>"] = str_body
                    mime_list.append(report_at)
                str_body  = []
                if boundary == None:
                    str_body.append(line)
                report_at = {
                    "Content-Type"              : None,
                    "Content-Transfer-Encoding" : None,
                    "<body>"                    : None,
                    "<decoded-body>"            : None,
                    "Sub-Boundary"              : None,
                    "Child-Mime"                : None,
                }
                if boundary == None:
                    f_body = True
                    #report_at["Content-Type"]   = ""
            #elif f_body == False and len(lines) == 0:
            #    f_body = True
            elif f_body == True and len(lines) == 0:
                #if report_at != None:
                #    report_at.append(report_at)
                f_body    = False
                f_head    = False
            elif f_body == False and f_head == True:
                if len(line) == 0:
                    f_body = True
                    report_at["<body>"] = ""
                    self.__mime_hdr_parser(hdr_buffer, report_at)
                else:
                    if line[0] == '\t' or line[0] == ' ':
                        hdr_buffer += "%s " % line
                    else:
                        self.__mime_hdr_parser(hdr_buffer, report_at)
                        hdr_buffer = line
            elif f_body == True and f_head == True:
                str_body.append(line)
        if report_at != None:
            report_at["<body>"] = str_body
            mime_list.append(report_at)
        
        for report_at in mime_list:
            subs_bound = report_at["Sub-Boundary"]
            body_list  = report_at["<body>"]
            if subs_bound != None:
                report_at["Child-Mime"] = self.__make_mime_report(body_list, subs_bound, leaf_node)
            else:
                if leaf_node != None:
                    leaf_node.append(report_at)

        return {boundary : mime_list}

    def load_all(self):
        if self.__load_text() == None:
            return False

        return True

    def __get_plain_text_list(self, word_dict, data_list, n_word_count, n_maximum_length):
        # decoded_body 를 잘라서 word_dict에 넣는다.
        if word_dict == None:
            word_dict   = {}
        count_knowns     = {}
        for decoded_body in data_list:
            if type(decoded_body) != list:
                (decoded_body, url_listup, domain_listup) = do_word_split(decoded_body)
            for idx, word in enumerate(decoded_body):
                if n_word_count + idx > len(decoded_body):
                    break
                composited_word = word
                #print(type(composited_word))
                for new_word in decoded_body[idx+1:idx+n_word_count]:
                    composited_word += " %s" % (new_word,)
                    if len(composited_word) <= n_maximum_length:
                        break
                if len(composited_word) > 50:
                    continue
                if composited_word not in word_dict:
                    word_dict[composited_word] = [0 # count word ham
                                                 ,0 # count word spam
                                                 ,0 # count file ham
                                                 ,0 # count file spam
                                                 ]
                if composited_word not in count_knowns.keys():
                    count_knowns[composited_word] = 1
                    word_dict[composited_word][self.eml_type + 2] += 1
                else:
                    count_knowns[composited_word] += 1
                word_dict[composited_word][self.eml_type] += 1
        return word_dict

    def get_header_object(self):
        return headerExtractor(self.msg_txt)

    def get_header_plain_text_list(self, n_word_count=3, n_maximum_length=32, word_dict=None):
        data_list       = []
        for item in self.msg_txt["heads"]:
            if ':' not in item:
                continue
            item = item.split(":")
            str_hdr = ""
            for tok in item[1:]:
                str_hdr += "%s" % tok
            data_list.append(str_hdr)

        self.word_dict = self.__get_plain_text_list(word_dict, data_list, n_word_count, n_maximum_length)
        return self.word_dict

    def get_body_binary_mime_list(self, n_binary_split=10, word_dict=None):
        data_list       = []
        for item in self.msg_txt["binary_mime"]:
            new_list = []
            raw_list = item["<body>"]
            raw_data = ""
            for line in raw_list:
                line      = line.replace('\n', '')
                line      = line.replace('\r', '')
                raw_data += line
            n_total_len = len(raw_data)
            n_rounde = int(n_total_len / n_binary_split)
            m_remain = int(n_total_len % n_binary_split)

            for idx in range(n_rounde):
                s_idx = (idx + 0) * n_binary_split
                e_idx = (idx + 1) * n_binary_split
                new_list.append(raw_data[s_idx:e_idx])
            #for idx in range(n_total_len-n_binary_split-1):
            #    s_idx = idx
            #    e_idx = idx + n_binary_split
            #    new_list.append(raw_data[s_idx:e_idx])
            data_list.append(new_list)
            #print(len(new_list))
        self.word_dict = self.__get_plain_text_list(word_dict, data_list, 1, n_binary_split + 1)
        return self.word_dict

    def get_body_plain_text_list(self, n_word_count=3, n_maximum_length=32, word_dict=None):
        data_list       = []
        for item in self.msg_txt["mime"]:
            if "<decoded-body>" in item.keys():
                decoded_body = item["<decoded-body>"]
            else:
                decoded_body = item["<body>"]
            if decoded_body == None:
                decoded_body = item["<body>"]
                if type(decoded_body) == list:
                    lines = ""
                    for line in decoded_body:
                        lines += line
                    decoded_body = self.__detect_html(lines)
            data_list.append(decoded_body)
        self.word_dict = self.__get_plain_text_list(word_dict, data_list, n_word_count, n_maximum_length)
        return self.word_dict

    '''
    def get_body_plain_text_list(self, n_word_count=3, n_maximum_length=32, word_dict=None):
        if word_dict == None:
            word_dict   = {}
        count_knowns    = {}
        for item in self.msg_txt["mime"]:
            if "<decoded-body>" in item.keys():
                decoded_body = item["<decoded-body>"]
            else:
                decoded_body = item["<body>"]
            if decoded_body == None:
                decoded_body = item["<body>"]
                if type(decoded_body) == list:
                    lines = ""
                    for line in decoded_body:
                        lines += line
                    decoded_body = self.__detect_html(lines)
            decoded_body = decoded_body.replace('\n', '')
            decoded_body = decoded_body.split(' ')
            for idx, word in enumerate(decoded_body):
                if n_word_count + idx > len(decoded_body):
                    break
                composited_word = word
                for new_word in decoded_body[idx+1:idx+n_word_count]:
                    composited_word += " %s" % (new_word,)
                    if len(composited_word) <= n_maximum_length:
                        break
                if len(composited_word) > 50:
                    continue
                if composited_word not in word_dict:
                    word_dict[composited_word] = [0 # count word ham
                                                 ,0 # count word spam
                                                 ,0 # count file ham
                                                 ,0 # count file spam
                                                 ]
                if composited_word not in count_knowns.keys():
                    count_knowns[composited_word] = 1
                    word_dict[composited_word][self.eml_type + 2] += 1
                else:
                    count_knowns[composited_word] += 1
                word_dict[composited_word][self.eml_type] += 1
        self.word_dict = word_dict
        return word_dict

    '''
    def print_word_dict(self, word_dict=None):
        if word_dict == None:
            if self.word_dict == None:
                return None
            word_dict = self.word_dict
        for key in word_dict.keys():
            count = word_dict[key]
            print("%-35s : ham=%d, spam=%d" % (key, count[0], count[1]))
        return word_dict

    def save_word_dict(self, path, word_dict=None):
        if word_dict == None:
            if self.word_dict == None:
                return None
            word_dict = self.word_dict

        #new_dict = copy.deepcopy(word_dict)
        new_list = []
        for key in word_dict.keys():
            count    = word_dict[key]
            info_str = "HAM=%d(%d), SPAM=%d(%d) : %s" % (count[0], count[2], count[1], count[3], key)
            dict_at  = {
                "ham_cnt"   : count[0],
                "spam_cnt"  : count[1],
                "total_cnt" : count[0] + count[1],
                "str"       : key,
                "info_str"  : info_str,
            }
            new_list.append(dict_at)

        new_list = sorted(new_list, key=itemgetter("total_cnt"), reverse=True)

        json_dict = json.dumps(word_dict, indent=4, ensure_ascii=True)
        with codecs.open("%s.json" % path , 'w', 'utf-8') as fd:
            fd.write(json_dict)

        with codecs.open("%s.txt" % path , 'wb') as fd:
            for line in new_list:
                str_out = "%s\n" % line["info_str"]
                #fd.write(str_out.encode('utf-8'))
                try:
                    fd.write(str_out.encode('utf-8'))
                except:
                    print("Error : %s" % str_out)
        return word_dict

    def load_word_dict(self, path):
        pass

def main():
    ps_path = '/srkim/mnt/hdd250G/maildata/terracespamadm/20190902/0850/2019-09-02-08:56:52:377003.qs.gz'
    #ps_path = 'Amazon.txt'
    e = mimeExtractor(ps_path, EML_TYPE_SPAM)
    e.load_all()
    #word_dict = e.get_body_plain_text_list(n_word_count=2, n_maximum_length=24)
    #word_dict = e.get_header_plain_text_list(n_word_count=2, n_maximum_length=24)
    word_dict = e.get_body_binary_mime_list(n_binary_split=20)
    for key in word_dict.keys():
        count = word_dict[key]
        print("%-15s : ham=%d, spam=%d" % (key, count[0], count[1]))

if __name__ == "__main__":
    main()

