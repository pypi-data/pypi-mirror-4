import serial
import time
import datetime
import io

from pyctu.commands import definitions


class CommandBase(object):
    """
    
    """

    def __init__(self, port, baudrate=9600, packet=None):
        self.packet = packet
        self.port = port
        self.baudrate = baudrate
        self._ser = serial.Serial(port, baudrate, timeout=0.1)
        self._sio = io.TextIOWrapper(io.BufferedRWPair(self._ser, self._ser))

    @property
    def categories(self):
        return sorted([field for field in definitions.fields.keys()])

    @property
    def fields(self):
        return definitions.fields
        
    def get_fields(self, category):
        return sorted([field for field in definitions.fields[category]])

    def _is_enabled(self):
        raise NotImplemented

    def _readline(self):
        raise NotImplemented
        
    def _readlines(self):
        raise NotImplemented

    def _read(self, multiline=False):
        if multiline:
            return self._readlines()
        else:
            return self._readline()

    def _write(self, command, multiline=False):
        raise NotImplemented

    def _write_value(self, command, value):
        raise NotImplemented

    def is_writeable(self, category, key):
        val = definitions.fields[category][key]
        return val['writeable']

    def get_value(self, category, key, multiline=False):
        val = definitions.fields[category][key]['value']
        if val is None:
            val = self._get_value(definitions.fields[category][key]['command'], multiline=multiline)
            definitions.fields[category][key]['value'] = val
        return val

    def set_value(self, category, key, value):
        self._set_value(definitions.fields[category][key]['command'], value)
        definitions.fields[category][key]['value'] = None

    def close(self):
        self._ser.close()

        
    

        

               

    

    
