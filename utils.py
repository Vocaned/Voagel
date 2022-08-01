import typing
import urllib
import aiohttp
import asyncio
import os
import logging
import html.parser
from datetime import timedelta

async def rest(url: str, method='GET', headers=None, data=None, auth=None, returns: typing.Union[str, typing.Tuple[str]] = 'json') -> typing.Union[object, typing.List[object]]:
    async with aiohttp.ClientSession() as s:
        if not headers:
            headers = {}
        if 'User-Agent' not in headers:
            headers['User-Agent'] = 'Lynn5 (Discord Bot) https://github.com/Fam0r/Lynn5'
        async with s.request(method, url, headers=headers, data=data, auth=auth) as r:
            temp = []

            if isinstance(returns, str):
                returns = (returns, )

            for out in returns:
                if out == 'json':
                    j = None
                    try:
                        j = await r.json()
                    except aiohttp.ContentTypeError:
                        pass
                    temp.append(j)
                elif out == 'status':
                    temp.append(r.status)
                elif out == 'raw':
                    temp.append(await r.read())
                elif out == 'text':
                    temp.append(await r.text())
                elif out == 'object':
                    temp.append(r)
                else:
                    raise NotImplementedError('Invalid rest return type ' + out)
            if not temp:
                print(await r.read())
                raise NotImplementedError('REST didn\'t return any data.')
            if len(temp) == 1:
                return temp[0]
            return temp

def escape_url(url: str) -> str:
    return urllib.parse.quote(url)

async def re_encode(fp: str) -> None:
    if not os.path.exists(fp):
        raise Exception("File passed to Re-Encode doesn't exist")

    out = await check_output(['ffmpeg', '-y', '-i', '-c:a', 'copy', fp, f'2{fp}'])
    if not os.path.exists(f'2{fp}'):
        raise Exception('Video encoding failed: \n'+out)
    os.replace(f'2{fp}', fp)

async def eight_mb(tmpdir: str, fp: str) -> str:
    size = os.path.getsize(fp)
    origsize = size

    maxsize = 8388119
    audio_bitrate=128000

    if not os.path.exists(fp):
        raise Exception("File passed to 8MB doesn't exist!")
    duration = await check_output(["ffprobe", "-v", "panic", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", fp])
    duration = float(duration)
    target_total_bitrate = (maxsize * 8) / duration
    for tolerance in [.98, .95, .90, .75, .5]:
        target_video_bitrate = (target_total_bitrate - audio_bitrate) * tolerance
        assert target_video_bitrate > 0
        logging.info("trying to force %s (%s) under %s with tolerance %s. trying %s/s",
        fp, bytes2human(origsize), bytes2human(maxsize), tolerance, bytes2human(target_video_bitrate / 8))
        pass1log = tmpdir + "/pass1.log"
        outfile = tmpdir + "/out.mp4"
        await check_output(['ffmpeg', '-y', '-i', fp, '-c:v', 'h264', '-b:v', str(target_video_bitrate), '-pass', '1',
                        '-f', 'mp4', '-passlogfile', pass1log, '/dev/null'])
        await check_output(['ffmpeg', '-i', fp, '-c:v', 'h264', '-b:v', str(target_video_bitrate), '-pass', '2',
                        '-passlogfile', pass1log, '-c:a', 'aac', '-b:a', str(audio_bitrate), "-f", "mp4", "-movflags",
                        "+faststart", outfile])
        if (size := os.path.getsize(outfile)) < maxsize:
            logging.info("successfully created %s video!", bytes2human(size))
            return outfile
        logging.info("tolerance %s failed. output is %s", tolerance, bytes2human(size))
        if os.path.exists(pass1log):
            os.remove(pass1log)
        if os.path.exists(outfile):
            os.remove(outfile)
    raise Exception(f"Unable to fit {fp} within {bytes2human(maxsize)}")

def bytes2human(n: int) -> str:
    symbols = ('KiB', 'MiB', 'GiB', 'TiB', 'PiB')
    prefix = {}
    for i, s in enumerate(symbols):
        prefix[s] = 1 << (i + 1) * 10
    for s in reversed(symbols):
        if n >= prefix[s]:
            value = float(n) / prefix[s]
            return f'{value:.1f}{s}'
    return f'{n}B'

async def subprocess(*args, **kwargs):
    try:
        proc = await asyncio.create_subprocess_exec(*args, **kwargs)
        await proc.wait()
        return proc
    except asyncio.CancelledError:
        proc.terminate()
        raise

async def check_output(args: typing.List[str], timeout: int = 120, raise_on_error: bool = False):
    proc = await asyncio.wait_for(subprocess(args[0], *args[1:], stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT), timeout)
    out = await proc.stdout.read()
    out = out.decode('utf-8')

    if raise_on_error and proc.returncode != 0:
        raise Exception(f'Shell process for `{args[0]}` exited with status `{proc.returncode}`')
    return out

class OpenGraphParser(html.parser.HTMLParser):
    def __init__(self, *, convert_charrefs: bool = ...) -> None:
        super().__init__(convert_charrefs=convert_charrefs)
        self.tags = {}

    def handle_starttag(self, tag, attrs):
        if tag != 'meta':
            return
        k = v = None
        for attr in attrs:
            if attr[0].lower() == 'name' or attr[0].lower() == 'property' and attr[1].startswith('og:'):
                k = attr[1]
            if attr[0].lower() == 'content':
                v = attr[1]
        if k and v:
            self.tags[k] = v

def timedelta_format(delta: timedelta):
    ret = []
    num_years = int(delta.days / 365)
    if num_years > 0:
        delta -= timedelta(days=num_years * 365)
        ret.append(f'{num_years} years')

    if delta.days > 0:
        ret.append(f'{delta.days} days')

    num_hours = int(delta.seconds / 3600)
    if num_hours > 0:
        delta -= timedelta(hours=num_hours)
        ret.append(f'{num_hours} hours')

    num_minutes = int(delta.seconds / 60)
    if num_minutes > 0:
        ret.append(f'{num_minutes} minutes')

    if not ret:
        ret.append('Less than a minute')
    return ' '.join(ret)
