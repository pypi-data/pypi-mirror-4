import curses

class Window(object):

    def _get_ch(self, win):
        x = win.getch()
        if x > 0 and x < 256:
            x = chr(x)
        else:
            x = ''
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
        return win

    def _add_title(self, win, title):
        win.addstr(1, 1, '{0}'.format(title).center(self._width - 2), curses.A_BOLD | curses.A_STANDOUT | curses.color_pair(1))

