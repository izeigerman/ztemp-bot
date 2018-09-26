import json
import logging


class SensorController:
    def __init__(self, sensor, settings_file=None, num_of_reading_retries=3):
        self._sensor = sensor
        self._max_temp = None
        self._min_temp = None
        self._alert_fired = False
        self._settings_file = settings_file
        self._previous_tick_reading = None
        self._num_of_reading_retries = num_of_reading_retries
        self._logger = logging.getLogger('SensorController')
        self._load_settings()

    def _load_settings(self):
        if self._settings_file and len(self._settings_file) > 0:
            try:
                with open(self._settings_file, 'r') as fd:
                    settings = json.load(fd)
                    self._max_temp = settings.get('max_temp', None)
                    self._min_temp = settings.get('min_temp', None)
            except FileNotFoundError:
                pass
            except:  # noqa
                self._logger.exception('Failed to load settings')

    def _save_settings(self):
        if self._settings_file and len(self._settings_file) > 0:
            try:
                with open(self._settings_file, 'w') as fd:
                    settings = {
                        'max_temp': self._max_temp,
                        'min_temp': self._min_temp
                    }
                    json.dump(settings, fd)
            except:  # noqa
                self._logger.exception('Failed to save settings')

    def _is_within_constrains(self, r):
        min_exceeded = self._min_temp is not None and r.temp < self._min_temp
        max_exceeded = self._max_temp is not None and r.temp > self._max_temp
        return not min_exceeded and not max_exceeded

    def get_sensor_reading(self):
        return self._sensor.read()

    def set_max_temp(self, max_temp):
        value = float(max_temp) if max_temp else None
        self._max_temp = value
        self._alert_fired = False
        self._save_settings()

    def get_max_temp(self):
        return self._max_temp

    def set_min_temp(self, min_temp):
        value = float(min_temp) if min_temp else None
        self._min_temp = value
        self._alert_fired = False
        self._save_settings()

    def get_min_temp(self):
        return self._min_temp

    def tick(self):
        if self._previous_tick_reading:
            for i in range(self._num_of_reading_retries + 1):
                reading = self.get_sensor_reading()
                prev_temp = self._previous_tick_reading.temp
                if reading and abs(reading.temp - prev_temp) < 1.0:
                    break
        else:
            reading = self.get_sensor_reading()

        if reading:
            self._previous_tick_reading = reading
            is_alert_fired = self._alert_fired
            if not is_alert_fired and not self._is_within_constrains(reading):
                self._alert_fired = True
                msg = 'WARNING: the temperature has reached '
                msg += '{0:.1f}°C'.format(reading.temp)
                return msg
            elif self._alert_fired and self._is_within_constrains(reading):
                self._alert_fired = False

        return None
