import typing
import urllib
import aiohttp

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
