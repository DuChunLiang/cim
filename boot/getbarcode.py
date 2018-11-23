import evdev
from evdev import *
import threading
import time
import datetime

current_barcode = ""

# Reads barcode from "device"
def readBarcodes(device):
    global current_barcode
    print ("Reading barcodes from device")
    print (device)
    for event in device.read_loop():
      if event.type == evdev.ecodes.EV_KEY and event.value == 1:
             keycode = categorize(event).keycode
             if keycode == 'KEY_ENTER':
                  current_barcode = ""
             else:
                  current_barcode += keycode[4:]
             print(current_barcode)

# Finds the input device with the name "Barcode Reader ".
# Could and should be parameterized, of course. Device name as cmd line parameter, perhaps?
def find_device(device_name):
      count = 0
      devices = [evdev.InputDevice(fn) for fn in evdev.list_devices()]
      for d in devices:
         if d.name == device_name:
            count = count + 1
            if count >= 2:
                print("Found device " + d.name + ", path is :"  + d.path)
                device = d
                return device

device_name = 'Barcode Reader '
device_name = 'Logitech USB Receiver'
# Find device...
device = find_device(device_name)

if device is None:
    print("Unable to find " + device_name)
else:
    # ... and read the bar codes.
    readBarcodes(device)

