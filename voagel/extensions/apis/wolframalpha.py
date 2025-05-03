from io import BytesIO
from urllib.parse import quote
import discord
from discord.ext import commands
from discord import app_commands, ui

from voagel.main import Bot, EMBED_COLOR
from voagel.utils import UserException


class WolframAlphaCommand(commands.Cog):
    """Wolfram Alpha"""

    def __init__(self, bot: Bot):
        self.bot = bot

    @app_commands.command()
    async def wolframalpha(self,
        inter: discord.Interaction,
        query: str
    ):
        """
        Ask questions to Wolfram Alpha

        Parameters
        ----------
        query: Query for Wolfram Alpha
        """

        await inter.response.defer()
        req = await self.bot.session.get(
            f'http://api.wolframalpha.com/v1/simple?appid={self.bot.get_api_key("wolframalpha")}&layout=labelbar&ip=None&units=metric&background=2F3136&foreground=white&i={quote(query)}'
        )

        if req.status != 200:
            err = req.text()
            if not err:
                err = '[unknown error]'

            if req.status == 501:
                raise UserException('WolframAlpha could not parse the query', err)
            raise Exception(f'WolframAlpha returned an error status {req.status}', err)

        data = await req.read()
        if len(data) == 0:
            raise Exception('WolframAlpha did not return any data.')

        view = ui.LayoutView()
        view.add_item(ui.Container(ui.MediaGallery(discord.MediaGalleryItem('attachment://wolfram.png'))))
        await inter.followup.send(view=view, file=discord.File(BytesIO(data), 'wolfram.png'))


async def setup(bot: Bot):
    await bot.add_cog(WolframAlphaCommand(bot))
