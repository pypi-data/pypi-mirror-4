import threading
import time
from gadgets import Sockets

class Trigger(threading.Thread):
    """
    A trigger is used to turn off a device in response to another event 
    (like a temperature reaching a certain value) or after waiting a certain
    amount of time.  When the Trigger is triggered it sends a 'completed' message
    to the rest of the system.
    """

    def __init__(self, location, on_event, off_event, message, addresses, target=None):
        self._location = location
        self._on_event = on_event
        self._off_event = off_event
        self._target = target
        self._message = message
        self._addresses = addresses
        self._sockets = None
        self._invalidated = False
        self._events = [off_event]
        super(Trigger, self).__init__()

    @property
    def sockets(self):
        if self._sockets is None:
            self._sockets = Sockets(self._addresses, events=self._events)
        return self._sockets

    def invalidate(self):
        pass

    def run(self):
        self.wait()
        if self._target is not None:
            self._target(self.status_message)
        event = 'completed {0}'.format(self._on_event)
        self.sockets.send(event)
        time.sleep(1)
        self.sockets.close()

    def wait(self):
        raise NotImplemented

    @property
    def status_message(self):
        """
        
        """
        return None
        
    def _get_units(self, message):
        pass

    
