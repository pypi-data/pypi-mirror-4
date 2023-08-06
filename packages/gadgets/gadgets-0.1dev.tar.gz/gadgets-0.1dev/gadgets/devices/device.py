from gadgets import Gadget
from gadgets.rcl import parse_command

class Device(Gadget):
    """
    Device is what should be subclassed if you want a Gadget that
    controls a physical device.

    Each device has an io attribute.  The object represented by io
    only has to have an on and off method.  The built in devices
    use io such as GPIO, PWM, and Poller.

    When a Device is turned on with arguments, it should start up
    a trigger.  A trigger is a threaded class that starts up and
    waits for some event to happen.  When the event happens it does
    two things: turns off the io object and notifies the reset of
    the system with a 'completed' event.

    For example, if you have a gadgets system for watering the grass
    you could send a RCL command like this:

    >>> from gadgets import Sockets
    >>> sock = Sockets()
    >>> sock.send('turn on front yard sprinkers')

    This is an example of an RCL command that has no arguments.  If
    this command was send instead:

    >>> sock.send('turn on front yard sprinkers for 15 minutes')

    the command is considered to have arguments.  If the Device that
    controls the front yard sprinklers is a Switch, then its trigger
    is a GPIOTimer.  A GPIOTimer would be started up and after 15
    minutes it would turn off the GPIO of the Switch that started
    it.
    """

    _units = []

    def __init__(self, location, name, addresses, io_factory=None, trigger_factory=None, on=None, off=None):
        print 'init'
        super(Device, self).__init__(location, name, addresses)
        if not on:
            on = self.get_on_event()
        if not off:
            off = self.get_off_event()
        self._on_event = on
        self._off_event = off
        self._off_trigger = None
        self._io_factory = io_factory
        if trigger_factory is not None:
            self._trigger_factory = trigger_factory
        self._io = None

    @property
    def events(self):
        """
        A list of events that will trigger the event_received method
        """
        return [self._on_event, self._off_event]

    @property
    def status(self):
        return self.io.status

    def get_on_event(self):
        """
        Unless the user passes in the on event or a subclass
        overrides this message, then this device turns on
        in response to this message.  So if this is a garage
        door opener, self._location is garage, self._name is
        opener.  The default on event will be:

        turn on garage door

        You might want to pass in the on event manually so that
        it becomes

        open garage door

        """
        return 'turn on {0} {1}'.format(self._location, self._name)

    def get_off_event(self):
        """see _get_on_event"""
        return 'turn off {0} {1}'.format(self._location, self._name)

    def event_received(self, event, message):
        """
        Called whenever one of the events returned by self.events
        is received.
        """
        if event.startswith(self._on_event):
            if len(event) > len(self._on_event):
                event, message = parse_command(event, message)
            self.on(message)
        elif event.startswith(self._off_event):
            self.off(message)
        
    @property
    def io(self):
        """
        Every device must have an io property.  Switch uses a GPIO,
        ElectricHeater uses PWM.  ElectricMotor uses GPIO and PWM.
        """
        if self._io is None:
            self._io = self._io_factory()
        return self._io

    def on(self, message):
        """
        Gets called by event_received in the case of an on event
        being received.  It calls on of self.io and starts a trigger.
        It also calls self._update_status to notify the whole gadgets
        system of a state change.
        """
        if not self.io.status:
            self.io.on()
            if self._should_get_trigger(message):
                self._invalidate_trigger()
                self._off_trigger = self._get_trigger(message)
                self._off_trigger.start()
            self._update_status(True)

    def off(self, message=None):
        """
        Gets called by event_received in the case of an off event.
        If a trigger is currently running it invalidates the trigger.
        It also calls self._update_status to notifiy the whole gadgets
        system of a state change.
        """
        if self.io.status:
            self.io.off()
            self._invalidate_trigger()
            self._update_status(False, message)

    def _should_get_trigger(self, message):
        return message.get('units') in self._units
        
    def _get_trigger(self, message):
        return self._trigger_factory(self._on_event, self._off_event, message, self.off)
        
    def _invalidate_trigger(self):
        if self._off_trigger is not None and self._off_trigger.is_alive():
            self._off_trigger.invalidate()
            self._off_trigger = None

    def _get_status_message(self, status, message=None):
        outgoing_message = {
            self._location: {
                self._name: {
                    'value': status
                }
            }
        }
        if message is not None:
            for location in message:
                for name, val in message[location].iteritems():
                    if location not in outgoing_message:
                        outgoing_message[location] = dict()
                    outgoing_message[location][name] = {
                        'value': val['value'],
                        'units': val['units']
                    }
        return outgoing_message
                                
    def _update_status(self, status, message=None):
        self.sockets.send(
            'update',
            self._get_status_message(status, message)
        )

    def _register(self):
        self.sockets.send(
            'register',
            {
                'location': self._location,
                'name': self._name,
                'on': self._on_event,
                'off': self._off_event,
                'uid': self.uid,
            }
        )
