import disnake
import lynn
from disnake.ext import commands
import utils
import json
import base64
from datetime import datetime
import socket
import time
import struct
from typing import Tuple
from io import BytesIO


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

    def _unpack_varint(self, sock):
        data = 0
        for i in range(5):
            ordinal = sock.recv(1)

            if len(ordinal) == 0:
                break

            byte = ord(ordinal)
            data |= (byte & 0x7F) << 7*i

            if not byte & 0x80:
                break

        return data

    def _pack_varint(self, data):
        ordinal = b''

        while True:
            byte = data & 0x7F
            data >>= 7
            ordinal += struct.pack('B', byte | (0x80 if data > 0 else 0))

            if data == 0:
                break

        return ordinal

    def _pack_data(self, data):
        """ Page the data """
        if isinstance(data, str):
            data = data.encode('utf8')
            return self._pack_varint(len(data)) + data
        elif isinstance(data, int):
            return struct.pack('H', data)
        elif isinstance(data, float):
            return struct.pack('L', int(data))
        else:
            return data

    def _send_data(self, connection, *args):
        """ Send the data on the connection """
        data = b''

        for arg in args:
            data += self._pack_data(arg)

        connection.send(self._pack_varint(len(data)) + data)

    def _read_fully(self, connection, extra_varint=False):
        """ Read the connection and return the bytes """
        packet_length = self._unpack_varint(connection)
        packet_id = self._unpack_varint(connection)
        byte = b''

        if extra_varint:
            # Packet contained netty header offset for this
            if packet_id > packet_length:
                self._unpack_varint(connection)

            extra_length = self._unpack_varint(connection)

            while len(byte) < extra_length:
                byte += connection.recv(extra_length)

        else:
            byte = connection.recv(packet_length)

        return byte


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

    def query_server(self, ip: str, port: str) -> Tuple[dict, int]:
        valid = False
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as conn:
                conn.settimeout(5)
                conn.connect((ip, port))
                valid = True

                # Send handshake + status request
                self._send_data(conn, b'\x00\x00', ip, port, b'\x01')
                self._send_data(conn, b'\x00')

                # Read response, offset for string length
                data = self._read_fully(conn, extra_varint=True)

                # Send and read unix time
                unix = time.time()
                self._send_data(conn, b'\x01', 123)
                _ = self._read_fully(conn)
                ping = int((time.time() - unix) * 1000)

                data = json.loads(data.decode('utf8'))
                data['ping'] = ping

                return data
        except socket.timeout as e:
            if not valid:
                raise Exception('Could not connect to server. Make sure the IP is valid.')
            raise e

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

        data = await self.bot.loop.run_in_executor(None, self.query_server, ip, port)

        embed = disnake.Embed(color=lynn.EMBED_COLOR)
        embed.timestamp = datetime.utcnow()
        embed.title = ip + (f':{port}' if port != 25565 else '')
        embed.set_footer(icon_url='https://www.minecraft.net/etc.clientlibs/minecraft/clientlibs/main/resources/favicon-96x96.png')

        if 'favicon' in data and data['favicon']:
            favicon = disnake.File(BytesIO(base64.b64decode(data['favicon'].replace('data:image/png;base64,', ''))), 'pack.png')
            embed.set_thumbnail(file=favicon)
        else:
            embed.set_thumbnail(url='https://static.wikia.nocookie.net/minecraft_gamepedia/images/7/78/Pack_64x64.png')

        if isinstance(data['description'], dict):
            # json text format
            desc = data['description']
            description = ''
            for obj in desc:
                if obj == 'extra':
                    for extra in desc[obj]:
                        if 'text' in extra:
                            description += extra['text']
                elif obj == 'text':
                    description += desc[obj]
        else:
            description = ''
            for i in range(len(data['description'])):
                # (Try to) clean up colorcodes from description
                if (data['description'][i] == '§') or (i != 0 and data['description'][i-1] == '§'):
                    continue
                description += data['description'][i]
        embed.description = description

        embed.add_field('Version', data['version']['name'])
        embed.add_field('Players', f"{data['players']['online']}/{data['players']['max']}")
        embed.add_field('Ping', f"{data['ping']}ms")

        if 'modinfo' in data:
            if data['modinfo']['type'] == 'FML':
                embed.add_field(name='Forge Server', value=f"{len(data['modinfo']['modList'])} mods enabled.")
            else:
                embed.add_field(name='Modded Server', value=f"Type: {data['modinfo']['type']}")
        elif 'forgeData' in data:
            embed.add_field(name='Forge Server', value=f"{len(data['forgeData']['mods'])} mods enabled.")

        await inter.send(embed=embed)

def setup(bot: lynn.Bot):
    bot.add_cog(MinecraftCommands(bot))
