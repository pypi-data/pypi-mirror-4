import curses, time
from gadgets.ui.window import Window

class Help(Window):
    """get help"""

    def __init__(self, lock, dialogs, db):
        self._dialogs = dialogs
        self._lock = lock
        self._width = 60
        self._height = 18

    def __call__(self, screen, data):
        self._lock.acquire()
        win = self._get_subwin(screen)
        self._add_title(win, 'help')
        row = 2
        for key, value in self._dialogs.iteritems():
            doc = value.callable.__doc__
            if doc is not None:
                win.addstr(row, 2, '{0}:  {1}'.format(chr(key), doc))
                row += 1
        row += 1
        win.addstr(row, 2, 'hit any key to exit help')
        win.move(row+1, 2)
        x = win.getch()
        self._lock.release()