import disnake
from disnake.ext import commands
from pycountry import languages

from voagel.main import Bot, EMBED_COLOR
from voagel.utils import escape_url
from voagel.autocompleters import language_autocomplete

class TranslateCommand(commands.Cog):
    """Translate"""

    def __init__(self, bot: Bot):
        self.bot = bot

    async def do_translate(self, fromlang: str, tolang: str, query: str):
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36'}
        req = await self.bot.session.get(
            f'https://translate.googleapis.com/translate_a/single?client=gtx&dt=t&ie=UTF-8&oe=UTF-8&sl={fromlang}&tl={tolang}&q={escape_url(query)}',
            headers=headers
        )
        data = await req.json()
        if not data:
            raise commands.CommandError('Did not get a response from Google. Probably an invalid language.')
        return data

    @commands.message_command(name='Auto Translate')
    async def auto_translate(self, inter: disnake.MessageCommandInteraction):
        query = inter.target.content
        if not query:
            raise Exception('No text found in message.')
        data = await self.do_translate('auto', 'eng', query)

        inlang = languages.get(alpha_2=data[2])
        if not inlang:
            inlang = data[2]
        else:
            inlang = inlang.name

        confidence = None
        if data[6] and data[6] != 1:
            confidence = f'(confidence: {round(data[6]*100)}%)'

        outtext = []
        if isinstance(data[0], list):
            for block in data[0]:
                outtext.append(block[0])
        else:
            outtext.append(data[0][0][0])

        embed = disnake.Embed(color=EMBED_COLOR)
        if confidence:
            embed.set_footer(text=confidence)
        embed.add_field(f'From `{inlang}`', query, inline=False)
        embed.add_field('To `English`', ' '.join(outtext), inline=False)
        embed.set_footer(text='Google Translate', icon_url=self.bot.get_asset('google_translate.png'))
        await inter.send(embed=embed)

    @commands.slash_command()
    async def translate(self,
        inter: disnake.ApplicationCommandInteraction,
        query: str,
        _from: str = commands.Param('auto', name='from', autocomplete=language_autocomplete),
        to: str = commands.Param('eng', autocomplete=language_autocomplete)
    ):
        """
        Translate stuff using Google Translate. Defaults to Auto-Detect -> English

        Parameters
        ----------
        query: Text to translate
        _from: Language to translate from
        to: Language to translate to
        """

        fromlang = _from
        tolang = to

        if fromlang != 'auto':
            try:
                fromlang = languages.lookup(fromlang)
                fromlang = fromlang.alpha_2
            except Exception as e:
                raise commands.BadArgument(f'No language found by `{_from}`') from e

        try:
            tolang = languages.lookup(tolang)
            outlang = tolang.name
            tolang = tolang.alpha_2
        except Exception as e:
            raise commands.BadArgument(f'No language found by `{to}`') from e

        # En is a language with like 200 native speakers.. English is more important
        if fromlang == 'en':
            fromlang = 'eng'
        if tolang == 'en':
            tolang = 'eng'

        await inter.response.defer()
        data = await self.do_translate(fromlang, tolang, query)

        inlang = languages.get(alpha_2=data[2])
        if not inlang:
            inlang = data[2]
        else:
            inlang = inlang.name

        confidence = ''
        if data[6] and data[6] != 1:
            confidence = f'(confidence: {round(data[6]*100)}%)'

        outtext = []
        if isinstance(data[0], list):
            for block in data[0]:
                outtext.append(block[0])
        else:
            outtext.append(data[0][0][0])

        embed = disnake.Embed(description=confidence, color=EMBED_COLOR)
        embed.add_field(f'From `{inlang}`', query, inline=False)
        embed.add_field(f'To `{outlang}`', ' '.join(outtext), inline=False)
        embed.set_footer(text='Google Translate', icon_url=self.bot.get_asset('google_translate.png'))
        await inter.send(embed=embed)

def setup(bot: Bot):
    bot.add_cog(TranslateCommand(bot))
