import time
from nose.tools import eq_
from gadgets.devices.heater.triggers.temperature import TemperatureTrigger
from gadgets import Addresses, Sockets, Broker

class TestTemperatureTrigger(object):

    def setup(self):
        self.addresses = Addresses()
        comparitor = lambda x, y: x >= y
        self.trigger = TemperatureTrigger(
            'tank',
            'heat tank',
            'stop heating tank',
            {'units': 'C', 'value': 88},
            self.addresses,
            comparitor
        )

    def test_create(self):
        eq_(self.trigger._target_temperature, 88)

    def test_run(self):
        b = Broker(self.addresses)
        b.start()
        time.sleep(1)
        self.trigger.start()
        sockets = Sockets(self.addresses, ['completed heat tank'])
        sockets.send('update temperature', {'tank': {'temperature': {'value': 87, 'units': 'C'}}})
        time.sleep(0.1)
        sockets.send('update temperature', {'tank': {'temperature': {'value': 88, 'units': 'C'}}})
        time.sleep(0.1)
        event, message = sockets.recv()
        eq_(event, 'completed heat tank')
        sockets.send('shutdown')
        sockets.close()
