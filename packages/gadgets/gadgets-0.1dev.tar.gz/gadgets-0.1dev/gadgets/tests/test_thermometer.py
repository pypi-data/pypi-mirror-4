import time, threading, random, uuid
from nose.tools import eq_
from gadgets import Addresses
from gadgets.sensors import Thermometer

class TestThermometer(object):

    def setup(self):
        port = random.randint(5000, 50000)
        self.addresses = Addresses(in_port=port, out_port=port + 1)
        thermometers = {
            'fish tank': 'x',
            'grow bed': 'y',
        }
        self.thermometer = Thermometer(thermometers, self.addresses)

    def test_create(self):
        pass

