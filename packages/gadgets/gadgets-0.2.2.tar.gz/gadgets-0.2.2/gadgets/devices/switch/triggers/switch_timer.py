import time
from gadgets.devices.trigger import Trigger


class SwitchTimer(Trigger):

    @property
    def _seconds(self):
        value = self._message.get('value', 0)
        units = self._message.get('units')
        if units == 'hours' or units == 'hour':
            seconds = value * 60.0 * 60.0
        elif units == 'minute' or units == 'minutes':
            seconds = value * 60.0
        elif units == 'second' or units == 'seconds':
            seconds = value
        return seconds

    def wait(self):
        time.sleep(self._seconds)

    def invalidate(self):
        """can't invalidate this trigger"""
        pass