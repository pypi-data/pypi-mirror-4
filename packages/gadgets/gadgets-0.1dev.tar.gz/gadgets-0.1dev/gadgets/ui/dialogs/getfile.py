import curses, time, os, glob
from gadgets.ui.window import Window

class GetFile(Window):
    """ """

    def __init__(self, label):
        self._label = label
        self._width = 40
        self._height = 4

    def _browse(self):
        path = os.getcwd()
        i = 0
        while True:
            self._win.addstr(2, 1, path)
            x = self._win.getch()
            if x == 10:
                return path
            elif x == 127: #backspace
                if path.endswith('/'):
                    path = path[:-1]
                self._win.addstr(2, 1, ' ' * (len(path) + 1))
                path, junk = os.path.split(path)
                path += '/'
            elif x == 9: #tab
                path, junk = os.path.split(path)
                contents = glob.glob(os.path.join(path, '{0}*'.format(junk)))
                if len(contents) > 0:
                    path = contents[0]
            else:
                path += chr(x)
            if x == ord('/'):
                i = 0

    def __call__(self, screen):
        self._win = self._get_subwin(screen)
        self._add_title(self._win, self._label)
        return self._browse()


        