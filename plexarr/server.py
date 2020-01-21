import os

from fastapi import FastAPI
from starlette.requests import Request
from plexapi.myplex import MyPlexAccount
from plexapi.exceptions import NotFound
from plexapi.video import Movie
from requests import request

from plexarr.convert import as_torrents

app = FastAPI()
account = MyPlexAccount(os.getenv('PLEX_USERNAME'), os.getenv('PLEX_PASSWORD'))
radarr_url = "{}/api".format(getenv('RADARR_URL'), )
radarr_api_key = getenv('RADARR_URL')


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
                     get_token: str = None):
    if get_token is not None:
        return {"token": "1337"}
    elif mode == 'list':
        torrents = ['foo']
        zeta = account.resource('zeta').connect()
        movies = zeta.library.recentlyAdded()
    else:
        import pdb; pdb.set_trace()
        request.get()
        zeta = account.resource('zeta').connect()
        movies = zeta.search(search_string)

    torrents = []
    for m in movies:
        if isinstance(m, Movie):
            torrents.extend(as_torrents(m))

    return dict(
        torrent_results=torrents
    )
