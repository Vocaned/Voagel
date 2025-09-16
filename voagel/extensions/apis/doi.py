import re
from urllib.parse import quote
import discord
from discord.ext import commands
from discord import app_commands, ui
import bibtexparser

from voagel.main import Bot


class DOICommand(commands.Cog):
    """DOI"""

    def __init__(self, bot: Bot):
        self.bot = bot

    @app_commands.command()
    async def doi(self,
        inter: discord.Interaction,
        query: str
    ):
        """
        Find information about a doi

        Parameters
        ----------
        query: doi
        """

        await inter.response.defer()
        req = await self.bot.session.get(
            f'https://doi.org/{quote(query)}',
            headers={'Accept': 'application/x-bibtex; charset=utf-8'}
        )

        text = await req.text()

        if req.status != 200:
            raise Exception(f'Got an error status {req.status}', text)

        try:
            library = bibtexparser.parse_string(text)
            data = library.entries[0].fields_dict
            view = ui.LayoutView()
            container = ui.Container()
            container.add_item(ui.TextDisplay(f'### [{data["title"]}]({data["url"]})\n{data["author"]}\n-# {data["month"].title()} {data["year"]}'))
        except:
            raise Exception('Failed to parse bibtex')


        view.add_item(container)
        await inter.followup.send(view=view)


async def setup(bot: Bot):
    await bot.add_cog(DOICommand(bot))
