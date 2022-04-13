import logging
import traceback
import disnake
from disnake.ext import commands
import lynn

class Errors(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_slash_command_error(self,
        inter: disnake.ApplicationCommandInteraction,
        error: commands.CommandError
    ):
        if isinstance(error, commands.CommandNotFound):
            return

        logging.warning('Ignoring exception in /%s', inter.application_command.name)
        try:
            with open('data/error.dat', 'w', encoding='utf-8') as f:
                f.write('\n'.join(traceback.format_exception(type(error), error, error.__traceback__)))
        except:
            logging.error('ERROR: Could not write error to error.dat')

        errtype = None
        errmsg = None

        if isinstance(error, commands.BotMissingPermissions):
            missing = [perm.replace('_', ' ').title() for perm in error.missing_perms]
            if len(missing) > 2:
                fmt = '{}, and {}'.format("**, **".join(missing[:-1]), missing[-1])
            else:
                fmt = ' and '.join(missing)
            _message = 'The bot is missing the **{}** permission(s) to run this command.'.format(fmt)
            errtype = 'Not enough permissions.'
            errmsg = _message
        elif isinstance(error, commands.NSFWChannelRequired):
            errtype = 'This command can only be used in NSFW channels.'
        elif isinstance(error, commands.DisabledCommand):
            errtype = 'This command has been disabled in this server.'
        elif isinstance(error, commands.CommandOnCooldown):
            errtype = 'This command is on cooldown'
            errmsg = f'Please try again in {round(error.retry_after)}s'
        elif isinstance(error, commands.MissingPermissions):
            missing = [perm.replace('_', ' ').title() for perm in error.missing_perms]
            if len(missing) > 2:
                fmt = '{}, and {}'.format("**, **".join(missing[:-1]), missing[-1])
            else:
                fmt = ' and '.join(missing)
            errtype = 'Not enough permissions.'
            errmsg = 'You need the **{}** permission(s) to use this command.'.format(fmt)
        elif isinstance(error, commands.UserInputError):
            errtype = 'Invalid input. Check /help page for command.'
        elif isinstance(error, commands.NoPrivateMessage):
            errtype = 'This command cannot be used in direct messages.'
        elif isinstance(error, commands.CheckFailure):
            errtype = 'You do not have permission to use this command.'
        elif isinstance(error, commands.ExtensionAlreadyLoaded):
            errtype = 'Extension already loaded.'
        elif isinstance(error, commands.ExtensionNotFound):
            errtype = 'Extension not found.'
        elif isinstance(error, commands.ExtensionNotLoaded):
            errtype = 'Extension not loaded.'
        elif isinstance(error, commands.ExtensionFailed):
            errtype = 'Failed to load extension.'
        elif isinstance(error, commands.CommandError):
            errtype = f'Uncaught exception occured in `{inter.application_command.name}`'

            original = getattr(error, 'original', error)
            errmsg = f'{type(original).__name__}: {original}'

        embed = disnake.Embed(color=lynn.ERROR_COLOR, title=errtype, description=errmsg)
        await inter.send(embed=embed, ephemeral=True)

def setup(bot: lynn.Bot):
    bot.add_cog(Errors(bot))
