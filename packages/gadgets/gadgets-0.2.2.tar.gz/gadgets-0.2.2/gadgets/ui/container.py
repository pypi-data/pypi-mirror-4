import re, json, os, copy, time, curses
from os import system
import curses


class Container(object):

    _sort = lambda a, b : a if a == 'temperature' else b
    
    def __init__(self, stdscr, row, col, data, name, command_mode):
        self._name = name
        self.row = row
        self._col = col
        self._win = stdscr
        self._data = data
        self._command_mode = command_mode
        self._on_str = lambda x: x and 'On' or 'Off'

    def _get_state(self):
        state = dict(devices={})
        for direction in self._data:
            for name, value in self._data[direction].iteritems():
                state['devices'][name] = value
        return state

    def draw(self):
        color = self._get_color(self._name, 0)
        self._win.addstr(self.row, self._col, self._name, color)
        self.row += 1
        state = self._get_state()
        keys = state['devices'].keys()
        if 'temperature' in keys:
            value = state['devices'].pop('temperature')
            self._write_data('temperature', value)
        if 'volume' in keys:
            value = state['devices'].pop('volume')
            self._write_data('volume', value)
        for key, value in state['devices'].iteritems():
            self._write_on_off(key, value)
        return self.row

    def _get_color(self, name, i):
        color = 0
        if self._command_mode.is_active:
            keys = self._command_mode.keys
            if len(keys) > i and keys[i] == name and keys[0] == self._name:
                color = curses.A_BOLD
        return color

    def _write_data(self, label, val):
        val = val['value']
        val = '{0}{1:>{2}.2f}'.format(label, val, 20 - len(label))
        self._win.addstr(self.row, self._col + 4, val)
        self.row += 1

    def _write_on_off(self, label, val):
        #val, target = val
        if val is None:
            return
        if val['value'] is not True and val['value'] is not False:
            s = val['value']
        else:
            s = self._on_str(val['value'])
        target = val.get('target')
        if isinstance(target, float):
            s = '{0} ({1:.2f})'.format(s, target)
        color = self._get_color(label, 1)
        self._win.addstr(self.row, self._col + 4, label, color)
        if val['value'] is True:
            self._win.addstr(self.row, self._col + 24 - len(s), s, curses.A_BOLD | curses.color_pair(2))
        else:
            self._win.addstr(self.row, self._col + 24 - len(s), s, curses.A_BOLD | curses.color_pair(3))
        self.row += 1
        
