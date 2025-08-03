from io import BytesIO
from urllib.parse import quote
import discord
from discord.ext import commands
from discord import app_commands, ui
from datetime import datetime
from urllib import parse

from voagel.main import Bot, EMBED_COLOR


class CVECommand(commands.Cog):
    """CVE"""

    def __init__(self, bot: Bot):
        self.bot = bot

    @app_commands.command()
    async def cve(self,
        inter: discord.Interaction,
        query: str
    ):
        """
        Find information about a CVE

        Parameters
        ----------
        query: CVE identifier
        """

        await inter.response.defer()
        req = await self.bot.session.get(
            f'https://cvedb.shodan.io/cve/{quote(query)}'
        )

        if req.status != 200:
            err = await req.json()
            if not err or 'detail' not in err:
                err = '[unknown error]'
            else:
                err = err['detail']

            raise Exception(f'Got an error status {req.status}', err)

        data = await req.json()

        view = ui.LayoutView()
        container = ui.Container()
        container.add_item(ui.TextDisplay(f'### {data["cve_id"]}\n{data["summary"]}'))

        buttons = ui.ActionRow()
        for link in list(dict.fromkeys(data['references']))[:5]: # Remove duplicates and slice at 5 elements
            buttons.add_item(ui.Button(label=str(parse.urlparse(link).netloc).lstrip('www.'), url=link))
        if buttons.children:
            container.add_item(buttons)

        severity = data['cvss']
        sevstr = 'None' if severity == 0 else 'Low' if severity < 4 else 'Medium' if severity < 7 else 'High' if severity < 9 else 'Critical' if severity <= 10 else 'Unknown'
        container.add_item(ui.TextDisplay(f'{severity} {sevstr} (v{data["cvss_version"]}) **@** <t:{int(datetime.fromisoformat(data["published_time"]).timestamp())}>'))

        view.add_item(container)
        await inter.followup.send(view=view)


async def setup(bot: Bot):
    await bot.add_cog(CVECommand(bot))
