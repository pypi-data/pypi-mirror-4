import serial
import time
import datetime
import io

from pyctu.commands.command_base import CommandBase


class AT(CommandBase):
    """
    sends local AT commands
    """

    def _is_enabled(self):
        self._ser.write('AT\r')
        enabled = ''
        failed = 0
        while enabled != 'OK\r':
            x = self._ser.read()
            if len(x) == 0:
                failed += 1
            if failed >= 5:
                return False
            enabled += x
        return True

    def _enable(self):
        time.sleep(1)
        self._ser.write('+++')
        time.sleep(1)
        if self._read() != 'OK':
            self._ser.write('ATAC\r')
            self._enable()

    def _readline(self):
        output = ''
        while not output.endswith('\r'):
            output += self._ser.read()
        return output.strip()

    def _readlines(self):
        val = self._sio.readlines(50, '\r')
        val = val.replace('\r', '\n')
        return val

    def _get_value(self, command, multiline=False):
        if not self._is_enabled():
            if not self._enable():
                self._remote_at = True
        self._ser.write('AT{0}\r'.format(command))
        return self._read(multiline=multiline)

    def _set_value(self, command, value):
        if not self._is_enabled():
            time.sleep(1)
            self._enable()
        self._ser.write('AT{0} {1}\r'.format(command, value))
        self._read()
        self._ser.write('ATWR\r')
        self._read()

