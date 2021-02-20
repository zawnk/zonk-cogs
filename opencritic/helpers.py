import logging
import discord
from datetime import datetime
import aiohttp

from .constants import API_URL
from .dataclasses import Game

log = logging.getLogger("red.zonk-cogs.opencritic")

async def make_embed_from_gameid(gameId: int):
    """ Creates an embed from the given gameId """

    game: Game = None
    gameUrl = API_URL + '/game/'

    async with aiohttp.ClientSession() as session:
        async with session.get(gameUrl+str(gameId)) as response:
            if response.status != 200:
                response.raise_for_status()
            game = await response.json()

    log.debug('building embed for game '+game['name']+' '+str(datetime.now()))
    em = None
    description = None
    scoreInfo = None
    bannerUrl = None
    platforms = []
    color = '000000'

    if game.get('description'):
        if len(game.get('description')) < 500:
            description = game.get('description')
        else:
            description = game.get('description')[:497]+'...'
    
    if game.get('Platforms'):
        for platform in game.get('Platforms'):
            platforms.append(platform['shortName'])

    if game.get('tier'):
        score = round(game['averageScore'])

        if score > 0:
            color = '80B60A'
        if score > 65:
            color = '4AA1CE'
        if score > 74:
            color = '9E00B4'
        if score > 83:
            color = 'FC430A'
    
    if game['averageScore'] > 0:
        scoreInfo = round(game['averageScore'], 2)
    else:
        scoreInfo = 'No score'

    if game.get('logoScreenshot', {}).get('thumbnail'):
        bannerUrl = 'https:'+game['logoScreenshot']['thumbnail']
    elif game.get('logoScreenshot', {}).get('fullRes'):
        bannerUrl = 'https:'+game['logoScreenshot']['fullRes']
    elif game.get('bannerScreenshot', {}).get('thumbnail'):
        bannerUrl = 'https:'+game['bannerScreenshot']['thumbnail']
    elif game.get('bannerScreenshot', {}).get('fullRes'):
        bannerUrl = 'https:'+game['bannerScreenshot']['fullRes']

    # Build Embed
    em = discord.Embed(url = 'https://opencritic.com/game/{}/a'.format(game['id']), colour = int(color, 16))
    em.title = "{} ({})".format(game['name'], scoreInfo)

    if description:
        em.description = description
    if bannerUrl:
        em.set_thumbnail(url=bannerUrl)
    if game.get('numReviews'):
        em.add_field(name="# of Reviews", value=game.get('numReviews', 'n/a'))
    if game.get('tier'):
        em.add_field(name="Tier", value=game.get('tier', 'n/a'))
    if len(platforms) > 0:
        em.add_field(name="Platform(s)", value=', '.join(platforms))

    em.set_footer(text="Powered by OpenCritic")
    return em