import re, json, os, copy, time, curses
from os import system
import curses

class MethodDisplay(object):
    
    def __init__(self, stdscr, x, y, data):
        self._name = 'method'
        self.row = 3
        self._win = stdscr.subwin(30, 50, y, x)
        self._steps = 26
        self._data = data
        self._method = data.get('method', {}).get('method', [])
        self._step = data.get('method', {}).get('step', 0)
        if len(self._method) > self._steps:
            self._max_start = len(self._method) - self._steps
        else:
            self._max_start = 0

    def _get_steps(self):
        if self._step == 0 or self._step == 1:
            start = 0
        elif self._step > self._max_start:
            start = self._max_start
        else:
            start = self._step - 1
        for i, j in enumerate(xrange(start, len(self._method))):
            if i < self._steps:
                yield i, j, self._method[j]

    def draw(self):
        self._win.clear()
        self._win.addstr(1, 2, self._name, curses.color_pair(1))
        for i, j, step in self._get_steps():
            if j == self._step:
                COLOR = curses.A_BOLD | curses.A_STANDOUT | curses.color_pair(1)
            else:
                COLOR = curses.color_pair(1)
            self._win.addstr(i + 2, 2, step, COLOR)
        y, x = self._win.getmaxyx()
        self._win.border()


