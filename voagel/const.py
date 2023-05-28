import tomllib
from pathlib import Path
import logging
import sys
from disnake.ext import commands

class Bot(commands.InteractionBot):
    def __init__(self, *args, **kwargs):
        self.config = {}
        self.data = {}

        super().__init__(*args, **kwargs)

    def get_api_key(self, key: str) -> str:
        val = self.config['secrets'].get(key, None)
        if not val:
            raise commands.DisabledCommand('API key for command missing. Ping the bot owner for help.')
        return val

    def load_config(self):
        Path('config').mkdir(exist_ok=True)
        Path('data').mkdir(exist_ok=True)
        if not Path('config', 'bot.toml').exists():
            logging.critical('Bot config could not be found. Copy bot.toml to the config folder and edit it to continue.')
            sys.exit(1)
        with open(Path('config', 'bot.toml'), 'rb', encoding='utf-8') as f:
            self.config = tomllib.load(f)

ERROR_COLOR = 0xff4444
EMBED_COLOR = 0x8f8f8f
