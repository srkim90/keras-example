# -*- coding: utf-8 -*-

'''
  Author   : Kim, Seongrae
  Filename : config.py
  Release  : 1
  Date     : 2018-07-02
 
  Description : config module for python
 
  Notes :
  ===================
  History
  ===================
  2018/07/02  created by Kim, Seongrae
'''
import re
import sys
from log import *
from singleton import *

class load_config(singleton_instance):
    def __init__(self, path):
        pass

    def loadCfgFile(self, path, funPtr):
        f = open(path, 'r')
        array = []
        while True:
            line = f.readline()
            if not line: break
            line2 = line.split('#')
            if len(line2[0]) <= 1:
                continue

            line3 = ''.join( c for c in line2[0] if  c not in '\r\n\t ' )
            nErr = funPtr(self, line3)
            
            if nErr != None:
                array.append(nErr)

        f.close()

        return array

    def conn_cfg_parser(self, line):
        i = 0
        __line = line.split(',')
        if len(__line) != 7 and len(__line) != 6 and len(__line) != 5 :
            return None

        #Type , L-Index, LocalIP1          , Service Port , Notify Port   , Transport     , ConnType
        if __line[0] != "L" and __line[0] != "P" and __line[0] != "S" and __line[0] != "T":
            return None

        #for item in __line:
        #    print (item)

        return __line
        

class cfgConnection(singleton_instance):
    cfgList = []
    def __init__(self, cfgList):
        self.cfgList = cfgList

    def getLocalCfg(self, idx):
        i = 0
        for item in self.cfgList:
            #print(item)
            if item[0] == "L":
                if i == idx:
                    return (item[2], item[3], item[4], item[5], item[6])
                i += 1


    def getLocalCfgList(self):
        l_list = []
        for item in self.cfgList:
            #print(item)
            if item[0] == "L":
                l_list.append((item[2], item[3], item[4], item[5], item[6]))
        return l_list

    def getLocalCnt(self):
        i = 0
        for item in self.cfgList:
            #print(item)
            if item[0] == "L":
                i += 1       
        return i

    def getPeerCfg(self, idx):
        i = 0
        for item in self.cfgList:
            #print(item)
            if item[0] == "P":
                if i == idx:
                    return (item[2], item[3], item[4], item[5], item[6])
                i += 1
        return None

    def getPeerCfgList(self):
        l_list = []
        for item in self.cfgList:
            #print(item)
            if item[0] == "P":
                l_list.append((item[2], item[3], item[4], item[5], item[6]))
        return l_list



    def getPeerlCnt(self):
        i = 0
        for item in self.cfgList:
            #print(item)
            if item[0] == "L":
                i += 1       
        return i

    def getSSLCfg(self):
        for item in self.cfgList:
            #print(item)
            if item[0] == "S":
                directory   = item[1]
                serverCert  = ("./%s/%s" % (directory, item[2]))
                serverKey   = ("./%s/%s" % (directory, item[3]))
                clientCerts = ("./%s/%s" % (directory, item[4]))
                clientKey   = ("./%s/%s" % (directory, item[5]))
                #print ("serverCert:%s, serverKey:%s, clientCerts:%s, clientKey:%s" % (serverCert, serverKey, clientCerts, clientKey))
                return (serverCert, serverKey, clientCerts, clientKey)
        return None

    def getTpsCfg(self):
        for item in self.cfgList:
            #print(item)
            if item[0] == "T":
                return (item[1], int(item[2]), int(item[3]), int(item[4]))
        return ("",0,0,0)


class cfg_data(singleton_instance):
    data_path   = None
    data_list   = []

    def __init__(self, data_path):
        if type(data_path) == str:
            data_path  = [data_path,]
        self.data_path = data_path
        self.data_list = []

        for file_name in self.data_path:
            self.read_data_file(file_name)

    def read_data_file(self, data_path):
        data_list = []
        category  = "root"
        cfg_fd    = open(data_path, 'r')
        data_dict = {}
        for line in cfg_fd:
            #line = line.rstrip('\r|\n|\t')
            line = re.sub('\r|\n|\t| ', '', line)  

            if len(line) < 3:
                continue

            if line[0] == '#':
                continue

            line = line.split('#')[0]

            if line.find("[") != -1 and line.find("]") != -1:
                if len(data_dict) != 0:
                    data_list.append((category, data_dict))
                    data_dict = {}
                category = line[1:-1]
                for at_check in data_list:
                    if at_check[0] == category:
                        print("Error. existing category : %s" % (category,))
                        raise Exception
                continue
            else:
                pair = line.split('=')
                if len(pair) == 2:
                    if pair[0] in data_dict:
                        PRINT("%sWarning%s: in category '%s', Item '%s' is already exist" % (C_RED, C_END, category, pair[0]))
                    else:
                        data_dict[pair[0]] = pair[1]

        if len(data_dict) != 0:
            data_list.append((category,data_dict))
            data_dict = {}

        self.data_list.extend(data_list)

    def print_data_dictionary(self):
        PRINT("%s" % (LINE80) )
        PRINT("  Data configuration file : '%s' information" % (self.data_path) )
        PRINT("%s" % (LINE80) )
        for item in self.data_list:
            category    = item[0]
            data_dict   = item[1]

            print()
            PRINT("%s[%s%s%s]%s" % (C_RED, C_GREEN, category, C_RED, C_END), tab=1)

            for key in data_dict.keys():
                PRINT("%-20s:%s" % (key, data_dict[key]), tab=2)
        PRINT("%s" % (LINE80) )

    def search_data_cfg(self, field, category="root"):
        for item in self.data_list:
            in_category    = item[0]
            in_data_dict   = item[1]

            #print("in_category='%s', in_data_dict='%s'" % (in_category, in_data_dict))

            if in_category != category:
                continue

            if field in in_data_dict:
                return in_data_dict[field]
        PRINT("Exception: Notfound fiel='%s' in category='%s'" % (field, category))
        raise Exception
        #return None

