import select, os, time
from gadgets.errors import GadgetsError

class RisingOrFalling(object):

    def __eq__(self, other):
        return other == '0\n' or other == '1\n'


class Poller(object):
    """
    Poller performs a poll on a gpio line.  Just call wait and it will block
    until the gpio pin goes high.

        >>> from gadgets.pins.beaglebone import pins
        >>> from gadgets.io import GPIO
        >>> poller = Poller(pins['gpio'][8][3])
        >>> poller.wait()

    This will then block until the pin goes high.
    """
    
    _export_path = '/sys/class/gpio/export'
    _mux_path = '/sys/kernel/debug/omap_mux/{0}'
    _base_path = '/sys/class/gpio/gpio{0}/{1}'
    _gpio_path = '/sys/class/gpio/gpio{0}'

    def __init__(self, pin, timeout=None, edge='rising'):
        if edge == 'rising':
            self._value = '1\n'
        elif edge == 'falling':
            self._value = '0\n'
        else:
            self._value = RisingOrFalling()
        self._edge = edge
        self._setup_pin(pin)
        if timeout:
            self._timeout = int(timeout * 1000.0)
        else:
            self._timeout = -1

    def _setup_pin(self, pin):
        mux = pin['mux']
        export = pin['export']
        self._path = self._base_path.format(export, 'value')
        self._write_to_path('27', self._mux_path.format(mux))
        self._write_to_path(str(export), self._export_path)
        self._write_to_path('in', self._base_path.format(export, 'direction'))
        self._write_to_path(self._edge, self._base_path.format(export, 'edge'))
        self._fd = None
        self._poller = None
        path = self._gpio_path.format(export)
        if not os.path.exists(path):
            raise GadgetsError('failed gpio export: {0}, mux: {1}, export: {2}'.format(path, mux, export))

    @property
    def fd(self):
        if self._fd is None:
            self._fd = os.open(self._path, os.O_RDONLY | os.O_NONBLOCK)
        return self._fd

    @property
    def poller(self):
        if self._poller is None:
            self._poller = self._get_poller()
        return self._poller

    def close(self):
        """
        Closes the file descriptor that Poller uses for the
        Linux poll.
        """
        os.close(self.fd)

    def wait(self):
        """
        Blocks until the pin goes high
        """
        while True:
            events = self.poller.poll(self._timeout)
            os.lseek(self.fd, 0, 0)
            val = os.read(self.fd, 2)
            if val == self._value:
                return events, val
        
    def _get_poller(self):
        os.read(self.fd, 2)
        poller = select.poll()
        poller.register(self.fd, select.POLLPRI)
        return poller

    def _write_to_path(self, value, path):
        try:
            f = open(path, 'w')
            f.write(str(value))
            f.close()
        except IOError:
            pass
