import os
import tempfile

import disnake
from disnake.ext import commands

from voagel.main import Bot
from voagel.utils import bytes2human, re_encode

try:
    import yt_dlp as yt_dl # type: ignore
except ImportError:
    import youtube_dl as yt_dl # type: ignore

class YtdlCommand(commands.Cog):
    """Youtube-DL command."""

    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.slash_command(name='dl')
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
                    if not info:
                        raise yt_dl.DownloadError(f'Could not get file info')

                    if 'is_live' in info and info['is_live']:
                        raise yt_dl.DownloadError('Cannot download a livestream')
                    if 'filesize' in info and info['filesize']:
                        if info['filesize'] > 100000000:
                            await inter.delete_original_message()
                            raise yt_dl.DownloadError(f'File is too large! ({bytes2human(info["filesize"])})')
                    elif 'filesize_approx' in info and info['filesize_approx']:
                        if info['filesize_approx'] > 100000000:
                            await inter.delete_original_message()
                            raise yt_dl.DownloadError(f'File is too large! ({bytes2human(info["filesize_approx"])})')
                    else:
                        await inter.edit_original_message('Could not calculate estimate of file size. Video could not be downloaded.')
                        await inter.delete_original_message(delay=20)
                        return

                    ydl.download(link)

                fp = tmpdir + '/' + info['id'] + '.' + info['ext']
                size = os.path.getsize(fp)
                if size > 26214400: # 25 MiB
                    raise yt_dl.DownloadError(f'File is too large! ({bytes2human(size)})')

                if link.split('//', 1)[-1].lstrip('www.').startswith('tiktok.com'):
                    # Tiktok downloads don't work on Discord by default
                    await inter.edit_original_message('Re-encoding video to fix TikTok download..')
                    await re_encode(fp)

                file = disnake.File(fp, filename=info['id'] + '.' + info['ext'], description='Source: ' + link)
                await inter.edit_original_message('', file=file)
            except FileNotFoundError as e:
                raise yt_dl.DownloadError('Could not download video.') from e

def setup(bot: Bot):
    bot.add_cog(YtdlCommand(bot))
