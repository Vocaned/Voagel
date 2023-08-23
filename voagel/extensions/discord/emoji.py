from typing import Optional
import zipfile
from io import BytesIO
import requests
import disnake
from disnake.ext import commands
from voagel.main import Bot


class EmojiCommand(commands.Cog):
    """Emoji commands"""

    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.slash_command()
    @commands.guild_only()
    @commands.bot_has_permissions(manage_emojis=True)
    @commands.has_permissions(manage_messages=True)
    async def emoji(self, inter: disnake.ApplicationCommandInteraction):
        """Emoji commands"""

    @emoji.sub_command()
    @commands.check(lambda ctx: ctx.guild.owner_id == ctx.author.id)
    async def clear(self, inter: disnake.ApplicationCommandInteraction):
        """Remove all emojis from the server"""
        await inter.response.defer()

        emojis = await inter.guild.fetch_emojis()
        for emoji in emojis:
            await inter.guild.delete_emoji(emoji)

        await inter.send(f'Removed {len(emojis)} emoji')

    @emoji.sub_command()
    async def add(self,
        inter: disnake.ApplicationCommandInteraction,
        emoji: disnake.Attachment,
        name: Optional[str] = None
    ):
        await inter.response.defer()

        if not name:
            name = emoji.filename.rsplit('.', 1)[0] # Use file name as emoji name

        e = await inter.guild.create_custom_emoji(name=name, image=await emoji.read(), reason=f'Uploaded by {inter.author.name}')

        await inter.send(f'Created {e}')

    @emoji.sub_command()
    @commands.check(lambda ctx: ctx.guild.owner_id == ctx.author.id)
    async def mass_add(self,
        inter: disnake.ApplicationCommandInteraction,
        link: str
    ):
        await inter.response.defer()

        req = requests.get(link, timeout=10)

        static: list[tuple[str, bytes]] = []
        animated: list[tuple[str, bytes]] = []

        formats = [
            'png',
            'jpg',
            'jpeg',
            'webp'
        ]

        with zipfile.ZipFile(BytesIO(req.content), 'r') as fz:
            for file in fz.infolist():
                if '.' not in file.filename or file.filename.rsplit('.', 1)[1].lower() not in ['gif', *formats]:
                    continue
                with fz.open(file.filename) as f:
                    if file.filename.rsplit('.', 1)[1].lower() == 'gif':
                        animated.append((file.filename.rsplit('.', 1)[0].rsplit('/', 1)[-1], f.read()))
                    else:
                        static.append((file.filename.rsplit('.', 1)[0].rsplit('/', 1)[-1], f.read()))

        current_emojis = await inter.guild.fetch_emojis()
        current_static = [e for e in current_emojis if e.animated]
        current_animated = [e for e in current_emojis if not e.animated]
        if len(static) > inter.guild.emoji_limit or len(animated) > inter.guild.emoji_limit or len(static) + len(current_static) > inter.guild.emoji_limit or len(animated) + len(current_animated) > inter.guild.emoji_limit:
            await inter.send(f'Found {len(static)} static and {len(animated)} animated emotes in zip.\nServer cannot fit more than {inter.guild.emoji_limit-len(current_static)} static and {inter.guild.emoji_limit-len(current_animated)} animated emotes.')
            return

        for emoji in static:
            await inter.guild.create_custom_emoji(name=emoji[0], image=emoji[1], reason=f'Mass-uploaded by {inter.author.name}')
        for emoji in animated:
            await inter.guild.create_custom_emoji(name=emoji[0], image=emoji[1], reason=f'Mass-uploaded by {inter.author.name}')

        await inter.send(f'Added {len(static)} static and {len(animated)} animated emotes.')

def setup(bot: Bot):
    bot.add_cog(EmojiCommand(bot))
