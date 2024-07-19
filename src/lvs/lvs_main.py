from lvs_device import LVS_device
import time


device = LVS_device()
if device.connect():
    exit()

i = 0
while True:
    print("request", i, end=':')
    device.request('Interval_all')
    i += 1
    i = i % 10000
    #time.sleep(30)

device.unconnect()
print("QQ")

#x = input()
