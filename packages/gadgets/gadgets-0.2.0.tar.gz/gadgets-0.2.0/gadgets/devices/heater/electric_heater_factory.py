from gadgets.devices.heater.pwm import PWMFactory
from gadgets.devices.heater.electric_heater import ElectricHeater

def electric_heater_factory(location, name, arguments, addresses, io_factory=None, on=None, off=None):
    if io_factory is None:
        io_factory = PWMFactory(arguments['pin'])
    return ElectricHeater(
        location,
        name,
        addresses,
        io_factory=io_factory,
        on=arguments.get('on'),
        off=arguments.get('off')
    )
    
