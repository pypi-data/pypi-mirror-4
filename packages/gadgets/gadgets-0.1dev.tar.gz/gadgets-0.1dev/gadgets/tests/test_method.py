import time, threading, random
from nose.tools import eq_
from gadgets import Gadgets, Addresses, Sockets, Broker
from gadgets.devices import cooler_factory
from gadgets.rcl.method_runner import MethodRunner


class TestMethod(object):
    """
    9-11, 14-19, 61-62, 68, 76-77, 87, 92, 94, 96, 98, 102, 105-106, 109-111, 114-115
    """

    def setup(self):
        port = random.randint(5000, 50000)
        self.addresses = Addresses(in_port=port, out_port=port + 1)
        self.sockets = Sockets(self.addresses, events=['turn', 'heat', 'drain'])
        self.gadgets = Gadgets([], self.addresses)

    def teardown(self):
        self.sockets.send('shutdown')
        
    def test_create(self):
        pass


    def test_method(self):
        t = threading.Thread(target=self.gadgets.start)
        t.start()
        time.sleep(1)
        method = [
            'turn on bathroom light',
            'wait for 1 second',
            'turn off bathroom light'
            ]
        self.sockets.send('method', {'method':method})
        event, message = self.sockets.recv()
        eq_(event, 'turn on bathroom light')
        event, message = self.sockets.recv()
        eq_(event, 'turn off bathroom light')
        event, message = self.sockets.recv()
        eq_(event, 'turn off bathroom light')

    def test_another_method(self):
        t = threading.Thread(target=self.gadgets.start)
        t.start()
        time.sleep(0.5)
        method = [
            'heat fish tank to 25 C',
            'wait for heat fish tank',
            'drain fish tank'
            ]
        self.sockets.send('method', {'method':method})
        event, message = self.sockets.recv()
        eq_(event, 'heat fish tank')
        self.sockets.send('completed heat fish tank')
        event, message = self.sockets.recv()
        eq_(event, 'drain fish tank')

    def test_read_step(self):
        method = [
            'turn on bathroom light',
            'wait for 1 second',
            'turn off bathroom light'
            ]
        mr = MethodRunner(method, self.addresses)
        event, message, method = mr._read_step(method[0])
        eq_(event, 'turn on bathroom light')
        eq_(message, {})

    def test_next_step(self):
        method = [
            'turn on bathroom light',
            'wait for 1 second',
            'turn off bathroom light'
            ]
        mr = MethodRunner(method, self.addresses)
        event, message, method = mr._read_step(method[1])
        eq_(event, 'wait')
        eq_(message, {'units': 'second', 'value': 1.0})
        
        

