import sys
import socket
import time
import datetime
from datetime import datetime
#import matplotlib.pyplot as plt
#import pandas as pd
import os
import serial


class LVS_device:
    def __init__(self):
        self.develop = False ## flag True for develop stage
        self.verbose = True  ## flag True for print a lot of information
        
        self.device_name = None
        self.MINID = 0
        self.MAXID = 0

        ## for data files
        self.workdir = "."       ## work directory name
        self.datadir = "."       ## data directory name
        self.datafilename = '_lvs_data.csv'
        self.logfilename  = '_lvs_log.txt'
        self.datafile_header = ''

        #self.buff = ''
        #self.info = ''
        
        ##  COM port properties
        self.portName = 'COM7'
        self.BPS      = 1200
        self.PARITY   = serial.PARITY_NONE
        self.STOPBITS = serial.STOPBITS_ONE
        self.BYTESIZE = serial.EIGHTBITS
        self.TIMEX    = 1
        
        ##  path separator
        if 'ix' in os.name:
            self.sep = '/'  ## -- path separator for LINIX
        else:
            self.sep = '\\' ## -- path separator for Windows

        ##  ----------------------------------
        ##    run init procedures
        self.fill_header()
        #self.read_path_file()
        ##  prepare dirs and files for data and logs
        self.prepare_dirs()
    

    ##  ----------------------------------------------------------------
    ##  ----------------------------------------------------------------
    ##   Fill header for data file
    ##  ----------------------------------------------------------------
    def fill_header(self):
        self.datafile_header = "Date;Time;Type;D/N;Pump Run Time Total(h:m);Time of Measurement(h:m);Motorspeed(%);Actual(m3/h);Actual(Nm3/h);Actual(m3);Actual(Nm3);Filter Press.(hPa);Air Pressure(hPa);Outdoor Temp.('C);Filter Temp.('C);Chamber Temp.('C);Temperature orifice('C);Rel.Humidity(%);Magazine Position;Measuring Typ;Sample ID;Max. Planned Pos.;Event;Error"


    ##  ----------------------------------------------------------------
    ##   Make dirs and filenames to save data
    ##  ----------------------------------------------------------------
    def prepare_dirs(self):
        ## get current datatime
        tt = datetime.now()
        timestamp = f"{tt.year}_{tt.month:02}"

        path = self.datadir
        if not os.path.exists(path):   os.system("mkdir " + path)

        ## for data files
        self.datafilename = path + self.sep + timestamp + self.datafilename
        if not os.path.lexists(self.datafilename):
            fdata = open(self.datafilename, "w")
            fdata.write(self.datafile_header)
            fdata.close()

        ## for log files
        self.logfilename  = path + self.sep + timestamp + self.logfilename 
        
        if self.verbose:
            print(self.datafilename)
            print(self.logfilename)



    def read_path_file(self):
        # check file
        #print("read file")
        try:
            f = open("PATHFILES.CNF")
        except:
            print("Error!! No file PATHFILES.CNF\n\n")
            return -1
        
        params = [x.replace('\n','') for x in f.readlines() if x[0] != '#']
        f.close()
        #print(params)
        
        for param in params:
            if "COM" in param:
                self.portName = (param.split('=')[1])
##            elif "BPS" in param:
##                self.BPS = int(param.split('=')[1])
##            elif "STOPBITS" in param:
##                self.STOPBITS   = int(param.split('=')[1])
##            elif "PARITY" in param:
##                parity   = int(param.split('=')[1])
##                if parity:
##                    self.PARITY = serial.PARITY_EVEN
##                else:
##                    self.PARITY = serial.PARITY_NONE
##            elif "TIMEX" in param:
##                self.TIMEX   = int(param.split('=')[1])
            elif "MINID" in param:
                self.MINID = int(param.split('=')[1])
                self.MAXID = self.MINID
            else:
                self.workdir = param


    def write_path_file(self):
        f = open("PATHFILES.CNF.bak", 'w')
        f.write("#\n")
        f.write("# Directorry for DATA:\n")
        f.write("#\n")
        f.write(self.pathfile+"\n")
        f.write("#\n")
        f.write("#\n")
        f.write("# TCA08:   Serial Port:\n")
        f.write("#\n")
        f.write("COM="+self.portName+"\n")
        f.write("#\n")
        f.write("#\n")
