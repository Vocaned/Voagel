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
        """How long does a game take to beat?

        Parameters
        ----------
        game: Game's name
        """
        results = await HowLongToBeat().async_search(game)
        if results is not None and len(results) > 0:
            result = max(results, key=lambda element: element.similarity)
            embed = disnake.Embed(title=f'How Long to Beat: {result.game_name}', url=result.game_web_link, color=lynn.EMBED_COLOR)
            embed.add_field('Main Story', f'{result.main_story} Hours')
            embed.add_field('Main + Extra', f'{result.main_extra} Hours')
            embed.add_field('Completionist', f'{result.completionist} Hours')

            if result.game_image_url:
                embed.set_thumbnail(result.game_image_url)

            await inter.send(embed=embed)
            return

        raise Exception('Game not found.')



def setup(bot: lynn.Bot):
    bot.add_cog(HowlongtobeatCommand(bot))
