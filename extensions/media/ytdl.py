import logging
import os
import tempfile

import disnake
import lynn
import utils
from disnake.ext import commands

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

    @commands.slash_command(name='dl', guild_ids=[702953546106273852])
    async def ytdl(self,
        inter: disnake.ApplicationCommandInteraction,
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
            'quiet': True,
            'merge_output_format': 'mp4',
            'format': 'bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4] / bv*+ba/b' # Download the best mp4 video available, or the best video if no mp4 available
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            # TODO: Download in a separate thread and async
            try:
                ydl_opts['outtmpl'] = tmpdir + '/%(id)s.%(ext)s'
                with yt_dl.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(link, download=False)
                    if 'is_live' in info and info['is_live']:
                        raise yt_dl.DownloadError('Cannot download a livestream')
                    if 'filesize' in info and info['filesize']:
                        if info['filesize'] > 100000000:
                            await inter.delete_original_message()
                            raise yt_dl.DownloadError(f'File is too large! ({utils.bytes2human(info["filesize"])})')
                    elif 'filesize_approx' in info and info['filesize_approx']:
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
                if size > 26214400: # 25 MiB
                    if size > 104857600: # 100 MiB
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
                        await inter.edit_original_message(f'Compressing {utils.bytes2human(size)} to 8MiB...')
                        await webhook.edit('Compressing video...', view=view)
                        try:
                            fp = await utils.eight_mb(tmpdir, fp)
                        except TimeoutError as e:
                            await webhook.edit('Process timed out. Donate so the bot owner can get a proper server to host the bot on.', view=view)
                            raise e
                    else:
                        await webhook.edit('Cancelled.', view=view)
                        await inter.delete_original_message()
                        return

                if link.split('//', 1)[-1].lstrip('www.').startswith('tiktok.com'):
                    # Tiktok downloads don't work on Discord by default
                    await inter.edit_original_message('Re-encoding video to fix TikTok download..')
                    await utils.re_encode(fp)

                file = disnake.File(fp, filename=info['id'] + '.' + info['ext'], description='Source: ' + link)
                await inter.edit_original_message('', file=file)
                if webhook is not None:
                    await webhook.edit('Compressed.')
            except FileNotFoundError as e:
                raise yt_dl.DownloadError('Could not download video.') from e

def setup(bot: lynn.Bot):
    bot.add_cog(YtdlCommand(bot))
