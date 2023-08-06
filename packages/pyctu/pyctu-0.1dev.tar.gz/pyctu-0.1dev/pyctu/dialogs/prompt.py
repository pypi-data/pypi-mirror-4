import curses, time
import string
from pyctu.window import Window

class Prompt(Window):
    """ """

    _characters = string.digits + string.letters

    def __init__(self, label, value, cast):
        self._label = label
        self._value = value
        self._cast = cast
        self._width = 40
        self._height = 4
        self._position = 2

    def _is_letter_or_number(self, key):
        try:
            key = chr(key)
        except ValueError:
            return False
        return key in self._characters
        
    def _handle_key(self, key):
        f = open('key', 'a')
        f.write(str(key))
        f.close()
        if key == 10:
            return False
        if self._is_letter_or_number(key):
            self._value += chr(key)
        elif key == 263 or key == 127:
            self._value = self._value[:-1]
        return True

    def __call__(self, screen):
        curses.curs_set(1)
        self._screen = self._get_subwin(screen)
        self._add_title(self._label)
        curses.echo()
        self._screen.addstr(2, 1, self._value)
        while self._handle_key(self._screen.getch()):
            self._screen.addstr(2, 1, ' ' * 38)
            self._screen.addstr(2, 1, self._value)
        curses.noecho()
        try:
            value = self._cast(self._value)
        except ValueError:
            value = None
        curses.curs_set(0)
        return value

