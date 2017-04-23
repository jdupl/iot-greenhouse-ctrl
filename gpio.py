class RPiGPIOWrapper():
    # Implementation for Raspberry pi 1 to 3
    # Pin ID are BCM numbering
    def __init__(self, bcm_pin_id):
        import RPi.GPIO as _GPIO
        self.GPIO = _GPIO
        self.pin_id = bcm_pin_id

    def output(self, value):
        self.__setup()
        print('outputting %s to %d' % (value, self.pin_id))
        self.GPIO.output(self.pin_id, value)

    def cleanup(self):
        self.GPIO.cleanup()

    def __setup(self):
        self.GPIO.setwarnings(False)
        self.GPIO.setmode(self.GPIO.BCM)
        self.GPIO.setup(self.pin_id, self.GPIO.OUT, initial=self.GPIO.HIGH)
