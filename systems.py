import time
import RPi.GPIO as _GPIO

from gpio import RPiGPIOWrapper


class AbstractSystem():

    def __init__(self, system_name):
        self.name = system_name

        self.state = 'unknown'
        self.last_change = 0

    def activate(self):
        print('Activate %s requested.' % self.name)

        if self.state == 'activated':
            print('System %s already activated.' % self.name)
            return

        print('Proceeding to activate %s.' % self.name)
        self.state = 'activating'
        self.last_change = time.time()
        self._activate()

        self.state = 'activated'
        self.last_change = time.time()
        print('%s is now activated.' % self.name)

    def deactivate(self):
        print('Deactivate %s requested.' % self.name)

        if self.state == 'deactivated':
            print('System %s already deactivated.' % self.name)
            return

            self.state = 'deactivating'
        self.last_change = time.time()
        self._deactivate()

        self.state = 'deactivated'
        self.last_change = time.time()

        print('%s is now deactivated.' % self.name)

    def _deactivate(self):
        # close valve to irrigation, close fan and window, etc.
        raise Exception('Abstract')

    def _activate(self):
        # open valve to irrigation, start fan and open window, etc.
        raise Exception('Abstract')


class Ventilation(AbstractSystem):

    def __init__(self, name, fan_subsystem, window_subsystem):
        super(Ventilation, self).__init__(name)
        self.fan_subsystem = fan_subsystem
        self.window_subsystem = window_subsystem

    def _activate(self):
        self.window_subsystem.activate()
        self.fan_subsystem.activate()

    def _deactivate(self):
        self.fan_subsystem.deactivate()
        self.window_subsystem.deactivate()


class WindowActuator(AbstractSystem):

    def __init__(self, name, close_window_relay_pin, open_window_relay_pin):
        super(WindowActuator, self).__init__(name)
        self.actuator_delay_sec = 5
        self.close_window_relay_pin = close_window_relay_pin
        self.open_window_relay_pin = open_window_relay_pin
        self.gpio_wrapper_close = RPiGPIOWrapper(close_window_relay_pin)
        self.gpio_wrapper_open = RPiGPIOWrapper(open_window_relay_pin)

    def _activate(self):
        print('Opening window. Waiting for actuator for %d seconds.' %
              self.actuator_delay_sec)
        # close 'opening' relay circuit (power on)
        self.gpio_wrapper_open.output(_GPIO.LOW)
        time.sleep(self.actuator_delay_sec)
        # open 'open' relay circuit (power off)
        self.gpio_wrapper_open.output(_GPIO.HIGH)
        self.gpio_wrapper_open.cleanup()
        print('Window is now opened.')

    def _deactivate(self):
        print('Closing window. Waiting for actuator for %d seconds.' %
              self.actuator_delay_sec)
        # close 'closing' relay circuit (power on)
        self.gpio_wrapper_close.output(_GPIO.LOW)
        time.sleep(self.actuator_delay_sec)
        # open 'closing' relay circuit (power off)
        self.gpio_wrapper_close.output(_GPIO.HIGH)
        self.gpio_wrapper_close.cleanup()
        print('Window is now closed.')


class Fan(AbstractSystem):

    def __init__(self, name, relay_pin):
        super(Fan, self).__init__(name)
        self.relay_pin = relay_pin

    def _activate(self):
        print('Powering on fan.')
        # open 'fan' relay
        print('Fan is powered on.')

    def _deactivate(self):
        print('Powering off fan.')
        # close 'fan' relay
        print('Fan is powered off.')
