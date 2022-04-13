import disnake
from disnake.ext import commands
import logging
import traceback
import lynn

class Errors(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # TODO: REWRITE THIS SHIT
    @commands.Cog.listener()
    async def on_slash_command_error(self,
        inter: disnake.ApplicationCommandInteraction,
        error: commands.CommandError
    ):
        error = getattr(error, 'original', error)

        if isinstance(error, commands.CommandNotFound):
            return

        logging.error('Ignoring exception in %s', inter.application_command.name)
        try:
            with open('data/error.dat', 'w', encoding='utf-8') as f:
                f.write('\n'.join(traceback.format_exception(type(error), error, error.__traceback__)))
        except:
            logging.error('ERROR: Could not write error to error.dat')

        errmsg = ''

        try:
            if hasattr(error, 'args'):
                errmsg = f"Error: `{type(error).__name__}: {error}`\n"
        except:
            pass

        if isinstance(error, commands.BotMissingPermissions):
            missing = [perm.replace('_', ' ').title() for perm in error.missing_perms]
            if len(missing) > 2:
                fmt = '{}, and {}'.format("**, **".join(missing[:-1]), missing[-1])
            else:
                fmt = ' and '.join(missing)
            _message = 'I need the **{}** permission(s) to run this command.'.format(fmt)
            errmsg += _message
            return

        if isinstance(error, commands.NSFWChannelRequired):
            errmsg += 'This command can only be used in NSFW channels.'
            return

        if isinstance(error, commands.DisabledCommand):
            errmsg += 'This command has been disabled in this server.'
            return

        if isinstance(error, commands.CommandOnCooldown):
            errmsg += f'This command is on cooldown, please retry in {round(error.retry_after)}s'
            return

        if isinstance(error, commands.MissingPermissions):
            missing = [perm.replace('_', ' ').title() for perm in error.missing_perms]
            if len(missing) > 2:
                fmt = '{}, and {}'.format("**, **".join(missing[:-1]), missing[-1])
            else:
                fmt = ' and '.join(missing)
            errmsg += 'You need the **{}** permission(s) to use this command.'.format(fmt)
            return

        if isinstance(error, commands.UserInputError):
            await inter.send('Invalid input. Check /help page for command.')
            return

        if isinstance(error, commands.NoPrivateMessage):
            try:
                await inter.send('This command cannot be used in direct messages.')
            except disnake.Forbidden:
                pass
            return

        if isinstance(error, commands.CheckFailure):
            errmsg += 'You do not have permission to use this command.'
            return

        if isinstance(error, commands.ExtensionAlreadyLoaded):
            errmsg += 'Extension already loaded.'
            return

        if isinstance(error, commands.ExtensionNotFound):
            errmsg += 'Extension not found.'
            return

        if isinstance(error, commands.ExtensionNotLoaded):
            errmsg += 'Extension not loaded.'
            return

        if isinstance(error, commands.ExtensionFailed):
            errmsg += 'Failed to load extension.'
            return

        await inter.send(errmsg)

def setup(bot: lynn.Bot):
    bot.add_cog(Errors(bot))
