import time, zmq
import threading
from collections import defaultdict
from gadgets import Gadget

def thermometer_factory(location, name, arguments, addresses):
    arguments.pop('type')
    return Thermometer(arguments, addresses)

class ThermometerReader(threading.Thread):

    _read_path = '/sys/bus/w1/devices/{0}/w1_slave'

    def __init__(self, location, uid, sleep_time):
        self.location = location
        self._uid = uid
        self.value = 0.0
        self.stop = False
        self._sleep_time = sleep_time
        self.difference = 0.0
        super(ThermometerReader, self).__init__()
        

    def run(self):
        time.sleep(1)
        f = open(self._read_path.format(self._uid, 'r'))
        while not self.stop:
            s = f.read()
            i = s.find('t=')
            f.seek(0)
            try:
                value = float(s[i+2:]) / 1000.0
            except ValueError:
                pass
            else:
                if value >= 0: #sometimes the dallas thermometers seem to crap out and show a negative value
                    self.difference = abs(value - self.value)
                    self.value = value
            time.sleep(self._sleep_time)
        f.close()


class Thermometer(Gadget):

    _w1_path = '/sys/bus/w1/devices'

    def __init__(self, thermometers, addresses, sleep_time=5):
        self.stop = False
        self._thermometers = thermometers
        self._sleep_time = sleep_time
        super(Thermometer, self).__init__('null', 'thermometer', addresses)

    @property
    def events(self):
        return []

    def run(self):
        self._register()
        readers = self._get_readers()
        poller = zmq.Poller()
        poller.register(self.sockets.subscriber, zmq.POLLIN)
        while not self.stop:
            socks = dict(poller.poll(timeout=self._sleep_time))
            if self.sockets.subscriber in socks and socks[self.sockets.subscriber] == zmq.POLLIN:
                event, message = self.sockets.recv()
                if event == 'shutdown':
                    self.stop = True
                    break
            output = defaultdict(dict)
            for reader in readers:
                output[reader.location]['temperature'] = {'value': reader.value, 'units': 'C'}
            self.sockets.send('update', output)
            time.sleep(self._sleep_time)
        self._stop(readers)

    def _register(self):
        for location in self._thermometers:
            self.sockets.send(
                'register',
                {
                    'location': location,
                    'name': self._name,
                    'uid': '{0} {1}'.format(location, self._name)
                }
            )

    def _get_readers(self):
        readers = [ThermometerReader(location, uid, self._sleep_time) for location, uid in self._thermometers.iteritems()]
        for reader in readers:
            reader.start()
        return readers
            
    def _stop(self, readers):
        print 'stopping readers'
        for reader in readers:
            reader.stop = True
        reader.join()
        

