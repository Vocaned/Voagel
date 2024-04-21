import disnake
from disnake.ext import commands
import os
from voagel.main import Bot
from voagel.utils import check_output



class AdminCommands(commands.Cog):
    """Admin commands"""

    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.slash_command()
    @commands.is_owner()
    async def admin(self, _: disnake.ApplicationCommandInteraction):
        """Administration commands"""
        ...

    @admin.sub_command()
    async def debug(self, inter: disnake.ApplicationCommandInteraction):
        """Show the latest error log"""
        if not 'last_error' in self.bot.data:
            await inter.send('No errors logged.', ephemeral=True)

        await inter.send(f'```{self.bot.data["last_error"][-1990:]}```', ephemeral=True) # Tail 1990 chars

    @admin.sub_command_group()
    async def module(self, _: disnake.ApplicationCommandInteraction):
        """Module commands"""
        ...

    @module.sub_command()
    async def load(self, inter: disnake.ApplicationCommandInteraction, module: str):
        """Load a module

        Parameters
        ----------
        module: Name of the module
        """
        self.bot.load_extension('voagel.extensions.'+module)
        await inter.send(f'Loaded {module}')

    @module.sub_command()
    async def unload(self, inter: disnake.ApplicationCommandInteraction, module: str):
        """Unload a module

        Parameters
        ----------
        module: Name of the module
        """
        self.bot.unload_extension('voagel.extensions.'+module)
        await inter.send(f'Unloaded {module}')

    @module.sub_command()
    async def reload(self, inter: disnake.ApplicationCommandInteraction, module: str):
        """Reload a module

        Parameters
        ----------
        module: Name of the module
        """
        self.bot.reload_extension('voagel.extensions.'+module)
        await inter.send(f'Reloaded {module}')

    @admin.sub_command_group()
    async def git(self, _: disnake.ApplicationCommandInteraction):
        """Git commands"""
        ...

    @git.sub_command()
    async def pull(self, inter: disnake.ApplicationCommandInteraction):
        """Pull the git repo"""
        await inter.response.defer()
        out1 = await check_output(['git', 'pull'], timeout=30)
        out2 = await check_output(['git', 'log', '@{1}..', '--format=%h %an | %B'], timeout=30)
        await inter.send(f'```{out1}\n\n{out2}```')

    @git.sub_command()
    async def fuck(self, inter: disnake.ApplicationCommandInteraction):
        """Did you fuck up the files again?"""
        await inter.send(f'```{await check_output(["git", "reset", "--hard", "origin/master"])}```')

def setup(bot: Bot):
    bot.add_cog(AdminCommands(bot))
