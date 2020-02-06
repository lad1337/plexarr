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

