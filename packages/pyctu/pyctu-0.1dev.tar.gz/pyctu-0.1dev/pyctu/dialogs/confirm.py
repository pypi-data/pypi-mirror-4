import curses, time
import string
from pyctu.window import Window

class Confirm(Window):
    """ """

    def __init__(self, msg):
        self._width = len(msg) + 6
        self._height = 5
        self._msg = msg
        self._confirm = False

    def _handle_key(self, key):
        if key == 10:
            return False
        if key == ord('y'):
            self._confirm = True
        elif key == ord('n'):
            self._confirm = False
        elif key == 260 or key == 261 or key == 9:
            self._confirm ^= True
        return True

    def _draw_buttons(self):
        ARG = curses.A_BOLD | curses.A_STANDOUT | curses.color_pair(1)
        self._screen.addstr(3, 3, 'yes', ARG * int(self._confirm))
        self._screen.addstr(3, 10, 'no', ARG * int(not self._confirm))

    def __call__(self, screen):
        self._screen = self._get_subwin(screen)
        self._add_title('confirm')
        self._screen.addstr(2, 1, self._msg)
        self._draw_buttons()
        while self._handle_key(self._get_ch()):
            self._draw_buttons()
        return self._confirm
            