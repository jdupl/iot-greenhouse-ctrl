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
            return False

        print('Proceeding to activate %s.' % self.name)
        self.state = 'activating'

        if not self._activate():
            self.state = 'deactivated'
            return False

        self.last_change = time.time()

        self.state = 'activated'
        self.last_change = time.time()
        print('%s is now activated.' % self.name)
        return True

    def deactivate(self):
        print('Deactivate %s requested.' % self.name)

        if self.state == 'deactivated':
            print('System %s already deactivated.' % self.name)
            return False

        print('Proceeding to deactivate %s.' % self.name)
        self.state = 'deactivating'

        if not self._deactivate():
            self.state = 'activated'
            return False

        self.last_change = time.time()

        self.state = 'deactivated'
        self.last_change = time.time()

        print('%s is now deactivated.' % self.name)
        return True

    def _deactivate(self):
        # close valve to irrigation, close fan and window, etc.
        raise Exception('Abstract')

    def _activate(self):
        # open valve to irrigation, start fan and open window, etc.
        raise Exception('Abstract')


class Ventilation(AbstractSystem):

    def __init__(self, name, fan_subsystem, window_subsystem):
        super(Ventilation, self).__init__(name)
        self.state = 'unknown'
        self.last_change = 0
        self.fan_subsystem = fan_subsystem
        self.window_subsystem = window_subsystem

    def close_up(self):
        self.fan_subsystem.deactivate()
        self.window_subsystem.deactivate()

    def _activate(self):
        if self.window_subsystem.activate():
            self.fan_subsystem.activate()
            return True

    def _deactivate(self):
        if self.fan_subsystem.deactivate():
            self.window_subsystem.deactivate()
            return True


class LegacyWindowActuator(AbstractSystem):

    def __init__(self, name,
                 vdc_close_window_relay_pin, neutral_close_relay_pin,
                 vdc_open_window_relay_pin, neutral_open_relay_pin):
        super(LegacyWindowActuator, self).__init__(name)
        self.actuator_delay_sec = 60
        self.duty = .75

        self.duty_cycle_delay = self.actuator_delay_sec * (1 - self.duty)

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

        print('Closing window. Waiting for actuator for %d seconds.' %
              self.actuator_delay_sec)
        # close 'vdc_close_window_relay_pin' and
        # 'neutral_close_relay_pin_wrapper' relays circuit (power on)
        self.vdc_close_window_relay_pin_wrapper.output(_GPIO.LOW)
        self.neutral_close_relay_pin_wrapper.output(_GPIO.LOW)

        # Let actuator work
        time.sleep(self.actuator_delay_sec * 1.5)

        # open 'close' relay circuit (power off)
        self.vdc_close_window_relay_pin_wrapper.output(_GPIO.HIGH)
        self.neutral_close_relay_pin_wrapper.output(_GPIO.HIGH)

        self.vdc_close_window_relay_pin_wrapper.cleanup()
        self.neutral_close_relay_pin_wrapper.cleanup()
        print('Window is now closed.')
        return True


class WindowActuator(AbstractSystem):

    def __init__(self, name,
                 open_window_relay_pin, close_window_relay_pin):
        super(WindowActuator, self).__init__(name)
        self.actuator_delay_sec = 30
        self.duty = .75

        self.duty_cycle_delay = self.actuator_delay_sec * (1 - self.duty)

        self.open_window_relay = open_window_relay_pin
        self.close_window_relay = close_window_relay_pin

        self.open_window_relay_pin_wrapper = RPiGPIOWrapper(
            open_window_relay_pin)
        self.close_window_relay_pin_wrapper = RPiGPIOWrapper(
            close_window_relay_pin)

    def _activate(self):
        # Extends actuator

        last_activation_ago = time.time() - self.last_change
        if last_activation_ago < self.duty_cycle_delay:
            print('Window can not be opened. Waiting for motor duty cooldown.')
            return False

        print('Opening window. Waiting for actuator for %d seconds.' %
              self.actuator_delay_sec)
        # Extend now
        self.open_window_relay_pin_wrapper.output(_GPIO.HIGH)
        self.close_window_relay_pin_wrapper.output(_GPIO.LOW)

        # Let actuator work
        time.sleep(self.actuator_delay_sec)

        # Stop actuator
        self.open_window_relay_pin_wrapper.output(_GPIO.LOW)
        self.close_window_relay_pin_wrapper.output(_GPIO.LOW)

        self.open_window_relay_pin_wrapper.cleanup()
        self.close_window_relay_pin_wrapper.cleanup()

        print('Window is now opened.')
        return True

    def _deactivate(self):
        # Retracts actuator
        last_activation_ago = time.time() - self.last_change

        print('Closing window. Waiting for actuator for %d seconds.' %
              self.actuator_delay_sec)
        # Retract now
        self.open_window_relay_pin_wrapper.output(_GPIO.LOW)
        self.close_window_relay_pin_wrapper.output(_GPIO.HIGH)

        # Let actuator work
        time.sleep(self.actuator_delay_sec * 1.5)

        # Stop actuator
        self.open_window_relay_pin_wrapper.output(_GPIO.LOW)
        self.close_window_relay_pin_wrapper.output(_GPIO.LOW)

        self.open_window_relay_pin_wrapper.cleanup()
        self.close_window_relay_pin_wrapper.cleanup()
        print('Window is now closed.')
        return True


class Fan(AbstractSystem):

    def __init__(self, name, relay_pin):
        super(Fan, self).__init__(name)
        self.relay_pin = relay_pin

        self.relay_pin_wrapper = RPiGPIOWrapper(
            relay_pin)

    def _activate(self):
        print('Powering on fan.')
        # open 'fan' relay
        self.relay_pin_wrapper.output(_GPIO.LOW)
        print('Fan is powered on.')
        return True

    def _deactivate(self):
        print('Powering off fan.')
        self.relay_pin_wrapper.output(_GPIO.HIGH)
        # close 'fan' relay
        print('Fan is powered off.')
        return True
