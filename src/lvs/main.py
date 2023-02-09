from lvs_device import LVS_device
#import socket
#import sys
#import socket
import time
#import os



##
##portx='COM1'
##bps=1200
##timex=5
### Последовательный порт выполняется до тех пор, пока он не будет открыт, а затем использование команды open сообщит об ошибке
##ser = serial.Serial(portx, int(bps), timeout=1, parity=serial.PARITY_NONE,stopbits=1)
##if (ser.isOpen()):
##print(“open success”)
### Некоторые данные в строке порта должны быть декодированы
##
##command = 
##ser.write(“hello”.encode())
##while (True):
##line = ser.readline()
##if(line):
##print(line)
##line=0
##else:
##print(“open failed”)
##ser.close () # Закройте порт



device = LVS_device()

##device.read_path_file()
##device.print_params()
##
##device.MAXID = device.MINID
##print(device.MAXID)
##
##print(device.MINID)
##device.MINID = device.MINID+10
##print(device.MINID)
##
##device.write_path_file()

device.connect()
#device.request('BH_protocol::DA')

for i in range(15):
    print("request", i)
    device.request('Interval_all')
    #time.sleep(30)
device.request('Interval_all')
device.unconnect()


print("QQ")
#x = input()






