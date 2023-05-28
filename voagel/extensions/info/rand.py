import disnake
from disnake.ext import commands
import random

from voagel.main import Bot

class RandomCommands(commands.Cog):
    """Random commands"""

    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.slash_command()
    async def dice(self, inter: disnake.ApplicationCommandInteraction, query: str):
        """Rolls n dice with set amount of faces. Default 1d6.

        Parameters
        ----------
        query: Parameters of the dice you want to roll
        """

        if not 'd' in query:
            n = int(query)
            f = 6
        else:
            n = int(query.split('d')[0])
            f = int(query.split('d')[1])

        if n == 0:
            await inter.send('You roll 0 dice. Nothing happens.')
            return
        if f == 0:
            await inter.send(f"You roll {n} {'dice' if n > 1 else 'die'} with 0 faces. The world implodes as your zero-dimensional {'dice' if n > 1 else 'die'} hit the table.")
            return

        if f < 0:
            await inter.send(f"You try to roll {n} {'dice' if n > 1 else 'die'} with negative faces, but you realize that you're all out of negative-dimensional dice.")
            return
        if n < 0:
            roll = random.randint(abs(n), abs(n)*f)
            await inter.send(f"You roll negative {n} dice. The dice jump from the table back into your hand. You rolled **{roll}**!")
            return

        roll = random.randint(n, n*f)
        await inter.send(f"You roll {n} {'dice' if n > 1 else 'die'} with {f} face{'s' if f > 1 else ''}. You rolled **{roll}**!")

    @commands.slash_command()
    async def coinflip(self, inter: disnake.ApplicationCommandInteraction):
        """Flips a coin"""
        flip = random.randint(0, 6000)
        if flip == 0:
            await inter.send('You flip a coin. It lands on its edge!')
        else:
            await inter.send(f"You flip a coin. It lands on **{'heads' if flip < 3000 else 'tails'}**.")

    @commands.slash_command()
    async def choose(self, inter: disnake.ApplicationCommandInteraction, choices: str):
        """Choose between a list of things

        Parameters
        ----------
        choices: List of possible choices, separated by a semicolon
        """
        await inter.send(f"Picked **{random.choice(choices.split(';')).strip()}**.")

def setup(bot: Bot):
    bot.add_cog(RandomCommands(bot))
