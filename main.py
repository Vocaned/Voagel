import glob
import logging
import disnake
import lynn

bot = lynn.Bot()

@bot.event
async def on_ready():
    logging.info("Bot is ready.")

if __name__ == '__main__':
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(lynn.ColorFormatter())

    logger.addHandler(ch)

    bot.load_config()

    for extension in [f.replace('.py', '').replace('/', '.').replace('\\', '.') for f in glob.glob('extensions/**/*.py', recursive=True)]:
        try:
            bot.load_extension(extension)
        except (disnake.ClientException, ModuleNotFoundError):
            logging.error('Failed to load extension %s.', extension, exc_info=True)

    bot.status = disnake.Status(bot.config['status'])
    bot.run(bot.config['secrets']['discord'])
