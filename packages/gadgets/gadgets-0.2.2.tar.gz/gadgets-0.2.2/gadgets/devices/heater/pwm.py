import time
import threading
from gadgets.io import GPIOFactory

class PWMFactory(object):

    def __init__(self, pin):
        self._pin = pin

    def __call__(self):
        pwm = PWM(GPIOFactory(self._pin, direction='out'))
        pwm.start()
        return pwm

class PWM(threading.Thread):
    """
    I started off with a beaglebone PWM pin  to control the amount
    of heating done by a electric heating coil.  I've been reading
    that electric stoves have a duty cycle of around 10  seconds,
    and that can be handled by gpio.
    """

    def __init__(self, gpio_factory, duty_cycle=10):
        self._gpio_factory = gpio_factory
        self._gpio = None
        self._duty_cycle = duty_cycle
        self._on_time = 0.0
        self._off_time = duty_cycle
        self._duty_percent = 0
        self._stop_event = threading.Event()
        self.status = False
        self._lock = threading.RLock()
        super(PWM, self).__init__()

    def run(self):
        while not self._stop_event.is_set():
            if self._on_time > 0:
                self.status = True
            if self._on_time > 0:
                if not self.gpio.status:
                    self.gpio.on()
                time.sleep(self._on_time)
            if self._off_time > 0:
                if self.gpio.status:
                    self.gpio.off()
                time.sleep(self._off_time)

    @property
    def gpio(self):
        if self._gpio is None:
            self._gpio = self._gpio_factory()
        return self._gpio

    def on(self):
        """
        turns on the pwm and sets the duty cycle to 100
        """
        self.duty_percent = 100

    def off(self):
        """
        turns off the pwm and sets the duty cycle to 0
        """
        self.duty_percent = 0

    def close(self):
        with self._lock:
            self._stop_event.set()
            self.gpio.close()

    @property
    def duty_percent(self):
        return self._duty_percent

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
        self._duty_percent = value
        with self._lock:
            self._on_time = self._duty_cycle * (float(value) / 100.0)
            self._off_time = self._duty_cycle - self._on_time
        
