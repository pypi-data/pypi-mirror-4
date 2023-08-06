import curses, time
import string
from pyctu.window import Window

class Bits(Window):
    """ """

    _characters = string.digits + string.letters

    def __init__(self, label, value, bits):
        self._label = label
        self._value = int('0x{0}'.format(value), 16)
        self._bits = bits
        self._width = 60
        self._height = 6
        self._cursor = 0


    def _draw_bit(self, i, ARG):
        """
        0xFFF:  0b111111111111
        """
        x = (len(self._bits) - i) + 3
        value = (self._value & 2 ** i) >> i
        self._screen.addstr(2, x, str(value), ARG)

    def _draw(self):
        self._screen.addstr(3, 2, ' ' * (self._width - 3))
        for i, label in enumerate(self._bits):
            if self._cursor == i:
                ARG = curses.A_BOLD | curses.A_STANDOUT | curses.color_pair(1)
                self._screen.addstr(3, 2, label)
            else:
                ARG = 0
            self._draw_bit(i, ARG)
        self._screen.addstr(2, 1, '0b')

    def _flip_bit(self):
        bit = (1 << self._cursor)
        self._value ^= bit

    def _select(self, x):
        if (x == ord('n') or x == 260) and self._cursor <= len(self._bits) - 1:
            self._cursor += 1
        elif (x == ord('p') or x == 261) and self._cursor > 0:
            self._cursor -= 1
        elif (x == 32): #space bar
            self._flip_bit()
 
    def __call__(self, screen):
        self._screen = self._get_subwin(screen)
        self._add_title(self._label)
        while True:
            self._draw()
            x = self._get_ch()
            if x == 10:
                return hex(self._value)[2:]
            self._select(x)
