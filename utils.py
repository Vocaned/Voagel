import typing
import urllib
import aiohttp
import asyncio
import os
import logging

class RestOptions:
    def __init__(self, method='GET', headers=None, data=None, auth=None, returns: typing.Union[str, typing.Tuple[str]] = 'json') -> None:
        self.method = method
        self.headers = headers
        self.data = data
        self.auth = auth
        self.returns = returns

async def rest(url: str, opts: RestOptions = RestOptions()) -> typing.Union[object, typing.List[object]]:
    async with aiohttp.ClientSession() as s:
        async with s.request(opts.method, url, headers=opts.headers, data=opts.data, auth=opts.auth) as r:
            temp = []

            if isinstance(opts.returns, str):
                opts.returns = (opts.returns, )

            for out in opts.returns:
                if out == 'json':
                    try:
                        j = await r.json()
                    except aiohttp.ContentTypeError:
                        j = None
                    finally:
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

async def eight_mb(tmpdir: str, fp: str) -> str:
    size = os.path.getsize(fp)

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
        fp, bytes2human(size), bytes2human(maxsize), tolerance, bytes2human(target_video_bitrate / 8))
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

async def check_output(args: typing.List[str], timeout: int = 30, raise_on_error: bool = False):
    proc = await asyncio.wait_for(subprocess(args[0], *args[1:], stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT), timeout)
    out = await proc.stdout.read()
    out = out.decode('utf-8')

    if raise_on_error and proc.returncode != 0:
        raise Exception(f'Shell process for `{args[0]}` exited with status `{proc.returncode}`')
    return out
