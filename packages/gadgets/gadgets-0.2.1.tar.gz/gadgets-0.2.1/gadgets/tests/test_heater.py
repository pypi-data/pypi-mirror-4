import time, threading, random
from nose.tools import eq_
from gadgets import Gadgets, Addresses, Sockets, Broker
from gadgets.devices import ElectricHeater, electric_heater_factory
from gadgets.devices.heater.pwm import PWM

port = random.randint(3000, 50000)


class FakeGPIO(object):

    def __init__(self):
        self.addresses = Addresses(in_port=port, out_port=port+1)
        self.sockets = Sockets(self.addresses)
        self.status = False
        self.closed = False

    def on(self):
        print "turning on"
        self.status = True

    def off(self):
        print "turning off"
        self.sockets.send('test pwm off')
        self.status = False

    def close(self):
        self.sockets.close()
        self.closed = True
        
def get_fake_gpio():
    return FakeGPIO()

def get_pwm(*args, **kw):
    return PWM(get_fake_gpio)

    
class TestHeater(object):

    def setup(self):
        self.addresses = Addresses(in_port=port, out_port=port+1)
        self.sockets = Sockets(self.addresses, events=['test pwm off'])
        
        self.heater = ElectricHeater(
            'living room',
            'heater',
            self.addresses,
            io_factory=get_pwm,
        )
        self.gadgets = Gadgets([self.heater], self.addresses)

    def test_create(self):
        pass

    def _read(self):
        with open(path, 'r') as f:
            return f.read()

    def test_on_and_off(self):
        """
        hard to test, try later when brain is smarter
        """
        pass
        # t = threading.Thread(target=self.gadgets.start)
        # t.start()
        # time.sleep(1)
        # self.sockets.send('heat living room', {'units': 'C', 'value': 88})
        # event, message = self.sockets.recv()
        # eq_(event, 'test pwm off')
        # eq_(self.heater.io.duty_percent, 100)
        # self.sockets.send('update temperature', {'living room': {'input': {'temperature': {'value': 87, 'units': 'C'}}}})
        # event, message = self.sockets.recv()
        # eq_(event, 'test pwm off')
        # eq_(self.heater.io.duty_percent, 25)
        # self.sockets.send('update temperature', {'living room': {'input': {'temperature': {'value': 88, 'units': 'C'}}}})
        # event, message = self.sockets.recv()
        # eq_(event, 'test pwm off')
        # eq_(self.heater.io.duty_percent, 0)
        # time.sleep(1)
        # self.sockets.send('shutdown')
        # time.sleep(0.2)
        # self.sockets.close()
