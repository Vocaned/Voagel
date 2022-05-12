import disnake
from disnake.ext import commands
from io import BytesIO
import lynn
import utils

class WolframAlphaCommand(commands.Cog):
    """Wolfram Alpha"""

    def __init__(self, bot: lynn.Bot):
        self.bot = bot

    @commands.slash_command(name='WolframAlpha', guild_ids=[702953546106273852])
    async def wolframalpha(self,
        inter: disnake.ApplicationCommandInteraction,
        query: str
    ):
        """
        Ask questions to Wolfram Alpha

        Parameters
        ----------
        query: Query for Wolfram Alpha
        """

        await inter.response.defer()
        data, status = await utils.rest(
            f"http://api.wolframalpha.com/v1/simple?appid={self.bot.get_api_key('wolframalpha')}&layout=labelbar&ip=None&units=metric&background=2F3136&foreground=white&i={utils.escape_url(query)}",
            returns=('raw', 'status')
        )

        if status != 200:
            err = data.decode('utf-8')
            if not err:
                err = '[unknown error]'

            if status == 501:
                raise Exception('WolframAlpha could not parse the query', err)
            raise Exception(f'WolframAlpha returned an error status {status}', err)

        if len(data) == 0:
            raise Exception('WolframAlpha did not return any data.')

        data = BytesIO(data)
        file = disnake.File(data, 'wolfram.png')
        await inter.send(file=file)


def setup(bot: lynn.Bot):
    bot.add_cog(WolframAlphaCommand(bot))
