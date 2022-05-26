import disnake
from disnake.ext import commands
import lynn
import os


class AdminCommands(commands.Cog):
    """Admin commands"""

    def __init__(self, bot: lynn.Bot):
        self.bot = bot

    @commands.slash_command()
    @commands.is_owner()
    async def admin(self, inter: disnake.ApplicationCommandInteraction):
        """Administration commands"""
        ...

    @admin.sub_command()
    async def debug(self, inter: disnake.ApplicationCommandInteraction):
        """Show the latest error log"""
        if not os.path.exists('data/error.dat'):
            await inter.send('No errors logged.', ephemeral=True)

        with open('data/error.dat', 'r', encoding='utf-8') as errors:
            error = errors.read()
            if not error:
                await inter.send('No errors logged.', ephemeral=True)
            else:
                await inter.send(f'```{error[-1990:]}```', ephemeral=True) # Tail 1990 chars

def setup(bot: lynn.Bot):
    bot.add_cog(AdminCommands(bot))
