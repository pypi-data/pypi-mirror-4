import curses, time
from gadgets.ui.window import Window

class Alert(Window):
    """ """

    def __init__(self, label, message):
        self._message = message
        self._label = label
        self._width = 40
        self._height = 4

    def __call__(self, screen):
        win = self._get_subwin(screen)
        self._add_title(win, self._label)
        win.addstr(2, 1, self._message)
        x = win.getstr()
        