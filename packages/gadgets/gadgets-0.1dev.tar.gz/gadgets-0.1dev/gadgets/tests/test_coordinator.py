import time, threading, random, uuid
from nose.tools import eq_, raises
from gadgets import Addresses, Sockets, Broker
from gadgets.coordinator import Coordinator
from gadgets.devices.device import Device
from gadgets.errors import GadgetsError

class GadgetTester(Device):

    def run(self):
        self._register()
        print('shut down')
        self.sockets.send('shutdown', {})

class TestCoordinator(object):

    def setup(self):
        port = random.randint(5000, 50000)
        self.addresses = Addresses(in_port=port, out_port=port + 1)
        self.coordinator = Coordinator(self.addresses)

    def test_create(self):
        pass

    def test_update(self):
        message = {
            'garage': {
                'opener': {
                    'value': True,
                }
            }
        }
        self.coordinator._update(message)
        eq_(dict(self.coordinator._state['locations']), {'garage': {'opener': {'units': None, 'value': True}}})

    def test_is_valid_update_message(self):
        message = {
            'location': 'garage',
            'name': 'opener',
            'value': True,
            'units': None,
            }
        assert self.coordinator._is_valid_update_message(message)

    def test_is_valid_registration_message(self):
        message = {
            'location': 'garage',
            'name': 'opener',
            'on': 'open garage',
            'off': 'close garage',
            'uid': 'garage opener'
            }
        assert self.coordinator._is_valid_registration_message(message)


    def test_handle_register(self):
        broker = Broker(self.addresses)
        broker.start()
        time.sleep(0.5)
        message = {
            'location': 'garage',
            'name': 'opener',
            'on': 'open garage',
            'off': 'close garage',
            'uid': 'garage opener'            
            }
        time.sleep(0.2)
        self.coordinator._handle_register(message)
        time.sleep(0.2)
        eq_(self.coordinator._ids, ['garage opener'])
        self.coordinator.sockets.send('shutdown')
        
    
