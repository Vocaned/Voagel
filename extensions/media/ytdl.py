import tempfile
import os
from disnake.ext import commands
import disnake
import lynn
import utils
import logging


try:
    import yt_dlp as yt_dl
except ImportError:
    import youtube_dl as yt_dl

class CompressQuestion(disnake.ui.View):
    def __init__(self):
        self.response = None
        super().__init__(timeout=20)

    @disnake.ui.button(label="Cancel", style=disnake.ButtonStyle.red)
    async def cancel(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        self.response = 'cancel'
        self.stop()

    @disnake.ui.button(label="Compress", style=disnake.ButtonStyle.green)
    async def compress(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        self.response = 'compress'
        self.stop()

    # Upload to website (12h temp file)


class YtdlCommand(commands.Cog):
    """Youtube-DL command."""

    def __init__(self, bot: lynn.Bot):
        self.bot = bot

    @commands.slash_command(name='DL', guild_ids=[702953546106273852])
    async def ytdl(self,
        inter: disnake.GuildCommandInteraction,
        link: str
    ):
        """Download any video on the internet

        Parameters
        ----------
        link: Link to the video
        """
        await inter.response.send_message('Downloading...')

        ydl_opts = {
            'geo_bypass': True,
            'no_color': True,
            'restrictfilenames': True,
            'quiet': True
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            # TODO: Download in a separate thread and async
            try:
                ydl_opts['outtmpl'] = tmpdir + '/%(id)s.%(ext)s'
                with yt_dl.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(link, download=False)
                    if 'is_live' in info and info['is_live']:
                        raise yt_dl.DownloadError('Cannot download a livestream')
                    if 'filesize' in info:
                        if info['filesize'] > 100000000:
                            await inter.delete_original_message()
                            raise yt_dl.DownloadError(f'File is too large! ({utils.bytes2human(info["filesize"])})')
                    elif 'filesize_approx' in info:
                        if info['filesize_approx'] > 100000000:
                            await inter.delete_original_message()
                            raise yt_dl.DownloadError(f'File is too large! ({utils.bytes2human(info["filesize_approx"])})')
                    else:
                        await inter.edit_original_message('Could not calculate estimate of file size. Video could not be downloaded.')
                        await inter.delete_original_message(delay=20)
                        return

                    ydl.download(link)

                fp = tmpdir + '/' + info['id'] + '.' + info['ext']
                size = os.path.getsize(fp)
                webhook = None
                if size > 8000000:
                    if size > 105000000:
                        raise yt_dl.DownloadError(f'File is too large! ({utils.bytes2human(size)})')

                    view = CompressQuestion()
                    webhook = await inter.followup.send(f'File is over 8MB! ({utils.bytes2human(size)})\nDo you want to compress the video to 8MB?', ephemeral=True, view=view)
                    await view.wait()
                    view.clear_items()
                    if view.response is None:
                        await webhook.edit('Prompt timed out.', view=view)
                        await inter.delete_original_message()
                        return
                    elif view.response == 'compress':
                        await webhook.edit('Compressing video...', view=view)
                        fp = await utils.eight_mb(tmpdir, fp)
                    else:
                        await webhook.edit('Cancelled.', view=view)
                        await inter.delete_original_message()
                        return

                file = disnake.File(fp, filename=info['id'] + '.' + info['ext'], description='Source: ' + link)
                await inter.edit_original_message(content='', file=file)
                if webhook != None:
                    await webhook.edit('Compressed.')
            except FileNotFoundError as e:
                raise yt_dl.DownloadError('Could not download video.') from e

def setup(bot: lynn.Bot):
    bot.add_cog(YtdlCommand(bot))
