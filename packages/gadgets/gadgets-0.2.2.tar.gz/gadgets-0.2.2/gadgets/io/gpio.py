"""
GPIOFactory
GPIO
"""
import os
from gadgets.io.io import IO
from gadgets.errors import GadgetsError

class GPIOFactory(object):
    """
    Creates GPIO objects
    """
    def __init__(self, pin, direction='out', pullup=False):
        self._pin = pin
        self._direction = direction
        self._pullup = pullup

    def __call__(self):
        return GPIO(self._pin, self._direction, self._pullup)


class GPIO(IO):
    """
    Turning on a pin using the linux sysfs interface requires you to:
    
    * make sure the mux mode of the pin is set to gpio (which requires you to find out the name of the pin)
    * figure out the number to write to /sys/class/gpio/export in order to enable the gpio interface
    * write 'out' to /sys/class/gpio/gpio<gpio number>/direction
    * write 1 to /sys/class/gpio/gpio<gpio number>/value

    All this just to turn on a pin.  This GPIO class takes care of all
    that for you.  All you have to do is pick the port and pin (port 8,
    pin 3 in this case) and initialize a GPIO object like:

        >>> from gadgets.pins.beaglebone import pins
        >>> from gadgets.io import GPIO
        >>> gpio = GPIO(pins['gpio'][8][3])

    Now you can turn the pin on and off by:
    
        >>> gpio.on()
        >>> gpio.off()

    If you want to use a gpio pin as input, you initialize it like this:

        >>> from gadgets.pins.beaglebone import pins
        >>> gpio = GPIO(pins['gpio'][8][11], direction='in')

    You can then read the value of the pin by:

        >>> print gpio.value
        0
    """

    _path = '/sys/class/gpio'
    _export_path = '/sys/class/gpio/export'
    _gpio_path = '/sys/class/gpio/gpio{0}'
    _base_path = '/sys/class/gpio/gpio{0}/{1}'
    _mux_path = '/sys/kernel/debug/omap_mux'

    def __init__(self, pin, direction='in', pullup=False):
        """
        mux: the name of the pin, as appears in omap_mux
        export: the gpio number that is written to export
        direction: 'in' or 'out'
        pullup: if True, configure the gpio to use the
        internal pullup resistor 
        """
        self._mux = pin['mux']
        self._export = pin['export']
        self._direction = direction
        self._pullup = pullup
        self._file_cache = None
        self._initialize_pin()
        self._value = 0
        self._status = False
        

    @property
    def status(self):
        return self._status

    @property
    def _file(self):
        """
        Returns the sysfs file object that is the
        Linux interface to the gpio pin.
        """
        if self._file_cache is None:
            self._file_cache = self._open_file()
        return self._file_cache

    def on(self):
        """
        Sets the gpio pin high.
        """
        if self._direction == 'out':
            self._value = 1
            self._file.write('1')
            self._file.flush()
            self._status = True

    def off(self):
        """
        Sets the gpio pin low.
        """
        if self._direction == 'out':
            self._value = 0
            self._file.write('0')
            self._file.flush()
            self._status = False

    def value(self):
        """
        Get the value of the gpio pin.
        """
        if self._direction == 'out':
            value = self._value
        else:
            value = int(self._file.read())
            self._file.seek(0)
        return value

    def close(self):
        """
        Closes the file that GPIO uses to set/read the
        value of the pin.
        """
        self._file.close()

    def _open_file(self):
        """
        Opens the sysfs gpio interface file that sets
        the pin high or low.
        """
        value_path = self._base_path.format(self._export, 'value')
        if self._direction == 'out':
            buf = open(value_path, 'w')
            buf.write('0')
            buf.flush()
        else:
            buf = open(value_path, 'r')
        return buf

    def _write_to_file(self, path, value):
        """
        writes the given value to a sysfs
        path
        """
        with open(path, 'w') as buf:
            buf.write(value)

    @property
    def mux_path(self):
        """
        creates the full path to the sysfs mux interface
        for this pin.  
        """
        return os.path.join(self._mux_path, self._mux)

    @property
    def home_dir(self):
        """
        After a gpio pin is enabled the sysfs interface for the
        pin is created as a directory.  This property creates
        the path to that directory.
        """
        return self._gpio_path.format(self._export)

    def _get_mux(self):
        """
        Need to find out if the muxing of gpio pins is specific to
        beaglebone.
        """
        bits = [1, 1, 1, 0, self._pullup, self._direction=='in']
        val = 0
        for i, bit in enumerate(bits):
            val |= bit << i
        return hex(val)[2:]

    def _initialize_pin(self):
        """
        Sets the mux value to gpio then enables the
        gpio sysfs inteface by writing the export name
        to the export file.
        """
        if self._mux:
            self._write_to_file(self.mux_path, self._get_mux())
        if not os.path.exists(self.home_dir):
            self._write_to_file(self._export_path, str(self._export))
        if not os.path.exists(self.home_dir):
            raise GadgetsError(
                'failed gpio export: {0}'.format(
                    self.home_dir))
        path = self._base_path.format(self._export, 'direction')
        self._write_to_file(path, self._direction)
