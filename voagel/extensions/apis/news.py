import time
from datetime import datetime

import disnake
import feedparser
from disnake.ext import commands
from voagel.main import Bot
from voagel.utils import OpenGraphParser, escape_url


class NewsCommand(commands.Cog):
    """Google News"""

    def __init__(self, bot: Bot):
        self.bot = bot

    class NewsView(disnake.ui.View):
        def __init__(self, feed: dict, bot: Bot):
            self.feed = feed
            self.bot = bot
            self.page = 0
            self.cache = {}
            super().__init__(timeout=30)

        async def get_embed(self):
            if self.page in self.cache:
                return self.cache[self.page]

            entry = self.feed['items'][self.page]

            ogparser = OpenGraphParser()
            req = await self.bot.session.get(entry['link'])
            ogparser.feed(await req.text())

            if not ogparser.tags: # Article didn't have any OpenGraph meta tags.
                del self.feed['items'][self.page] # Delete result and try the next one
                return await self.get_embed()

            embed = disnake.Embed(color=0xf5c518)
            embed.url = entry['link']
            embed.set_author(name=entry['source']['title'])
            embed.timestamp = datetime.fromtimestamp(time.mktime(entry.published_parsed)).astimezone()

            embed.set_footer(text=f'({self.page+1}/{len(self.feed["items"])+1})')

            if 'og:title' in ogparser.tags:
                embed.title = ogparser.tags['og:title']
            else:
                embed.title = entry['title'].rstrip(' - ' + entry['source']['title']) # Google News shows source in title, so remove it

            if 'og:description' in ogparser.tags:
                embed.description = ogparser.tags['og:description']
            if 'og:image' in ogparser.tags:
                embed.set_image(ogparser.tags['og:image'])

            self.cache[self.page] = embed
            return embed

        @disnake.ui.button(label="⏪", style=disnake.ButtonStyle.blurple)
        async def cancel(self, _: disnake.ui.Button, inter: disnake.MessageInteraction):
            if self.page > 0:
                self.page -= 1
                await inter.response.edit_message(embed=await self.get_embed())

        @disnake.ui.button(label="⏩", style=disnake.ButtonStyle.blurple)
        async def compress(self, _: disnake.ui.Button, inter: disnake.MessageInteraction):
            if self.page < len(self.feed['items']):
                self.page += 1
                await inter.response.edit_message(embed=await self.get_embed())

    @commands.slash_command()
    async def news(self,
        inter: disnake.ApplicationCommandInteraction,
        query: str = ''
    ):
        """
        Look up news using Google News. Defaults to world news

        Parameters
        ----------
        query: News to search for
        """

        await inter.response.defer()
        if query:
            req = await self.bot.session.get(f'https://news.google.com/rss/search?q={escape_url(query)}&hl=en-US&gl=US&ceid=US:en')
        else:
            # CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx1YlY4U0FtVnVHZ0pWVXlnQVAB = World News
            req = await self.bot.session.get('https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx1YlY4U0FtVnVHZ0pWVXlnQVAB?hl=en-US&gl=US&ceid=US:en')

        feed = feedparser.parse(await req.text())

        if not feed['items']:
            raise Exception('Google News did not return any news for your query.')

        view = self.NewsView(feed, self.bot)
        hook = await inter.followup.send(embed=await view.get_embed(), view=view, wait=True)
        await view.wait()
        view.clear_items()
        await hook.edit(embed=await view.get_embed(), view=view) # Update one last time to remove the view buttons


def setup(bot: Bot):
    bot.add_cog(NewsCommand(bot))
