import Adafruit_DHT


class SensorReading:
    def __init__(self, temp, humidity):
        self._temp = temp
        self._humidity = humidity

    @property
    def temp(self):
        return self._temp

    @property
    def humidity(self):
        return self._humidity


class DHTSensor:
    def __init__(self, pin):
        self._pin = pin

    def read(self):
        hum, temp = Adafruit_DHT.read_retry(Adafruit_DHT.DHT22, self._pin)
        return SensorReading(temp, hum)


class DummySensor:
    def __init__(self, reading):
        self._reading = reading

    def read(self):
        return self._reading
