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

        await inter.send(f'Removed {len(emojis)} emojis')

    @emoji.sub_command()
    async def add(self,
        inter: disnake.ApplicationCommandInteraction,
        emoji: disnake.Attachment,
        name: str = None
    ):
        await inter.response.defer()

        if not name:
            name = emoji.filename.rsplit('.', 1)[0] # Use file name as emoji name

        e = await inter.guild.create_custom_emoji(name=name, image=emoji.read(), reason=f'Uploaded by {inter.author.name}')

        await inter.send(f'Created {e}')

def setup(bot: Bot):
    bot.add_cog(EmojiCommand(bot))
