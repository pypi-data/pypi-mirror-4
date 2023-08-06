import curses
import time
import glob
import os
import re
import string
import multiprocessing

from pyctu.window import Window
from pyctu.commands import definitions
from pyctu.dialogs.page_select import PageSelect
from pyctu.commands.firmware import FirmwareProcess


class FirmwareUpdate(Window):
    """
    Select new firmware
    """
    _ebl_expression = re.compile('_([0-9A-F]+)?')

    def __init__(self, xbee):
        self._xbee = xbee
        self._label = 'firmware update'
        self._width = 60
        self._height = 12
        self._port = xbee.port
        self._baudrate = xbee.baudrate
        

    def __call__(self, screen):
        self._screen = self._get_subwin(screen)
        firmware = self._get_firmware()
        names = sorted([os.path.basename(path) for path in firmware], key=self._get_ebl_key)
        names = self._add_help_text(names)
        select = PageSelect('firmware', names)
        i = select(self._screen)
        if i != -1:
            chosen = firmware[i]
            self._reprogram(chosen)
        return self._xbee

    def _reprogram(self, path):
        self._xbee.close()
        out_queue = multiprocessing.Queue()
        in_queue = multiprocessing.Queue()
        updater = FirmwareProcess(in_queue, out_queue, self._xbee.port, path)
        updater.start()
        self._screen.clear()
        self._screen.border()
        self._add_title(self._label)
        self._screen.addstr(2,2, 'hit any key after reseting the xbee')
        self._screen.refresh()
        self._screen.getch()
        out_queue.put({'confirm':True})
        updating = True
        while updating:
            self._screen.clear()
            self._screen.border()
            self._add_title(self._label)
            msg = in_queue.get()
            progress = msg.get('progress', 0)
            x = (self._width - 4) * progress / 100
            if progress == 100:
                updating = False
            self._screen.addstr(3, (self._width / 2) - 8, 'writing firmware')
            msg = '{0}%'.format(progress)
            self._screen.addstr(4, self._width / 2, msg)
            progress_bar = '*' * x
            self._screen.addstr(5, 2, progress_bar)
            self._screen.refresh()
        Class = self._xbee.__class__
        self._xbee = Class(self._xbee.port, self._xbee.baudrate)

    def _get_firmware_path(self):
        path = os.path.join(os.path.expanduser('~'), '.pyctu')
        if not os.path.exists(path):
            os.mkdir(path)
        return path

    def _get_ebl_key(self, name):
        if '/' in name:
            name = os.path.basename(name)
        m = self._ebl_expression.search(name)
        return m.group()

    def _add_help_text(self, names):
        new_names = []
        for name in names:
            m = self._ebl_expression.search(name)
            x = m.group()[2]
            help_text = definitions.ebl_types.get(x, '')
            if len(help_text) > 0:
                offset = self._width - len(name) - 10
            else:
                offset = 0
            name = '{0}{1:>{2}}'.format(name, help_text, offset)
            new_names.append(name)
        return new_names

    def _get_firmware(self):
        path = self._get_firmware_path()
        return sorted(glob.glob('{0}/ebl_files/*.ebl'.format(path)), key=self._get_ebl_key)

    

    

            
            
        
        

