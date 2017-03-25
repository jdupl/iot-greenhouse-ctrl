import time

import smbus
import Adafruit_DHT

# Change to 0 if using pi with 256MB
i2c_bus = smbus.SMBus(1)


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


class ADCSensor(AbstractSensor):
    def __init__(self, i2c_addr, location):
        self.i2c_addr = i2c_addr
        self.location = location

    def read(self):
        for x in range(0, 4):
            i2c_bus.write_byte_data(0x48, 0x40 | ((x + 1) & 0x03), 0)
            v = i2c_bus.read_byte(0x48)
            print(v,)
            time.sleep(0.1)
        print()


class DHT22Sensor(DHTSensor):
    def __init__(self, bcm_pin, location):
        self.dht_type = Adafruit_DHT.DHT22
        super(DHT22Sensor, self).__init__(bcm_pin, location)


class DHT11Sensor(DHTSensor):
    def __init__(self, bcm_pin, location):
        self.dht_type = Adafruit_DHT.DHT11
        super(DHT11Sensor, self).__init__(bcm_pin, location)
