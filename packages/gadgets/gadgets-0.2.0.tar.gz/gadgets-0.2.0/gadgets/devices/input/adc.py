import time
import threading

from gadgets import Gadget
from gadgets.io import ADC

class ADCPollerFactory(object):

    def __init__(self, location, name, addresses, arguments):
        self._location = location
        self._name = name
        self._addresses = addresses
        self._pin = arguments['pin']
        self._delay = arguments.get('delay')

    def __call__(self):
        return ADCPoller(self._location, self._name, self._addresses, self._pin, delay=self._delay)

class ADCWorker(threading.Thread):
    """
    
    """

    def __init__(self, target, pin, threshold=None, sleep_time=5, delay=None):
        """
        threshold: if you only want to see updates if the adc goes above
                   or below a certain value, set a threshold from 0 to
                   4095
        """
        self._target = target
        self._threshold = threshold
        self._sleep_time = sleep_time
        self._delay = delay
        self._pin = pin
        self._io = None
        self._stop_event = threading.Event()
        self._state = False
        super(ADCWorker, self).__init__()

    @property
    def io(self):
        if self._io is None:
            self._io = ADC(self._pin['name'])
        return self._io

    def _get_value(self):
        values = [self.io.value for i in xrange(10)]
        return sum(values) / 10.0

    def run(self):
        value = self._get_value()
        self._write_to_target(value)
        while not self._stop_event.is_set():
            time.sleep(self._sleep_time)
            value = self._get_value()
            if self._threshold and value >= self._threshold and not self._state:
                self._state = True
                self._write_to_target(value)
            elif self._threshold and value <= self._threshold and self._state:
                self._state = False
                self._write_to_target(value)
            else:
                self._write_to_target(value)
                
        self.adc.close()

    def _write_to_target(self, value):
        if self._delay:
            time.sleep(self._delay)
        self._target(value)
        
    def close(self):
        self._stop_event.set()

        
class ADCPoller(Gadget):

    InputClass = ADCWorker
    _direction = 'input'

    def __init__(self, location, name, addresses, pin, delay=None):
        self._poller = None
        self._pin = pin
        self._delay = delay
        self._stop_event = threading.Event()
        super(ADCPoller, self).__init__(location, name, addresses)
    
    @property
    def events(self):
        return []

    def event_received(self, event, message):
        pass 

    def _update(self, value):
        self.sockets.send('update', {self._location: {self._direction: {self._name: {'value': value}}}})

    @property
    def poller(self):
        if self._poller is None:
            self._poller = self.InputClass(self._update, self._pin, delay=self._delay)
        return self._poller
                          
    def close(self):
        time.sleep(1)
        self.sockets.close()
        self.poller.close()
        
    def run(self):
        self.poller.start()
        super(ADCPoller, self).run()
                          
