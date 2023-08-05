""" parse netstat command lines output into python named-tuples!

Features: 
    parse output into list of named_tuple: inet_connection,but each field is still in str type;  
    display DNS name by default,  using '-n' to get numeric repr of result, 
    select() and find() by varios condition;  

documentation:
    get the exmaple by: print pynetstat.__usage__ (support doctest)
    and read __main__ function (an simple test procedure) in this script

note: 
    usage of netstat needs admin's right on windows to get program name,
    but it is not needed on Linux

implementation:
    since  the output format of netstat is stable, it is possible to parse the output string
    see readme.txt for details of implementation
    all the fields will be convert to specific type, but keep as str type 
    if numeric format string is preferred, try "-n" options, by default, DNS name, or port repr name is used
    Since each kind of protocol family has different headers, they are queried in seperated command line
    Also, summery (-s) and interface (-i) also started in seperated subprocess

changelog:
    v0.1 beta testing, blocking mode
    v0.2 add one nonblocking runner thread, to call subprocess.Popen, 
        by default: AUTO_UPDATING=False and NONBLOCKING_MODE=True
        These switches can be set after import and before instantiate netstat() class
        time.sleep(second): while not netstat.is_ready():time.sleep(1)

Operation System Support:
    detect Windows or Linux platform, python 2 and python 3
    If the OS difference is distinct, using class to fit each os. 
    only ASCII and UTF-8 english version OS is tested

tested:  
    pyhton 2.7(32bit) on win7 64bit;
    pyhton 2.7(64bit)  ubuntu 12.04 64bit;   
    python 3.3 on on win7 64bit, but test failed due to string parse operation

todo: 
    pyhton 3.x support:    string operation errors is found, try 2to3
    currently all output fields are string type, but python 3.3 got ipaddress module, 
    Mac OS X support:     no such OS to test
    using LINUX command options to unify all platform?:  ->not sure it is a good ideal
    How to test whether user has admin right on windows?  :  -> LINUX: os.geteuid()==0 
    how to start the refresh in another thread, so do not block the caller -> done in v0.2
    continous mode is not supported, manually refresh the stat! -> call update() manually 
    "how to split -aep into -a -e -p ???"
    using logging module instead of print() 
    
"""

from __future__ import print_function
__author__="Qingfeng Xia"
__version__="0.2.0"


__usage__=""" 
                #example of using this module in blocking mode: 
                import pynetstat
                pynetstat.NONBLOCKING_MODE=False
                from pynetstat import netstat 
                s=netstat("-t", "-e")  
                # list of strings or  single strings with options seperated by a single space key
                s.update()  # a bloking operation,#netstat program needs several seconds to finish
                #it can auto start after ctor(),  if pynetstat.AUTO_UPDATING=True
                s.display() 
                s=netstat("-u -e")   # now show UDP connections
                s.update()  # a bloking operation 
                if s.haserror:  
                    print "there is some error happend!"
                else:
                    s.tofile()  #save as csv, by default    sep='|',   
                
                #nonblocking mode in v0.2
                import time
                pynetstat.NONBLOCKING_MODE=True
                s.update() 
                s=netstat("-t", "-e")   # keyword arg:  nonblocking_mode=True
                while not s.ready:     # make sure check the readiness before saving or displaying
                    #do other things, or just wait 1second:  
                    #time.sleep(1)  # 
                s.display() 
                print "show all the functions of netstat class"
                dir(netstat)
                """


##############################################
EMPYTY_FIELD=""
AUTO_UPDATING=False
NONBLOCKING_MODE=True
_DEBUG=True
#import logging  #  "pynetstat_##.log"   # ALWASY REPLACE OLD LOG?
#################################################
#filters output
import subprocess
import sys
import datetime
import time

if sys.version_info >= (3, 0):
    PY3=True
    print("")
else:
    PY3=False
    
############################################
_NT=False
_LINUX=False
_POSIX=False
import os
if os.name=="nt":
    _NT=True
elif sys.platform[:5] == 'linux':
    _LINUX=True
    _POSIX=True
else:
    print("OS current not supported")
    sys.exit(-1)
