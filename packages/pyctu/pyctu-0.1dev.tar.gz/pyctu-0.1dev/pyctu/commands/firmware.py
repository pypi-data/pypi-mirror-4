# -*- coding: utf-8 -*-
"""
Programming:
1. Set DTR / SLEEP_RQ low (TTL 0V) and RTS high.
2. Send a serial break to the DIN pin and power cycle or reset the module.
3. When the module powers up, DTR / SLEEP_RQ and DIN should be low (TTL 0V) and RTS should 
be high.
4. Terminate the serial break and send a carriage return at 115200bps to the module.XBee®/XBee‐PRO® ZB RF Modules
© 2009 Digi International, Inc.      122
5. If successful, the module will send the Ember boot loader menu out the DOUT pin at 
115200bps.
6. Commands can be sent to the boot loader at 115200bps.

** XBee-ZB Firmware Versions **

XBee version numbers will have 4 significant digits. A version number is reported by issuing an 
ATVR command.  The response returns 3 or 4 numbers. All numbers are hexadecimal and can have a 
range from 0-0xF. A version is reported as "ABCD". Digits ABC are the main release number and D 
is the revision number from the main release. "B" is a variant designator. The following 
variants exist in ZB firmware:

•	“0" - Coordinator, AT Command Mode (AP=0) 
•	“1" - Coordinator, API Mode (AP=1,2) 
•	“2" - Router AT Command Mode (AP=0) 
•	“3" - Router API Mode (AP=1,2) 
•	“8” – End Device, AT Command Mode (AP=0)
•	“9” – End Device, API Mode (AP=1,2)

Digi has developed an assortment of sensor adapter products that use the ZB firmware.  (See
www.digi.com for details.)  Adapter firmware versions include the following variants:
•	“4" - Router/End Device Sensor Adapter
•	“5" - End Device Power Harvester Adapter
•	“6" - Router/End Device Analog IO Adapter
•	“7" - Router/End Device Digital IO Adapter

All releases will have an even number for C. All internal development will have an odd number 
for C. Field D is always present, even when D is 0. 
"""

import sys
import time
import serial
import multiprocessing
import threading

from pyctu.commands.xmodem import XMODEM

class FirmwareProcess(multiprocessing.Process):

    def __init__(self, out_queue, in_queue, port, path):
        self._port = port
        self._path = path
        self._reset = False
        self._updater = None
        super(FirmwareProcess, self).__init__()
        self._in_queue = in_queue
        self._out_queue = out_queue

    def run(self):
        updater = FirmwareUpdater(self._port, self._path)
        updater.start()
        self._in_queue.get()
        updater._reset = True
        while updater.progress < 100:
            msg = {'progress': updater.progress}
            self._out_queue.put(msg)
            time.sleep(1)
        msg = {'progress': updater.progress}
        self._out_queue.put(msg)

class FirmwareUpdater(threading.Thread):

    def __init__(self, port, path):
        self._port = port
        self._path = path
        self._reset = False
        self._modem = None
        super(FirmwareUpdater, self).__init__()

    @property
    def progress(self):
        if self._modem is None:
            return 0
        else:
            return int(self._modem.percentage)

    def _write_firmware(self):
        stream = open(self._path, 'rb')
        self._modem.send(stream)
        stream.close()
        
    def _read(self, eol='\r'):
        if isinstance(eol, tuple):
            condition = lambda x: eol[0] in x or eol[1] in x
        else:
            condition = lambda x: eol in x
        output = ''
        while True:
            x = self._ser.read()
            output += x
            if condition(output):
                return output.strip()

    def run(self):
        self._ser = serial.Serial(self._port, 115200, timeout=5)
        self._modem = XMODEM(self._ser)
        self._ser.setDTR(True)
        self._ser.setRTS(False)
        self._ser.setBreak(True)
        while not self._reset:
            time.sleep(0.1)
        self._ser.setBreak(False)
        time.sleep(1)
        self._ser.write('\r')
        self._read('BL > ')
        self._ser.write('3')
        val = self._read()
        val = self._read()
        self._ser.write('1')
        self._read('C')
        self._write_firmware()
        val = self._read()
        val = self._read()
        self._ser.write('2')
        time.sleep(0.2)
        self._ser.close()
        time.sleep(0.2)

def main():
    port = sys.argv[1]
    path = sys.argv[2]
    updater = FirmwareUpdater(port, path)
    updater.start()
    raw_input('press enter after reseting the xbee')
    updater._reset = True
    while updater.is_alive():
        print '\r{0}'.format(updater.progress)
        time.sleep(1)

if __name__ == '__main__':
    main()
    
    

    