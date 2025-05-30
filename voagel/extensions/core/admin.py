import discord
from discord.ext import commands
from discord import app_commands
from voagel.main import Bot, ERROR_COLOR
from voagel.utils import check_output
from contextlib import redirect_stdout
import textwrap
from io import StringIO

async def is_admin(inter: discord.Interaction) -> bool:
    assert isinstance(inter.client, commands.Bot)
    return await inter.client.is_owner(inter.user)

class AdminCommands(commands.Cog):
    """Admin commands"""

    def __init__(self, bot: Bot):
        self.bot = bot

    admin = app_commands.Group(name='admin', description='Administration commands')
    module = app_commands.Group(name='module', description='Module commands', parent=admin)
    git = app_commands.Group(name='git', description='Git commands', parent=admin)

    admin.interaction_check = is_admin
    module.interaction_check = is_admin
    git.interaction_check = is_admin

    @admin.command()
    async def sync(self, inter: discord.Interaction):
        """Syncs all slash commands"""
        await inter.response.defer(thinking=True)
        await self.bot.tree.sync()
        await inter.response.send_message('Synced commands.')

    class EvalModal(discord.ui.Modal, title='Eval'):
        code = discord.ui.TextInput(
            label='Python Code',
            custom_id='code',
            style=discord.TextStyle.paragraph,
            required=True
        )

        async def on_submit(self, inter: discord.Interaction) -> None:
            code = self.code.value
            """Eval"""
            env = {
                'bot': inter.client,
                'inter': inter,
                'channel': inter.channel,
                'user': inter.user,
                'guild': inter.guild
            }
            env.update(globals())

            if code.startswith('```') and code.endswith('```'):
                code = '\n'.join(code.split('\n')[1:-1])
            else:
                code = code.strip('` \n')

            stdout = StringIO()

            to_compile = f'async def func():\n{textwrap.indent(code, "  ")}'
            exec(to_compile, env)

            func = env['func']
            with redirect_stdout(stdout):
                try:
                    ret = await func()
                except Exception as e:
                    embed = discord.Embed(color=ERROR_COLOR, title=type(e).__name__, description=e)
                    await inter.response.send_message(embed=embed)
                    return
                value = stdout.getvalue()

            if inter.response.is_done():
                return # Message sent from eval, don't make an another one
            else:
                output = ''
                if ret:
                    output += f'Return: ```\n{ret}\n```\n'
                if value:
                    output += f'```\n{value}\n```\n'
                if not output:
                    output = '[No response]'
                await inter.response.send_message(output)

    @commands.is_owner()
    @admin.command()
    async def eval(self, inter: discord.Interaction):
        await inter.response.send_modal(self.EvalModal())

    @module.command()
    async def load(self, inter: discord.Interaction, module: str):
        """Load a module

        Parameters
        ----------
        module: Name of the module
        """
        await inter.response.defer(thinking=True)
        await self.bot.load_extension('voagel.extensions.'+module)
        await inter.followup.send(f'Loaded {module}')

    @module.command()
    async def unload(self, inter: discord.Interaction, module: str):
        """Unload a module

        Parameters
        ----------
        module: Name of the module
        """
        await inter.response.defer(thinking=True)
        await self.bot.unload_extension('voagel.extensions.'+module)
        await inter.followup.send(f'Unloaded {module}')

    @module.command()
    async def reload(self, inter: discord.Interaction, module: str):
        """Reload a module

        Parameters
        ----------
        module: Name of the module
        """
        await inter.response.defer(thinking=True)
        await self.bot.reload_extension('voagel.extensions.'+module)
        await inter.followup.send(f'Reloaded {module}')

    @git.command()
    async def pull(self, inter: discord.Interaction):
        """Pull the git repo"""
        await inter.response.defer(thinking=True)
        out1 = await check_output(['git', 'pull'], timeout=30)
        out2 = await check_output(['git', 'log', '@{1}..', '--format=%h %an | %B'], timeout=30)
        await inter.followup.send(f'```{out1}\n\n{out2}```')

    @git.command()
    async def fuck(self, inter: discord.Interaction):
        """Did you fuck up the files again?"""
        await inter.response.send_message(f'```{await check_output(["git", "reset", "--hard", "origin/master"])}```')

async def setup(bot: Bot):
    await bot.add_cog(AdminCommands(bot))
