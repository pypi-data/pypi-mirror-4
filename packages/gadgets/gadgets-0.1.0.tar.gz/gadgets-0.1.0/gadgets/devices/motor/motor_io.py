from gadgets.io.io import IO

class MotorIOFactory(object):
    """
    Creates a MotorIO object.
    """

    def __init__(self, gpio_a_factory, gpio_b_factory, pwm_factory):
        self._gpio_a_factory = gpio_a_factory
        self._gpio_b_factory = gpio_b_factory
        self._pwm_factory = pwm_factory

    def __call__(self):
        return MotorIO(
            self._gpio_a_factory(),
            self._gpio_b_factory(),
            self._pwm_factory()
        )

class MotorIO(IO):
    """
    Implements gadgets.io.io:IO
    
    This is a compound io object that consists of two gpio pins and
    one pwm.  The gpio pins are used to set the direction the motor
    spins and the PWM is used to set the speed at which it turns.
    This particular class was developed for the Pololu VNH5019 Motor
    Driver:
    
    http://www.pololu.com/catalog/product/1451

    It is possible that it could be used for any motor driver that
    uses two gpios and one pwm.
    """

    def __init__(self, gpio_a, gpio_b, pwm):
        self._gpio_a = gpio_a
        self._gpio_b = gpio_b
        self._pwm = pwm
        self._status = False

    @property
    def status(self):
        return self._status

    def on(self, value):
        value = value.get('value', 100)
        if value < 0:
            self._gpio_b.on()
            self._gpio_a.off()
            self._status = True
        elif value > 0:
            self._gpio_a.on()
            self._gpio_b.off()
            self._status = True
        else:
            self.off()
            
        self._pwm.duty_percent = abs(int(value))

    def off(self):
        self._pwm.off()
        self._gpio_a.on()
        self._gpio_b.on()
        self._status = False

    def close(self):
        self._pwm.close()
        self._gpio_a.close()
        self._gpio_b.close()
        
