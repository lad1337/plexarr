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
from plexapi.video import Movie
from plexapi.media import Media


def generate_scene_title(movie: Movie, media: Media):
    return f"{movie.title} {movie.year} {media.videoResolution}p Plexarr".replace(' ', '.')


def as_torrents(movie: Movie):
    for media in movie.media:
        yield dict(
            title=generate_scene_title(movie, media),
            category="Movies/x264",
            download="\n".join([movie._server.url(f"{p.key}?download=1") for p in media.parts]),
            seeders=100,
            leachers=13,
            size=sum(p.size for p in media.parts)
        )