#os.name give "POSIX" for linux, and sys.platform==linux2 for python 2.x
#if sys.platform == 'win32':   to distinguish WIN65
    
    
###############################################    
if _LINUX:
    inet_header=('Proto', 'Recv-Q', 'Send-Q', 'Local Address',  'Foreign Address', 'State',  #base output
                                "User",  "Inode" ,"PID/Program name") # second part are extended fileds "-e -p"
if _NT:
    inet_header=('Proto', 'Local Address',  'Foreign Address', 'State',  #base output
                                 "PID", "Program name") # second part are extended fileds "-o -b",  -o (PID) need not admin right
# AF_UNIX only for POSIX system
unix_header=('Proto', 'RefCnt Flags', 'Type',  'State',   'I-Node',   
                                'PID/Program name',    'Path')  # second part are extended fileds "-e -p"
    
#namedtuple for connection stat
import collections
if _LINUX:
    inet_connection = collections.namedtuple('inet_connection', 'Proto RecvQ SendQ LocalAddress  LocalPort ForeignAddress ForeignPort State User Inode PID Program')    # 
if _NT:
    inet_connection = collections.namedtuple('inet_connection', 'Proto LocalAddress  LocalPort ForeignAddress ForeignPort State PID Program')    # 
#some fields may need to be dropped: Recv-Q Send-Q and Inode (not available on Windows)
unix_connection=collections.namedtuple('unix_connection', "Proto RefCount Flags Type State Inode PID Program Path")



def parse_inet_connection_nt( entry,sep=' '):
    """ each entry contains one or more lines
    """
    line=entry[0].strip() # if it is empty line, it 
    if len(line) ==0:  #end of file reached, this should be tested outside
        return None 
    if not len(line)>3 :
        return None  # end of output, is another empty line
    count=len(inet_header)
    l=line.split(sep)
    fields=[it for it in l if it!=sep and it!='']  # filter  empty item or sep string
    if _DEBUG:  print(fields)  # it is possible to using dict as  **kwargs
    d={}
    d["Proto"]=fields[0]
    portpos=fields[1].rfind(':')
    d["LocalAddress"]=fields[1][:portpos]    
    d["LocalPort"]=fields[1][portpos+1:]   # :::*  for  IP all zero, and any ports
    portpos=fields[2].rfind(':')
    d["ForeignAddress"]=fields[2][:portpos]      # using rfind(':')
    d["ForeignPort"]=fields[2][portpos+1:]
    if d["Proto"].upper()=="UDP":   # UDP has no STATE field, which is empty
        d["State"]=EMPYTY_FIELD
        i=3
    else:
        d["State"]=fields[3]
        i=4
    d["PID"]=fields[i]  # -o 
    if  len(entry)>1:   #self.show_extrainfo 
        prog=entry[1].strip()   #  strip endline and leading spaces
        if prog[0] != "["  and len(entry)>2:
            l=entry[2].strip()
            d["Program"]=prog+l
        else:
            d["Program"]=prog    # do not strip brackets [program]
    else:
        #d["PID"]=None
        d["Program"]=EMPYTY_FIELD
    #return d  # not in original order!
    t=inet_connection(**d)  # must specify all the fileds as  init arguements
    return t

           
