from typing import List

import disnake
import lynn
import utils
from disnake.ext import commands
from pycountry import languages


async def autocomplete(inter, string: str) -> List[str]:
    langs = []

    for lang in languages:
        try:
            if string.lower() in lang.name.lower() and lang.alpha_2:
                langs.append(lang.name)
        except Exception:
            pass

    return langs[:25]

class TranslateCommand(commands.Cog):
    """Translate"""

    def __init__(self, bot: lynn.Bot):
        self.bot = bot

    async def do_translate(self, fromlang: str, tolang: str, query: str):
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36'}
        data = await utils.rest(
            f'https://translate.googleapis.com/translate_a/single?client=gtx&dt=t&ie=UTF-8&oe=UTF-8&sl={fromlang}&tl={tolang}&q={utils.escape_url(query)}',
            headers=headers
        )
        if not data:
            raise commands.CommandError('Did not get a response from Google. Probably an invalid language.')
        return data

    @commands.message_command(name='Auto Translate', guild_ids=[702953546106273852])
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

        confidence = ''
        if data[6] and data[6] != 1:
            confidence = f'(confidence: {round(data[6]*100)}%)'

        embed = disnake.Embed(title='Google Translate', description=confidence, color=lynn.EMBED_COLOR)
        embed.add_field(f'From `{inlang}`', query, inline=False)
        embed.add_field('To `English`', data[0][0][0], inline=False)
        await inter.send(embed=embed)

    @commands.slash_command(guild_ids=[702953546106273852])
    async def translate(self,
        inter: disnake.ApplicationCommandInteraction,
        query: str,
        _from: str = commands.Param('auto', name='from', autocomplete=autocomplete),
        to: str = commands.Param('eng', autocomplete=autocomplete)
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

        embed = disnake.Embed(title='Google Translate', description=confidence, color=lynn.EMBED_COLOR)
        embed.add_field(f'From `{inlang}`', query, inline=False)
        embed.add_field(f'To `{outlang}`', data[0][0][0], inline=False)
        await inter.send(embed=embed)

def setup(bot: lynn.Bot):
    bot.add_cog(TranslateCommand(bot))
