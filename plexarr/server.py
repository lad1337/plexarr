import os
import logging

from fastapi import FastAPI
from starlette.requests import Request
from plexapi.myplex import MyPlexAccount
from plexapi.exceptions import NotFound
from plexapi.video import Movie

from plexarr.convert import as_torrents
from plexarr.utils import get_name_from_radarr

app = FastAPI()
account = MyPlexAccount(os.getenv('PLEX_USERNAME'), os.getenv('PLEX_PASSWORD'))

logger = logging.getLogger('plexarr')
logger.setLevel(logging.INFO)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/servers")
async def servers():
    servers = [s for s in account.resources() if 'server' in s.provides]
    return [s.name for s in servers]


@app.get("/api/search")
async def search(q: str = ''):
    results = []
    if not q:
        return results

    for server in [s for s in account.resources() if 'server' in s.provides]:
        try:
            con = server.connect(timeout=3)
        except NotFound:
            continue
        results.extend([{
                "title": i.title,
                "type": i.__class__.__name__,
                "server": server.name,
                } for i in con.search(q)
        ])
    return results


@app.get("/pubapi_v2.php")
async def rarbg_fake(r: Request, mode: str = None, imdbId: str = None, search_string: str = None,
                     get_token: str = None, search_imdb: str = None):
    if get_token is not None:
        return {"token": "1337"}
    elif mode == 'list':
        torrents = ['foo']
        zeta = account.resource('zeta').connect()
        movies = zeta.library.recentlyAdded()
    else:
        title = ''
        if search_imdb is not None:
            title = get_name_from_radarr(search_imdb)
        elif search_string:
            title = search_string
        logger.info(f"searching plex for: {title}")

        zeta = account.resource('zeta').connect()
        movies = zeta.search(title)

    torrents = []
    for m in movies:
        if isinstance(m, Movie):
            torrents.extend(as_torrents(m))

    return dict(
        torrent_results=torrents
    )
