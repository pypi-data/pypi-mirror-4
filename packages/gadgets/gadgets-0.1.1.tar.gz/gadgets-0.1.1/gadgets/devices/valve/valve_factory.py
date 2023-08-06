from gadgets.devices.valve.triggers import FloatTriggerFactory
from gadgets.devices.valve.valve import Valve
from gadgets.devices.valve.triggers import GravityTriggerFactory, GravityTrigger, TimerTriggerFactory, UserTriggerFactory
from gadgets.io import GPIOFactory
from gadgets.errors import GadgetsError

def get_float_trigger_factory(location,arguments, addresses):
    return FloatTriggerFactory(location, arguments['pin'], arguments['volume'], addresses)

def get_gravity_trigger_factory(location, arguments, addresses):
    try:
        kw = dict(
            location=location,
            addresses=addresses,
            source=arguments['source'],
            tank_radius=arguments['tank_radius'],
            valve_radius=arguments['valve_radius'],
            valve_coefficient=arguments['valve_coefficient']
        )
    except KeyError:
        raise GadgetsError(GravityTriggerFactory.__init__.__doc__)
    return GravityTriggerFactory(**kw)

def get_timer_trigger_factory(location, arguments, addresses):
    try:
        kw = dict(
            location=location,
            addresses=addresses,
            source=arguments['source'],
            drain_time=arguments['drain_time'],
        )
    except KeyError:
        raise GadgetsError(TimerTriggerFactory.__init__.__doc__)
    return TimerTriggerFactory(**kw)

def get_user_trigger_factory(location, arguments, addresses):
    try:
        kw = dict(
            location=location,
            addresses=addresses,
            source=arguments['source'],
        )
    except KeyError:
        raise GadgetsError(UserTriggerFactory.__init__.__doc__)
    return UserTriggerFactory(**kw)

class ValveFactory(object):

    gpio_factory = GPIOFactory
    
    def __call__(self, location, name, arguments, addresses):
        kw = dict(
            location=location,
            name=name,
            addresses=addresses,
            io_factory=self.gpio_factory(arguments['pin'], direction='out'),
        )
        trigger_type = arguments['trigger']['type']
        if trigger_type == 'float':
            trigger_factory = get_float_trigger_factory(location, arguments['trigger'], addresses)
        if trigger_type == 'gravity':
            trigger_factory = get_gravity_trigger_factory(location, arguments['trigger'], addresses)
        if trigger_type == 'timer':
            trigger_factory = get_timer_trigger_factory(location, arguments['trigger'], addresses)
        if trigger_type == 'user':
            trigger_factory = get_user_trigger_factory(location, arguments['trigger'], addresses)
        kw['trigger_factory'] = trigger_factory
        return Valve(**kw)
