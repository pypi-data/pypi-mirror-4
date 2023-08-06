import curses, time
from gadgets.ui.window import Window
from gadgets.ui.dialogs.prompt import Prompt
from gadgets.ui.dialogs.alert import Alert

KEYCODE_ENTER = 10
KEYCODE_ESC = 27

class CommandMode(Window):
    """
    
    """

    def __init__(self, parent):
        self._parent = parent
        self._lock = parent._lock
        self._command_mode = self._get_command_mode()
        self.is_active = False

    def _get_command_mode(self):
        return {
            'sequence':'',
            'keys': [],
        }

    @property
    def keys(self):
        return self._command_mode['keys']

    def __call__(self, x):
        if x == KEYCODE_ESC:
            self._command_mode = self._get_command_mode()
            self.is_active = False
        elif len(self._command_mode['keys']) < 2:
            self._update_command_mode(x)
        elif len(self._command_mode['keys']) == 2 and x == KEYCODE_ENTER:
            self._do_command()
        elif len(self._command_mode['keys']) == 2 and x == ord('a'):
            argument = self._get_argument()
            if argument:
                self._do_command(argument)
        
    def _get_argument(self):
        self._lock.acquire()
        p = Prompt('value', str)
        argument = p(self._parent._screen)
        try:
            val, units = argument.split(' ')
        except ValueError:
            a = Alert('Error', 'enter a value and its units')
            a(self._parent._screen)
            return_value = None
        else:
            return_value = {'value': float(val), 'units': units}
        self._lock.release()
        return return_value

    def _do_command(self, argument={}):
        keys = self._command_mode['keys']
        d = self._parent._data['locations']
        f = open('command.txt', 'w')
        f.write(str(keys))
        f.write('\n')
        f.write(str(d))
        f.close()
        for i, name in enumerate(self._command_mode['keys']):
            if i == 0:
                d = d[name]['output']
            else:
                d = d[name]
        status = 'off' if d['value'] else 'on'
        command = self._parent._getter.commands[keys[0]][keys[1]][status]
        self._parent.sockets.send(str(command), argument)

    def _update_command_mode(self, x):
        self._command_mode['sequence'] += chr(x)
        sequence = self._command_mode['sequence']
        d = self._parent._data['locations']
        for i, name in enumerate(self._command_mode['keys']):
            if i == 0:
                d = d[name]['output']
            else:
                d = d[name]
        keys = [key for key in d.keys() if key.startswith(sequence)]
        if len(keys) == 1:
            self._command_mode['keys'].append(keys[0])
            self._command_mode['sequence'] = ''
