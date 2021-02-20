import logging
import aiohttp
import asyncio
from datetime import datetime
from .constants import API_URL
from .menus import BaseMenu, GameMenuPage

from redbot.core import commands
from urllib.parse import quote

log = logging.getLogger("red.zonk-cogs.opencritic")
log.setLevel(logging.DEBUG)

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

        headers = {"accept": "application/json"}

        # Queries api for a game
        searchUrl = API_URL + '/game/search?criteria=' + quote(title)
        data = []

        log.debug('starting clientsession '+ str(datetime.now()))
        async with aiohttp.ClientSession() as session:
            log.debug('starting get request '+ str(datetime.now()))
            async with session.get(searchUrl) as response:
                log.debug('checking for status '+ str(datetime.now()))
                if response.status != 200:
                    response.raise_for_status()
                log.debug('awaiting to json the response next '+ str(datetime.now()))
                data = await response.json()

        log.debug('received results from search term '+ str(datetime.now()))
        # Handle if nothing is found
        if len(data) == 0:
            await ctx.send("I couldn't find anything! Try it with another title!")
            return

        # get array of gameIds
        gameIds = []

        for game in data:
            gameIds.append(game['id'])
        
        await BaseMenu(
            source=GameMenuPage(gameIds),
            delete_message_after=False,
            clear_reactions_after=True,
            timeout=60,
        ).start(ctx=ctx)