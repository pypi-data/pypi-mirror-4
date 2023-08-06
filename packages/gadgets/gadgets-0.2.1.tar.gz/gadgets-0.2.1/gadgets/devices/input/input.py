from gadgets.devices.device import Device

class Input(Device):

    _direction = 'input'

    def run(self):
        self.io.start()
        super(Input, self).run()

    @property
    def events(self):
        """
        """
        return []

    def get_on_event(self, on=None):
        return None

    def get_off_event(self, on=None):
        return None

    def _register(self):
        self.sockets.send(
            'register',
            {
                'location': self._location,
                'direction': self._direction,
                'name': self._name,
                'uid': self.uid,
                'input': True
            }
        )

    
