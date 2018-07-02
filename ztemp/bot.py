from telegram.ext import (CommandHandler, Updater)


def temp_arg_handler(handler):
    def wrapper(ztemp_bot, bot, update, *vargs, **kwargs):
        args = kwargs['args']
        if args and len(args) == 1:
            try:
                temp_arg = float(args[0])
                handler(ztemp_bot, bot, update, temp_arg)
            except ValueError:
                error_msg = 'Invalid temperature value "{}"'.format(args[0])
                bot.send_message(chat_id=update.message.chat_id,
                                 text=error_msg)
        else:
            bot.send_message(chat_id=update.message.chat_id,
                             text='One argument is expected')
    return wrapper


def private_handler(handler):
    def wrapper(ztemp_bot, bot, update, *vargs, **kwargs):
        if str(update.message.chat_id) == str(ztemp_bot._bot_chat_id):
            handler(ztemp_bot, bot, update, *vargs, **kwargs)
    return wrapper


class ZtempBot:
    def __init__(self, telegram_token, sensor_controller,
                 tick_interval, bot_chat_id):
        self._token = telegram_token
        self._sensor_controller = sensor_controller
        self._tick_interval = tick_interval
        self._bot_chat_id = bot_chat_id
        self._help_message = self._generate_help_message()

    @staticmethod
    def _generate_help_message():
        msg = 'The following commands are supported:\n'
        msg += '/gettemp - prints the current temperature and humidity.\n'
        msg += '/setmaxtemp <value> - sets the maximum temperature.\n'
        msg += '/setmintemp <value> - sets the minimum temperature.\n'
        msg += '/resetmaxtemp - resets the current '
        msg += 'maximum temperature threshold.\n'
        msg += '/resetmintemp - resets the current '
        msg += 'minimum temperature threshold.\n'
        msg += '/help - prints this help message.'
        return msg

    @private_handler
    def _on_get_temp(self, bot, update):
        reading = self._sensor_controller.get_sensor_reading()
        if reading:
            message = '{0:.1f}°C, humidity {1:0.1f}%'.format(reading.temp,
                                                             reading.humidity)
            bot.send_message(chat_id=update.message.chat_id, text=message)
        else:
            error_msg = 'Failed to read data from sensor. Please try again'
            bot.send_message(chat_id=update.message.chat_id, text=error_msg)

    @private_handler
    @temp_arg_handler
    def _on_set_max_temp(self, bot, update, temp):
        self._sensor_controller.set_max_temp(temp)
        msg = 'Maximum temperature is now set to {0:.1f}°C'.format(temp)
        bot.send_message(chat_id=update.message.chat_id, text=msg)

    @private_handler
    @temp_arg_handler
    def _on_set_min_temp(self, bot, update, temp):
        self._sensor_controller.set_min_temp(temp)
        msg = 'Minimum temperature is now set to {0:.1f}°C'.format(temp)
        bot.send_message(chat_id=update.message.chat_id, text=msg)

    @private_handler
    def _on_reset_max_temp(self, bot, update):
        self._sensor_controller.set_max_temp(None)
        msg = 'Maximum temperature threshold has been removed'
        bot.send_message(chat_id=update.message.chat_id, text=msg)

    @private_handler
    def _on_reset_min_temp(self, bot, update):
        self._sensor_controller.set_min_temp(None)
        msg = 'Minimum temperature threshold has been removed'
        bot.send_message(chat_id=update.message.chat_id, text=msg)

    @private_handler
    def _on_help(self, bot, update):
        bot.send_message(chat_id=update.message.chat_id,
                         text=self._help_message)

    def _on_get_chat_id(self, bot, update):
        bot.send_message(chat_id=update.message.chat_id,
                         text=update.message.chat_id)

    def _tick(self, bot, job):
        tick_result = self._sensor_controller.tick()
        if tick_result:
            bot.send_message(chat_id=self._bot_chat_id, text=tick_result)

    def _setup_handlers(self, updater):
        dispatcher = updater.dispatcher
        job_queue = updater.job_queue

        get_temp_handler = CommandHandler('gettemp', self._on_get_temp)
        dispatcher.add_handler(get_temp_handler)

        set_max_handler = CommandHandler('setmaxtemp', self._on_set_max_temp,
                                         pass_args=True)
        dispatcher.add_handler(set_max_handler)

        set_min_handler = CommandHandler('setmintemp', self._on_set_min_temp,
                                         pass_args=True)
        dispatcher.add_handler(set_min_handler)

        reset_max_handler = CommandHandler('resetmaxtemp',
                                           self._on_reset_max_temp)
        dispatcher.add_handler(reset_max_handler)

        reset_min_handler = CommandHandler('resetmintemp',
                                           self._on_reset_min_temp)
        dispatcher.add_handler(reset_min_handler)

        get_chat_id_handler = CommandHandler('getchatid',
                                             self._on_get_chat_id)
        dispatcher.add_handler(get_chat_id_handler)

        help_handler = CommandHandler('help', self._on_help)
        dispatcher.add_handler(help_handler)

        job_queue.run_repeating(self._tick, interval=self._tick_interval,
                                first=0)

    def run(self):
        updater = Updater(token=self._token)
        self._setup_handlers(updater)
        updater.start_polling()
