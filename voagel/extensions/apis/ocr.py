import re
import base64
from io import BytesIO

import disnake
from disnake.ext import commands
from voagel.main import Bot, EMBED_COLOR


class OCRCommand(commands.Cog):
    """OCR"""

    def __init__(self, bot: Bot):
        self.bot = bot

    async def do_ocr(self, img: bytes) -> dict:
        data={'requests': [{
            'features': [{'type': 'TEXT_DETECTION'}],
            'image': {'content': base64.b64encode(img).decode()}
        }]}
        req = await self.bot.session.post(f'https://content-vision.googleapis.com/v1/images:annotate?key={self.bot.get_api_key("gcp_ocr")}', json=data)
        j = await req.json()
        print(j)

        if not j or not j['responses']:
            raise Exception('Did not get a response from API.')

        return j['responses'][0]

    @commands.message_command(name='Auto OCR')
    async def auto_ocr(self, inter: disnake.MessageCommandInteraction):
        """
        OCR.
        """
        if len(inter.target.attachments) > 0:
            link = inter.target.attachments[0].url
        else:
            link = re.search(r'https?://\S+', inter.target.content)
            if not link:
                raise Exception('Could not find an image in the specified message.')
            link = link.group()

        await inter.response.defer()
        imgres = await self.bot.session.get(link)
        img = await imgres.read()
        res = await self.do_ocr(img)
        if not res['fullTextAnnotation']:
            raise Exception('Did not detect text.')
        else:
            embed = disnake.Embed(color=EMBED_COLOR)
            embed.set_footer(text='Google Cloud Vision', icon_url=self.bot.get_asset('gcp.png'))
            embed.description = f'```\n{res["fullTextAnnotation"]["text"]}\n```'
            embed.set_thumbnail(file=disnake.File(fp=BytesIO(img), filename=link.split('/')[-1].split('?')[0]))
            await inter.send(embed=embed)

    @commands.slash_command(name='ocr')
    async def ocr(self,
        inter: disnake.ApplicationCommandInteraction,
        attachment: disnake.Attachment | None = None,
        link: str | None = None
    ):
        """
        OCR.

        Parameters
        ----------
        link: Link to image
        attachment: Image
        """

        if attachment:
            if link:
                raise Exception('Both attachment and link provided. Please only enter one')
            link = attachment.url

        if not link:
            raise Exception('No link or attachment provided')

        await inter.response.defer()
        imgres = await self.bot.session.get(link)
        img = await imgres.read()
        res = await self.do_ocr(img)
        if not res['fullTextAnnotation']:
            raise Exception('Did not detect text.')
        else:
            embed = disnake.Embed(color=EMBED_COLOR)
            embed.set_footer(text='Google Cloud Vision', icon_url=self.bot.get_asset('gcp.png'))
            embed.description = f'```\n{res["fullTextAnnotation"]["text"]}\n```'
            embed.set_thumbnail(file=disnake.File(fp=BytesIO(img), filename=link.split('/')[-1].split('?')[0]))
            await inter.send(embed=embed)

def setup(bot: Bot):
    bot.add_cog(OCRCommand(bot))
