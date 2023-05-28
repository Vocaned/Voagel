import disnake
from disnake.ext import commands
import lynn
import mmh3

class DatamineCommand(commands.Cog):
    """Datamine commands"""

    def __init__(self, bot: lynn.Bot):
        self.bot = bot

    @commands.slash_command(guild_ids=[702953546106273852])
    async def datamine(self, inter: disnake.ApplicationCommandInteraction):
        """Secret Discord stuff"""
        ...

    @datamine.sub_command()
    async def guild_experiment_placement(self,
        inter: disnake.ApplicationCommandInteraction,
        experiment_id: str,
        guild_id: str
    ):
        """Get experiment bucket range for specific experiment and guild

        Parameters
        ----------
        experiment_id: ID (string) of the experiment
        guild_id: ID (int) of the guild"""
        m = mmh3.hash(f'{experiment_id}:{guild_id}'.encode(), signed=False) % 10000
        await inter.send(f'`{guild_id}` is in `{experiment_id}` bucket range **{m}**')


def setup(bot: lynn.Bot):
    bot.add_cog(DatamineCommand(bot))
