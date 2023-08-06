from gadgets.devices.motor.triggers.counter import CounterTrigger

class MotorTriggerFactory(object):

    def __init__(self, location, addresses, units, pin):
        self._units = units
        self._pin = pin
        self._location = location
        self._addresses = addresses

    def __call__(self, on_event, off_event, message, target):
        print message
        units = message.get('units')
        if units in self._units['all']:
            if units in self._units['counter']:
                ticks = message.get('value', 0)
                return CounterTrigger(
                    self._location,
                    on_event,
                    off_event,
                    message,
                    self._addresses,
                    target,
                    abs(ticks),
                    self._pin
                )