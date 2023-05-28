import disnake
from disnake.ext import commands

from voagel.main import Bot

class PingCommand(commands.Cog):
    """Ping command"""

    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.slash_command()
    async def ping(self, inter: disnake.ApplicationCommandInteraction):
        """Get the bot's current websocket latency."""
        await inter.response.send_message(f"pong: {round(self.bot.latency * 1000)}ms")

def setup(bot: Bot):
    bot.add_cog(PingCommand(bot))
