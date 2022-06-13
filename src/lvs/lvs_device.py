import sys
import socket
import time
import datetime
from datetime import datetime
#import pandas as pd
import os
import serial


class LVS_device:
    def __init__(self):
        self.develop = False ## flag True for develop stage
        self.logfilename = "lvs_log.txt"
        self.configfilename = "lvs_config.py"
        self.datafilename = 'dummy_data.dat'

        self.MINID = 0
        self.MAXID = 0
        self.pathfile = None ## data directory name

        ##  COM port properties
        self.com_wait = 5    ## seconds to sleep before read answer from comport
        self.timeout = 15    ## seconds to wait  response from COM port
        self.portName = None
        self.BPS = 1200
        self.PARITY = serial.PARITY_NONE
        self.STOPBITS = serial.STOPBITS_ONE
        self.BYTESIZE = serial.EIGHTBITS
        self.TIMEX = 1

        self.buff = ''
        self.info = ''
        self.device_name = None

        self.file_header = ''

        if 'ix' in os.name:
            self.sep = '/'  ## -- path separator for LINIX
        else:
            self.sep = '\\' ## -- path separator for Windows

        ## ----------------------------------
        ##    run init procedures
        #self.fill_header()  ## fill header
        self.read_path_file()


    ## ----------------------------------------------------------------
    ##  Fill header for data file
    ## ----------------------------------------------------------------
    def fill_header(self):
        self.file_header = ""


    ## ----------------------------------------------------------------
    ## read config params from file tca08_config.py as a python module
    ## ----------------------------------------------------------------
    def read_path_file(self):
        # check file
        try:
            import lvs_config as config
        except:
            print(f"\nread_path_file Error!! No file {self.configfilename} to read config\n\n")
            return -1

        self.portName = config.COM
        self.MINID = int(config.MINID)
        #self.MAXID = self.MINID
        self.pathfile = config.path

        try:
            self.develop = config.develop
        except:
            pass

        if self.develop == True:
            print("--------------------------------------------")
            print("  Warning!   Run in emulation mode!    ")
            print("--------------------------------------------")

        self.prepare_dirs()
        self.prepare_filenames()


    ## ----------------------------------------------------------------
    ##  make filenames to save data
    ## ----------------------------------------------------------------
    def prepare_filenames(self):
        ## get current datatime
        tt = datetime.now()
        timestamp = str(tt.year) + '_' + str(tt.month)

        ## make names
        self.datafilename = self.pathfile + self.sep + timestamp + "_data.tsv"
        self.logfilename  = self.pathfile + self.sep + timestamp + "_lvs_log.txt" 
        print(self.datafilename)
        print(self.logfilename)



    ## ----------------------------------------------------------------
    ##  make dirs to save data
    ## ----------------------------------------------------------------
    def prepare_dirs(self):
        ## \todo ПОПРАВИТЬ в конфигурацилонном файле СЛЕШИ В ИМЕНИ ДИРЕКТОРИИ  !!!   для ВИНДА
        if 'ix' in os.name:
            sep = '/'  ## -- separator for LINIX
        else:
            sep = '\\' ## -- separator for Windows

        path = self.pathfile
        if not os.path.exists(path):   os.system("mkdir " + path)
        path = self.pathfile + sep + 'Data'
        if not os.path.exists(path):   os.system("mkdir " + path)
        path = self.pathfile + sep + 'Logs'
        if not os.path.exists(path):   os.system("mkdir " + path)



    ## ----------------------------------------------------------------
    ## save config to bak file
    ## ----------------------------------------------------------------
    def write_path_file(self):
        filename = self.configfilename + ".bak"
        if not self.pathfile:
            print("\nwrite_path_file Error!!: no data to write to file ", filename, '\n')
            return -1

        f = open(filename, 'w')
        f.write("# Attention! Write with python sintax!!!!\n")
        f.write("#\n#\n# Directory for DATA:\n#\n")
        f.write("path = '" + self.pathfile + "'\n")

        f.write("#\n#\n# LVS:   Serial Port:\n#\n")
        f.write("COM = '" + self.portName + "'\n")

        f.write("#\n#\n# LVS:  Last Records:\n#\n")
        f.write("MINID = " + str(self.MINID) + "\n")
        f.close()


    ## ----------------------------------------------------------------
    ## print params from config file
    ## ----------------------------------------------------------------
    def print_params(self):
        print("Directory for DATA: ", self.pathfile)
        print("portName = ", self.portName)
        print("MINID = ",    self.MINID)


    ## ----------------------------------------------------------------
    ## Open COM port
    ## ----------------------------------------------------------------
    def connect(self):
        self.ser = serial.Serial(
                port =     self.portName,
                baudrate = self.BPS,       # 115200,
                parity =   self.PARITY,    # serial.PARITY_NONE,
                stopbits = self.STOPBITS,  # serial.STOPBITS_ONE,
                bytesize = self.BYTESIZE,  # serial.EIGHTBITS
                timeout  = self.timeout
                )
        if (self.ser.isOpen()):
            print("COM port open success\n")
            return 0
        print("CON port open failed\n")
        return -1


    ## ----------------------------------------------------------------
    ## Close COM port
    ## ----------------------------------------------------------------
    def unconnect(self):
        self.ser.close() # Закройте порт


    ## ----------------------------------------------------------------
    ## Send request to COM port
    ## ----------------------------------------------------------------
    def request(self, command, start=0, stop=0):
        f = open(self.logfilename, 'a') 

        command = chr(2) + 'DA' + chr(3)
        #print(command)
        f.write(str(command))

        try:
            self.ser.write(command.encode())
        except:
            text = '\nrequest(): Error in writing to COM port!\n Check: COM port is open?'
            print(text)
            f.write(text + '\n')
            return -1

        time.sleep(self.com_wait)

        ## read answer from buffer
        self.buff = ""
        while self.ser.in_waiting:
            line = self.ser.read() #.decode()
            if (line):
                self.buff += line
                #print("{{"+line+"}}")
                #f.write("{{"+str(line)+"}}\n")
                if line == b'\x03':
                    ## read 2 bytes to finish detector data line
                    for _ in range(2):
                        line = self.ser.read()
                        if line: 
                            self.buff += line

                    ## print data string to data file
                    print("One line received from device")
                    f.write("{{" + str(self.buff) + "}}\n")
                    ## open data file
                    fdata = open(self.datafilename, 'a')
                    fdata.write(self.buff.decode() + '\n')
                    fdata.write(str(self.buff) + '\n')
                    fdata.close()

                    ## refresh buffer 
                    self.buff = ''

        #print(self.buff)

        if len(self.buff) == 0:
            text = 'Warning!! No answer to request for command' + command
            print(text)
            f.write(text + '\n')
        #print('request(): buff = ', self.buff)
        f.write("\n")
        f.close()





    ## ----------------------------------------------------------------
    ##  END
    ## ----------------------------------------------------------------




    def parse_raw_data(self):
        if len(self.buff) < 10:
            return
        #self.buff = self.buff.split("TCA>")
        print(self.buff)
        for line in self.buff:
            if len(line) < 50:
                continue
            print(line)
            mm, dd, yy = line.split("|")[2][:10].split('/')
            if mm != self.mm or yy != self.yy:
                filename = '_'.join((yy, mm)) + '_TCA-S08-01006.raw'
                filename = self.pathfile +'\\raw\\' + filename
                print(filename)
                if self.file_raw:
                    self.file_raw.close()
                self.file_raw = open(filename, "a")
            self.file_raw.write(line)
            self.file_raw.write('\n')
            
        self.file_raw.flush()
        self.mm = mm
        self.yy = yy


    def parse_format_W_data(self):
        ## main
        print('qqqqqqqqqqq')
        if len(self.buff) < 10:
            return
        #self.buff = self.buff.split("TCA>")
        if 'ix' in os.name:
            self.buff = self.buff.split("\n")  ## for Linux
        else:
            self.buff = self.buff.split("\r\n") ## for Windows

        lastmm, lastyy = '0', '0'
        filename = ''
        lastline = ''
        need_check = True
        dateformat = "%Y/%m/%d %H:%M:%S"
        #print('lines:')
        #print(self.buff)

        ## for excel data
        header = self.file_header[self.file_header.find("Date"):].split("; ")
        columns = ['Date(yyyy/MM/dd)', 'Time(hh:mm:ss)', 'BC1', 'BC2', 'BC3', 'BC4', 'BC5', 'BC6', 'BC7', 'BB(%)']
        colnums = [header.index(x) for x in columns]      
        rows_list = []

        for line in self.buff[::-1]:
            #print('line:   ',line)
            yy, mm, _ = line.split()[0].split('/')
            #print(yy, mm)

            # for first line or new file
            if mm != lastmm or yy != lastyy:
                ##### ddat file 
                filename = '_'.join((yy, mm)) + '_TCA-S08-01006.wdat'
                filename = self.pathfile +'\wdat\\' + filename
                print(filename,mm,yy,lastmm,lastyy)
                try:
                    ## ddat file exists
                    f = open(filename, 'r')
                    lastline = f.readlines()[-1].split()
                    #print(lastline)
                    f.close()
                    print('3')
                    lasttime = lastline[0] + ' ' + lastline[1]
                    print('1  ',lasttime)
                    lasttime = datetime.strptime(lasttime, dateformat)
                    print('4',lastmm,lastyy,mm,yy)
                    need_check = True
                except:
                    ## no file
                    print('NOT FILE', filename)
                    f = open(filename, 'a')        
                    f.write(self.file_header)
                    f.close()
                    lastline = []
                    need_check = False 
                lastmm = mm
                lastyy = yy

            ## add line data to dataframe 
            line_to_dataframe = [line.split()[i] for i in colnums]
            #print("line_to_dataframe:>",line_to_dataframe)
            line_to_dataframe = line_to_dataframe[:2]\
                                + [int(x) for x in line_to_dataframe[2:-1]]\
                                + [float(line_to_dataframe[-1])]
            rows_list.append(line_to_dataframe)
            #print(rows_list)


            ## check line to be added to datafile
            if need_check: # and len(lastline):
                #print(line)
                nowtime  = line.split()[0] + ' ' + line.split()[1]
                #print(nowtime)
                nowtime  = datetime.strptime(nowtime,  dateformat)
                print(nowtime - lasttime)
                ## if line was printed earlier
                if nowtime <= lasttime:
                    continue

            need_check = False

            ## write to file
            f = open(filename, 'a')
            f.write(line+'\n')
            f.close()
