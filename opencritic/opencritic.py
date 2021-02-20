import logging
import aiohttp
import asyncio
from .constants import API_URL
from .menus import BaseMenu, GameMenuPage

from redbot.core import commands
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

        await ctx.trigger_typing()
        # Queries api for a game
        searchUrl = API_URL + '/game/search?criteria=' + quote(title)
        data = []

        async with aiohttp.ClientSession() as session:
            async with session.get(searchUrl) as response:
                if response.status != 200:
                    response.raise_for_status()
                data = await response.json()

        # Handle if nothing is found
        if len(data) == 0:
            await ctx.send("I couldn't find anything! Try it with another title!")
            return

        gameIds = []

        for game in data:
            gameIds.append(game['id'])
        
        await BaseMenu(
            source=GameMenuPage(gameIds),
            delete_message_after=False,
            clear_reactions_after=True,
            timeout=60,
        ).start(ctx=ctx)