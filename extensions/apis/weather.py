import disnake
from disnake.ext import commands
import lynn
from typing import List
import utils
import datetime

cities = []

async def autocomplete(inter, string: str) -> List[str]:
    result = []

    if len(string) < 3:
        return ['...',]

    for city in cities:
        if city.lower().startswith(string.lower()):
            result.append(city)

    for city in cities:
        if string.lower() in city.lower().split(',')[0]:
            if city not in result:
                result.append(city)

    result.append(string)

    return result[:25]

class WeatherCommand(commands.Cog):
    """Weather command"""

    def __init__(self, bot: lynn.Bot):
        self.bot = bot

    async def cog_load(self):
        # TODO: better list of cities
        # Populate cities
        global cities

        tmp = []

        j = await utils.rest('https://countriesnow.space/api/v0.1/countries')
        assert not j['error']

        for country in j['data']:
            for city in country['cities']:
                tmp.append(f'{city}, {country["country"]}')

        cities = tmp

    # TODO: Dark Sky is EOL, switch weather API
    @commands.slash_command(guild_ids=[702953546106273852])
    async def weather(self,
        inter: disnake.ApplicationCommandInteraction,
        location: str = commands.Param(autocomplete=autocomplete)
    ):
        """What's the weather like?

        Parameters
        ----------
        location: Name of the place
        """
        if location == '...':
            raise Exception("You're supposed to enter a city. This isn't one.")

        await inter.response.defer()
        geocoding = await utils.rest('https://nominatim.openstreetmap.org/search?format=json&limit=25&accept-language=en&q='+utils.escape_url(location))
        if not geocoding:
            raise Exception('Location not found.')

        data = await utils.rest(f"https://api.darksky.net/forecast/{self.bot.get_api_key('darksky')}/{geocoding[0]['lat']},{geocoding[0]['lon']}?exclude=minutely,hourly,daily,flags&units=si")

        if 'alerts' in data and data['alerts']:
            col = 0xff0000
        else:
            col = 0xffb347

        embed = disnake.Embed(title=geocoding[0]['display_name'], color=col)
        embed.set_thumbnail(f"https://darksky.net/images/weather-icons/{data['currently']['icon']}.png")

        if 'alerts' in data:
            alerts = []
            for alert in data['alerts']:
                if len(alerts) > 3:
                    continue
                if alert['title'] not in alerts:
                    embed.add_field(alert['title'], alert['description'][:1024], inline=False)
                    alerts.append(alert['title'])

        embed.add_field(data['currently']['summary'], str(round(data['currently']['temperature'], 2)) + '°C (' + str(round(data['currently']['temperature'] * (9/5) + 32, 2)) + '°F)\n' \
        + 'Feels Like: ' + str(round(data['currently']['apparentTemperature'], 2)) + '°C (' + str(round(data['currently']['apparentTemperature'] * (9/5) + 32, 2)) + '°F)\n' \
        + 'Humidity: ' + str(round(data['currently']['humidity'] * 100, 2)) + '%\n' \
        + 'Clouds: ' + str(round(data['currently']['cloudCover'] * 100, 2)) + '%\n' \
        + 'Wind: ' + str(data['currently']['windSpeed']) + ' m/s (' + str(round(int(data['currently']['windSpeed']) * 2.2369362920544, 2)) + ' mph)', inline=False)
        embed.set_footer(text='Powered by Dark Sky and OpenStreetMap')
        embed.timestamp = datetime.datetime.fromtimestamp(data['currently']['time'], tz=datetime.timezone.utc)

        await inter.send(embed=embed)

def setup(bot: lynn.Bot):
    bot.add_cog(WeatherCommand(bot))
