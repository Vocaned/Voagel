import re

import disnake
import lynn
import utils
from disnake.ext import commands


class OCRCommand(commands.Cog):
    """OCR"""

    def __init__(self, bot: lynn.Bot):
        self.bot = bot

    async def do_ocr(self, engine: int, link: str, lang=None) -> dict:
        data={'url': link, 'OCREngine': engine}
        if lang:
            data['language'] = lang
        return await utils.rest('https://api.ocr.space/parse/image',
            method='POST', headers={'apikey': self.bot.get_api_key('ocrspace')}, data=data
        )

    all_choices = [
        'English', 'Arabic', 'Bulgarian', 'Chinese (Simplified)', 'Chinese (Traditional)', 'Croatian',
        'Czech', 'Danish', 'Dutch', 'Finnish', 'French', 'German', 'Greek', 'Hungarian', 'Korean',
        'Italian', 'Japanese', 'Polish', 'Portuguese', 'Russian', 'Slovenian', 'Spanish', 'Swedish', 'Turkish'
    ]
    latin_choices = ['English', 'Croatian', 'Czech', 'Danish', 'Dutch', 'Finnish', 'French', 'German', 'Hungarian', 'Italian', 'Polish', 'Portuguese', 'Slovenian', 'Spanish', 'Swedish', 'Turkish']
    lang_map = {
        'Arabic': 'ara',
        'Bulgarian': 'bul',
        'Chinese (Simplified)': 'chs',
        'Chinese (Traditional)': 'cht',
        'Croatian' : 'hrv',
        'Czech' : 'cze',
        'Danish' : 'dan',
        'Dutch' : 'dut',
        'English' : 'eng',
        'Finnish' : 'fin',
        'French' : 'fre',
        'German' : 'ger',
        'Greek' : 'gre',
        'Hungarian' : 'hun',
        'Korean' : 'kor',
        'Italian' : 'ita',
        'Japanese' : 'jpn',
        'Polish' : 'pol',
        'Portuguese' : 'por',
        'Russian' : 'rus',
        'Slovenian' : 'slv',
        'Spanish' : 'spa',
        'Swedish' : 'swe',
        'Turkish' : 'tur',
    }

    @commands.message_command(name='Auto OCR', guild_ids=[702953546106273852])
    async def auto_ocr(self, inter: disnake.MessageCommandInteraction):
        """
        OCR.space V2 engine. Latin characters only. Max 5000x5000px!
        """
        if len(inter.target.attachments) > 0:
            link = inter.target.attachments[0].url
        else:
            link = re.search(r'https?://\S+', inter.target.content)
            if not link:
                raise Exception('Could not find an image in the specified message.')

        await inter.response.defer()
        res = await self.do_ocr(2, link)
        if not res:
            raise Exception('Did not get a response from API.')
        if res['OCRExitCode'] != 1:
            raise Exception(res['ErrorMessage'])
        else:
            await inter.send(f"```{res['ParsedResults'][0]['ParsedText']} ```")

    @commands.slash_command(name='ocr', guild_ids=[702953546106273852])
    async def ocr_v2(self,
        inter: disnake.ApplicationCommandInteraction,
        link: str, # TODO: Make optional once image uploading on slash commands becomes available
        language: str = commands.Param(None, choices=latin_choices)
    ):
        """
        OCR.space V2 engine. Latin characters only. Max 5000x5000px!

        Parameters
        ----------
        link: Link to image
        language: Manual language selection
        """
        if language:
            language = self.lang_map[language]

        await inter.response.defer()
        res = await self.do_ocr(2, link, language)
        if not res:
            raise Exception('Did not get a response from API.')
        if res['OCRExitCode'] != 1:
            raise Exception(res['ErrorMessage'])
        else:
            await inter.send(f"```{res['ParsedResults'][0]['ParsedText']} ```")

    @commands.slash_command(name='ocrv3', guild_ids=[702953546106273852])
    async def ocr_v3(self,
        inter: disnake.ApplicationCommandInteraction,
        link: str, # TODO: Make optional once image uploading on slash commands becomes available
        language: str = commands.Param(choices=all_choices)
    ):
        """
        OCR.space V3 engine. Good Asian script support. Max 1000x1000px!

        Parameters
        ----------
        link: Link to image
        language: Manual language selection
        """
        if language:
            language = self.lang_map[language]

        await inter.response.defer()
        res = await self.do_ocr(3, link, language)
        if not res:
            raise Exception('Did not get a response from API.')
        if res['OCRExitCode'] != 1:
            raise Exception(res['ErrorMessage'])
        else:
            await inter.send(f"```{res['ParsedResults'][0]['ParsedText']} ```")


def setup(bot: lynn.Bot):
    bot.add_cog(OCRCommand(bot))
