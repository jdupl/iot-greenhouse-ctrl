import time


class AbstractSystem():

    def __init__(self):
        self.state = 'unknown'
        self.last_change = 0

    def activate(self):
        self.last_change = time.time()
        self.state = 'activating'
        self.__activate()
        self.last_change = time.time()
        self.state = 'activated'

    def deactivate(self):
        self.last_change = time.time()
        self.state = 'deactivating'
        self.__deactivate()
        self.last_change = time.time()
        self.state = 'deactivated'

    def __deactivate(self):
        # close valve to irrigation, close fan and window, etc.
        raise Exception('Abstract')

    def __activate(self):
        # open valve to irrigation, start fan and open window, etc.
        raise Exception('Abstract')


class Ventilation(AbstractSystem):

    def __init__(self, fan_subsystem, window_subsystem):
        super(Ventilation, self).__init__()
        self.fan_subsystem = fan_subsystem
        self.window_subsystem = window_subsystem

    def __activate(self):
        print('Activating ventilation.')
        self.window_subsystem.activate()
        self.fan_subsystem.activate()
        print('Ventilation activated.')

    def __deactivate(self):
        print('Deactivating ventilation.')
        self.fan_subsystem.deactivate()
        self.window_subsystem.deactivate()
        print('Ventilation deactivated.')


class WindowActuator(AbstractSystem):

    def __init__(self, close_window_relay_pin, open_window_relay_pin):
        super(WindowActuator, self).__init__()
        self.actuator_delay_sec = 30
        self.close_window_relay_pin = close_window_relay_pin
        self.open_window_relay_pin = open_window_relay_pin

    def __activate(self):
        print('Opening window. Waiting for actuator for %d seconds.' %
              self.actuator_delay_sec)
        # open 'opening' relay
        time.sleep(self.actuator_delay_sec)
        # close 'open' relay
        print('Window is now opened.')

    def __deactivate(self):
        print('Closing window. Waiting for actuator for %d seconds.' %
              self.actuator_delay_sec)
        # open 'closing' relay
        time.sleep(self.actuator_delay_sec)
        # close 'closing' relay
        print('Window is now closed.')


class Fan(AbstractSystem):

    def __init__(self, relay_pin):
        super(Fan, self).__init__()
        self.relay_pin = relay_pin

    def __activate(self):
        print('Powering on fan.')
        # open 'fan' relay
        print('Fan is powered on.')

    def __deactivate(self):
        print('Powering off fan.')
        # close 'fan' relay
        print('Fan is powered off.')
