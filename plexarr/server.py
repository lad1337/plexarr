import os
import logging
import typing as t

from fastapi import FastAPI
from furl import furl
from starlette.requests import Request
from plexapi.myplex import MyPlexAccount
from plexapi.exceptions import BadRequest
from plexapi.video import Movie
import aria2p

from plexarr.utils import get_name_from_radarr
from plexarr.models import AddTorrent
from plexarr.models import SearchResult
from plexarr.models import DownloadItem


app = FastAPI()
logger = logging.getLogger("plexarr")
logger.setLevel(logging.INFO)

try:
    account = MyPlexAccount(os.getenv("PLEX_USERNAME"), os.getenv("PLEX_PASSWORD"))
except BadRequest:
    account = None
    logger.warning("Could not login to PLEX")
aria2 = aria2p.API(
    aria2p.Client(host=os.getenv("ARIA2_RPC", "http://localhost"), port=6800, secret="")
)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/servers")
async def servers():
    servers = [s for s in account.resources() if "server" in s.provides]
    return [s.name for s in servers]


@app.post("/api")
async def downloader(action: AddTorrent) -> dict:
    method = action.method
    logger.info(action)
    if method == "core.getSystemInfo":
        response = {
            "Commitish": "e51736c",
            "Branch": "develop",
            "Versions": {"libtorrent": "1.0.5.0", "hadouken": "5.1.1"},
        }
    elif method == "webui.list":
        downloads = aria2.get_downloads()
        logger.info(f"aria2 downloads: {downloads}")
        response = {"torrents": [DownloadItem.from_airi2(d) for d in downloads]}
    elif method == "webui.addTorrent":
        type_, url, data = action.params
        url = furl(url)
        logger.info(url.query.params)
        download = aria2.add_uris(uris=[url.query.params["ws"]])
        logger.info(f"Added download {download.gid}")
        response = str(download.gid)
    else:
        response = {}

    return {
        "result": response,
        "id": action.id,
        "jsonrpc": "2.0",
    }


@app.get("/pubapi_v2.php")
async def search(
    r: Request,
    mode: str = None,
    imdbId: str = None,
    search_string: str = None,
    get_token: str = None,
    search_imdb: str = None,
):
    """rarbg_fake"""
    if get_token is not None:
        return {"token": "1337"}
    elif mode == "list":
        torrents = ["foo"]
        zeta = account.resource("zeta").connect()
        movies = zeta.library.recentlyAdded()
    else:
        title = ""
        if search_imdb is not None:
            title = get_name_from_radarr(search_imdb)
        elif search_string:
            title = search_string
        logger.info(f"searching plex for: {title}")

        zeta = account.resource("zeta").connect()
        movies = zeta.search(title)

    torrents = []
    for m in movies:
        if isinstance(m, Movie):
            for media in m.media:
                torrents.append(SearchResult.from_plex(m, media, account.authenticationToken))

    return dict(torrent_results=torrents)
