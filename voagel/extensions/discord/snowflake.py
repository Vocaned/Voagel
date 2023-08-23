import disnake
from disnake.ext import commands

from voagel.main import Bot, EMBED_COLOR

class SnowflakeCommand(commands.Cog):
    """Snowflake command."""

    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.slash_command()
    async def snowflake(self,
        inter: disnake.ApplicationCommandInteraction,
        snowflake: disnake.Object
    ):
        """
        Get information from any snowflake or discord object

        Parameters
        ----------
        snowflake: Snowflake ID or Discord object
        """

        embed = disnake.Embed(color=EMBED_COLOR)
        embed.add_field('Timestamp', f'{int(snowflake.created_at.timestamp())}\n<t:{int(snowflake.created_at.timestamp())}:F>', inline=False)
        embed.add_field('Internal Worker ID', (snowflake.id & 0x3E0000) >> 17, inline=False)
        embed.add_field('Internal Process ID', (snowflake.id & 0x1F000) >> 12, inline=False)
        embed.add_field('Increment', snowflake.id & 0xFFF, inline=False)
        embed.set_footer(text=snowflake.id)
        await inter.send(embed=embed)

def setup(bot: Bot):
    bot.add_cog(SnowflakeCommand(bot))
