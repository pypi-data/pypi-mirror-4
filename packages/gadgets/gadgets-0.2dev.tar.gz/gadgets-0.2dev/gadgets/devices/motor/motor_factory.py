from gadgets.io import GPIOFactory
from gadgets.io import PWMFactory
from gadgets.devices.motor.triggers import MotorTriggerFactory
from gadgets.devices.motor.motor_io import MotorIOFactory
from gadgets.devices.motor.motor import Motor


def motor_factory(location, name, arguments, addresses):
    gpio_a = GPIOFactory(arguments['gpio_a'], direction='out')
    gpio_b = GPIOFactory(arguments['gpio_b'], direction='out')
    pwm = PWMFactory(arguments['pwm'], frequency=20000)
    io_factory = MotorIOFactory(gpio_a, gpio_b, pwm)
    units = {
        'all': Motor._units,
        'time': Motor._time_units,
        'percent': Motor._percent_units,
        'counter': Motor._counter_units
    }
    trigger_factory = MotorTriggerFactory(
        location,
        addresses,
        units,
        arguments['poller']
    )
        
    return Motor(
        location=location,
        name=name,
        addresses=addresses,
        io_factory=io_factory,
        trigger_factory=trigger_factory,
        on=arguments.get('on'),
        off=arguments.get('off'),
    )
    