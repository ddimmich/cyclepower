import os, sys
import binascii
from bluepy import btle

"""
From: 
https://gist.github.com/sam016/4abe921b5a9ee27f67b3686910293026

attributes.put("00002a5d-0000-1000-8000-00805f9b34fb", "Sensor Location");
attributes.put("00002a63-0000-1000-8000-00805f9b34fb", "Cycling Power Measurement");
attributes.put("00002a64-0000-1000-8000-00805f9b34fb", "Cycling Power Vector");
attributes.put("00002a65-0000-1000-8000-00805f9b34fb", "Cycling Power Feature");
attributes.put("00002a66-0000-1000-8000-00805f9b34fb", "Cycling Power Control Point");


attributes.put("00001816-0000-1000-8000-00805f9b34fb", "Cycling Speed and Cadence");
attributes.put("00001818-0000-1000-8000-00805f9b34fb", "Cycling Power");
attributes.put(HEART_RATE_MEASUREMENT, "Heart Rate Measurement");
"""

"""
 {
    "id": "org.bluetooth.characteristic.cycling_power_measurement",
    "name": "Cycling Power Measurement",
    "code": "0x2A63",
    "specification": "GSS"
  },
  {
    "id": "org.bluetooth.characteristic.cycling_power_vector",
    "name": "Cycling Power Vector",
    "code": "0x2A64",
    "specification": "GSS"
  },
  {
    "id": "org.bluetooth.characteristic.cycling_power_feature",
    "name": "Cycling Power Feature",
    "code": "0x2A65",
    "specification": "GSS"
  },
  {
    "id": "org.bluetooth.characteristic.cycling_power_control_point",
    "name": "Cycling Power Control Point",
    "code": "0x2A66",
    "specification": "GSS"
  },
  {
    "id": "org.bluetooth.service.cycling_speed_and_cadence",
    "name": "Cycling Speed and Cadence",
    "code": "0x1816",
    "specification": "GSS"
  },
  {
    "id": "org.bluetooth.service.cycling_power",
    "name": "Cycling Power",
    "code": "0x1818",
    "specification": "GSS"
  },
"""


class MyDelegate(btle.DefaultDelegate):
    def __init__(self, params):
        btle.DefaultDelegate.__init__(self)
        # ... initialise here

    def handleNotification(self, cHandle, data):
        # ... perhaps check cHandle
        # ... process 'data'
        # TODO: figure out what the values are!
        print(f'{cHandle}: {binascii.b2a_hex(data)}')


def main():
    if not os.geteuid() == 0:
        # todo - get the user to set perms as in the readme.
        sys.exit("\nOnly root can run this script\n")
    scanner = btle.Scanner()

    print('Scanning...')
    # try to find the right kind of devices
    for x in scanner.scan():
        print(f'Scan data: {x.getScanData()}')
        if x.addr != 'c8:d6:80:ac:85:d1':
            print(f'Skipping {x.addr}, {x.addrType}, {x.iface}')
            continue
        p = btle.Peripheral(x.addr, x.addrType, x.iface)

        # uuids = p.discoverServices()
        for service in p.discoverServices():
            print(f'{service.getCommonName()}, {service}')
            if service.getCommonName() == 'Cycling Power':
                break

        power = p.getServiceByUUID(service)
        for c in power.getCharacteristics():
            print(f'{c.uuid} supportsread: {c.supportsRead()}, props {c.propertiesToString()} Handle: {c.getHandle()}')
            if c.supportsRead(): print(c.read())
            if 'WRITE' in c.propertiesToString():
                # these may be useful at some point.
                pass
                #print(c.write(b'\x01\x00'))
            if 'NOTIFY' in c.propertiesToString():
                # Grab notify
                notify = c

        # Start listening...
        p.setDelegate(MyDelegate(notify.getHandle()))
        p.writeCharacteristic(notify.getHandle()+1, b'\x01\x00', True)
    try:
        while True:
            if p.waitForNotifications(1.0):
                # handleNotification() was called
                continue
            else:
                print("Waiting...")
    finally:
        # switch off listening, and disconnect
        print('Bye!')
        p.writeCharacteristic(notify.getHandle()+1, b'\x00\x00', True)
        p.disconnect()


if __name__ == "__main__":
    main()

