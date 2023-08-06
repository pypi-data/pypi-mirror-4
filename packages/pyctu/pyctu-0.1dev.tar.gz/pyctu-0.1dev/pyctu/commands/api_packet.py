import serial
import binascii
import struct
import time
import datetime
import ctypes
import io

class APIPacket(object):
    """
    sends remote API commands
    a packet looks like:

    7E Length (2 bytes) Frame_Data Checksum
    """
    _api_template = b'\x7E{length}{frame_data}{checksum}'
    _remote_at_request = b'{frame_type}{frame_id}{address}{remote_address}{options}{command}{parameter}'
    _local_at_request = b'{frame_type}{frame_id}{command}{parameter}'
    _command_template = b'{0}{1}'
    _byte_struct = struct.Struct('>B')
    _short_struct = struct.Struct('>H')

    def __init__(self, address=''):
        self.address = address
        self._frame_id = 0
        self._parsers = {
            '\x88': self._local_api_parser,
            '\x97': self._remote_api_parser,
        }

    @property
    def frame_id(self):
        self._frame_id += 1
        if self._frame_id >= 0xff:
            self._frame_id = 0
        return chr(self._frame_id)

    def _get_command(self, command):
        """'D4' -> \x44\x34"""
        return self._command_template.format(
            chr(ord(command[0])),
            chr(ord(command[1]))
        )

    def _get_length(self, data):
        return self._short_struct.pack(len(data))

    def remote_api(self, command, parameter='', options='\x02', remote_address='\xFF\xFE'):
        frame_data = self._remote_at_request.format(
            frame_type='\x17',
            frame_id=self.frame_id,
            address=self.address,
            remote_address=remote_address,
            options=options,
            command=self._get_command(command),
            parameter=parameter
        )
        return self._get_api_packet(frame_data)

    def local_api(self, command, parameter=''):
        frame_data = self._local_at_request.format(
            frame_type='\x08',
            frame_id=self.frame_id,
            command=self._get_command(command),
            parameter=parameter,
        )
        return self._get_api_packet(frame_data)

    def _get_api_packet(self, frame_data):
        return self._api_template.format(
            length=self._get_length(frame_data),
            frame_data=frame_data,
            checksum=self._get_checksum(frame_data)
        )

    def parse(self, response):
        if len(response) == 0:
            return ''
        frame_type = response[3:4]
        parser = self._parsers.get(frame_type)
        if parser is not None:
            return parser(response)
        return ''


    def _remote_api_parser(self, response):
        if len(response) == 0:
            return ''
        length = struct.unpack('>H', response[1:3])[0]
        response = response[3:-1]
        status = response[4:5]
        #if status == '\x00':
        return binascii.hexlify(response[15:])
        #return 'error'

    def _local_api_parser(self, response):
        if len(response) == 0:
            return ''
        length = struct.unpack('>H', response[1:3])[0]
        
        response = response[3:-1]
        status = response[4:5]
        if status == '\x00':
            return binascii.hexlify(response[5:])
        return 'error'

    def _get_checksum(self, data):
        total = 0
        for item in data:
            total += self._byte_struct.unpack(item)[0]
        return chr(0xff - (0xff & total))
