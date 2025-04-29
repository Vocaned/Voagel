import re
import base64
import aiohttp
from io import BytesIO

import discord
from discord.ext import commands
from discord import app_commands, ui
from voagel.main import Bot, EMBED_COLOR
from voagel.utils import UserException

class WhisperCommand(commands.Cog):
    """Whisper"""

    def __init__(self, bot: Bot):
        self.bot = bot
        self.bot.tree.add_command(app_commands.ContextMenu(
            name='Transcribe',
            callback=self.auto_transcribe
        ))
        self.bot.tree.add_command(app_commands.ContextMenu(
            name='Transcribe (Translate)',
            callback=self.auto_translate
        ))

    class OutputView(ui.LayoutView):
        def __init__(self, res: str):
            super().__init__()
            container = ui.Container()
            container.add_item(ui.TextDisplay(res))
            self.add_item(container)


    async def do_transcribe(self, audio: bytes, content_type: str, task: str = 'transcribe') -> str:
        data = aiohttp.FormData()
        data.add_field('audio_file',
                       audio,
                       content_type=content_type)
        req = await self.bot.session.post(f'{self.bot.config["apis"]["whisper"]}/asr?encode=true&task={task}&vad_filter=true&output=txt', data=data)

        if req.status != 200:
            raise Exception(f'Failed to transcribe file: {req.status}')

        return await req.text(encoding='utf-8')

    async def auto_translate(self, inter: discord.Interaction, message: discord.Message):
        """
        Transcribe
        """
        if len(message.attachments) > 0:
            link = message.attachments[0].url
        else:
            link = re.search(r'https?://\S+', message.content)
            if not link:
                raise UserException('Could not find audio in the specified message.')
            link = link.group()

        await inter.response.defer()
        req = await self.bot.session.get(link)
        audio = await req.read()
        res = await self.do_transcribe(audio, req.content_type, task='translate')

        view = self.OutputView(res)
        await inter.followup.send(view=view)

    async def auto_transcribe(self, inter: discord.Interaction, message: discord.Message):
        """
        Transcribe
        """
        if len(message.attachments) > 0:
            link = message.attachments[0].url
        else:
            link = re.search(r'https?://\S+', message.content)
            if not link:
                raise UserException('Could not find audio in the specified message.')
            link = link.group()

        await inter.response.defer()
        req = await self.bot.session.get(link)
        audio = await req.read()
        res = await self.do_transcribe(audio, req.content_type)

        view = self.OutputView(res)
        await inter.followup.send(view=view)

    @app_commands.command(name='transcribe')
    async def transcribe(self,
        inter: discord.Interaction,
        attachment: discord.Attachment | None = None,
        link: str | None = None,
        translate: bool = False
    ):
        """
        Transcribe

        Parameters
        ----------
        link: Link to audio
        attachment: Audio
        translate: Should the audio be translated to English?
        """

        if attachment:
            if link:
                raise UserException('Both attachment and link provided. Please only enter one')
            link = attachment.url

        if not link:
            raise UserException('No link or attachment provided')

        await inter.response.defer()
        req = await self.bot.session.get(link)
        audio = await req.read()
        res = await self.do_transcribe(audio, req.content_type, task='translate' if translate else 'transcribe')

        view = self.OutputView(res)
        await inter.followup.send(view=view)

async def setup(bot: Bot):
    await bot.add_cog(WhisperCommand(bot))
