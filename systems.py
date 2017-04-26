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

        if not self._activate():
            self.state = 'deactivated'
            return

        self.last_change = time.time()

        self.state = 'activated'
        self.last_change = time.time()
        print('%s is now activated.' % self.name)

    def deactivate(self):
        print('Deactivate %s requested.' % self.name)

        if self.state == 'deactivated':
            print('System %s already deactivated.' % self.name)
            return

        print('Proceeding to deactivate %s.' % self.name)
        self.state = 'deactivating'

        if not self._deactivate():
            self.state = 'activated'
            return

        self.last_change = time.time()

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

    def __init__(self, name,
                 vdc_close_window_relay_pin, neutral_close_relay_pin,
                 vdc_open_window_relay_pin, neutral_open_relay_pin):
        super(WindowActuator, self).__init__(name)
        self.actuator_delay_sec = 60
        self.duty = .25

        self.duty_cycle_delay = self.actuator_delay_sec / self.duty

        self.vdc_close_window_relay_pin = vdc_close_window_relay_pin
        self.neutral_close_relay_pin = neutral_close_relay_pin
        self.vdc_open_window_relay_pin = vdc_open_window_relay_pin
        self.neutral_open_relay_pin = neutral_open_relay_pin

        self.vdc_close_window_relay_pin_wrapper = RPiGPIOWrapper(
            vdc_close_window_relay_pin)
        self.neutral_close_relay_pin_wrapper = RPiGPIOWrapper(
            neutral_close_relay_pin)
        self.vdc_open_window_relay_pin_wrapper = RPiGPIOWrapper(
            vdc_open_window_relay_pin)
        self.neutral_open_relay_pin_wrapper = RPiGPIOWrapper(
            neutral_open_relay_pin)

    def _open_all_relays(self):
        # power off everything
        self.vdc_close_window_relay_pin_wrapper.output(_GPIO.HIGH)
        self.neutral_close_relay_pin_wrapper.output(_GPIO.HIGH)
        self.vdc_open_window_relay_pin_wrapper.output(_GPIO.HIGH)
        self.neutral_open_relay_pin_wrapper.output(_GPIO.HIGH)

        self.vdc_close_window_relay_pin_wrapper.cleanup()
        self.neutral_close_relay_pin_wrapper.cleanup()
        self.vdc_open_window_relay_pin_wrapper.cleanup()
        self.neutral_open_relay_pin_wrapper.cleanup()
        time.sleep(1)

    def _activate(self):
        self._open_all_relays()

        last_activation_ago = time.time() - self.last_change
        if last_activation_ago < self.duty_cycle_delay:
            print('Window can not be opened. Waiting for motor duty cooldown.')
            return False

        print('Opening window. Waiting for actuator for %d seconds.' %
              self.actuator_delay_sec)
        # close 'vdc_open_window_relay_pin' and
        # 'neutral_open_relay_pin_wrapper' relays circuit (power on)
        self.vdc_open_window_relay_pin_wrapper.output(_GPIO.LOW)
        self.neutral_open_relay_pin_wrapper.output(_GPIO.LOW)

        # Let actuator work
        time.sleep(self.actuator_delay_sec)

        # open 'open' relay circuit (power off)
        self.vdc_open_window_relay_pin_wrapper.output(_GPIO.HIGH)
        self.neutral_open_relay_pin_wrapper.output(_GPIO.HIGH)

        self.vdc_open_window_relay_pin_wrapper.cleanup()
        self.neutral_open_relay_pin_wrapper.cleanup()

        print('Window is now opened.')
        return True

    def _deactivate(self):
        self._open_all_relays()
        last_activation_ago = time.time() - self.last_change

        if last_activation_ago < self.duty_cycle_delay:
            print('Window can not be opened. Waiting for motor duty cooldown.')
            return False

        print('Closing window. Waiting for actuator for %d seconds.' %
              self.actuator_delay_sec)
        # close 'vdc_close_window_relay_pin' and
        # 'neutral_close_relay_pin_wrapper' relays circuit (power on)
        self.vdc_close_window_relay_pin_wrapper.output(_GPIO.LOW)
        self.neutral_close_relay_pin_wrapper.output(_GPIO.LOW)

        # Let actuator work
        time.sleep(self.actuator_delay_sec)

        # open 'close' relay circuit (power off)
        self.vdc_close_window_relay_pin_wrapper.output(_GPIO.HIGH)
        self.neutral_close_relay_pin_wrapper.output(_GPIO.HIGH)

        self.vdc_close_window_relay_pin_wrapper.cleanup()
        self.neutral_close_relay_pin_wrapper.cleanup()
        print('Window is now closed.')
        return True


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
