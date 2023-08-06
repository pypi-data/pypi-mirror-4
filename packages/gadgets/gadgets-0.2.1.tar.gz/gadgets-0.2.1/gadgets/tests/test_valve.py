import time, random, threading, os, uuid
from nose.tools import eq_
from gadgets.devices.valve.valve_factory import ValveFactory
from gadgets import Addresses, Gadgets, Sockets

lock = threading.Lock()
path = '/private/tmp/switch'

class FakeGPIO(object):

    def __init__(self):
        lock.acquire()
        self.status = False
        self.write('off')

    def write(self, status):
        with open(path, 'w') as f:
            f.write(status)

    def on(self):
        self.write('on')
        self.status = True

    def off(self):
        self.write('off')
        self.status = False
        if lock.locked():
            lock.release()

    def close(self):
        pass


class FakeGPIOFactory(object):

    def __init__(self, *args, **kw):
        pass
    def __call__(self, *args, **kw):
        return FakeGPIO()

class TestValve(object):

    def setup(self):
        self._off = False
        port = random.randint(5000, 50000)
        self.addresses = Addresses(in_port=port, out_port=port + 1)
        self.uid = str(uuid.uuid1())
        self.sockets = Sockets(self.addresses, events=[self.uid])

    def _get_gadgets(self, trigger_args):
        ValveFactory.gpio_factory = FakeGPIOFactory
        args = {
            'pin': None,
            'trigger': trigger_args
        }
        
        factory = ValveFactory()
        self.valve = factory(
            'bucket',
            'valve',
            args,
            self.addresses
        )
        self.gadgets = Gadgets([self.valve], self.addresses)

    def teardown(self):
        self.sockets.close()

    def is_on(self):
        with open(path, 'r') as f:
            status = f.read()
            return status == 'on'

    def test_create(self):
        trigger_args = {
            'type': 'gravity',
            'source': 'barrel',
            'tank_radius': 20.0,
            'valve_radius': 1.0,
            'valve_coefficient': 1.0
        }
        self._get_gadgets(trigger_args)
        
    def test_gravity(self):
        trigger_args = {
            'type': 'gravity',
            'source': 'barrel',
            'tank_radius': 20.0,
            'valve_radius': 1.0,
            'valve_coefficient': 1.0
        }
        self._get_gadgets(trigger_args)
        t = threading.Thread(target=self.gadgets.start)
        t.start()
        time.sleep(1)
        self.sockets.send(
            'update',
            {
                'bucket': {'input': {'volume': {'value': 1, 'units': 'liters'}}},
                'barrel': {'input': {'volume': {'value': 3, 'units': 'liters'}}}
            }
        )
        time.sleep(0.3)
        eq_(self.gadgets.coordinator._state['locations']['bucket']['output']['valve']['value'], False)
        eq_(self.gadgets.coordinator._state['locations']['barrel']['input']['volume']['value'], 3)
        eq_(self.gadgets.coordinator._state['locations']['bucket']['input']['volume']['value'], 1)
        self.sockets.send('fill bucket', {'units': 'liters', 'value': 2})
        time.sleep(0.2)
        lock.acquire()
        lock.release()
        time.sleep(1)
        eq_(self.gadgets.coordinator._state['locations']['bucket']['output']['valve']['value'], False)
        self.sockets.send('shutdown')
        eq_(self.gadgets.coordinator._state['locations']['barrel']['input']['volume']['value'], 2)
        eq_(self.gadgets.coordinator._state['locations']['bucket']['input']['volume']['value'], 2)

    def test_gravity_when_target_already_reached(self):
        trigger_args = {
            'type': 'gravity',
            'source': 'barrel',
            'tank_radius': 20.0,
            'valve_radius': 1.0,
            'valve_coefficient': 1.0
        }
        self._get_gadgets(trigger_args)
        
        t = threading.Thread(target=self.gadgets.start)
        t.start()
        time.sleep(1)
        self.sockets.send(
            'update',
            {
                'bucket': {'input': {'volume': {'value': 1, 'units': 'liters'}}},
                'barrel': {'input': {'volume': {'value': 3, 'units': 'liters'}}}
            }
        )
        time.sleep(0.3)
        eq_(self.gadgets.coordinator._state['locations']['bucket']['output']['valve']['value'], False)
        eq_(self.gadgets.coordinator._state['locations']['barrel']['input']['volume']['value'], 3)
        eq_(self.gadgets.coordinator._state['locations']['bucket']['input']['volume']['value'], 1)
        self.sockets.send('fill bucket', {'units': 'liters', 'value': 1})
        eq_(self.gadgets.coordinator._state['locations']['bucket']['output']['valve']['value'], False)
        time.sleep(0.3)
        self.sockets.send('shutdown')
        eq_(self.gadgets.coordinator._state['locations']['barrel']['input']['volume']['value'], 3)
        eq_(self.gadgets.coordinator._state['locations']['bucket']['input']['volume']['value'], 1)

    def test_timer_trigger_valve(self):
        f = open(path, 'w')
        f.write('')
        f.close()
        trigger_args = {
            'type': 'timer',
            'source': 'barrel',
            'drain_time': 0.5 / 60.0
        }
        self._get_gadgets(trigger_args)

        t = threading.Thread(target=self.gadgets.start)
        t.start()
        time.sleep(1)
        self.sockets.send(
            'update',
            {
                'bucket': {'input': {'volume': {'value': 1, 'units': 'liters'}}},
                'barrel': {'input': {'volume': {'value': 3, 'units': 'liters'}}}
            }
        )
        time.sleep(1)
        eq_(self.gadgets.coordinator._state['locations']['bucket']['output']['valve']['value'], False)
        eq_(self.gadgets.coordinator._state['locations']['barrel']['input']['volume']['value'], 3)
        eq_(self.gadgets.coordinator._state['locations']['bucket']['input']['volume']['value'], 1)
        self.sockets.send('fill bucket', {'units': 'liters', 'value': 1})
        time.sleep(0.2)
        lock.acquire()
        lock.release()
        time.sleep(0.3)
        self.sockets.send('status', {'id': self.uid, 'location':'barrel'})
        event, status = self.sockets.recv()
        eq_(status['locations']['barrel']['input']['volume']['value'], 0)
        eq_(status['locations']['bucket']['input']['volume']['value'], 4)
        self.sockets.send('shutdown')

    def test_user_trigger_valve(self):
        f = open(path, 'w')
        f.write('')
        f.close()
        trigger_args = {
            'type': 'user',
            'source': 'barrel',
            'drain_time': 0.5 / 60.0
        }
        self._get_gadgets(trigger_args)
        t = threading.Thread(target=self.gadgets.start)
        t.start()
        time.sleep(1)
        self.sockets.send(
            'update',
            {
                'bucket': {'input': {'volume': {'value': 1, 'units': 'liters'}}},
                'barrel': {'input': {'volume': {'value': 3, 'units': 'liters'}}}
            }
        )
        time.sleep(1)
        eq_(self.gadgets.coordinator._state['locations']['bucket']['output']['valve']['value'], False)
        eq_(self.gadgets.coordinator._state['locations']['barrel']['input']['volume']['value'], 3)
        eq_(self.gadgets.coordinator._state['locations']['bucket']['input']['volume']['value'], 1)
        self.sockets.send('fill bucket', {'units': 'liters', 'value': 1})
        time.sleep(1)
        self.sockets.send('confirmed fill bucket')
        time.sleep(0.2)
        self.sockets.send('status', {'id': self.uid, 'location':'barrel'})
        event, status = self.sockets.recv()
        eq_(status['locations']['barrel']['input']['volume']['value'], 0)
        eq_(status['locations']['bucket']['input']['volume']['value'], 4)
        self.sockets.send('shutdown')