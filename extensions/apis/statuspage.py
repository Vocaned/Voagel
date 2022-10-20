from datetime import datetime
from enum import Enum
from typing import List

import disnake
import lynn
import utils
from disnake.ext import commands

statusPages = {
    # Unfortunately statuspage.io doesn't include system metrics in their API.
    # System metric IDs must be hardcoded because of that.
    # TODO: BeautifulSoup scraping?
    'Discord': ('https://discordstatus.com', ('ztt4777v23lf',)),
    'Twitter': ('https://api.twitterstat.us', None),
    'Reddit': ('https://reddit.statuspage.io', ('rx2nb3pfx3w6', '0jwzw9drbt3d', '5nx0js42cvh6', 'ykb0vk6gm40h', 'k7t111j3ykjr', 'zry7jgt3xffg')),
    'Cloudflare': ('https://www.cloudflarestatus.com', None),
    'Dropbox': ('https://status.dropbox.com', None),
    'GitHub': ('https://www.githubstatus.com', None),
    'Medium': ('https://medium.statuspage.io', ('kb1b7qv1kfv1', 'd9gjgw59bwfz', 'lwb7fbwqljjz')),
    'Epic Games': ('https://status.epicgames.com', None),
    'Glitch': ('https://status.glitch.com', ('2hfs13clgy2x', 'lz9n5qdj9h67', '4kppgbgy1vg6', 'yfyd7k8t6c2t', 'f9m2jkbys0lt', '8hhlmmyf9fqw'))
}

class StatuspageComamnd(commands.Cog):
    """Statuspage Command"""

    def __init__(self, bot: lynn.Bot):
        self.bot = bot

    @commands.slash_command(guild_ids=[702953546106273852])
    async def statuspage(self,
        inter: disnake.ApplicationCommandInteraction,
        service: str = commands.Param(choices=statusPages.keys())
    ):
        """Shows status pages of different services.

        Parameters
        ----------
        service: Service to get status page for
        """
        if service not in statusPages:
            raise Exception('Invalid statuspage')

        await inter.response.defer()

        page = statusPages[service]

        col = 0x00
        j = await utils.rest(page[0] + '/index.json', returns='json')
        if j['status']['indicator'] == 'none':
            col = 0x00ff00
        elif j['status']['indicator'] == 'minor':
            col = 0xffa500
        elif j['status']['indicator'] == 'major':
            col = 0xff0000

        embeds = []
        embed = disnake.Embed(title=f"**{service} Status** - {j['status']['description']}", colour=col, url=page[0])
        embed.timestamp = datetime.utcnow()
        for comp in j['components']:
            embed.add_field(comp['name'], comp['status'].replace('_', ' ').title())

        if page[1]:
            # Seperate component and metric statuses by using an invisible field
            embed.add_field('\U00002063', '\U00002063', inline=False)
            for metric in page[1]:
                m = await utils.rest(f"{page[0]}/metrics-display/{metric}/day.json", returns='json')
                if 'summary' not in m or 'last' not in m['summary']:
                    continue
                last = m['summary']['last']
                last = str(round(last, 2)) if last else '0'
                embed.add_field(m['metrics'][0]['metric']['name'], last)

        embeds.append(embed)

        for incident in j['incidents']:
            if incident['status'] == 'resolved' or incident['status'] == 'completed':
                continue
            firstUpdate = incident['incident_updates'][-1]
            lastUpdate = incident['incident_updates'][0]
            if incident['status'] == 'scheduled':
                col = 0xffa500
            else:
                col = 0xff0000

            embed = disnake.Embed(title='**' + incident['status'].replace('_', ' ').title() + '** - ' + incident['name'], color=col)
            if firstUpdate['affected_components']:
                embed.add_field('Affected components', '\n'.join(c['name'] for c in firstUpdate['affected_components']))
            if firstUpdate != lastUpdate and len(firstUpdate) + len(lastUpdate) + 5 < 1900:
                embed.description = '**' + datetime.fromisoformat(lastUpdate['created_at'].rstrip('Z')).strftime('%b %d %H:%M:%S %Y UTC%z') \
                                  + '**: ' + lastUpdate['body'] + '\n\n\n**' \
                                  + datetime.fromisoformat(firstUpdate['created_at'].rstrip('Z')).strftime('%b %d %H:%M:%S %Y UTC%z') \
                                  + '**: ' + firstUpdate['body']
            else:
                embed.description = firstUpdate['body']

            if incident['scheduled_for']:
                embed.timestamp = datetime.fromisoformat(incident['scheduled_for'].rstrip('Z'))
                embed.set_footer(text=incident['impact'].title() + ' • Starts')
            else:
                embed.timestamp = datetime.fromisoformat(incident['created_at'].rstrip('Z'))
                embed.set_footer(text=incident['impact'].title() + ' • Started')

            embeds.append(embed)

        if len(embeds) > 10:
            await inter.send(f'Only showing 10 incidents. {len(embeds)} total', embeds=embeds[:10])
        else:
            await inter.send(embeds=embeds[:10])

def setup(bot: lynn.Bot):
    bot.add_cog(StatuspageComamnd(bot))
