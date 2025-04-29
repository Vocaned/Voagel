import discord
from discord.ext import commands
from discord import app_commands, ui

from voagel.main import Bot, EMBED_COLOR
from voagel.utils import UserException

class TranslateCommand(commands.Cog):
    """Translate"""

    class OutputView(ui.LayoutView):
        def __init__(self, fromlang: str, fromtext: str, tolang: str, totext: str, confidence: float | None = None):
            super().__init__()
            container = ui.Container()
            container.add_item(ui.TextDisplay(f'### From {fromlang}\n{fromtext}'))
            container.add_item(ui.Separator())
            container.add_item(ui.TextDisplay(f'### To {tolang}\n{totext}' + (f'\n-# confidence: {round(confidence*100, 2)}%' if confidence else '')))
            self.add_item(container)

    def __init__(self, bot: Bot):
        self.bot = bot
        self.gcp_languages: dict[str, str] = {}
        self.bot.tree.add_command(app_commands.ContextMenu(
            name='Auto Translate',
            callback=self.auto_translate
        ))

    async def get_languages(self) -> dict[str, str]:
        if not self.gcp_languages:
            params = {
                'target': 'en',
                'key': self.bot.get_api_key('gcp_translate')
            }
            req = await self.bot.session.get(f'https://translation.googleapis.com/language/translate/v2/languages', params=params)
            data = await req.json()

            if 'error' in data:
                raise Exception('Google Translate returned an error: ' + str(data['error']))

            for l in data['data']['languages']:
                self.gcp_languages[l['name']] = l['language']

        return self.gcp_languages

    async def do_translate(self, fromlang: str | None, tolang: str, query: str):
        params = {
            'q': [query],
            'target': tolang,
            'key': self.bot.get_api_key('gcp_translate')
        }

        if fromlang:
            params['source'] = fromlang

        req = await self.bot.session.post(f'https://translation.googleapis.com/language/translate/v2', params=params)
        data = await req.json()

        if 'error' in data:
            raise Exception('Google Translate returned an error: ' + str(data['error']))

        return data['data']

    async def do_ocr_translate(self, fromlang: str | None, tolang: str, img: bytes):
        ocr_cog = self.bot.get_cog('OcrCommand')
        if not ocr_cog:
            raise commands.errors.DisabledCommand()

        ocr_res: dict = ocr_cog.do_ocr(img) # type: ignore
        print(ocr_res)

    async def auto_translate(self, inter: discord.Interaction, message: discord.Message):
        await inter.response.defer()

        query = message.content
        if not query:
            raise UserException('No text found in message.')
        data = (await self.do_translate(None, 'en', query))['translations'][0]

        fromlang = 'Unknown'
        if 'detectedSourceLanguage' in data:
            fromcode = fromlang = data['detectedSourceLanguage']
            for lang, code in (await self.get_languages()).items():
                if fromcode == code:
                    fromlang = lang

        view = self.OutputView(fromlang, query, 'English', data['translatedText'], data['confidence'] if 'confidence' in data and data['confidence'] < 1.0 else None)
        await inter.followup.send(view=view)

    @app_commands.rename(_from='from')
    @app_commands.command()
    async def translate(self,
        inter: discord.Interaction,
        query: str,
        _from: str = 'auto',
        to: str = 'English'
    ):
        """
        Translate stuff using Google Translate. Defaults to Auto-Detect -> English

        Parameters
        ----------
        query: Text to translate
        _from: Language to translate from
        to: Language to translate to
        """

        await inter.response.defer()

        fromlang = _from if _from != 'auto' else None
        tolang = to
        fromcode = None
        tocode = None

        if fromlang:
            fromcode = (await self.get_languages()).get(fromlang)
            if not fromcode:
                raise commands.BadArgument(f'No language found by `{fromlang}`')

        tocode = (await self.get_languages()).get(tolang)
        if not tocode:
            raise commands.BadArgument(f'No language found by `{to}`')

        data = (await self.do_translate(fromcode, tocode, query))['translations'][0]

        if 'detectedSourceLanguage' in data:
            fromcode = fromlang = data['detectedSourceLanguage']
            for lang, code in (await self.get_languages()).items():
                if fromcode == code:
                    fromlang = lang


        view = self.OutputView(str(fromlang), query, tolang, data['translatedText'], data['confidence'] if 'confidence' in data and data['confidence'] < 1.0 else None)
        print(str(view.to_components()))
        await inter.followup.send(view=view)

    @translate.autocomplete('_from')
    @translate.autocomplete('to')
    async def language_autocomplete(self, _: discord.Interaction, string: str) -> list[app_commands.Choice[str]]:
        """Autocomplete languages"""

        out = []

        for lang, __ in (await self.get_languages()).items():
            try:
                if string.lower() in lang.lower():
                    out.append(lang)
            except Exception:
                pass

        return [
                app_commands.Choice(name=x, value=x) for x in out[:25]
        ]


async def setup(bot: Bot):
    await bot.add_cog(TranslateCommand(bot))
