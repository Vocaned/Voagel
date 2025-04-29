import discord
from discord.ext import commands
from discord import app_commands, ui
import datetime
from urllib.parse import quote

from voagel.main import Bot, EMBED_COLOR
from voagel.utils import UserException

class WeatherCommand(commands.Cog):
    """Weather command"""

    def __init__(self, bot: Bot):
        self.bot = bot

    class OutputView(ui.LayoutView):
        def __init__(self, geocoding: dict, data: dict):
            super().__init__()
            container = ui.Container()

            top = ui.Section(ui.TextDisplay(f'''## {geocoding[0]["display_name"]}
### {data["current"]["condition"]["text"]}
**Temperature** {data["current"]["temp_c"]}°C ({data["current"]["temp_f"]}°F)
**Feels Like** {data["current"]["feelslike_c"]}°C ({data["current"]["feelslike_f"]}°F)
**Humidity** {data["current"]["humidity"]}%
**Clouds** {data["current"]["cloud"]}%
**Wind** {round(data["current"]["wind_kph"] / 3.6, 2)} m/s ({data["current"]["wind_mph"]} mph)

**Sunrise** at {data["forecast"]["forecastday"][0]["astro"]["sunrise"]}
**Sunset** at {data["forecast"]["forecastday"][0]["astro"]["sunset"]}
'''), accessory=ui.Thumbnail(f'https:{data["current"]["condition"]["icon"]}'.replace('64x64', '128x128')))
            container.add_item(top)

            if data['alerts']['alert']:
                container.add_item(ui.Separator())
            alerts = []
            for alert in data['alerts']['alert'][:3]:
                # Don't show duplicate alerts
                if alert['desc'] in alerts:
                    continue
                alerts.append(alert['desc'])

                parts = [
                    '**',
                    f'{alert["severity"]} ' if alert['severity'] else '',
                    f'{alert["msgtype"]}: ' if alert['msgtype'] else '',
                    alert['headline'] or "",
                    '**\n',
                    (alert["desc"] or "")[:1024],
                    (f'```\n{alert["instruction"]}\n```') if alert['instruction'] else ''
                ]
                container.add_item(ui.TextDisplay(''.join(parts)))

            #TODO: attribution

            self.add_item(container)

    @app_commands.command()
    async def weather(self,
        inter: discord.Interaction,
        location: str
    ):
        """What's the weather like?

        Parameters
        ----------
        location: Name of the place
        """
        if location == '...':
            raise UserException("You're supposed to enter a city. This isn't one.")

        await inter.response.defer()
        req = await self.bot.session.get(f'https://nominatim.openstreetmap.org/search?format=json&limit=25&accept-language=en&q={quote(location)}')
        geocoding = await req.json()
        if not geocoding:
            raise UserException('Location not found.')

        req = await self.bot.session.get(f"https://api.weatherapi.com/v1/forecast.json?key={self.bot.get_api_key('weatherapi')}&q={geocoding[0]['lat']},{geocoding[0]['lon']}&aqi=yes&alerts=yes")
        data = await req.json()

        if not data or 'error' in data:
            if 'error' in data and 'message' in data['error']:
                raise Exception(data['error']['message'])
            raise Exception('Unknown error occured')

        view = self.OutputView(geocoding, data)
        await inter.followup.send(view=view)

async def setup(bot: Bot):
    await bot.add_cog(WeatherCommand(bot))
