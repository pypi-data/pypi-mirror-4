

class ADC(object):
    """
    ADC reads the adc pins (what else?).
    NOTE: On a beaglebone, you must do:
    
    # modprobe ti_tscadc
    for the adc pins to be enabled.
    """

    _base_path = '/sys/devices/platform/omap/tsc/{0}'

    def __init__(self, name):
        """
        name:  the name of the file that is read
        to obtain the adc value.
        """
        self._file_cache = None
        self._path = self._base_path.format(name)

    @property
    def value(self):
        value = int(self._file.read().replace('\x00', ''))
        self._file.seek(0)
        return value

    @property
    def _file(self):
        if self._file_cache is None:
            self._file_cache = open(self._path, 'r')
        return self._file_cache
            
    def close(self):
        self._file.close()

