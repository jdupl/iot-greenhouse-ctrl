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

    for equipment in systems:
        equipment.deactivate()


def system_operational(sensors):
    # False if an important sensor is down for an extended period of time
    for sensor in sensors:
        if sensor.last_success + MAX_SENSOR_DOWNTIME_SEC <= time.time():
            print('ERROR: sensor %s is down for an extended period !' %
                  sensor.location)
            return False
    return True


def update_systems_status_routine(sensors, systems):
    pass


def main():
    sensors = [
        # DHT11Sensor(25, 'outside'),
        DHT22Sensor(24, 'back'),
        DHT22Sensor(23, 'front')
    ]

    fan = Fan(22)
    window_actuator = WindowActuator(17, 27)

    systems = [
        Ventilation(fan, window_actuator)
    ]

    while True:
        vals = get_current_values(sensors)
        print(vals)

        if not system_operational(sensors):
            emergency_deactivate(systems)
        else:
            update_systems_status_routine(sensors, systems)

        time.sleep(10)


if __name__ == '__main__':
    main()
