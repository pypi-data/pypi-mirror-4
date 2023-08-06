import threading, time
from gadgets import Addresses, GadgetsFactory, Sockets
from gadgets.devices import Switch, Valve
from gadgets.pins.beaglebone import pins
from nose.tools import eq_

class TestGadgetsFactory(object):

    def setup(self):
        self.addresses = Addresses()
        self.factory = GadgetsFactory(self.addresses)

    def test_create(self):
        pass

    def test_create_switch(self):
        args = {
            'locations': {
                'fish tank': {
                    'light': {
                        'type': 'switch',
                        'pin': pins['gpio'][8][12]
                    }
                }
            }
        }
        gadgets = self.factory(args)
        devices = gadgets._gadgets
        eq_(len(devices), 1)
        assert isinstance(devices[0], Switch)

    def test_create_float_valve(self):
        args = {
            'locations': {
                'fish tank': {
                    'valve': {
                        'type': 'valve',
                        'pin': pins['gpio'][8][12],
                        'trigger': {
                            'type':'float',
                            'pin': pins['gpio'][8][11],
                            'volume': {
                                'value': 5.5,
                                'units': 'gallons',
                            }
                        }
                    }
                }
            }
        }
        gadgets = self.factory(args)
        devices = gadgets._gadgets
        eq_(len(devices), 1)
        t = threading.Thread(target=gadgets.start)
        t.start()
        time.sleep(1)
        eq_(dict(gadgets.coordinator._external_events), {u'fish tank': {u'valve': {'on': u'fill fish tank', 'off': u'stop filling fish tank'}}})
        sockets = Sockets()
        sockets.send('shutdown')
        assert isinstance(devices[0], Valve)
        sockets.close()
