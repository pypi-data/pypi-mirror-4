from gadgets.devices.device import Device
from gadgets.errors import GadgetsError

class Valve(Device):
    """
    Valve is pretty close to Switch, but uses volume units
    for its triggers instead of time units.  On the surface
    Valve is pretty simple, but it has 4 different triggers 
    making it the most complicated Device.  All of these
    triggers were designed for my automatic brewery.  They are::

    FloatTrigger -   Waits until a float switch is activated.
    
    GravityTrigger - Uses the equation of water flowing through
                     an orfice to determine how much water has
                     flowed in a given amount of time.
    
    TimerTrigger -   The user initializes it with the maximum
                     amount of time required for the source tank
                     to completely drain.  This is useful for a
                     tank that is full of grains, making the equation
                     used by GravityTrigger inaccurate.
    
    UserTrigger -    Sends a message to whatever user-inteface is
                     being used.  The user-interface should display
                     a message asking the user to indicate when the
                     source tank is empty.  This is useful when the
                     valve is really a pump.  The user (via the user-
                     interface) confirms the tank is empty and the pump
                     shuts off immediately.  Most pumps don't like to
                     be run dry.
    
    The valve triggers have more documentation.

    Here is an example with four tanks (to illustrate all four triggers).
    The first tank uses a FloatTrigger and the one below it uses a GravityTrigger.

    >>> from gadgets import get_gadgets
    >>> from gadgets.pins.beaglebone import pins
    >>> brewery_def = {
    ...     'locations': {
    ...         'hot liquor tank': {
    ...             'valve': {
    ...                 'type': 'valve',
    ...                 'pin': pins['gpio'][8][11],
    ...                 'trigger': {
    ...                     'type': 'float',
    ...                     'pin': pins['gpio'][8][12],
    ...                     'volume': 26.5,
    ...                 }
    ...             }
    ...         },
    ...         'mash tun': {
    ...             'valve': {
    ...                 'type': 'valve',
    ...                 'pin': pins['gpio'][8][12],
    ...                 'trigger': {
    ...                     'type': 'gravity',
    ...                         'source': 'hot liquor tank',
    ...                         'tank_radius': 7.5,
    ...                         'valve_radius': 0.1875,
    ...                         'valve_coefficient': 0.43244,    
    ...                 }
    ...             }
    ...         },
    ...         'boiler': {
    ...             'valve': {
    ...                 'type': 'valve',
    ...                 'pin': pins['gpio'][8][12],
    ...                 'trigger': {
    ...                     'type': 'timer',
    ...                         'source': 'mash tun',
    ...                         'drain_time': 240 #seconds
    ...                 }
    ...             }
    ...         }
    ...         'carboy': {
    ...             'valve': {
    ...                 'type': 'valve',
    ...                 'pin': pins['gpio'][8][12],
    ...                 'trigger': {
    ...                     'type': 'user',
    ...                         'source': 'boiler',
    ...                 }
    ...             }
    ...         },
    ...     }
    ... }
    >>> from gadgets import Sockets
    >>> sock = Sockets()
    >>> sock.send('fill hot liquor tank')

    You don't have to tell the hot liquor tank a volume in the command,
    because it can only be filled to one known volume (26.5 liters in this
    case)

    Once the hot liquor tank is filled you can add any amount of water into the
    mash tun:

    >>> sock.send('fill mash tun to 6.5 liters')

    Knowing about the laws of physics, the GravityTrigger will turn off its valve
    after the appropriate amount of time.
    """

    _units = ['liters', 'gallons']
    _on_template = 'fill {location}'
    _off_template = 'stop filling {location}'

    def _get_trigger(self, message):
        try:
            trigger = self._trigger_factory(
                self._on_event,
                self._off_event,
                message,
                self.off
            )
        except GadgetsError, e:
            self.off()
        else:
            return trigger

    def _should_get_trigger(self, message):
        return True #we don't want tanks overflowing

    def _register(self):
        super(Valve, self)._register()
        self.sockets.send('update', {self._location: {'input': {'volume': {'value': 0.0, 'units': 'liters'}}}})

