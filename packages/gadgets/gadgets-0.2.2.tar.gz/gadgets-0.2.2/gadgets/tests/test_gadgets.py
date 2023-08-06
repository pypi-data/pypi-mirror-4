import time, threading, random, uuid
from nose.tools import eq_, raises
from gadgets import Gadgets, Addresses, Sockets, Broker
from gadgets.devices.device import Device
from gadgets.errors import GadgetsError

class GadgetTester(Device):

    def run(self):
        self._register()
        print('shut down')
        self.sockets.send('shutdown', {})

class TestGadgets(object):

    def setup(self):
        port = random.randint(5000, 50000)
        self.addresses = Addresses(in_port=port, out_port=port + 1)
        self.gadgets = Gadgets([], self.addresses)

    def test_create(self):
        pass

    def test_remote_register(self):
        t = threading.Thread(target=self.gadgets.start)
        t.start()
        time.sleep(1)
        gt = GadgetTester('garage', 'opener', self.addresses)
        gt.start()
        time.sleep(0.3)
        eq_(self.gadgets.coordinator._ids, ['garage opener'])

    def test_error(self):
        sockets = Sockets(self.addresses)
        t = threading.Thread(target=self.gadgets.start)
        t.start()
        time.sleep(1)
        try:
            raise GadgetsError('this is my error', sockets)
        except GadgetsError:
            pass
        eq_(self.gadgets.coordinator._state['errors'], ['this is my error'])
        sockets.send('shutdown')
        sockets.close()

    def test_status(self):
        t = threading.Thread(target=self.gadgets.start)
        t.start()
        time.sleep(1)
        self.gadgets.coordinator._state['locations']['back yard'] = {'sprinklers': {'value': True}}
        uid = 'back yard sprinklers'
        sockets = Sockets(self.addresses, events=[uid])
        time.sleep(0.2)
        msg = {'id': uid}
        sockets.send('status', msg)
        event, message = sockets.recv()
        sockets.send('shutdown')
        eq_(event, uid + ' status')
        eq_(message, {u'errors': [], u'locations': {u'back yard': {u'sprinklers': {u'value': True}}}, u'method': {}})

