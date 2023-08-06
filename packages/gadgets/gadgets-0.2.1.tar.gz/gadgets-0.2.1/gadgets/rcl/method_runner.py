import time, threading

from gadgets import Gadget
from gadgets.rcl.command_parser import parse_command

class Countdown(threading.Thread):
    
    def __init__(self, seconds, target):
        self._seconds = seconds
        self._target = target
        super(Countdown, self).__init__()

    def run(self):
        t = 0
        while t < self._seconds:
            time.sleep(1)
            t += 1
            self._target(self._seconds - t)
        self._target(0)

class MethodRunner(Gadget):
    """
    reads a list of RCL messages and uses the
    command parser to turn them into Gadget
    messages for the system.
    """

    
    _time_units = ['seconds', 'minutes', 'hours', 'second', 'minute', 'hour']

    def __init__(self, method, addresses):
        super(MethodRunner, self).__init__('method', 'runner', addresses)
        self._method = method
        self._countdown = 0
        self._step = 0

    @property
    def events(self):
        return ['completed']

    def run(self):
        run = True
        while run:
            if self._step == len(self._method):
                run = False
            else:
                step = self._method[self._step]
            event, message, method = self._read_step(step)
            self.sockets.send('update', {'method': {'step':self._step}})
            method(event, message)
            self._step += 1
        self.sockets.send('update', {'method': {'complete':True}})

    def _read_step(self, step):
        event, message = parse_command(step, {})
        if message.get('units') in self._time_units and event == 'wait':
            method = self._wait_for_time
        elif event.startswith('wait'):
            method = self._wait
        elif event.startswith('goto'):
            message = {'value': int(step.replace('goto ', '')) - 1}
            method = self._goto
        else:
            method = self.sockets.send
        return event, message, method

    def _goto(self, event, message):
        self._step = message.get('value', 0)

    def _wait(self, event, message):
        """
        waits a 'completed' event
        
        """
        if event.startswith('wait for user'):
            step = event.replace('wait for user ', '')
            self.sockets.send('WAITFORUSER', {'event': step['event']})
        elif event.startswith('wait for'):
            step = event.replace('wait for ', '')
        self._do_wait(step)

    def _do_wait(self, step):
        event, message = self.sockets.recv() #only 'completed' events should be recieved
        completed = event.replace('completed ', '')
        if completed != step:
            self._do_wait(step)

    def _wait_for_time(self, event, message):
        seconds = None
        if message['units'] == 'minutes' or message['units'] == 'minute':
            seconds = message['value'] * 60.0
        elif message['units'] == 'hours' or message['units'] == 'hour':
            seconds = message['value'] * 60.0 * 60.0
        elif message['units'] == 'seconds' or message['units'] == 'second':
            seconds = message['value']
        if seconds:
            self._sleep(seconds)

    @property
    def countdown(self):
        return self._countdown

    def set_countdown(self, seconds):
        self._countdown = seconds
        self._sockets.send('update', {'method': {'countdown': int(self._countdown)}})

    def _sleep(self, seconds):
        countdown = Countdown(seconds, self.set_countdown)
        countdown.start()
        time.sleep(seconds)

def run_method(method, broadcast, addresses):
    runner = MethodRunner(method, broadcast, addresses)
    runner.start()
    
