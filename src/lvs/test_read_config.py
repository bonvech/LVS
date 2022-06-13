from lvs_device import LVS_device
import serial

device = LVS_device()

#device.read_path_file()
device.print_params()
device.write_path_file()

device.connect()
device.request()
device.unconnect()

#x = input("\n\ninput enter to finish")
