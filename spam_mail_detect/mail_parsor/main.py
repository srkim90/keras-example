#!/bin/env python
# -*- coding: utf-8 -*-

'''
  Filename : main.py at mail_parsor
  Release  : 1
  Date     : 2020-02-09
   
  Description : mime extractor of spam detect module
  
  Notes :
  ===================
  History
  ===================
  2020/02/09 created 
'''
import threading
import traceback
from mime_extractor import *
from multiprocessing.pool import Pool

def is_eml_file(f_name):
    f_name = f_name.replace("\r","")
    f_name = f_name.replace("\n","")
    ln_f_name = len(f_name)
    if ln_f_name > 4 and os.path.exists(f_name) == True and (f_name[-3:].lower() == ".qs" or f_name[-4:].lower() == "s.gz"):
        return True
    return False

def do_analyze(index, total_list, input_list):
    ln_save         = 0
    word_dict       = None
    old_total_cnt   = 0
    save_name       = "/srkim/mnt/hdd250G/maildata/word_dict"

    try:
        for count,item in enumerate(total_list):
            e = mimeExtractor(item, EML_TYPE_SPAM)
            if e.load_all() == False:
                print("FAIL [%d/%d] %s" % (count, len(total_list), item))
                continue

            #word_dict = None
            word_dict = e.get_body_plain_text_list(n_word_count=1, n_maximum_length=24, word_dict=word_dict)

            hdr = e.get_header_object()

            v =  hdr.get_header_tlv()
            #for item in v:
            #    print(item)

            total_cnt = 0
            for jdx,key in enumerate(word_dict.keys()):
                ln_word = word_dict[key]
                total_cnt += (ln_word[0] + ln_word[1])
                #print("%-15s : ham=%d, spam=%d" % (key, ln_word[0], ln_word[1]))
                #if count > 5:
                #    break

            if (count != 0 and count % 1000 == 0) or (count + 1 == len(total_list)):
                full_name = "%s/%s_report_%d_%03d.dat" % (save_name, input_list, index, ln_save)
                print(" - save report : \n  --%s.txt \n  --%s.json" % (full_name, full_name))
                try:
                    e.save_word_dict(full_name, word_dict)
                except Exception as e:
                    pass
                word_dict = None
                ln_save += 1

            print("SUCC [%d/%d] %s word-cnt=%d" % (count, len(total_list), item, (total_cnt - old_total_cnt)))
            old_total_cnt = total_cnt

        print("thread end : index=%d" % (index))
        return True
    except Exception as e:
        print("Exception : %s" % (e,))
        traceback.print_exc()
        return False

def __analyze_join_th(proc_pool, params):
    hProc = proc_pool.apply_async(do_analyze, params)
    ret   = hProc.get()
    return ret 


MAX_PROC = 6
def main():
    n_proc     = 1
    total_list = []
    input_list = ""
    for param in sys.argv[1:]:
        if is_eml_file(param):
            total_list.append(param)
        elif (param == "terracespamadm_list.txt" or param == "terracehamadm_list.txt") and os.path.exists(param) == True:
            input_list = param.split(".")[0]
            with open(param) as fd:
                for line in fd.readlines():
                    line = line.replace("\r","")
                    line = line.replace("\n","")
                    if is_eml_file(line):
                        total_list.append(line)
        else:
            continue

    split_list = []
    ln_list    = len(total_list)    

    if ln_list < 1000:
        n_proc      = 1
        split_list  = [total_list,]
    else:
        n_proc      = MAX_PROC
        n_split     = int(ln_list / n_proc)
        for idx in range(n_proc):
            start_idx = idx     * n_split
            end_idx   = (idx+1) * n_split
            if idx + 1 != n_proc:
                split_list.append(total_list[start_idx:end_idx])
            else:
                split_list.append(total_list[start_idx:])

    thread_list = []
    proc_pool   = Pool(processes=n_proc)
    for idx,list_at in enumerate(split_list):
        hThread = threading.Thread(target=__analyze_join_th, args=(proc_pool, (idx, list_at, input_list)))
        hThread.daemon = True
        hThread.start()
        thread_list.append(hThread)

    for hThread in thread_list:
        hThread.join()

    return True

if __name__ == "__main__":
    main()

