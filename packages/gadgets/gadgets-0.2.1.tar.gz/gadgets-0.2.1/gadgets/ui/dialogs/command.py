import curses, time
from gadgets.ui.window import Window
from gadgets.ui.dialogs.prompt import Prompt

class Command(Window):
    """enter a command"""

    def __init__(self, parent, lock):
        self._parent = parent
        self._lock = lock

    def __call__(self, screen, data):
        with self._lock:
            p = Prompt('enter a command', str)
            command = p(screen)
            self._parent.sockets.send(command)
