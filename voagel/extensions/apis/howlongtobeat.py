import discord
from discord.ext import commands
from discord import app_commands, ui
from howlongtobeatpy import HowLongToBeat
from voagel.main import Bot, EMBED_COLOR
from voagel.utils import UserException

class HowlongtobeatCommand(commands.Cog):
    """Howlongtobeat command"""

    def __init__(self, bot: Bot):
        self.bot = bot

    @app_commands.command()
    async def howlongtobeat(self,
        inter: discord.Interaction,
        game: str
    ):
        """How long does a game take to beat?

        Parameters
        ----------
        game: Game's name
        """
        await inter.response.defer()
        results = await HowLongToBeat().async_search(game)
        if results is not None and len(results) > 0:
            result = max(results, key=lambda element: element.similarity)

            view = ui.LayoutView()
            container = ui.Container()
            container.add_item(ui.Section(ui.TextDisplay(f'## {result.game_name}'), accessory=ui.Button(label='HowLongToBeat', url=result.game_web_link)))
            bottomtext = ui.TextDisplay(f'''
**Main Story** {result.main_story} hours
**Main + Extra** {result.main_extra} hours
**Completionist** {result.completionist} hours
''')
            if result.game_image_url:
                container.add_item(ui.Section(bottomtext, accessory=ui.Thumbnail(result.game_image_url)))
            else:
                container.add_item(bottomtext)

            container.add_item(container)
            await inter.followup.send(view=view)
        else:
            raise UserException('Game not found.')

async def setup(bot: Bot):
    await bot.add_cog(HowlongtobeatCommand(bot))
