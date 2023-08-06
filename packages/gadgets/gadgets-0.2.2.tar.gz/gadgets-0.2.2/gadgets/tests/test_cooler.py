import time, threading, random, multiprocessing
from nose.tools import eq_
from gadgets import Gadgets, Addresses, Sockets, Broker
from gadgets.devices import cooler_factory

path = '/private/tmp/cooler'
port = random.randint(3000, 50000)


class FakeGPIO(object):

    def __init__(self):
        print 'gpio init'
        self.addresses = Addresses(in_port=port, out_port=port+1)
        self.sockets = Sockets(self.addresses)
        self.status = False

    def _write(self, msg):
        print 'gpio write', msg
        with open(path, 'w') as f:
            f.write(msg)
        print 'gpio send'
        self.sockets.send('test update')

    def on(self):
        print 'gpio on'
        self._write('on')
        self.status = True

    def off(self):
        self._write('off')
        self.status = False

    def close(self):
        pass
        

def get_fake_gpio(*args, **kw):
    return FakeGPIO()

class TestCooler(object):

    def setup(self):
        self.addresses = Addresses(in_port=port, out_port=port + 1)
        self.sockets = Sockets(self.addresses, events=['test update'])
        self.cooler = cooler_factory('tank', 'cooler', {}, self.addresses, io_factory=get_fake_gpio)
        self.gadgets = Gadgets([self.cooler], self.addresses)

    def teardown(self):
        self.sockets.send('shutdown')
        time.sleep(0.2)
        self.sockets.close()

    def test_create(self):
        pass

    def _read(self):
        with open(path, 'r') as f:
            return f.read()

    def test_on_and_off(self):
        t = threading.Thread(target=self.gadgets.start)
        t.start()
        time.sleep(1)
        self.sockets.send('cool tank', {'units': 'C', 'value': 20})
        self.sockets.recv() #sync
        eq_(self._read(), 'on')
        time.sleep(0.2)
        self.sockets.send('update temperature', {'tank': {'temperature': {'value': 20, 'units': 'C'}}})
        self.sockets.recv() #sync
        eq_(self._read(), 'off')
        time.sleep(0.2)
        

        
