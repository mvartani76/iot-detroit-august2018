#!/usr/bin/env python3

import smbus
import errno

def i2c_find(bus_number):
    bus_number = bus_number  # 1 indicates /dev/i2c-1
    bus = smbus.SMBus(bus_number)
    device_count = 0
    i2c_found = False

    for device in range(3, 128):
        try:
            bus.write_byte(device, 0)
            print("Found {0}".format(hex(device)))
            device_count = device_count + 1
            i2c_found = True
        except IOError as e:
            if e.errno != errno.EREMOTEIO:
                print("Error: {0} on address {1}".format(e, hex(address)))
                i2c_found = False
        except Exception as e: # exception if read_byte fails
            print("Error unk: {0} on address {1}".format(e, hex(address)))
            i2c_found = False

    bus.close()
    bus = None
    print("Found {0} device(s)".format(device_count))
    return i2c_found