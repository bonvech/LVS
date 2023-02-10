from lvs_device import LVS_device
import time


device = LVS_device()
device.connect()

#for i in range(2400):
i = 0
while True:
    print("request", i, end=':')
    device.request('Interval_all')
    i += 1
    #time.sleep(30)

device.unconnect()
print("QQ")



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

#x = input()