def parse_inet_connection_linux(line, sep=' '):
    """ string.split(' ')  can not split fileds with multiple spaces between field -> filtering
    header of UNIX/inet family is fixed, a namedtuple is declared and return by parsing
    all decimal string is not cast into integer!!!
    unknown field is a single slash '-',  -> replaced by None,  
    "*" means any IP/port in ascii format;  in numeric format:  0.0.0.0 means ANY IP address
    """
    count=len(inet_header)
    l=line.split(sep)
    fields=[it for it in l if it!=sep and it!='']  # filter  empty item or sep string
    #print(fields)  # it is possible to using dict as  **kwargs
    d={}
    d["Proto"]=fields[0]
    d["RecvQ"]=fields[1]  #may be removed, to compatible with windows output
    d["SendQ"]=fields[2]   #maybe removed, to compatible with windows output
    # IPv6 using ":::portNumber" (numeric format)  , [::]:* (ASCII format)
    portpos=fields[3].rfind(':')
    d["LocalAddress"]=fields[3][:portpos]    
    d["LocalPort"]=fields[3][portpos+1:]   # :::*  for  IP all zero, and any ports
    portpos=fields[4].rfind(':')
    d["ForeignAddress"]=fields[4][:portpos]      # using rfind(':')
    d["ForeignPort"]=fields[4][portpos+1:]
    if d["Proto"].upper()=="UDP":   # UDP has no STATE field, which is empty
        d["State"]=EMPYTY_FIELD
        i=5
    else:
        d["State"]=fields[5]
        i=6
    d["User"]=fields[i]
    d["Inode"]=fields[i+1]       #may be removed, to compatible with windows output
    #last fields, need to test existence first?
    if fields[i+2]=='-':
        d["PID"], d["Program"]=EMPYTY_FIELD,EMPYTY_FIELD
    else:
        d["PID"], d["Program"]=fields[i+2].split('/')
    #return d  # not in original order!
    t=inet_connection(**d)  # must specify all the fileds as  init arguements
    return t
    
       
def parse_connection_AF_UNIX(line, spe=' '):
    """  at least three spaces is used to split each column!  sep="   " then trim the leading and trailing space?
    "Flags" field contain sep char (space),  "[ ]", is that only one space inside brackets?
    AF_UNIX has types: DGRAM(UDP) which has no state, STREAM and SQ
    run as root can give more information, but there is no need to run as root
    last field: "path" can be empty, or file name with space, some paht begin with @, which means just a tmp
    """
    count=len(inet_header)
    l=line.split(sep)
    fields=[it for it in l if it!=sep and it!='']  # filter  empty item or sep string, path with spaces will be changed
    print(fields)  # it is possible to using dict as  **kwargs
    d={}
    #"Proto RefCount Flags Type State Inode PID Program Path"
    d["Proto"]=fields[0]  #it must be "unix"
    d["RefCount"]=fields[1]
    d["Flags"]=[]    # a list, empty of multiple string items, searching ']'
    i=3 # assert( fields[2] =='[')
    while fields[i] != ']': 
        d["Flags"].append(fields[i] )
        i+=1
    d["Type"]=fields[i+1] 
    if d["Type"].upper()=="DGRAM":   # UDP has no STATE field, which is empty
        i+=1
        d["State"]=EMPYTY_FIELD
    else:
        i+=2
        d["State"]=fields[i]
    d["Inode"]=fields[i+1]
    #split the PID/Program name
    if fields[i+2]=='-':
        d["PID"], d["Program"]=EMPYTY_FIELD,EMPYTY_FIELD
    else:
        d["PID"], d["Program"]=fields[i+2].split('/')
    # last fields,     last field: "path" can be empty, or file name with space
    if fields >=i+3:
        d["Path"]=" ".join(fields[i+3:])    # the orignal path with multiple spaces can not be recovered!!!
    else:
        d["Path"]=EMPYTY_FIELD
    #return d  # not in original order!
    t=inet_connection(**d)  # must specify all the fileds as  init arguements
    return t
    
    
