import glob
import logging
import disnake
import sys
import tomllib
import aiohttp
from pathlib import Path
from disnake.ext import commands

ERROR_COLOR = 0xff4444
EMBED_COLOR = 0x8f8f8f

class Bot(commands.InteractionBot):
    def __init__(self, *args, **kwargs):
        self.config = {}
        self.data = {}

        self.session = aiohttp.ClientSession(headers={'User-Agent': 'Voagel (Discord Bot) https://github.com/Fam0r/Voagel'})

        super().__init__(*args, **kwargs)

    async def on_ready(self):
        logging.info("Bot is ready.")

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

def main() -> None:
    bot = Bot(intents=disnake.Intents.default())
    bot.load_config()

    for extension in [f.replace('.py', '').replace('/', '.').replace('\\', '.') for f in glob.glob('extensions/**/*.py', recursive=True)]:
        try:
            bot.load_extension(extension)
        except (disnake.ClientException, ModuleNotFoundError):
            logging.error('Failed to load extension %s.', extension, exc_info=True)

    bot.status = disnake.Status(bot.config['bot']['status'])
    bot.activity = disnake.Activity(name=bot.config['bot']['activity'], type=bot.config['bot']['activity_type'])
    bot.run(bot.get_api_key('discord'))
