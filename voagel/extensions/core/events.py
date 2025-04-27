import discord
import logging
from discord.ext import commands
from voagel.main import Bot
import uuid


class EventCommands(commands.Cog):
    """Event commands"""

    def __init__(self, bot: Bot):
        self.bot = bot

    async def log_event(self, title: str, description: str):
        channel_id = self.bot.config['bot'].get('log_channel')
        if channel_id is None:
            logging.info('%s: %s', title, description)
            return

        channel = self.bot.get_channel(channel_id)
        if channel is None or not isinstance(channel, discord.TextChannel):
            logging.error('Log channel %s invalid', channel_id)
            return

        embed = discord.Embed(title=title, description=description)
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_ready(self):
        await self.log_event('IDENTIFY', f'{self.bot.user.id if self.bot.user else 'None'}-{hex(uuid.getnode())}')

    @commands.Cog.listener()
    async def on_resumed(self):
        await self.log_event('RESUME', f'{self.bot.user.id if self.bot.user else 'None'}-{hex(uuid.getnode())}')

async def setup(bot: Bot):
    await bot.add_cog(EventCommands(bot))