class netstat(object):
    """ by default, linux netstat will list also the UNIX(IPC socket) family, which is too lengthy to show
        Also, the output using ASCII representation of port number, DNS name, 
        therefore, if no option is specified , list opened/active inet v4 socket, 
        which equals to  "netstat -t -n -e -p" on LINUX
        
        On windows, no program name and PID is shown, since admin 's right is needed
    """
    def __init__(self, *options, **kwargs):  #
        """
        """
        self.description="netstat output"
        #fileds may be cleared in some stage
        self.inet_connections=[]  #AF_INET (IPv4), list of inet_stat namedtuple
        self.unix_connections=[] # family "AF_UNIX"  list of unix_stat namedtuple
        self.ready=False
        self.haserror=False
        self.timestamp=None
        #
        self.continuous=False  #using a timmer 
        self.interval=5  # default continuous update interval: 5 seconds 
        #self.show_extendedfields=True   # always show this fields
        #self.show_programfields=True
        self.show_AF_UNIX=False
        self.show_summary=False
        self.show_all=False
        self.show_extrainfo=True
        self.show_numeric=False
        self.family_options=[]
        if _NT:
            self.cmdoptions=[ '-o']  # it is the default command line output, it output  only AF_INET , show PID
        if _LINUX:
            self.cmdoptions=[ '-a', '-e', '-p']  # default, output AF_INET  
        if len(options):
            if len(options)>1:   # if all options are secified in one string with space sep
                options_string=" ".join(options)  #  "how to split -aep into -a -e -p ???"
            else:
                options_string=options[0]
            self.set_options(options_string.lower())
        else:
            self.help()
        # nonblocking mode
        self.proc=None
        self.thread=None
        self.nonblocking=NONBLOCKING_MODE  
        if AUTO_UPDATING:
            if self.nonblocking: self.run()
            else: self.update()  #get the result in blocking mode
            
    def set_options_nt(self, options):
        #AF_FAMILY selections
        family_set=["UDP","TCP","TCPV6","UDPV6"]
        if '-p' in options:   # specify inet AF_FAMILY options
            for  o in options:
                self.family_options=[" -p "+proto  for proto in family_set  if  o.find(proto)>=0]
            # building -proto
            if len(self.family_options): self.cmdoptions.append(" ".join(self.family_options))
        if ( '-b' in options ) :
            try: 
                import ctypes   #new in python 2.5, it is standard lib, so there should be no ImportError
            except ImportError:
                print("ctypes is not installed, failt to detect adminstrator right")
            isadmin=False
            try:
                isadmin=ctypes.windll.shell32.IsUserAnAdmin()
            except Error:   #any error
                print("Fail to call win32 api: ctypes.windll.shell32.IsUserAnAdmin()")
            #self.cmdoptions.append('-o')  #'-o' in options 
            if isadmin:
                self.cmdoptions.append('-b')
                self.show_extrainfo=True
        else:
            self.show_extrainfo=False
            #
            
    def set_options_linux(self, options):
        self.show_extrainfo=True
        #AF_FAMILY selections
        if '-u' in options or "--udp" in options:
            self.family_options.append('-u')  #UDP, has not state field, None!
        if '-t' in options or "--tcp" in options:
            self.family_options.append('-t')  #TCP, repeating options will be skip by netstat command
        if '-w' in options or "--raw" in options:
            self.family_options.append('-w')  # raw socket inet connection
        self.cmdoptions+=self.family_options
        # only avaible on POSIX platform
        if '-x' in options or "--unix" in options:    # only available on POSIX
            self.show_AF_UNIX=True
            
    def set_options(self, options):
        """ by default, '-e -p' is called to collect the complete information
        if multiple options is secified, they are joined by space char
        windows support only the short format option like "-n"
        """
            
        """
        if '-e' in options or "--extend" in options:
            self.cmdoptions.append('-e')  #  print a second line for these fileds USER   ???
            self.extendedfields=True
        if '-p' in options or "--program" in options:
            self.cmdoptions.append('-p')  #   summer     21788       2026/firefox 
            self.programfields=True
        """
        #print(options)
        if options:  # parameter is specified, not None
            if _NT:
                self.set_options_nt(options)
            if _LINUX:
                self.set_options_linux(options)
            #  generic OS independent options ##############################
            # -n(--numeric)  will affect the output format,  
            if '-n' in options or "--numeric" in options:
                self.show_numeric=True
            # what is the impact of -v?
            # -a  (all )   default display only connected socket  "-l" "--listen"
            if '-a' in options or "--all" in options:
                self.cmdoptions.append('-a')   #filter_options
                self.show_all=True
            else:
                #self.cmdoptions.append('-l')    #windows has no such options
                self.show_all=False
            # special query, skip!
            if '-i' in options or "--interface" in options:
                print("list ethernet interfaces is not implemented ") # not supported on Windows
            if '-r' in options or "--route" in options:
                print("list route table is not implemented") #
            #special options, must be call after parse all other options!
            if '-g' in options or "--group" in options:
                self.cmdoptions.append('-g')  #multicast membership
            if '-h' in options or "--help" in options:
                self.help()
            if '-V' in options or "--version" in options:
                self.version()
            if '-s' in options or "--statistics" in options:
                #--statistics , -s, will show some summary info for each protocol
                self.show_summary=True
            #all other options will be omit!!!
            if _DEBUG: print(self.cmdoptions)#print the command line if debug
        else:
            #by default , do nothing
            pass
        
    def help(self):
        #print(USAGE)
        return USAGE  #if in module mode
    
    def version(self):
        print("python-netstat version:"+__version__)
        print("nettools netstat command line version:")
        proc = subprocess.Popen(cmd,stdout=subprocess.PIPE, shell=True)
        print(readlines(proc.stdout))
        
    def clear(self):
        """ clear the output lists, useful in continous mode
        """
        self.inet_connections=[]  #AF_INET (IPv4), list of inet_stat namedtuple
        self.unix_connections=[]
        self.haserror=False  # clear flag
        self.ready=False 
        self.proc=None
        
    def process(self):
        """  this method can be called directly or run in another thread
        only one thread is started to call several subprocessed!
        test netstat.ready==True, for the readiness of data collection.
        """
        cmd=["netstat"] + self.cmdoptions
        self.proc = subprocess.Popen(cmd,stdout=subprocess.PIPE)  #shell=True
        if _LINUX:
            #need flush() ? 
            self.parse_inet_output_linux(self.proc.stdout)
            #between the moving from 
            if  self.show_AF_UNIX:
                #call the subprocess first
                self.proc = subprocess.Popen(cmd,stdout=subprocess.PIPE) 
                self.parse_output_AF_UNIX(self.proc.stdout)
        elif _NT:
            lines=self.proc.stdout.readlines()
            self.parse_inet_output_nt(lines)  # change the input param from stream into lines? 
            #so the parse can be delay to display/tofile(), but it make program more conplicate!
        else:
            #print("Error: call on non-supported platform")
            sys.exit(-1)
        #if self.show_summary:
        #    self.summary()
        if _DEBUG: print("process of netstat output is finished successfully")

    def is_ready(self):
        """ whether subprocessing has finished
        proc.communicate() ensures process completion due to it calls Popen.wait(). 
        But proc.poll() does not ensure process completion. It returns None if the process is not finished.
        it is not as good as test thread.is_alive(),  process is finished, but parsing in thread is not  finished 
        """
        #if self.proc:
            #if self.proc.poll()==None:   # self.proc is created in thread, access it need protection? it seems need not in this simple f
        if self.thread and self.proc:
            if  self.thread.is_alive():
                #time.sleep(1000)  # sleep 1000ms, sleep() should be put in runner thread?
                return False  #
            else:
                #
                self.ready=True
                return True
        else:
            if _DEBUG: print("call is_ready() before call create thread or subprocess")
            return False
        
    def update(self):
        """ in blocking  or nonblocking mode depends on self.nonblocking
        rerun the updated output from netstat command, build the output list
        print() is not threading safe, thereby, using logging module if needed
        """
        self.clear()
        self.timestamp=datetime.datetime.now() #time.time() give only UTC seconds
        if self.nonblocking:     #used in nonblocking mode to update 
            import threading
            self.thread=threading.Thread(target=self.process)
            self.thread.start()
        else:
            #if _DEBUG: print("command line to call in update():",cmd)
            self.process()
            self.ready=True
            
    def select(self, field):  
        """ show only the selected key/column/field of the namedtuple to show
        return None if field name error
        """
        if field in self.inet_connections._fields():  # ??
            # dome something, yield a generator
            for con in self.inet_connections:
                yield con[field]
        else:
            print("The specified column name does not listed in header:")
            print(self.inet_connections.keys())
            print("please try again")
            # no return means there is error!
            
    def find(self, keyword, connlist=None):
        """ search keyword in each field and each record in inet_connnections's string fields, 
        if found, print the line and return the list
        if no field name is provide, it will search all fileds may contain such a string keyword
        """
        found=[]
        if not type(keyword) is str:
            print("keyword must be string type")
            return []
        if connlist==None: clist=self.inet_connnections
        for l in clist:   # what happen if list is empty?
            if ( any( [ v.find(keyword) > -1  for k,v in l     if  type(v) is str ])    ):
                if _DEBUG: print(l)
                found.append(l)
        return found
        
    #DNS name lookup
    def repr(self):
        pass # if --numeric is used, get the ascii repr
        
    def display(self):
        """ print out the command line output, not aligned
        """
        if not self.ready:
            print("subprocess is not ready, please try later")
            return
        if len(self.inet_connections):
            print("result of command: netstat ",' '.join(self.cmdoptions), "at time", self.timestamp)
            print(self.description)
            print('\t\t'.join(inet_connection._fields))  # how to fit lenght of output by multiple TAB?
            for l in self.inet_connections:
                #print(list(l))
                print('\t\t'.join(list(l)) ) #
        else:
            print("There is no connection by sepecific options, try another options")
         
    def summary(self):
        """ netstat -s will not display list of connections, but a summary, 
        this function (subprocess) return fast enough, so will not be called in thead
        possible return is the output as generator, available for both Linux and Windows?
        On windows, it summarize: ICMPv6 and ICMP,  IP and IPv6, except TCP and UDP
        another way of return is: do the summary based on the inet_connections list, 
        """
        c=self.cmdoptions
        c.append('-s')
        cmd=["netstat"]+c
        #print(cmd)
        proc = subprocess.Popen(cmd,stdout=subprocess.PIPE)   # do not assign to self.proc!
        #, shell=True, on windows am cmd window is shown!
        return proc.stdout.readlines()  
        
    def tofile(self,filename, sep='|'):
        """ save  inet_connections as CSV file , using | to sep fields which is easy to parse back"""
        if len(self.inet_connections):
            with open(filename, "w") as f:
                f.write(sep.join(inet_connection._fields)+os.linesep)  # f.write() will auto append end of line? NO!
                for t in self.inet_connections:
                    f.write(sep.join(list(t))+os.linesep)  # ["Program"] should not contain newline -> strip()
                    # order when translate into list? yes , the are in order!    None item is not accceptable
        else:
            if _DEBUG: print("DEBUG: self.inet_connections is empty, so do nothing in tofile")
        
    
    def parse_inet_output_nt(self,lines):
        """XP WINDOWS 7 output format seems identical!
        effective line begin with set("TCP","UDP")
        the connection description is at least 1 line, but it could be 2 or 3 lines is program name is shown,  
        windows list only inet_family
        (1)if there is error, only two two llines 
        example output, need adminstrator's right, user input("-o -b") means, show extensions
        netstat -p UDP -b
        The requested operation requires elevation.
        
        (2) normal output, if no active connections, still show header line followed by one empty line
        C:\Windows\system32>netstat -a -b -o
        
        Active Connections
        
        Proto  Local Address          Foreign Address        State           PID
        TCP    0.0.0.0:135            Eunice-WANG:0          LISTENING       900
        RpcSs
        [svchost.exe]
        TCP    0.0.0.0:1025           Eunice-WANG:0          LISTENING       608
        [wininit.exe]
        TCP    0.0.0.0:1026           Eunice-WANG:0          LISTENING       300
        eventlog
        [svchost.exe]
        TCP    0.0.0.0:1027           Eunice-WANG:0          LISTENING       720
        [lsass.exe]
        TCP    0.0.0.0:1028           Eunice-WANG:0          LISTENING       408
        Schedule
        [svchost.exe]
        
        """
        # #empty line
        lc=len(lines)
        if lc<3:
            self.haserror=True
            return
        self.description=lines[1]     #if normal output, the first and third line is empty line
        if lc<=5:
            return  #no active connection after 
        #
        self.header=inet_header  # line #4
        if lines[3].lstrip()[:5] != "Proto":               #identify the header line!
            print("Error, the fourth line is not header line")
            print(lines[3])
            self.haserror=True
            return # 
        #build entry
        i=4
        family_set=["TCP","UDP"]  # also  TCPV6  ICMPV6 IP
        while (lc>i) :
            if  (lines[i].lstrip()[:3]  in family_set) :
                entry=[lines[i]]
                i+=1
                while ( lc>i) and (lines[i].lstrip()[:3] not in family_set):
                    entry.append(lines[i])
                    i+=1
                t=parse_inet_connection_nt(entry)  
                if t!=None:
                    self.inet_connections.append(t)
            else:
                print("Error: unexpected connection description line")
                self.haserror=True
        #another way is output list of lines as one connection entry
           
    def parse_inet_output_linux(self,f):
        """ the description is at least 1 line, but it could be more lines,  
        """
        #TCP/IP only, what happend if no effection conntions is listed?
        self.description=f.readline()
        while f.readline()[:5] != "Proto":               #identify the header line!
            print("Error, the fourth line is not header line")
            self.haserror=True
            return  #  will read line will NOT show in later readlines() ??
        #
        self.header=inet_header
        for line in f.readlines():  # out put of readlines()  last list item is None? readlines() keep endofline!
           #the real code does filtering here
           print(line)  #for each line, the last filed may be omit
           self.inet_connections.append(parse_inet_connection_linux(line))
           
    def parse_output_AF_UNIX(self, f):
        """ only for Linux IPC pipe 
        """
        #self.description=f.readline()
        while f.readline()[:5] != "Proto":               #identify the header line!
            continue  #  will read line will NOT show in later readlines() ??
        #header line  has already been skipped!
        self.header=AF_UNIX_header
        for line in f.readlines():
           #the real code does filtering here
           if _DEBUG: print(line)  #for each line, the last filed may be omit
           self.inet_connections.append(parse_connection_AF_UNIX(line))
    #end of class definition
    
    
