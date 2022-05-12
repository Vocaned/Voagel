import disnake
from disnake.ext import commands
import lynn
import re

def converter(_, argument: str) -> disnake.Object:
    match = re.match(r"([0-9]{15,20})$", argument) or re.match(
        r"<(?:@(?:!|&)?|#)([0-9]{15,20})>$", argument
    )

    if match is None:
        raise commands.ObjectNotFound(argument)

    result = int(match.group(1))

    return disnake.Object(id=result)

class SnowflakeCommand(commands.Cog):
    """Snowflake command."""

    def __init__(self, bot: lynn.Bot):
        self.bot = bot

    @commands.slash_command(name='Snowflake', guild_ids=[702953546106273852])
    async def snowflake(self,
        inter: disnake.GuildCommandInteraction,
        snowflake: disnake.Object = commands.Param(description='Snowflake ID or Discord object', converter=converter)
    ):
        """
        Get information from any snowflake or discord object
        """
        embed = disnake.Embed(title=snowflake.id, color=lynn.EMBED_COLOR)
        embed.add_field('Timestamp', snowflake.created_at.strftime('%c'), inline=False)
        embed.add_field('Internal Worker ID', (snowflake.id & 0x3E0000) >> 17, inline=False)
        embed.add_field('Internal Process ID', (snowflake.id & 0x1F000) >> 12, inline=False)
        embed.add_field('Increment', snowflake.id & 0xFFF, inline=False)
        await inter.send(embed=embed)

def setup(bot: lynn.Bot):
    bot.add_cog(SnowflakeCommand(bot))
