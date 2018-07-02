import logging
import json
import sys
from ztemp.bot import ZtempBot
from ztemp.controller import SensorController
from ztemp.sensor import (DummySensor, SensorReading)


def run():
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(format=log_format, level=logging.INFO)

    if len(sys.argv) < 2:
        print('Missing configuration file')
        sys.exit()

    with open(sys.argv[1], 'r') as fd:
        config = json.load(fd)

    telegram_token = config['telegram']['token']
    bot_chat_id = config['telegram']['chat_id']
    sensor_read_interval = config['sensor']['read_interval']
    sensor_pin = config['sensor']['pin']

    reading = SensorReading(28.0, 56.0)
    sensor = DummySensor(reading)
    controller = SensorController(sensor)
    bot = ZtempBot(telegram_token, controller, sensor_read_interval,
                   bot_chat_id)
    bot.run()


if __name__ == '__main__':
    run()
