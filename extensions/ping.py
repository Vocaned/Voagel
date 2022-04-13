import disnake
from disnake.ext import commands
import lynn

class PingCommand(commands.Cog):
    """Ping command."""

    def __init__(self, bot: lynn.Bot):
        self.bot = bot

    @commands.slash_command(guild_ids=[702953546106273852])
    async def ping(self, inter: disnake.GuildCommandInteraction):
        """Get the bot's current websocket latency."""
        await inter.response.send_message(f"pong: {round(self.bot.latency * 1000)}ms")

def setup(bot: lynn.Bot):
    bot.add_cog(PingCommand(bot))
