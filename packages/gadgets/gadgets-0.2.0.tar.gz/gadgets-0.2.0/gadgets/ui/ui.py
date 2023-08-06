import sys
import curses
import threading
import os
import time
import zmq
import imp
import collections
import json
import argparse

from gadgets.ui.data_getter import DataGetter
from gadgets.ui.database import SQL, Mongo
from gadgets.ui.container import Container
from gadgets.ui.dialogs.prompt import Prompt
from gadgets.ui.dialogs.command import Command
from gadgets.ui.dialogs.command_mode import CommandMode
from gadgets.ui.dialogs.alert import Alert
from gadgets.ui.dialogs.notes import Notes
from gadgets.ui.dialogs.method import Method
from gadgets.ui.dialogs.help import Help
from gadgets.ui.window import Window
from gadgets.ui.method_display import MethodDisplay
from gadgets import Addresses, Sockets


class UI(Window):

    Dialog = collections.namedtuple('Dialog', 'callable keyword_factory')

    def __init__(self, addresses,  db_host=None, db_port=27017, locations=[], mini=False):
        self._mini = mini
        self._addresses = addresses
        self._screen = None
        self._data = dict()
        self._getter = DataGetter(
            self.set_data,
            self._addresses
        )
        self.sockets = Sockets(addresses)
        self._lock = threading.RLock()
        self._title_bar_string = 'help: h  quit: q'
        self._location_names = locations
        self._stop = False
        self._command_mode = CommandMode(self)
        self._confirm = None
        self._commands = None
        if db_host is None:
            self._db = SQL()
        else:
            self._db = Mongo(db_host, db_port)
        self._dialogs = {
            ord('c'): self.Dialog(self._enter_command_mode, None),
            ord('C'): self.Dialog(Command(self, self._lock), None),
            ord('n'): self.Dialog(Notes(self.sockets, self._lock, self._db), self._get_method_id),
            ord('m'): self.Dialog(Method(self.sockets, self._lock, self._db), None),
            ord('f'): self.Dialog(self._user_confirmed, None),
        }
        self._dialogs[ord('h')] = self.Dialog(Help(self._lock, self._dialogs, self._db), None)

    def add_dialog(self, key, DialogClass, dialog_kw):
        self._dialogs[ord(key)] = self.Dialog(DialogClass(self.sockets, self._lock, self._db), dialog_kw)

    def _get_method_id(self):
        return {'method_id': self._data.get('method', {}).get('_id')}

    def set_data(self, data):
        self._data = data
        self._draw()
        return True

    def _do_dialog(self, x):
        dialog = self._dialogs.get(x)
        if dialog is not None:
            kw_factory = dialog.keyword_factory
            if kw_factory is not None:
                kw = kw_factory()
            else:
                kw = {}
            dialog.callable(self._screen, self._data, **kw)

    def __call__(self, screen):
        self._lock.acquire()
        self._screen = screen
        if self._mini:
            self._height = 22
        else:
            self._height = 30
        if self._mini:
            self._width = 30
        else:
            self._width = 80
        self._getter.start()
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_YELLOW, -1)
        curses.init_pair(2, curses.COLOR_GREEN, -1)
        curses.init_pair(3, curses.COLOR_RED, -1)
        while 'locations' not in self._data:
            time.sleep(0.1)
        if self._location_names == []:
            self._location_names = self._getter.locations
        self._row, self._col = self._get_center(screen)
        self._lock.release()
        self._draw()
        x = 'go'
        
        while x != ord('q'):
            x = self._screen.getch()
            if self._command_mode.is_active:
                self._do_command_mode(x)
            else:
                self._do_dialog(x)
            self._draw()
        self._stop = True
        self._getter.stop()

    def _enter_command_mode(self, screen, data):
        """enter command mode"""
        self._command_mode.is_active = True

    def _do_command_mode(self, x):
        self._command_mode(x)

    def _user_confirmed(self, screen, data):
        if self._confirm is not None:
            self.sockets.send('completed {0}'.format(self._confirm))
            self._confirm = None

    def _draw(self):
        if self._stop:
            return
        self._lock.acquire()
        self._screen.clear()
        self._draw_top_bar()
        self._locations = self._draw_locations()
        if not self._mini:
            self._draw_method()
        self._draw_bottom_bar()
        self._screen.refresh()
        curses.curs_set(0)
        self._lock.release()

    def _draw_method(self):
        self._method_display = MethodDisplay(self._screen, self._col + 30, self._row + 2, self._data)
        self._method_display.draw()

    def _draw_locations(self):
        locations = []
        row = 1
        col = self._col
        win = self._screen.subwin(self._height, self._width, self._row + 2, self._col)
        win.border()
        for name in self._location_names:
            c =  Container(
                win,
                row,
                2,
                self._data['locations'][name],
                name,
                self._command_mode
            )
            row = c.draw()
            locations.append(c)
        return locations

    def _draw_top_bar(self):
        msg ='{0:<{1}}'.format(self._title_bar_string, self._width)
        color = curses.A_BOLD | curses.A_STANDOUT | curses.color_pair(1)
        self._screen.addstr(self._row + 1, self._col, msg, color)
        if self._command_mode.is_active:
            msg = 'COMMAND MODE'
            self._screen.addstr(self._row + 1, self._col + ((self._width / 2 - (len(msg)/2))), msg, color)

    def _draw_bottom_bar(self):
        if len(self._data.get('errors', [])) > 0:
            msg = str(self._data['errors'])
        elif self._data.get('method', {}).get('countdown') is not None:
            msg = self._data['method']['countdown']
        elif self._data.get('user_confirm'):
            self._confirm = self._data['user_confirm']
            msg = "press 'f' when {0}".format(self._confirm)
        else:
            msg = ''
        self._screen.addstr(self._row + self._height + 2, self._col, '{0}'.format(msg).center(self._width), curses.A_BOLD | curses.A_STANDOUT | curses.color_pair(1))

def get_args():
    parser = argparse.ArgumentParser(description='Start up the gadgets ui')
    parser.add_argument('--host', type=str, default='localhost')
    parser.add_argument('--port', type=int, default=5000)
    parser.add_argument('--mini', action='store_true')
    return parser.parse_args()

def main():
    args = get_args()
    config_path = os.path.join(os.path.expanduser('~'), '.gadgets', '{0}.py'.format(args.host))
    if os.path.exists(config_path):
       config = imp.load_source(args.host, config_path)
       locations = config.locations
    else:
        locations = []
    addresses = Addresses(host=args.host)
    ui = UI(addresses, locations=locations, mini=args.mini)
    curses.wrapper(ui)
    ui._getter.stop()
    os.system('stty sane')

if __name__ == '__main__':
    main()

