import time
import threading

from gadgets import Gadget
from gadgets.io import Poller

class ButtonPollerFactory(object):

    def __init__(self, location, name, addresses, pin):
        self._location = location
        self._name = name
        self._addresses = addresses
        self._pin = pin

    def __call__(self):
        return ButtonPoller(self._location, self._name, self._addresses, self._pin)

        
class ButtonPoller(Gadget):

    PollerClass = Poller

    def __init__(self, location, name, addresses, pin):
        self._poller = None
        self._pin = pin
        self._stop_event = threading.Event()
        super(ButtonPoller, self).__init__(location, name, addresses)
    
    @property
    def events(self):
        return []

    @property
    def poller(self):
        if self._poller is None:
            self._poller = self.PollerClass(self._pin, timeout=1, edge='both')
        return self._poller

    def close(self):
        self._stop_event.set()
        time.sleep(1)
        self.sockets.close()
        self.poller.close()
        
    def run(self):
        while not self._stop_event.is_set():
            events, val = self.poller.wait()
            if events:
                self.sockets.send('update', {self._location: {self._name: {'value': self._get_value(val)}}})

    def _get_value(self, val):
        return val == '1\n' and 'Closed' or 'Open'

