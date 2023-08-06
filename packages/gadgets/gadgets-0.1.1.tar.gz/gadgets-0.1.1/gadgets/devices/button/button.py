from gadgets.devices.device import Device

class Button(Device):

    def run(self):
        self.io.start()
        super(Button, self).run()

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
                'name': self._name,
                'uid': self.uid,
                'input': True
            }
        )

    