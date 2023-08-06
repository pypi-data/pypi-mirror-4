import time, threading, random
from nose.tools import eq_
from gadgets import Gadgets, Addresses, Sockets, Broker
from gadgets.devices.device import Device

path = '/private/tmp/switch'

class FakeGPIO(object):

    def __init__(self):
        self.status = False

    def on(self):
        with open(path, 'w') as f:
            f.write('on')
        self.status = True

    def off(self):
        with open(path, 'w') as f:
            f.write('off')
        self.status = False

    def close(self):
        pass

def get_fake_gpio():
    return FakeGPIO()

class TestDevice(object):

    def setup(self):
        port = random.randint(5000, 50000)
        self.addresses = Addresses(in_port=port, out_port=port + 1)
        self.sockets = Sockets(self.addresses, events=['update'])
        self.device = Device(
            'living room',
            'light',
            self.addresses,
            io_factory=get_fake_gpio,
        )
        self.gadgets = Gadgets([self.device], self.addresses)

    def teardown(self):
        self.sockets.send('shutdown')
        time.sleep(0.1)
        self.sockets.close()
        
    def test_create(self):
        pass

    def test_on_and_off(self):
        t = threading.Thread(target=self.gadgets.start)
        t.start()
        time.sleep(1)
        self.sockets.send('turn on living room light')
        time.sleep(0.3)
        with open(path, 'r') as f:
            eq_(f.read(), 'on')
        self.sockets.send('turn off living room light')
        time.sleep(0.2)
        with open(path, 'r') as f:
            eq_(f.read(), 'off')
            

    
        