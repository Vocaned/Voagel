import disnake
from disnake.ext import commands

from voagel.main import Bot

class ModCommands(commands.Cog):
    """Moderator Commands"""

    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.slash_command(name='hackban')
    @commands.guild_only()
    @commands.bot_has_permissions(ban_members=True)
    @commands.default_member_permissions(ban_members=True)
    async def hackban(self,
        inter: disnake.ApplicationCommandInteraction,
        id: disnake.Object,
        reason: str = ''
    ):
        """Ban an user by their ID

        Parameters
        ----------
        id: User ID
        reason: Reason
        """
        assert inter.guild
        await inter.guild.ban(id, reason=reason, delete_message_days=0)
        baninfo = await inter.guild.fetch_ban(id)
        await inter.send(f'{baninfo.user.name}#{baninfo.user.discriminator} has been banned.')

    @commands.slash_command(name='purge')
    @commands.guild_only()
    @commands.bot_has_permissions(manage_messages=True)
    @commands.default_member_permissions(manage_messages=True)
    async def purge(self,
        inter: disnake.ApplicationCommandInteraction,
        count: int = commands.Param(gt=0, le=100),
        user: disnake.Member | None = None
    ):
        """Purge the last {count} messages from the channel.

        Parameters
        ----------
        count: How many messages to purge
        user: Only purge messages from a specific user
        """
        assert isinstance(inter.channel, disnake.guild.GuildMessageable)

        if user:
            deleted = await inter.channel.purge(limit=count, check=lambda m: m.author.id == user.id)
        else:
            deleted = await inter.channel.purge(limit=count)

        await inter.send(f'Deleted {len(deleted)} messages.', ephemeral=True)

def setup(bot: Bot):
    bot.add_cog(ModCommands(bot))
