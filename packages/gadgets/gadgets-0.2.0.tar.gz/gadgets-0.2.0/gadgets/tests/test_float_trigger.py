import time
from gadgets.devices.valve.triggers import FloatTrigger
from gadgets import Addresses

class FakePoller(object):

    def __init__(self, *args, **kw):
        pass

    def wait(self):
        time.sleep(0.4)

    def close(self):
        pass

class TestFloatTrigger(object):

    def setup(self):
        self.addresses = Addresses()
        FloatTrigger._poller_class = FakePoller
        self.trigger = FloatTrigger(
            'tank',
            'fill tank',
            'stop filling tank',
            {'units': 'liters', 'value': 3.3},
            self.addresses,
            self.off,
            {'mux':'x', 'export': 'y'},
            20.0,
        )
        self._off = False

    def off(self, message):
        self._off = True

    def test_create(self):
        pass

    def test_run(self):
        self.trigger.start()
        while not self._off:
            pass
        assert self._off
