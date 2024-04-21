from typing import Optional
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
    @commands.has_permissions(manage_emojis=True)
    async def emoji(self, inter: disnake.ApplicationCommandInteraction):
        """Emoji commands"""

    @emoji.sub_command()
    async def add(self,
        inter: disnake.ApplicationCommandInteraction,
        emoji: disnake.Attachment,
        name: Optional[str] = None
    ):
        assert inter.guild
        await inter.response.defer()

        if not name:
            name = emoji.filename.rsplit('.', 1)[0] # Use file name as emoji name

        e = await inter.guild.create_custom_emoji(name=name, image=await emoji.read(), reason=f'Uploaded by {inter.author.name}')

        await inter.send(f'Created {e}')

def setup(bot: Bot):
    bot.add_cog(EmojiCommand(bot))
