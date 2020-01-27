"""
{
    "title":"Off.Piste.2016.iNTERNAL.BDRip.x264-LiBRARiANS",
    "category":"Movies/x264",
    "download":"magnet:...",
    "seeders":12,
    "leechers":6,
    "size":504519520,
    "pubdate":"2017-05-21 02:13:49 +0000",
    "episode_info":{
        "imdb":"tt4443856",
        "tvrage":null,
        "tvdb":null,
        "themoviedb":"430293"
    },
    "ranked":1,
    "info_page":"https://torrentapi.org/...."
}
"""
from hashlib import sha1
from urllib.parse import unquote
from typing import List


from plexapi.video import Movie
from plexapi.media import Media
from torf import Torrent
from furl import furl


def generate_scene_title(movie: Movie, media: Media) -> str:
    server_name = movie._server.friendlyName
    return f"{movie.title} {movie.year} {media.videoResolution}p Plexarr[{server_name}]".replace(
        " ", "."
    )


def generate_magnet_link(title: str, size: int, urls: List[str]) -> str:
    magnet = furl(scheme="magnet")
    magnet.add(
        query_params={"xt": "urn:btih:c12fe1c06bba254a9dc9f519b335aa7c1367a88a", "ws": urls[0]}
    )
    return unquote(magnet.url)

    t = Torrent(name=title, httpseeds=urls)
    t.pieces = 1
    t.metainfo["info"]["pieces"] = b""


def as_torrents(movie: Movie, token: str) -> dict:
    for media in movie.media:
        urls = [movie._server.url(f"{p.key}?download=1&X-Plex-Token={token}") for p in media.parts]
        title = generate_scene_title(movie, media)
        size = sum(p.size for p in media.parts)
        magnet = generate_magnet_link(title, size, urls)

        yield dict(
            title=title,
            category="Movies/x264",
            # radarr extracts the info hash from the magnet link ... -.-
            download=magnet,
            seeders=100,
            leechers=100,
            size=size,
            pubdate=movie.updatedAt.isoformat(),
        )
