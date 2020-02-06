import os
from functools import wraps
from hashlib import sha1
from urllib.parse import unquote
from typing import List


from plexapi.video import Movie
from plexapi.media import Media
from furl import furl

import requests

radarr_url = "{}/api".format(os.getenv("RADARR_URL"),)
radarr_api_key = os.getenv("RADARR_KEY")


def get_name_from_radarr(imdb_id: str):
    response = requests.get(f"{radarr_url}/movie", params={"apikey": radarr_api_key},)
    for movie in response.json():
        if movie.get("imdbId") == imdb_id:
            return movie["title"]


def generate_scene_title(movie: Movie, media: Media) -> str:
    server_name = movie._server.friendlyName
    return f"{movie.title} {movie.year} {media.videoResolution}p Plexarr[{server_name}]".replace(
        " ", "."
    )


def generate_magnet_link(title: str, size: int, urls: List[str]) -> str:
    magnet = furl(scheme="magnet")
    magnet.add(query_params={"xt": "urn:btih:c12fe1c06bba254a9dc9f519b335aa7c1367a88a", "ws": urls})
    return magnet.url.replace("%3A", ":", 2)
