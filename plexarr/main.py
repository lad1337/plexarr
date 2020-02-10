import os
import logging
import typing as t

from fastapi import FastAPI
from requests.exceptions import ConnectionError
from furl import furl
from starlette.requests import Request
from plexapi.myplex import MyPlexAccount
from plexapi.exceptions import BadRequest
from plexapi.exceptions import NotFound
from plexapi.video import Movie
import aria2p

from .utils import get_name_from_radarr
from .models import AddTorrent
from .models import SearchResult
from .models import DownloadItem
from .utils import get_servers_for_account


app = FastAPI()
logger = logging.getLogger("plexarr")
logger.setLevel(logging.DEBUG)

DOWNLOAD_DIR = os.getenv("DOWNLOAD_DIR", "~")
try:
    account = MyPlexAccount(os.getenv("PLEX_USERNAME"), os.getenv("PLEX_PASSWORD"))
except (ConnectionError, BadRequest):
    account = None
    logger.warning("Could not login to PLEX")
aria2 = aria2p.API(
    aria2p.Client(host=os.getenv("ARIA2_RPC", "http://localhost"), port=6800, secret="")
)
SERVER_CONNECTIONS = set()


@app.get("/")
async def root():
    return {"message": "Plexarr"}


@app.get("/servers")
async def servers():
    servers = get_servers_for_account(account)
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
    elif method == "webui.addTorrent":
        type_, url, data = action.params
        url = furl(url)
        logger.debug(url.query.params)
        _, _, btih = url.query.params["xt"].rpartition(":")
        destination = os.path.abspath(os.path.join(os.path.expanduser(DOWNLOAD_DIR), btih))
        download = aria2.add_uris(uris=[url.query.params["ws"]], options={"dir": destination})
        logger.info(f"Added download {download.gid} -> {btih}")
        response = btih
    elif method == "webui.list":
        downloads = aria2.get_downloads()
        logger.info(f"aria2 downloads: {downloads}")
        response = {"torrents": [DownloadItem.from_airi2(d).as_list() for d in downloads]}
    elif method == "webui.perform":
        sub_action, params = action.params
        logger.debug(params)
        if sub_action == "removedata":
            for d in aria2.get_downloads():
                logger.debug(d.dir)
                if params[0].lower() in str(d.dir):
                    logger.info(f"Removing {d.name}")
                    d.remove()
                    break
            response = True
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

    title = ""
    if search_imdb is not None:
        title = get_name_from_radarr(search_imdb)
    elif search_string:
        title = search_string
    logger.info(f"searching plex for: {title}")

    torrents = []

    if not SERVER_CONNECTIONS:
        for resource in get_servers_for_account(account):
            # zeta = account.resource("zeta").connect()
            logger.info(f"Connecting to {resource}")
            try:
                server = resource.connect()
            except NotFound:
                logger.info(f"Could not connect to {resource}")
                continue
            SERVER_CONNECTIONS.add(server)

    search_results = []
    for server in SERVER_CONNECTIONS:
        logger.info(f"Searching on {server}")
        try:
            results = server.search(title)
        except ConnectionError:
            server.connect()
            results = server.search(title)
        search_results.extend(results)

    for result in search_results:
        if isinstance(result, Movie):
            for media in result.media:
                torrents.append(SearchResult.from_plex(result, media, server._token))

    return {"torrent_results": torrents}
