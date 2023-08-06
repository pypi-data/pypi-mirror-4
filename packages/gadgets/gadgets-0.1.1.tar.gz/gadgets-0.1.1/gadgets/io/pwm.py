import os
from gadgets.io.io import IO

class PWMFactory(object):

    def __init__(self, pin, frequency=20000, mux_path='/sys/kernel/debug/omap_mux'):
        self._pin = pin
        self._frequency = frequency
        self._mux_path = mux_path

    def __call__(self):
        return PWM(self._pin, self._frequency, self._mux_path)
        

class PWM(IO):
    """
    Uses the pwm pins' sysfs interface.  You can use a pwm pin like this:

        >>> from gadgets.pins.beaglebone import pins
        >>> from gadgets.io import GPIO
        >>> pwm = PWM(pins['pwm'][8][13])

    Now you can turn it on and vary the duty percent:

        >>> pwm.on() #turns the pin on with a 100 duty_percent
        >>> pwm.duty_percent = 50
    
    NOTE:  The beaglebone pwm clock must be enabled before using this class.
    You can enable it by calling enable-pwm from the command line (requires
    gadgets and python-mmap to be installed)
    """
    
    _mux = 'echo {0} > {1}/{2}'
    _command = 'echo {0} > /sys/class/pwm/{1}/{2}'

    def __init__(self, pin, frequency=20000, mux_path='/sys/kernel/debug/omap_mux'):
        """
        mux:  the name that appears in the omap_mux directory
        directory: the directory for the pwm pin in /sys/class/pwm
        mode:  the mux mode of the pin that enables pwm
        frequency:  the pwm frequency in Hz
        mux_path:  defaults to /sys/kernel/debug/omap_mux
        """
        mux = pin['mux']
        directory = pin['directory']
        mode = pin['mode']
        self._current_value = None
        self._directory = directory
        os.system(self._mux.format(mode, mux_path, mux))
        self._write_value('run', '0')
        self._write_value('duty_percent', '0')
        self._write_value('period_freq', str(frequency))
        self._status = False

    @property
    def status(self):
        return self._status

    def on(self):
        """
        turns on the pwm and sets the duty cycle to 100
        """
        self.duty_percent = 100
        self._status = True

    def off(self):
        """
        turns off the pwm and sets the duty cycle to 0
        """
        self.duty_percent = 0
        self._status = False
        self._write_value('run', '0')

    def close(self):
        pass

    @property
    def duty_percent(self):
        return self._current_value

    @property
    def value(self):
        return self.duty_percent

    @duty_percent.setter
    def duty_percent(self, value):
        """
        duty_percent(value)
        value: an integer from 0 to 100

        Writes to the sysfs duty_percent interface.  If the pwm
        was turned off before this call, the pwm will be turned
        on.
        """
        if self._current_value != value:
            self._current_value = value
            self._write_value('run', '0')
            self._write_value('duty_percent', value)
            self._write_value('run', '1')

    def _write_value(self, path, value):
        command = self._command.format(value, self._directory, path)
        os.system(command)
