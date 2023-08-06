import time, random, threading
from nose.tools import eq_
from gadgets.devices.valve.triggers import GravityTriggerFactory
from gadgets import Addresses, Gadgets, Sockets

class TestGravityTrigger(object):

    def setup(self):
        self._off = False
        port = random.randint(5000, 50000)
        self.addresses = Addresses(in_port=port, out_port=port + 1)
        self.sockets = Sockets(self.addresses)
        self.gadgets = Gadgets([], self.addresses)
        
        t = threading.Thread(target=self.gadgets.start)
        t.start()
        time.sleep(1)
        self.gadgets.coordinator._state['locations']['barrel'] = {'input': {'volume': {'value': 3, 'units': 'liters'}}}
        self.gadgets.coordinator._state['locations']['bucket'] = {'input': {'volume': {'value': 1, 'units': 'liters'}}}
        factory = GravityTriggerFactory(
            'bucket',
            self.addresses,
            'barrel',
            20.0,
            1.0,
            1.0
        )
        self.trigger = factory(
            'fill bucket',
            'stop_filling_bucket',
            {'units':'liters', 'value': 2.0},
            self.off
            )
        

    def teardown(self):
        self.sockets.close()

    def off(self, message):
        self._off = True

    def _test_create(self):
        self.sockets.send('shutdown')
        time.sleep(0.2)

    def test_run(self):
        self.trigger.start()
        while not self._off:
            time.sleep(0.1)
        self.sockets.send('shutdown')
        eq_(self._off, True)
        #eq_(self.gadgets._state['locations'], {'barrel': {'volume': {'units': 'liters', 'value': 2}}, 'bucket': {'volume': {'units': 'liters', 'value': 2}}})
