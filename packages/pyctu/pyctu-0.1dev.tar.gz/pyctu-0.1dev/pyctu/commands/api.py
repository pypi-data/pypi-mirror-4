import serial
import binascii
import struct
import time
import datetime
import ctypes
import io

from pyctu.commands.command_base import CommandBase


class API(CommandBase):
    """
    sends API commands
    (local and remote)
    """
    _byte_struct = struct.Struct('>B')
    _short_struct = struct.Struct('>H')

    @property
    def xbee(self):
        if not hasattr(self, '_xbee'):
            self._xbee = XB 
    
    def _readline(self):
        output = ''
        length = None
        err = 0
        while len(output) < 3:
            s = self._ser.read(1)
            if s == '':
                err += 1
            if err > 2:
                return 'error'
            output += s
        length = self._short_struct.unpack(output[1:])[0] + 4
        err = 0
        while len(output) < length:
            s = self._ser.read(1)
            if s == '':
                err += 1
            if err > 2:
                return 'error'
            output += s
        return self.packet.parse(output)

    def _readlines(self):
        val = self._sio.readlines(50, '\r')
        val = val.replace('\r', '\n')
        return val

    def _get_value(self, command, multiline=False):
        if self.packet.address:
            p = self.packet.remote_api(command)
        else:
            p = self.packet.local_api(command)
        f = open('command', 'a')
        f.write(binascii.hexlify(self.packet.address) + '\n')
        f.close()
        self._ser.write(p)
        return self._read(multiline=multiline)

    def _set_value(self, command, value):
        value = self._byte_struct.pack(int(value))
        if self.packet.address:
            p = self.packet.remote_api(command, parameter=value)
        else:
            p = self.packet.local_api(command, parameter=value)
        self._ser.write(p)
        return self._read()

    def send(self, command, value=None, packet=None):
        if packet is not None:
            self.packet = packet
        p = self.packet.remote_api(command, parameter=value)
        self._ser.write(p)

    def send_local(self, command, value=None, packet=None):
        if packet is not None:
            self.packet = packet
        p = self.packet.local_api(command, value)
        self._ser.write(p)
