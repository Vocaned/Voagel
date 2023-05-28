import re

import disnake
from disnake.ext import commands
from voagel.main import Bot


class OCRCommand(commands.Cog):
    """OCR"""

    def __init__(self, bot: Bot):
        self.bot = bot

    async def do_ocr(self, engine: int, link: str, lang=None) -> dict:
        data={'url': link, 'OCREngine': engine}
        if lang:
            data['language'] = lang
        req = await self.bot.session.post('https://api.ocr.space/parse/image', data=data, headers={'apikey': self.bot.get_api_key('ocrspace')})
        return await req.json()

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

    @commands.message_command(name='Auto OCR')
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
            link = link.group()

        await inter.response.defer()
        res = await self.do_ocr(2, link)
        if not res:
            raise Exception('Did not get a response from API.')
        if res['OCRExitCode'] != 1:
            raise Exception(res['ErrorMessage'])
        else:
            await inter.send(f"```{res['ParsedResults'][0]['ParsedText']} ```")

    @commands.slash_command(name='ocr')
    async def ocr_v2(self,
        inter: disnake.ApplicationCommandInteraction,
        language: str = commands.Param(None, choices=latin_choices), # type: ignore # TODO: fix typing
        attachment: disnake.Attachment | None = None,
        link: str | None = None
    ):
        """
        OCR.space V2 engine. Latin characters only. Max 5000x5000px!

        Parameters
        ----------
        language: Manual language selection
        link: Link to image
        attachment: Image
        """
        if language:
            language = self.lang_map[language]

        if attachment:
            if link:
                raise Exception('Both attachment and link provided. Please only enter one')
            link = attachment.url

        if not link:
            raise Exception('No link or attachment provided')

        await inter.response.defer()
        res = await self.do_ocr(2, link, language)
        if not res:
            raise Exception('Did not get a response from API.')
        if res['OCRExitCode'] != 1:
            raise Exception(res['ErrorMessage'])
        else:
            await inter.send(f"```{res['ParsedResults'][0]['ParsedText']} ```")

    @commands.slash_command(name='ocrv3')
    async def ocr_v3(self,
        inter: disnake.ApplicationCommandInteraction,
        language: str = commands.Param(None, choices=all_choices), # type: ignore # TODO: fix typing
        attachment: disnake.Attachment | None = None,
        link: str | None = None
    ):
        """
        OCR.space V3 engine. Good Asian script support. Max 1000x1000px!

        Parameters
        ----------
        language: Manual language selection
        link: Link to image
        attachment: Image
        """
        if language:
            language = self.lang_map[language]

        if attachment:
            if link:
                raise Exception('Both attachment and link provided. Please only enter one')
            link = attachment.url

        if not link:
            raise Exception('No link or attachment provided')

        await inter.response.defer()
        res = await self.do_ocr(3, link, language)
        if not res:
            raise Exception('Did not get a response from API.')
        if res['OCRExitCode'] != 1:
            raise Exception(res['ErrorMessage'])
        else:
            await inter.send(f"```{res['ParsedResults'][0]['ParsedText']} ```")


def setup(bot: Bot):
    bot.add_cog(OCRCommand(bot))
