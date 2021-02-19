import logging
import aiohttp
import asyncio
from datetime import datetime


import discord
from redbot.core import commands, Config, checks
from redbot.core.utils.menus import menu, commands, DEFAULT_CONTROLS
from urllib.parse import quote

log = logging.getLogger("red.zonk-cogs.opencritic")
log.setLevel(logging.WARN)

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
            description = None
            scoreInfo = None
            platforms = []
            color = '000000'

            if result.get('description'):
                if len(result.get('description')) < 500:
                    description = result.get('description')
                else:
                    description = result.get('description')[:497]+'...'
            
            if result.get('Platforms'):
                for platform in result.get('Platforms'):
                    platforms.append(platform['shortName'])

            if result.get('tier'):
                score = round(result['averageScore'])

                if score > 0:
                    color = '80B60A'
                if score > 65:
                    color = '4AA1CE'
                if score > 74:
                    color = '9E00B4'
                if score > 83:
                    color = 'FC430A'
            
            if result['averageScore'] > 0:
                scoreInfo = round(result['averageScore'], 2)
            else:
                scoreInfo = 'No score'

            # Build Embed
            embed = discord.Embed(colour = int(color, 16))
            embed.title = "{} ({})".format(result['name'], scoreInfo)

            if description:
               embed.description = description
            if result.get('logoScreenshot', {}).get('fullRes'):
               embed.set_thumbnail(url='https:'+result['logoScreenshot']['fullRes'])
            if result.get('numReviews'):
                embed.add_field(name="# of Reviews", value=result.get('numReviews', 'n/a'))
            if result.get('tier'):
               embed.add_field(name="Tier", value=result.get('tier', 'n/a'))
            if len(platforms) > 0:
               embed.add_field(name="Platform(s)", value=', '.join(platforms))

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