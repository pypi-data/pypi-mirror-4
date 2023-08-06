import time, threading, random, uuid, tempfile, os
from nose.tools import eq_
from gadgets import Addresses, get_gadgets, Sockets
from gadgets.sensors import Thermometer

class TestThermometer(object):

    def setup(self):
        port = random.randint(5000, 50000)
        self.addresses = Addresses(in_port=port, out_port=port + 1)
        self.sockets = None
        self.thermometer = Thermometer('livingroom', 'thermometer', self.addresses, uid='x')

    def teardown(self):
        if self.sockets is not None:
            self.sockets.send('shutdown')
            time.sleep(0.2)
            self.sockets.close()

    def test_create(self):
        pass

    def test_run(self):
        tmp = tempfile.mkdtemp()
        os.mkdir(os.path.join(tmp, 'x'))
        path = os.path.join(tmp, 'x', 'w1_slave')
        f = open(path, 'w')
        f.write('t=21500')
        f.close()
        Thermometer._read_path = '{0}/x/w1_slave'.format(tmp)
        arguments = {
            'locations': {
                'living room': {
                    'thermometer': {
                        'type': 'thermometer',
                        'uid': 'x',
                        'timeout': 0.5,
                    }
                }
            }
        }
        gadgets = get_gadgets(arguments, self.addresses)
        t = threading.Thread(target=gadgets.start)
        t.start()
        time.sleep(2)
        self.sockets = Sockets(self.addresses, events=['test thermometer'])
        self.sockets.send('status', {'id': 'test thermometer'})
        event, message = self.sockets.recv()
        eq_(event, 'test thermometer')
        expected = {u'errors': [], u'locations': {u'thermometer': {u'temperature': {u'units': u'C', u'value': 21.5}}}, u'method': {}}
        eq_(message, expected)

        
        
        
