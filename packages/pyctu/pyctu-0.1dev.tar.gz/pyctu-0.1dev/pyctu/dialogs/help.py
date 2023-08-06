import curses, time
import string
from pyctu.window import Window

class Help(Window):
    """Type a value and press enter """

    _characters = string.digits + string.letters

    def __init__(self, msg):
        self._label = 'help'
        self._msg = msg
        self._width = 40
        self._height = 20
        self._position = 2

    def __call__(self, screen):
        curses.curs_set(1)
        self._screen = self._get_subwin(screen)
        self._screen.clear()
        self._screen.border()
        self._add_title(self._label)
        for i, row in enumerate(self._msg.split('\n')):
            self._screen.addstr(2 + i, 1, row)
        self._get_ch()