##        f.write("BPS=115200\n")
##        f.write("#\n")
##        f.write("STOPBIT=1\n")
##        f.write("#\n")
##        f.write("PARITY=0\n")
##        f.write("#\n")
##        f.write("TIMEX=5\n")
##        f.write("#\n")
        f.write("# TCA08:  Last Records:\n")
        f.write("#\n")
        f.write("MINID="+str(self.MINID)+"\n")
        f.write("#\n")
        f.close()


    ##  ----------------------------------------------------------------
    ##  Print params 
    ##  ----------------------------------------------------------------
    def print_params(self):
        print("Directory for DATA:   ", self.datadir)
        print("portName = ", self.portName)
        print("BPS = ",      self.BPS)
        print("STOBITS = ",  self.STOPBITS)
        print("PARITY = ",   self.PARITY)
        print("BYTESIZE = ", self.BYTESIZE)
        print("TIMEX = ",    self.TIMEX)
        print("MINID = ",    self.MINID)


# Последовательный порт выполняется до тех пор, пока он не будет открыт, а затем использование команды open сообщит об ошибке
##        self.ser = serial.Serial(
##                port=self.COM,
##                baudrate=self.BPS,
##                timeout=1,
##                parity=self.PARITY,
##                stopbits=self.STOPBIT
##                )
##        self.ser = serial.Serial(
##                port=self.portName,
##                baudrate=115200,
##                parity=serial.PARITY_NONE,
##                stopbits=serial.STOPBITS_ONE,
##                bytesize=serial.EIGHTBITS
##                )


    ##  ----------------------------------------------------------------
    ##  Open COM port
    ##  ----------------------------------------------------------------
    def connect(self):
        print(f"Connection to COM port {self.portName} ...", end='')
        if self.develop:
            print("   simulation")
            return 2

        self.ser = serial.Serial(
                port =     self.portName,
                baudrate = self.BPS,       # 115200,
                parity =   self.PARITY,    # serial.PARITY_NONE,
                stopbits = self.STOPBITS,  # serial.STOPBITS_ONE,
                bytesize = self.BYTESIZE,  # serial.EIGHTBITS
                #timeout  = self.timeout
                )
        if (self.ser.isOpen()):
            print(f"{self.portName} port open success\n")
            return 0
        print(f"\n\n Error! {self.portName} port open failed\n")
        return -1


    ##  ----------------------------------------------------------------
    ##  Close COM port
    ##  ----------------------------------------------------------------
    def unconnect(self):
        print(f"Close COM port {self.portName} ... ", end='')
        if self.develop:
            print("...   simulation")
            return 2
        self.ser.close() # Закройте порт    


    ##  ----------------------------------------------------------------
    ##  Send request to COM port
    ##  ----------------------------------------------------------------
    def request(self, command):
        flog = open(self.logfilename, 'a') 

        if 'BH_protocol::DA' in command:
            command = chr(2) + 'D'+'A' + chr(3)
            flog.write(str(command))
            print(command)
            self.ser.write(command.encode())
            time.sleep(5)
        else:
            time.sleep(30)

        dataline = ''
        while self.ser.in_waiting:
            line = self.ser.read()
            #print(line)
            if (line):
                try:
                    line = str(line.decode())
                    f.write("{{"+str(line)+"}}\n")  #print("{{"+line+"}}")
                    dataline = dataline + line
                except Exception as err:
                    ##  напечатать строку ошибки
                    text = f"ERROR: {err}" + '\n'
                    print(text)
                    flog.write(text)
                    ##  напечатать ошибочный байт
                    print("Cant decode byte:", ord(line), line)
                    flog.write("Cant decode byte: " + str(ord(line)) + '\n')
                    flog.write("{{"+str(line)+"}}\n")
                line=""
            else:
                text = "Error: no line in read in request :: is open failed\n"
                print(text)
                flog.write(text)
                break
        
        dataline = dataline.replace('\r', '')
        ## write to logfilename
        flog.write("dataline: " + dataline.rstrip() + '\n')
        flog.close()
        
        ## write dataline to datafile
        print(dataline)
        if len(dataline) > 4:
            with open(self.datafilename, 'a') as fdata:
                fdata.write(dataline) 

                
    ##  ----------------------------------------------------------------
    ##  ----------------------------------------------------------------
    ##  ----------------------------------------------------------------
    ##  ----------------------------------------------------------------
    ##  ----------------------------------------------------------------
    ##  ----------------------------------------------------------------

