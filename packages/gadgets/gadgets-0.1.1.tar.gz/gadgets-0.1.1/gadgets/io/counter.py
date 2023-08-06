from gadgets.io.poller import Poller
import threading

class Counter(object):
    """
    Blocks for a given number of rising edges on a gpio pin.
    """
    
    def __init__(self, pin, ticks):
        """
        pin: a gpio pin from gadgets.pins
        ticks: the number of rising edges for which to wait
        """
        self._ticks = int(ticks)
        self._poller = Poller(pin)

    def wait(self):
        """
        Blocks until for the number of rising
        edges specified by self._ticks
        """
        for i in xrange(self._ticks):
            self._poller.wait()
        self._poller.close()

