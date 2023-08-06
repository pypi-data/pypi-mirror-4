import curses, time
from gadgets.ui.window import Window

class Confirm(Window):
    """ """

    def __init__(self, label):
        self._label = label
        self._width = len(label) + 2
        self._height = 4

    def __call__(self, screen):
        win = self._get_subwin(screen)
        self._add_title(win, self._label)
        win.addstr(2, 1, 'y  n'.center(len(self._label)))
        x = win.getch()
        return x == ord('y')