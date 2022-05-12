import json
import os
import logging
import sys
from disnake.ext import commands

class ColorFormatter(logging.Formatter):
    _debug = "\x1b[0;30m"
    _info = "\x1b[0;36m"
    _warn = "\x1b[33;20m"
    _err = "\x1b[31;20m"
    _critical = "\x1b[31;1m"
    _reset = "\x1b[0m"
    _format = "%(asctime)s %(levelname)s: %(message)s (%(filename)s:%(lineno)d)"

    FORMATS = {
        logging.DEBUG: _debug + _format + _reset,
        logging.INFO: _info + _format + _reset,
        logging.WARNING: _warn + _format + _reset,
        logging.ERROR: _err + _format + _reset,
        logging.CRITICAL: _critical + _format + _reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)

class Bot(commands.Bot):
    def __init__(self):
        self.config = {}
        self.data = {}

        super().__init__()

    def get_api_key(self, key: str) -> str:
        val = self.config['secrets'].get(key, None)
        if not val:
            raise commands.DisabledCommand('API key for command missing. Ping the bot owner for help.')
        return val

    def load_config(self):
        if not os.path.exists('config'):
            os.mkdir('config')
        if not os.path.exists('data'):
            os.mkdir('data')
        if not os.path.exists('config/bot.json'):
            logging.critical('Bot config could not be found. Copy bot.json to the config folder and edit it to continue.')
            sys.exit(1)
        with open('config/bot.json', 'r', encoding='utf-8') as f:
            self.config = dict(json.load(f))

ERROR_COLOR = 0xff4444
EMBED_COLOR = 0x8f8f8f
