import curses, time
import string
from pyctu.window import Window

class Select(Window):
    """ """

    _characters = string.digits + string.letters

    def __init__(self, label, value, vocabulary):
        self._label = label
        self._value = value
        self._vocabulary = vocabulary
        self._width = 60
        self._height = 20
        self._selected = 0
        self._page = 0

    def _draw(self):
        row = 0
        for key, value in self._vocabulary:
            if self._value == str(key):
                self._selected = row
                ARG = curses.A_BOLD | curses.A_STANDOUT | curses.color_pair(1)
            else:
                ARG = 0
            self._screen.addstr(row + 2, 2, '{0}:   {1}'.format(key, value), ARG)
            row += 1

    def _select(self, x):
        if (x == ord('n') or x == 258) and self._selected <= len(self._vocabulary):
            self._value = str(self._vocabulary[self._selected + 1][0])
        if (x == ord('p') or x == 259) and self._selected > 0:
            self._value = str(self._vocabulary[self._selected - 1][0])
        
 
    def __call__(self, screen):
        self._screen = self._get_subwin(screen)
        self._add_title(self._label)
        while True:
            self._draw()
            x = self._get_ch()
            if x == 10:
                return str(self._value)
            self._select(x)
