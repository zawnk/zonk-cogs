import logging
import aiohttp
import asyncio

import discord
from redbot.core import commands, Config, checks
from redbot.core.utils.menus import menu, commands, DEFAULT_CONTROLS
from urllib.parse import quote

log = logging.getLogger("red.zonk-cogs.opencritic")

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

        apiUrl = "https://api.opencritic.com/api"
        headers = {"accept": "application/json"}

        # Queries api for a game
        searchUrl = apiUrl + '/game/search?criteria=' + quote(title)
        async with aiohttp.ClientSession() as session:
            async with session.get(url=searchUrl, headers=headers) as response:
                data = await response.json()

        # Handle if nothing is found
        if len(data) == 0:
            await ctx.send("I couldn't find anything! Try it with another title!")
            return

        # Set variable to be appended to
        embeds = []
        tasks = []

        # Loop and ask for more information and build embed
        gameUrl = apiUrl + '/game/'
        async with aiohttp.ClientSession() as session:
            for game in data:
                # Queries api for a game information
                url = gameUrl + str(game['id'])
                # async with aiohttp.ClientSession() as session:
                #     async with session.get(url=url, headers=headers) as response:
                #         data = await response.json()
                #         log.debug(data)
                task = asyncio.create_task(get(session, url))
                tasks.append(task)

        results = await asyncio.gather(*tasks)
        
        for result in results:
            # Build Embed
            embed = discord.Embed()
            embed.title = "{} ({})".format(result['name'], result['medianScore'])
            # if data['imdbID']:
            #    embed.url = "http://www.imdb.com/title/{}".format(data['imdbID'])
            # if data['Plot']:
            #    embed.description = data['Plot'][:500]
            # if data['Poster'] != "N/A":
            #    embed.set_thumbnail(url=data['Poster'])
            # if data['Runtime']:
            #    embed.add_field(name="Runtime", value=data.get('Runtime', 'N/A'))
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
    
    async def get(self, session, url):
        async with session.get(url) as response:
            if response.status != 200:
                response.raise_for_status()
            return await response.json()