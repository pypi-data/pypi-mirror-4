import curses, time
from gadgets.ui.window import Window

class Prompt(Window):
    """ """

    def __init__(self, label, cast):
        self._label = label
        self._cast = cast
        self._width = 40
        self._height = 4

    def __call__(self, screen):
        win = self._get_subwin(screen)
        self._add_title(win, self._label)
        win.move(2,1)
        curses.echo()
        curses.curs_set(1)
        x = win.getstr()
        curses.curs_set(0)
        curses.noecho()
        try:
            x = self._cast(x)
        except ValueError:
            x = None
        return x
        