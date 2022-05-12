import disnake
import lynn
from disnake.ext import commands
import utils
import json
import base64
from datetime import datetime


class MinecraftCommands(commands.Cog):
    """Minecraft Commands"""

    def __init__(self, bot: lynn.Bot):
        self.bot = bot

    async def get_UUID(self, name: str) -> str:
        status, text = await utils.rest(f'https://api.mojang.com/users/profiles/minecraft/{name}', returns=('status', 'text'))
        if status == 200:
            j = json.loads(text)
            if 'id' in j:
                return j['id']

        status, text = await utils.rest(f'https://api.mojang.com/users/profiles/minecraft/{name}?at=0', returns=('status', 'text'))
        if status == 200:
            j = json.loads(text)
            if 'id' in j:
                return j['id']

        raise Exception('Player not found')

    async def get_skin(self, uuid: str) -> dict:
        j = await utils.rest(f'https://sessionserver.mojang.com/session/minecraft/profile/{uuid}', returns='json')
        try:
            val = j['properties'][0]['value']
        except KeyError:
            raise Exception("Mojang's servers didn't return valid skin data.")

        return json.loads(base64.b64decode(val))

    @commands.slash_command(guild_ids=[702953546106273852])
    async def minecraft(self, inter: disnake.ApplicationCommandInteraction):
        ...

    @minecraft.sub_command()
    async def player(self,
        inter: disnake.ApplicationCommandInteraction,
        username: str
    ):
        """Looks up information about a player

        Parameters
        ----------
        username: Username of the player
        """
        await inter.response.defer()

        uuid = await self.get_UUID(username)
        skin = await self.get_skin(uuid)
        history = await utils.rest(f'https://api.mojang.com/user/profiles/{uuid}/names', returns='json')

        names = []
        user = history[-1]['name']
        for entry in history:
            # Escape special markdown characters
            names.append(entry['name'].replace('*', '\\*').replace('_', '\\_').replace('~', '\\~'))
        names.reverse()
        names[0] += ' **[CURRENT]**'

        embeds = []
        embed = disnake.Embed(title='Minecraft Player', color=lynn.EMBED_COLOR)
        embed.set_author(name=user, icon_url=f'https://crafatar.com/avatars/{uuid}.png')
        embed.add_field('Name History', '\n'.join(names), inline=False)
        embed.set_footer(text=f'UUID: {uuid}', icon_url='https://www.minecraft.net/etc.clientlibs/minecraft/clientlibs/main/resources/favicon-96x96.png')
        embed.timestamp = datetime.now()
        embed.set_image(url=f'https://crafatar.com/renders/body/{uuid}.png')

        try:
            embed.add_field(name='Skin URL', value='[Click me]('+skin['textures']['SKIN']['url']+')')
        except KeyError:
            pass
        embeds.append(embed)

        if 'CAPE' in skin['textures']:
            embed = disnake.Embed(title='Minecraft Cape', color=lynn.EMBED_COLOR)
            embed.set_author(name=user, icon_url=f'https://crafatar.com/avatars/{uuid}.png')
            embed.set_image(url=skin['textures']['CAPE']['url'])
            embeds.append(embed)

        of = await utils.rest(f'http://s.optifine.net/capes/{user}.png', returns='status')
        if of == 200:
            embed = disnake.Embed(title='Optifine Cape', color=lynn.EMBED_COLOR)
            embed.set_author(name=user, icon_url=f'https://crafatar.com/avatars/{uuid}.png')
            embed.set_image(url=f'http://s.optifine.net/capes/{user}.png')
            embeds.append(embed)

        await inter.send(embeds=embeds)

    # TODO: Finish this
    @minecraft.sub_command()
    async def server(self,
        inter: disnake.ApplicationCommandInteraction,
        address: str
    ):
        """Looks up information about a server

        Parameters
        ----------
        address: Host/IP (and optionally port) of the Minecraft server
        """
        await inter.response.defer()

        port = int(25565 if not ':' in address else address.split(':')[-1])
        ip = address.split(':')[0]

        embed = disnake.Embed(color=lynn.EMBED_COLOR)
        embed.title = ip + (f':{port}' if port != 25565 else '')
        embed.description = 'WIP'

        await inter.send(embed=embed)

def setup(bot: lynn.Bot):
    bot.add_cog(MinecraftCommands(bot))
