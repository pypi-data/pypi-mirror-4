import curses, time
import string
from pyctu.window import Window

class Reset(Window):
    """ """

    def __init__(self, key, xbee, category, field):
        self._key = key
        self._xbee = xbee
        self._category = category
        self._field = field
        self._label = field['command']
        self._width = 20
        self._height = 20


    def __call__(self, screen):
        curses.curs_set(1)
        self._screen = self._get_subwin(screen)
        self._add_title(self._label)
        curses.echo()
        win.addstr(2, 1, 'hit enter to reset, any other key to exit')
        x = win.getch()
        if x == 10:
            self._xbee.get_value(self._category, self._key)

        

