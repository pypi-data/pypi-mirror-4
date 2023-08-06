import sys
import os
import curses
import argparse
import struct

from pyctu.commands import AT
from pyctu.commands.api import API
from pyctu.commands.api_packet import APIPacket
from pyctu.window import Window
from pyctu.dialogs.prompt import Prompt
from pyctu.dialogs.select import Select
from pyctu.dialogs.bits import Bits
from pyctu.dialogs.reset import Reset
from pyctu.dialogs.multiline import Multiline
from pyctu.dialogs.firmware_update import FirmwareUpdate

class UI(Window):

    def __doc__(self):
        return 'hi'

    def __init__(self, port, baud, api_mode=False, address=None):
        self._api_mode = api_mode
        if api_mode:
            packet = APIPacket()
            self._xbee = API(port, baud, packet)
        elif address:
            packet = APIPacket(address)
            self._xbee = API(port, baud, packet)
        else:
            self._xbee = AT(port, baud)
        self._tab_index = 0
        self._cursor = -1
        self._tabs = None
        self._actions = {
            ord('p'): self._move_up,
            ord('n'): self._move_down,
            258: self._move_down,         #down arrow
            259: self._move_up,         #down arrow
            261: self._next_tab,
            260: self._previous_tab,
            ord('f'): self._next_tab,
            ord('b'): self._previous_tab,
            10: self._prompt,               #enter key
            }
        self._dialogs = {
            'ND': Multiline,
            'ED': Multiline,
            'RE': Reset,
            'firmware_update': FirmwareUpdate
            }

        self._tools = {
            'firmware_update': {'command': 'firmware_update', 'writeable': True, 'value': None, 'special_command': True},
            }

    def _run_dialog(self, x):
        if x in self._actions:
            m = self._actions[x]
            m()
        
    def __call__(self, screen):
        self._height, self._width = screen.getmaxyx()
        self._screen = screen
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)
        self._row, self._col = self._get_center(screen)
        self._draw()
        x = 'go'
        q = ord('q')
        while x != q:
            x = self._get_ch()
            self._run_dialog(x)
            self._draw()
        self._xbee.close()

    def _draw(self):
        self._screen.clear()
        self._screen.border()
        self._draw_tabs()
        self._draw_fields()
        self._draw_values()
        curses.curs_set(0)

    def _draw_xbee_fields(self):
        row = 3
        category = self._xbee.categories[self._tab_index]
        for field in self._xbee.get_fields(category):
            self._screen.addstr(row , 3, '{0}:'.format(field))
            row += 1

    def _draw_tools_fields(self):
        row = 3
        for field in sorted(self._tools.iterkeys()):
            self._screen.addstr(row , 3, '{0}:'.format(field))
            row += 1

    def _draw_fields(self):
        if self._tab_index < len(self._xbee.categories):
            self._draw_xbee_fields()
        else:
            self._draw_tools_fields()

    def _draw_xbee_values(self):
        row = 3
        category = self._xbee.categories[self._tab_index]
        for field in self._xbee.get_fields(category):
            if self._cursor == row - 3:
                ARG = curses.A_BOLD | curses.A_STANDOUT | curses.color_pair(1)
            else:
                ARG = 0
            if self._xbee.fields[category][field].get('special_command'):
                self._screen.addstr(row , 40, '<enter>', ARG)
            else:
                self._screen.addstr(row , 40, self._xbee.get_value(category, field), ARG)
            row += 1

    def _draw_tools(self):
        row = 3
        for field in sorted(self._tools):
            if self._cursor == row - 3:
                ARG = curses.A_BOLD | curses.A_STANDOUT | curses.color_pair(1)
            else:
                ARG = 0
            self._screen.addstr(row , 40, '<enter>', ARG)
            row += 1

    def _draw_values(self):
        if self._tab_index < len(self._xbee.categories):
            self._draw_xbee_values()
        else:
            self._draw_tools()

    @property
    def tabs(self):
        if self._tabs is None:
            self._tabs = [(i, category) for i, category in enumerate(self._xbee.categories + ['tools'])]
        return self._tabs
        
    def _draw_tab(self, i, x, category):
        if i == self._tab_index:
            ARG = curses.A_BOLD | curses.A_STANDOUT | curses.color_pair(1)
        else:
            ARG = 0
        self._screen.addstr(1, x, ' {0} '.format(category), ARG)
        y, x = self._screen.getyx()
        return x

    def _draw_tabs(self):
        x = 2
        for i, category in self.tabs:
            x = self._draw_tab(i, x, category)
        self._screen.addstr(2, 1, '_' * (self._width - 2))

    def _xbee_prompt(self):
        category = self._xbee.categories[self._tab_index]
        field = self._xbee.get_fields(category)[self._cursor]
        val = self._xbee.get_value(category, field)
        vocab = self._xbee.fields[category][field].get('vocabulary')
        bits = self._xbee.fields[category][field].get('bits')
        if vocab is not None:
            dialog = Select(field, val, vocab)
        elif self._xbee.fields[category][field].get('special_command'):
            Dialog = self._dialogs[self._xbee.fields[category][field]['command']]
            dialog = Dialog(field, self._xbee, category, self._xbee.fields[category][field])
        elif bits is not None:
            dialog = Bits(field, val, bits)
        else:
            dialog = Prompt(field, val, str)
        val = dialog(self._screen)
        if val is not None:
            self._xbee.set_value(category, field, val)

    def _tools_prompt(self):
        field = sorted(self._tools.iterkeys())[self._cursor]
        d = self._tools[field]
        Dialog = self._dialogs[d['command']]
        dialog = Dialog(self._xbee)
        self._xbee = dialog(self._screen)

    def _prompt(self):
        if self._tab_index == len(self.tabs) - 1:
            self._tools_prompt()
        else:
            self._xbee_prompt()

    def _move_xbee_cursor(self, direction):
        category = self._xbee.categories[self._tab_index]
        fields = self._xbee.get_fields(category)
        self._cursor += 1 * direction
        if self._cursor <= len(fields) - 1 and self._cursor >= 0:
            field = self._xbee.get_fields(category)[self._cursor]
            if not self._xbee.is_writeable(category, field):
                self._move_cursor(direction)

    def _move_tools_cursor(self, direction):
        fields = sorted(self._tools.iterkeys())
        if not (self._cursor <= len(fields) - 1 and self._cursor >= 0):
            self._cursor += 1 * direction
        
    def _move_cursor(self, direction):
        if self._tab_index < len(self.tabs) - 1:
            self._move_xbee_cursor(direction)
        else:
            self._move_tools_cursor(direction)
                
    def _move_down(self):
        self._move_cursor(1)

    def _move_up(self):
        self._move_cursor(-1)

    def _next_tab(self):
        if self._tab_index < len(self.tabs) - 1:
            self._tab_index += 1
            self._cursor = -1

    def _previous_tab(self):
        if self._tab_index > 0:
            self._tab_index -= 1
            self._cursor = -1

            

def get_args():
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('port')
    parser.add_argument('--baud', type=int, default=9600)
    parser.add_argument('--api', action='store_true')
    parser.add_argument('-a', '--address', type=str, default='')
    return parser.parse_args()

    
def main():
    args = get_args()
    addr = args.address
    if addr == '':
        addr = None
    else:
        a = ''
        for i in xrange(0, len(addr), 2):
            a += struct.pack('B', int(addr[i:i+2], 16))
        addr = a
    ui = UI(args.port, args.baud, api_mode=args.api, address=addr)
    curses.wrapper(ui)
    os.system('stty sane')

