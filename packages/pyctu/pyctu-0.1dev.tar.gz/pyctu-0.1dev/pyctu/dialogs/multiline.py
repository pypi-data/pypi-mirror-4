import curses, time
import string
from pyctu.window import Window

class Multiline(Window):
    """ """

    def __init__(self, key, xbee, category, field):
        self._key = key
        self._xbee = xbee
        self._category = category
        self._field = field
        self._label = field['command']
        self._width = 60
        self._height = 20

    def __call__(self, screen):
        self._screen = self._get_subwin(screen)
        self._add_title(self._label)
        self._screen.addstr(2, 1, 'discovering nodes')
        values = self._xbee.get_value(self._category, self._key, multiline=True)
        f = open('multi', 'w')
        f.write(values)
        f.close()
        for i, value in enumerate(values.split('\r')):
            self._screen.addstr(i + 3, 1, value)
        self._screen.addstr(self._height - 2, 1, 'press any key to exit')
        x = self.get_ch()
        
