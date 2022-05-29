import disnake
from disnake.ext import commands
import datetime

import lynn
import utils

class WeatherCommand(commands.Cog):
    """Weather command"""

    def __init__(self, bot: lynn.Bot):
        self.bot = bot

    def get_embed_color(self, data: dict) -> int:
        if len(data['alerts']['alert']) > 0:
            return 0xfe1111
        if 'thunder' in data['current']['condition']['text'].lower():
            return 0xfea011
        if 'snow' in data['current']['condition']['text'].lower():
            return 0xfefefe
        if 'ice' in data['current']['condition']['text'].lower() or \
           'blizzard' in data['current']['condition']['text'].lower():
            return 0xa0fefe
        if 'fog' in data['current']['condition']['text'].lower() or \
           'mist' in data['current']['condition']['text'].lower() or \
           'sleet' in data['current']['condition']['text'].lower() or \
           'overcast' in data['current']['condition']['text'].lower():
            return 0xa0a0a0

        return 0xfefea0

    @commands.slash_command(guild_ids=[702953546106273852])
    async def weather(self,
        inter: disnake.ApplicationCommandInteraction,
        location: str
    ):
        """What's the weather like?

        Parameters
        ----------
        location: Name of the place
        """
        if location == '...':
            raise Exception("You're supposed to enter a city. This isn't one.")

        await inter.response.defer()
        geocoding = await utils.rest(f'https://nominatim.openstreetmap.org/search?format=json&limit=25&accept-language=en&q={utils.escape_url(location)}')
        if not geocoding:
            raise Exception('Location not found.')

        data = await utils.rest(f"https://api.weatherapi.com/v1/forecast.json?key={self.bot.get_api_key('weatherapi')}&q={geocoding[0]['lat']},{geocoding[0]['lon']}&aqi=yes&alerts=yes")

        if not data or 'error' in data:
            if 'error' in data and 'message' in data['error']:
                raise Exception(data['error']['message'])
            raise Exception('Unknown error occured')

        embed = disnake.Embed(title=geocoding[0]['display_name'])
        embed.set_thumbnail(f"https:{data['current']['condition']['icon']}".replace('64x64', '128x128'))

        embed.add_field(data['current']['condition']['text'], f"**Temperature**: {data['current']['temp_c']}°C ({data['current']['temp_f']}°F)\n" \
        + f"**Feels Like**: {data['current']['feelslike_c']}°C ({data['current']['feelslike_f']}°F)\n" \
        + f"**Humidity**: {data['current']['humidity']}%\n" \
        + f"**Clouds**: {data['current']['cloud']}%\n" \
        + f"**Wind**: {round(data['current']['wind_kph'] / 3.6, 2)} m/s ({data['current']['wind_mph']} mph)\n" \
        + f"\nSun from {data['forecast']['forecastday'][0]['astro']['sunrise']} to {data['forecast']['forecastday'][0]['astro']['sunset']}", inline=False)

        for alert in data['alerts']['alert'][:3]:
            title = alert['severity']+' ' if alert['severity'] else '' + alert['msgtype'] if alert['msgtype'] else ''
            embed.add_field(f"{title+': ' if title else ''}{alert['headline']}", (f"**{alert['event']}**" + ('\n'+alert['desc'] if alert['desc'] else ''))[:1024])

        embed.colour = self.get_embed_color(data)
        embed.set_footer(text='Powered by WeatherAPI.com and OpenStreetMap')
        embed.timestamp = datetime.datetime.fromtimestamp(data['current']['last_updated_epoch'], tz=datetime.timezone.utc)

        await inter.send(embed=embed)

def setup(bot: lynn.Bot):
    bot.add_cog(WeatherCommand(bot))
