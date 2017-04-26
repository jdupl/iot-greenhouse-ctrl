import time

from sensors import DHT11Sensor, DHT22Sensor
from systems import Ventilation, Fan, WindowActuator


MAX_SENSOR_DOWNTIME_SEC = 2 * 60


def get_current_values(sensors):
    next_values = {}

    for sensor in sensors:
        sensor_reading = sensor.read()

        if not sensor_reading:
            print('Warning: could not read %s' % sensor.location)
            continue

        next_values[sensor.location] = sensor_reading

    return next_values


def emergency_deactivate(systems):
    # Kill power to all equipment
    print('DEACTIVATING DOWN ALL SYSTEMS')

    for name, equipment in systems.items():
        equipment.deactivate()


def system_operational(sensors):
    # False if an important sensor is down for an extended period of time
    for sensor in sensors:
        if sensor.last_success + MAX_SENSOR_DOWNTIME_SEC <= time.time():
            print('ERROR: sensor %s is down for an extended period !' %
                  sensor.location)
            return False
    return True


def too_cold(vals):
    return vals['front']['temperature'] <= 19


def too_hot(vals):
    return vals['front']['temperature'] > 21


def update_systems_status_routine(vals, systems):
    if too_hot(vals):
        systems['ventilation'].activate()
    if too_cold(vals):
        systems['ventilation'].deactivate()


def main():
    sensors = [
        # DHT11Sensor(25, 'outside'),
        # DHT22Sensor(24, 'back'),
        DHT22Sensor(23, 'front')
    ]

    fan = Fan('Fan 1', 22)
    window_actuator = WindowActuator('Window 1',
                                     vdc_close_window_relay_pin=24,
                                     neutral_close_relay_pin=22,
                                     vdc_open_window_relay_pin=27,
                                     neutral_open_relay_pin=17)
    ventilation = Ventilation('Ventilation system 1', fan, window_actuator)

    systems = {
        'ventilation': ventilation
    }

    vals = {}

    systems['ventilation'].deactivate()

    while True:
        new_vals = get_current_values(sensors)
        for k, v in vals.items():
            if k not in new_vals:
                new_vals[k] = vals[k]
        vals = new_vals
        print(vals)

        if not system_operational(sensors):
            emergency_deactivate(systems)
        else:
            update_systems_status_routine(vals, systems)

        time.sleep(10)


if __name__ == '__main__':
    main()
