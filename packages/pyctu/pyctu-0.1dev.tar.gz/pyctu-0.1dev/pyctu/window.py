import curses


class Window(object):

    _short_doc = ''

    def _get_ch(self):
        x = self._screen.getch()
        if x == ord('h'):
            from pyctu.dialogs.help import Help
            d = Help(self.__doc__)
            d(self._screen)
        return x

    def _get_center(self, screen):
        height, width = screen.getmaxyx()
        col = (width/2) - (self._width/2)
        row = (height/2) - (self._height/2)
        return row, col
    
    def _get_subwin(self, screen):
        row, col = self._get_center(screen)
        win = screen.derwin(self._height, self._width, row, col)
        win.clear()
        win.border()
        win.keypad(1)
        return win

    def _add_title(self, title):
        self._screen.addstr(1, 1, '{0}'.format(title).center(self._width - 2), curses.A_BOLD | curses.A_STANDOUT | curses.color_pair(1))
        if self._short_doc != '':
            self._screen.addstr(self._height - 2, 1, '{0}'.format(self._short_doc).center(self._width - 2), curses.A_BOLD | curses.A_STANDOUT | curses.color_pair(1))


