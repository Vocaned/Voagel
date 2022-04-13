import disnake
import json
import os
import logging
import sys
from disnake.ext import commands

class Bot(commands.Bot):
    def __init__(self):
        self.config = {}
        self.data = {}

        super().__init__()

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