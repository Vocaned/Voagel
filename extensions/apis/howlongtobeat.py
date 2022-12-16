import disnake
from disnake.ext import commands
import lynn
from howlongtobeatpy import HowLongToBeat

class HowlongtobeatCommand(commands.Cog):
    """Howlongtobeat command"""

    def __init__(self, bot: lynn.Bot):
        self.bot = bot

    @commands.slash_command()
    async def howlongtobeat(self,
        inter: disnake.ApplicationCommandInteraction,
        game: str
    ):
        """How long does a game take to beat?"""
        results = await HowLongToBeat().async_search(game)
        if results is not None and len(results) > 0:
            result = max(results, key=lambda element: element.similarity)
            embed = disnake.Embed(title='How Long to Beat', color=lynn.EMBED_COLOR)
            embed.set_author(name=result.game_name, url=result.game_web_link)
            embed.add_field('Main Story', result.main_story + ' Hours')
            embed.add_field('Main + Extra', result.main_extra + ' Hours')
            embed.add_field('Completionist', result.completionist + ' Hours')
            embed.add_field('All Styles', result.all_styles + ' Hours')
            await inter.send(embed=embed)
            return

        raise Exception('Game not found.')



def setup(bot: lynn.Bot):
    bot.add_cog(HowlongtobeatCommand(bot))
