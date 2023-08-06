import time, threading, random
from nose.tools import eq_
from gadgets import Gadgets, Addresses, Sockets, Broker
from gadgets.devices import ElectricHeater, electric_heater_factory

path = '/private/tmp/electric_heater'
port = random.randint(3000, 50000)


class FakePWM(object):

    def __init__(self):
        self.addresses = Addresses(in_port=port, out_port=port+1)
        self.sockets = Sockets(self.addresses)
        self.status = False
        self._duty_percent = 100

    def write(self, msg):
        with open(path, 'w') as f:
            f.write(msg)
        self.sockets.send('test update')

    def on(self):
        print 'on'
        self.write('on {0}%'.format(self._duty_percent))
        self.status = True

    def off(self):
        self.write('off')
        self.status = False
        time.sleep(0.3)
        self.sockets.close()

    @property
    def duty_percent(self):
        pass

    @duty_percent.setter
    def duty_percent(self, value):
        self._duty_percent = value
        self.on()


def get_fake_pwm(*args, **kw):
    return FakePWM()

class TestHeater(object):

    def setup(self):
        
        self.addresses = Addresses(in_port=port, out_port=port+1)
        self.sockets = Sockets(self.addresses, events=['test update'])
        ElectricHeater._pwm_factory = get_fake_pwm
        self.heater = ElectricHeater(
            'living room',
            'heater',
            self.addresses,
            io_factory=get_fake_pwm,
        )
        self.gadgets = Gadgets([self.heater], self.addresses)

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
        self.sockets.send('heat living room', {'units': 'C', 'value': 88})
        self.sockets.recv()
        eq_(self._read(), 'on 100%')
        self.sockets.send('update temperature', {'living room': {'temperature': {'value': 87, 'units': 'C'}}})
        self.sockets.recv()
        eq_(self._read(), 'on 25%')
        self.sockets.send('update temperature', {'living room': {'temperature': {'value': 88, 'units': 'C'}}})
        self.sockets.recv()
        eq_(self._read(), 'on 0%')
        time.sleep(1)
