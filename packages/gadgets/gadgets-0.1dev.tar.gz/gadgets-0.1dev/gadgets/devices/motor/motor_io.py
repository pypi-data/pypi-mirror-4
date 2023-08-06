

class MotorIOFactory(object):

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
    A compound IO object for a motor driver
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
        print 'off'
        self._pwm.off()
        self._gpio_a.on()
        self._gpio_b.on()

        
        