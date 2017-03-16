import time
import Adafruit_DHT


MAX_SENSOR_DOWNTIME_SEC = 2 * 60


class AbstractSensor():

    def __init__(self):
        self.last_failure = 0
        self.last_success = 0

    def read(self):
        raise('Abstract')


class DHTSensor(AbstractSensor):
    def __init__(self, bcm_pin, location):
        self.bcm_pin = bcm_pin
        self.location = location

    def read(self):
        rel_humidity, temp = Adafruit_DHT.read_retry(
            self.dht_type, self.bcm_pin)

        if not temp or not rel_humidity:
            self.last_failure = time.time()
            return

        self.last_success = time.time()
        return {
            'temperature': temp,
            'rel_humidity': rel_humidity
        }


class DHT22Sensor(DHTSensor):
    def __init__(self, bcm_pin, location):
        self.dht_type = Adafruit_DHT.DHT22
        super(DHT22Sensor, self).__init__(bcm_pin, location)


class DHT11Sensor(DHTSensor):
    def __init__(self, bcm_pin, location):
        self.dht_type = Adafruit_DHT.DHT11
        super(DHT11Sensor, self).__init__(bcm_pin, location)


def get_current_values(sensors):
    next_values = {
        'temperature': {},
        'rel_humidity': {},
        'soil_humidity': {},
    }

    for sensor in sensors:
        sensor_reading = sensor.read()

        if not sensor_reading:
            print('Warning: could not read %s' % sensor.location)
            continue

        next_values[sensor.location] = sensor_reading

    return next_values


def emergency_shutdown(equipments):
    # Kill power to all equipment
    print('SHUTTING DOWN ALL EQUIPMENT')
    for equipment in equipments:
        equipment.poweroff()


def system_operational(sensors):
    # False if an important sensor is down for an extended period of time
    for sensor in sensors:
        if sensor.last_success + MAX_SENSOR_DOWNTIME_SEC <= time.time():
            print('ERROR: sensor %s is down for an extended period !' %
                  sensor.location)
            return False
    return True


def main():
    sensors = [
        DHT11Sensor(25, 'outside'),
        DHT22Sensor(24, 'back'),
        DHT22Sensor(23, 'front')
    ]

    equipments = [

    ]

    while True:
        vals = get_current_values(sensors)
        print(vals)

        if not system_operational():
            emergency_shutdown(equipments)

        time.sleep(10)


if __name__ == '__main__':
    main()
