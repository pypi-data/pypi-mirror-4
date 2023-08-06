from gadgets.io import GPIOFactory
from gadgets.devices.cooler.cooler import Cooler
from gadgets.devices.heater.triggers.temperature import TemperatureTriggerFactory

def cooler_factory(location, name, arguments, addresses, io_factory=None, trigger_factory=None):
    comparitor = lambda x, y: x <= y
    if io_factory is None:
        io_factory = GPIOFactory(arguments['pin'], direction='out')
    if trigger_factory is None:
        trigger_factory=TemperatureTriggerFactory(location, addresses, comparitor=comparitor)
    kw = dict(
        location=location,
        name=name,
        addresses=addresses,
        io_factory=io_factory,
        trigger_factory=trigger_factory
    )
    if 'on' in arguments:
        kw['on'] = arguments['on']
    if 'off' in arguments:
        kw['off'] = arguments['off']
    return Cooler(**kw)
        