def test1():
    """
    #example usage of Popen()
    proc = Popen('./test.py',stdin=PIPE,stdout=PIPE,shell=True)  
    for line in sys.stdin:  
            proc.stdin.write(line)  
            proc.stdin.flush()   # if in continous mode, 
            output = proc.stdout.readline()  
            sys.stdout.write(output)  
    """
    #build the command line
    if _LINUX:
        cmd=['netstat','-a','-u', '-e','-p']
    elif _NT:
        cmd=['netstat','-b', '-u']
    else:
        print("OS not supported yet")
    proc = subprocess.Popen(cmd,stdout=subprocess.PIPE)
    for line in proc.stdout:
       #the real code does filtering here
       print(line)
       #pass
       
    #parse_inet_connection(line, sep=' ')
    s="tcp     0    0 localhost:domain     *:*      LISTEN      root    8801     -"
    print(parse_inet_connection(s, sep=' '))  #sucessfully
    #
    
def test():
    print(os.name)
    if _LINUX:  
        print("test under Linux")
        ns=netstat('-a','-t', '-e','-p','-s')
        if not AUTO_UPDATING:            ns.update()
        if NONBLOCKING_MODE:
            while not ns.is_ready(): continue
        print(ns.inet_connections[0])
        #ns.display()
        ns.tofile("netstat_list.csv")
    if _NT:
        print("test under Windows")
        #ns=netstat('-a','-b')  # which will not output but report no right to do that 
        ns=netstat('-a') #show output,  failed in python 3.3,  string
        if not AUTO_UPDATING:            ns.update()
        if NONBLOCKING_MODE:
            while not ns.is_ready(): 
                time.sleep(1)  # sleep 1s, sleep(second)  
                continue
        print(ns.inet_connections[0])
        #ns=netstat('-p', 'UDP', '-p','TCP')      # parse protocal failed!  -> to do
        # if no active connection, it will still show header and end with one line
        #
        ns=netstat('-b')
        if not AUTO_UPDATING:    ns.update()
        if NONBLOCKING_MODE:
            while not ns.is_ready(): 
                time.sleep(1)  # sleep 1
                continue
        ns.display()
        ns.tofile("netstat_list.csv")  # sucessful,  by setting EMPYTY_FIELD=""
        
        #test with adminstrator right!
       
if __name__ == "__main__":
    test()
    
    



