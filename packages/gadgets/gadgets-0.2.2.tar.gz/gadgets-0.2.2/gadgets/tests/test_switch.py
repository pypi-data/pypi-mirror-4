import time, threading, random
from nose.tools import eq_
from gadgets import Gadgets, Addresses, Sockets, Broker
from gadgets.devices import Switch, switch_factory

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

class TestSwitch(object):

    def setup(self):
        port = random.randint(5000, 50000)
        self.addresses = Addresses(in_port=port, out_port=port + 1)
        self.sockets = Sockets(self.addresses, events=['update'])
        self.switch = Switch(
            'living room',
            'light',
            self.addresses,
            io_factory=get_fake_gpio,
        )
        self.gadgets = Gadgets([self.switch], self.addresses)
        
    def test_create(self):
        pass

    def test_on_and_off(self):
        t = threading.Thread(target=self.gadgets.start)
        t.start()
        time.sleep(1)
        self.sockets.send('turn on living room light')
        print self.sockets.recv()
        with open(path, 'r') as f:
            eq_(f.read(), 'on')
        self.sockets.send('turn off living room light')
        print self.sockets.recv()
        time.sleep(0.2)
        with open(path, 'r') as f:
            eq_(f.read(), 'off')
        self.sockets.send('shutdown')

    def test_timed_on_and_off(self):
        t = threading.Thread(target=self.gadgets.start)
        t.start()
        time.sleep(1)
        self.sockets.send('turn on living room light', {'units': 'seconds', 'value': 1})
        print self.sockets.recv()
        with open(path, 'r') as f:
            eq_(f.read(), 'on')
        print self.sockets.recv()
        with open(path, 'r') as f:
            eq_(f.read(), 'off')
        self.sockets.send('shutdown')

    def test_on_and_off_with_time_and_rcl(self):
        t = threading.Thread(target=self.gadgets.start)
        t.start()
        time.sleep(1)
        self.sockets.send('turn on living room light for 0.5 seconds')
        print self.sockets.recv()
        with open(path, 'r') as f:
            eq_(f.read(), 'on')
        print self.sockets.recv()
        with open(path, 'r') as f:
            eq_(f.read(), 'off')
        self.sockets.send('shutdown')

    def test_switch_factory(self):
        switch = switch_factory('basement', 'fan', {'pin': None}, self.addresses)
        assert isinstance(switch, Switch)
        

