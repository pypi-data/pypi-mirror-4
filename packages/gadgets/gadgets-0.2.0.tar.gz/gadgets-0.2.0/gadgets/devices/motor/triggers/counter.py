from gadgets.devices.trigger import Trigger
from gadgets.io.counter import Counter


class CounterTrigger(Trigger):

    def __init__(self, location, on_event, off_event, message, addresses, target=None, ticks=0, pin=None):
        self._ticks = ticks
        self._pin = pin
        super(CounterTrigger, self).__init__(location, on_event, off_event, message, addresses, target=target)

    def wait(self):
        counter = Counter(self._pin, self._ticks)
        counter.wait()

    