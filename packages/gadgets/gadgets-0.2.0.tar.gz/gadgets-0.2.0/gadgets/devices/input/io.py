import time
import threading
import datetime

from gadgets import Gadget
from gadgets.io import Poller

class InputPollerFactory(object):

    def __init__(self, location, name, addresses, arguments):
        self._location = location
        self._name = name
        self._addresses = addresses
        self._pin = arguments['pin']
        self._delay = arguments.get('delay')
        self._ticks = arguments.get('ticks')

    def __call__(self):
        return InputPoller(self._location, self._name, self._addresses, self._pin, delay=self._delay, ticks=self._ticks)

        
class InputPoller(Gadget):

    PollerClass = Poller
    _direction = 'input'

    def __init__(self, location, name, addresses, pin, delay=None, ticks=None):
        self._poller = None
        self._pin = pin
        self._delay = delay
        self._ticks = ticks
        self._ticks_count  = 0
        self._edge = 'both'
        if self._ticks is not None:
            self._edge = 'rising'
        self._stop_event = threading.Event()
        super(InputPoller, self).__init__(location, name, addresses)
    
    @property
    def events(self):
        return []

    @property
    def poller(self):
        if self._poller is None:
            self._poller = self.PollerClass(self._pin, timeout=1, edge='rising')
        return self._poller

    def close(self):
        self._stop_event.set()
        time.sleep(1)
        self.sockets.close()
        self.poller.close()

    def _check_ticks(self):
        if self._ticks_count == 0:
            self._start = datetime.datetime.now()
        self._ticks_count += 1
        if self._ticks_count < self._ticks:
            return True
        else:
            self._end = datetime.datetime.now()
            self._ticks_count = 0
            return False
        
    def run(self):
        while not self._stop_event.is_set():
            events, val = self.poller.wait()
            if events:
                if self._ticks and not self._check_ticks():
                    continue
                if self._delay:
                    time.sleep(self._delay)
                value, units = self._get_value(val)
                self.sockets.send('update', {self._location: {self._direction: {self._name: {'value': value, 'units': units}}}})

    def _get_value(self, val):
        if self._ticks:
            delta = self._end - self._start
            return self._ticks / delta.total_seconds(), 'ticks/second'
        ret = val == '1\n' and 'closed' or 'open'
        return ret, 'boolean'
