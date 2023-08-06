

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

class MotorIO(object):
    """
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
        self.status = False

    def on(self, value):
        value = value.get('value', 100)
        if value < 0:
            self._gpio_b.on()
            self._gpio_a.off()
        elif value > 0:
            self._gpio_a.on()
            self._gpio_b.off()
        else:
            self.off()
        self._pwm.duty_percent = abs(int(value))

    def off(self):
        self._pwm.off()
        self._gpio_a.on()
        self._gpio_b.on()