def my_print(s):
    print (s)

def printConfig(cfgConn, cfgData, printFn=None):

    if printFn == None:
        printFn = my_print

    C_END     = "\033[0m"
    C_BOLD    = "\033[1m"
    C_INVERSE = "\033[7m"
    C_ITALIC  = "\033[3m"
     
    C_BLACK  = "\033[30m"
    C_RED    = "\033[31m"
    C_GREEN  = "\033[32m"
    C_YELLOW = "\033[33m"
    C_BLUE   = "\033[34m"
    C_PURPLE = "\033[35m"
    C_CYAN   = "\033[36m"
    C_WHITE  = "\033[37m"
     
    C_BGBLACK  = "\033[40m"
    C_BGRED    = "\033[41m"
    C_BGGREEN  = "\033[42m"
    C_BGYELLOW = "\033[43m"
    C_BGBLUE   = "\033[44m"
    C_BGPURPLE = "\033[45m"
    C_BGCYAN   = "\033[46m"
    C_BGWHITE  = "\033[47m"

    os.system ('clear')

    printFn("  ----------------------------------------------------------------------       ")
    printFn("  " + C_RED + " HTTP/2" + C_WHITE + C_BOLD + " UDM/UDR" + C_END + " Simulator Start")
    printFn("  ----------------------------------------------------------------------       ")
    printFn("                                                                               ")
    printFn("   " + C_BOLD + "UDM/UDR" + C_END + " Simulator-Configurations                 ")
    printFn("  ======================================================================       ")
    printFn("                                                                               ")
    printFn("")
    printFn("  %-5s%-10s%-20s%-15s%-15s%-15s%-15s" % ("Type", "L-Index", "LocalIP", "Service Port", "Notify Port", "Transport", "ConnType"))
    printFn("  %s" % line120);

    if cfgConn != None:
        i = 0
        while True:
            Result = cfgConn.getLocalCfg(i)
            if Result == None:
                break;
            IP, ServicePort, NotifyPort, Transport, ConnType = cfgConn.getLocalCfg(i)

            str_Transport = "HTTP" if Transport == "0" else "HTTPS" 
            str_ConnType  = "UDR"  if ConnType  == "0" else "UDM" #( 0: Service-provider   , 1 : Service-Consumer )

            printFn ("  %-5s%-10d%-20s%-15s%-15s%-15s%-15s" % ("L", i, IP, ServicePort, NotifyPort, str_Transport, str_ConnType))
            i += 1
            #printFn (Result)
    printFn("  %s" % line120);

    printFn("")
    printFn("  %-5s%-10s%-20s%-15s%-15s%-15s%-15s" % ("Type", "P-Index", "PeerIP", "Service Port", "Notify Port", "Transport", "ConnType"))
    printFn("  %s" % line120);
    if cfgConn != None:
        i = 0
        while True:
            Result = cfgConn.getPeerCfg(i)
            if Result == None:
                break;
            IP, ServicePort, NotifyPort, Transport, ConnType = cfgConn.getPeerCfg(i)

            str_Transport = "HTTP" if Transport == "0" else "HTTPS" 
            str_ConnType  = "UDR"  if ConnType  == "0" else "UDM" #( 0: Service-provider   , 1 : Service-Consumer )

            printFn ("  %-5s%-10d%-20s%-15s%-15s%-15s%-15s" % ("P", i, IP, ServicePort, NotifyPort, str_Transport, str_ConnType))
            i += 1
            #printFn (Result)
    printFn("  %s" % line120);
     
    if cfgConn != None:
        printFn("")
        printFn("  %-15s%-20s%-15s%-15s%-15s" % ("Type", "Prefix" ,  "Start-Sub" , "Max-Sub" , "TPS"))
        printFn("  %s" % line120);
        prefix, start_sub, max_sub, tps = cfgConn.getTpsCfg()
        printFn("  %-15s%-20s%-15s%-15s%-15s" % ("T", prefix, start_sub, max_sub, tps))
        printFn("  %s" % line120);

        printFn("\n  Press the < " + C_BOLD + "tab" + C_END + " > key at any time for completions.")

def loadConfig(config_peer, config_data):
    fCfg = load_config.instance(config_peer)
    connCfgArray = fCfg.loadCfgFile(config_peer, load_config.conn_cfg_parser)

    cfgConn = cfgConnection.instance(connCfgArray)

    e = cfg_data.instance(config_data)
    #e.print_data_dictionary()

    return cfgConn

    #IP, ServicePort, NotifyPort, Transport, ConnType = cfgConn.getLocalCfg(0)
    #
    #printFn ("IP:%s, ServicePort:%s, NotifyPort:%s, Transport:%s, ConnType:%s" % (IP, ServicePort, NotifyPort, Transport, ConnType))
    

if __name__ == '__main__':
    loadConfig(sys.argv[1], sys.argv[2])
