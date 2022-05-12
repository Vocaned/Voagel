import time
from datetime import datetime

import disnake
import feedparser
import lynn
import utils
from disnake.ext import commands


class NewsCommand(commands.Cog):
    """Google News"""

    def __init__(self, bot: lynn.Bot):
        self.bot = bot

    class NewsView(disnake.ui.View):
        def __init__(self, feed):
            self.feed = feed
            self.page = 0
            self.cache = {}
            super().__init__(timeout=30)

        async def get_embed(self):
            if self.page in self.cache:
                return self.cache[self.page]

            entry = self.feed['items'][self.page]

            article = await utils.rest(entry['link'], returns='text')
            ogparser = utils.OpenGraphParser()
            ogparser.feed(article)

            if not ogparser.tags: # Article didn't have any OpenGraph meta tags. Probably blocked in EU.
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

    @commands.slash_command(name='News', guild_ids=[702953546106273852])
    async def news(self,
        inter: disnake.ApplicationCommandInteraction,
        query: str = None
    ):
        """
        Look up news using Google News. Defaults to world news

        Parameters
        ----------
        query: News to search for
        """

        await inter.response.defer()
        if query:
            resp = await utils.rest(f'https://news.google.com/rss/search?q={utils.escape_url(query)}&hl=en-US&gl=US&ceid=US:en', returns='text')
        else:
            # CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx1YlY4U0FtVnVHZ0pWVXlnQVAB = World News
            resp = await utils.rest('https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx1YlY4U0FtVnVHZ0pWVXlnQVAB?hl=en-US&gl=US&ceid=US:en', returns='text')

        feed = feedparser.parse(resp)

        if not feed['items']:
            raise Exception('Google News did not return any news for your query.')

        view = self.NewsView(feed)
        hook = await inter.followup.send(embed=await view.get_embed(), view=view)
        await view.wait()
        view.clear_items()
        await hook.edit(embed=await view.get_embed(), view=view) # Update one last time to remove the view buttons


def setup(bot: lynn.Bot):
    bot.add_cog(NewsCommand(bot))
