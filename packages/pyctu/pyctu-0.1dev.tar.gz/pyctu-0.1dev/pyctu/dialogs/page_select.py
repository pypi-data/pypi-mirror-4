import curses, time
import string
from pyctu.window import Window
from pyctu.dialogs.confirm import Confirm

class PageSelect(Window):
    """
    Press 'n' and 'p' to scroll
    through the pages.
    Enter a number to
    select a firmware.
    Press 'q' to quit.
    """
    
    _short_doc = '<p>revious page <n>ext page'

    _characters = string.digits + string.letters

    def __init__(self, label, choices):
        self._label = label
        self._choices = choices
        self._width = 60
        self._height = 12
        self._selected = 0
        self._page = 0
        self._page = 0
        self._moves = {
            ord('n'): self._next_page,
            ord('p'): self._previous_page,
            }

    def _select(self, x):
        if (x == ord('n') or x == 258) and self._selected <= len(self._vocabulary):
            self._value = str(self._vocabulary[self._selected + 1][0])
        if (x == ord('p') or x == 259) and self._selected > 0:
            self._value = str(self._vocabulary[self._selected - 1][0])

    def _draw_page(self):
        self._screen.clear()
        self._screen.border()
        self._add_title(self._label)
        row = 3
        col = 2
        start = self._page * 5
        end = start + 5
        for i, choice in enumerate(self._choices[start:end]):
            self._screen.addstr(row, col, '{0}: {1}'.format(i + 1,  choice))
            row += 1
        
 
    def __call__(self, screen):
        self._screen = self._get_subwin(screen)
        self._add_title(self._label)
        x = ''
        while x != ord('q'):
            self._draw_page()
            x = self._get_ch()
            if x in self._moves:
                self._moves[x]()
            elif x > ord('0') and x < ord('6'):
                x = int(chr(x)) - 1
                i = self._page * 5 + x
                chosen = self._choices[i]
                dialog = Confirm(chosen)
                if dialog(self._screen):
                    return i
        return -1

    def _next_page(self):
        self._page += 1

    def _previous_page(self):
        self._page -= 1



                
                    
                    




        