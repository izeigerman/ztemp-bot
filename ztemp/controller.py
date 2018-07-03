import json
import logging


class SensorController:
    def __init__(self, sensor, settings_file=None):
        self._sensor = sensor
        self._max_temp = None
        self._min_temp = None
        self._alert_fired = False
        self._settings_file = settings_file
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
            except:
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
            except:
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
        res = self.get_sensor_reading()
        if res:
            if not self._alert_fired and not self._is_within_constrains(res):
                self._alert_fired = True
                msg = 'WARNING: the temperature has reached '
                msg += '{0:.1f}°C'.format(res.temp)
                return msg
            elif self._alert_fired and self._is_within_constrains(res):
                self._alert_fired = False

        return None
