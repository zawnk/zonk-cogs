import logging
import aiohttp
import asyncio
from datetime import datetime


import discord
from redbot.core import commands, Config, checks
from redbot.core.utils.menus import menu, commands, DEFAULT_CONTROLS
from urllib.parse import quote

log = logging.getLogger("red.zonk-cogs.opencritic")
# log.setLevel(logging.DEBUG)

class OpenCritic(commands.Cog):
    """Search for games' score on OpenCritic"""

    __author__ = ["zonk"]
    __version__ = "1.0.0"

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.bot_has_permissions(embed_links=True, add_reactions=True)
    async def opencritic(self, ctx, *, title):
        """Search for a game"""
        log.debug('in command now ' + str(datetime.now()))

        apiUrl = "https://api.opencritic.com/api"
        headers = {"accept": "application/json"}

        # Queries api for a game
        searchUrl = apiUrl + '/game/search?criteria=' + quote(title)
        async with aiohttp.ClientSession() as session:
            data = await OpenCritic.get(self, session, searchUrl)

        log.debug('received results from name '+ str(datetime.now()))
        # Handle if nothing is found
        if len(data) == 0:
            await ctx.send("I couldn't find anything! Try it with another title!")
            return

        # Set variable to be appended to
        embeds = []
        urls = []
        results = []

        gameUrl = apiUrl + '/game/'

        for game in data:
            urls.append(gameUrl + str(game['id']))
        
        async with aiohttp.ClientSession() as session:
            results = await OpenCritic.getAll(self, session, urls)

        log.debug('creating embeds now')
        for result in results:
            # Build Embed
            embed = discord.Embed()
            embed.title = "{} ({})".format(result['name'], round(result['averageScore'], 2))
            # if data['imdbID']:
            #    embed.url = "http://www.imdb.com/title/{}".format(data['imdbID'])
            if result.get('description'):
               embed.description = result['description'][:500]
            if result.get('mastheadScreenshot', {}).get('thumbnail'):
               embed.set_thumbnail(url=result['mastheadScreenshot']['thumbnail'])
            if result.get('tier'):
               embed.add_field(name="Tier", value=data.get('tier', 'n/a'))
            # if data['Genre']:
            #    embed.add_field(name="Genre", value=data.get('Genre', 'N/A'))
            # if data.get("BoxOffice"):
            #    embed.add_field(name="Box Office", value=data.get('BoxOffice', 'N/A'))
            # if data['Metascore']:
            #    embed.add_field(name="Metascore", value=data.get('Metascore', 'N/A'))
            # if data['imdbRating']:
            #    embed.add_field(name="IMDb", value=data.get('imdbRating', 'N/A'))
            embed.set_footer(text="Powered by OpenCritic")
            embeds.append(embed)

        await menu(ctx, pages=embeds, controls=DEFAULT_CONTROLS, message=None, page=0, timeout=20)
    
    async def getAll(self, session, urls):
        log.debug('in getall '+ str(datetime.now()))
        tasks = []
        for url in urls:
            task = asyncio.create_task(OpenCritic.get(self, session, url))
            tasks.append(task)
        results = await asyncio.gather(*tasks)
        return results

    async def get(self, session, url):
        log.debug('in getall for url '+url+' '+ str(datetime.now()))
        async with session.get(url) as response:
            if response.status != 200:
                response.raise_for_status()
            return await response.json()