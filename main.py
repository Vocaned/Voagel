import glob
import logging
import disnake
from disnake.ext import commands
import lynn

bot = lynn.Bot()

@bot.event
async def on_ready():
    logging.info("Bot is ready.")

if __name__ == '__main__':
    logging.basicConfig(encoding='utf-8', level=logging.INFO)

    for extension in [f.replace('.py', '').replace('/', '.').replace('\\', '.') for f in glob.glob('extensions/**/*.py', recursive=True)]:
        try:
            bot.load_extension(extension)
        except (disnake.ClientException, ModuleNotFoundError):
            logging.error('Failed to load extension %s.', extension, exc_info=True)

    bot.load_config()
    bot.status = disnake.Status(bot.config['status'])
    bot.run(bot.config['secrets']['discord'])
