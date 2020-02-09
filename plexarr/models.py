from pathlib import Path
import typing as t
import logging

from aria2p.downloads import Download
from furl import furl
from pydantic import BaseModel
from plexapi.video import Movie
from plexapi.media import Media

from plexarr.utils import generate_scene_title
from plexarr.utils import generate_magnet_link

logger = logging.getLogger(__name__)


def to_camel(string: str) -> str:
    return "".join(word.capitalize() for word in string.split("_"))


class AddTorrent(BaseModel):
    id: t.Union[str, int, None]
    method: str
    params: t.List[t.Any]


class SearchResult(BaseModel):
    title: str
    category: str = "Movies/x264"
    download: str
    seeders: int = 100
    leechers: int = 100
    size: int
    pubdate: str

    class Config:
        allow_population_by_field_name = True

    @classmethod
    def from_plex(cls, movie: Movie, media: Media, token: str) -> "SearchResult":
        urls = [
            furl(movie._server.url(f"{p.key}?download=1&X-Plex-Token={token}")).url
            for p in media.parts
        ]
        title = generate_scene_title(movie, media)
        size = sum(p.size for p in media.parts)
        magnet = generate_magnet_link(title, size, urls)

        return cls(
            title=title,
            size=size,
            pubdate=movie.updatedAt.isoformat(),
            magnet=magnet,
            download=magnet,
        )


class DownloadItem(BaseModel):
    """
        InfoHash = Convert.ToString(item[0]),
        State = ParseState(Convert.ToInt32(item[1])),
        Name = Convert.ToString(item[2]),
        TotalSize = Convert.ToInt64(item[3]),
        Progress = Convert.ToDouble(item[4]),
        DownloadedBytes = Convert.ToInt64(item[5]),
        UploadedBytes = Convert.ToInt64(item[6]),
        -
        -
        DownloadRate = Convert.ToInt64(item[9]),
        Label = Convert.ToString(item[11]),
        - x 10
        Error = Convert.ToString(item[21]),
        - x 5
        SavePath = Convert.ToString(item[26])

        {
            if ((state & 1) == 1)
            {
                return HadoukenTorrentState.Downloading;
            }
            else if ((state & 2) == 2)
            {
                return HadoukenTorrentState.CheckingFiles;
            }
            else if ((state & 32) == 32)
            {
                return HadoukenTorrentState.Paused;
            }
            else if ((state & 64) == 64)
            {
                return HadoukenTorrentState.QueuedForChecking;
            }

            return HadoukenTorrentState.Unknown;
        }
    """

    infoHash: str
    progress: float
    name: str
    label: str = ""
    savePath: str
    state: int
    totalSize: int
    downloadedBytes: int
    uploadedBytes: int = 0
    downloadRate: int
    error: str = ""

    @classmethod
    def from_airi2(cls, item: Download) -> "DownloadItem":
        state = {"paused": 32, "complete": 1, "active": 1}.get(item.status, 0)
        info_hash = item.dir.parts[-1]
        r = cls(
            infoHash=info_hash,
            progress=item.progress * 10,
            name=item.name,
            savePath=str(item.dir),
            state=state,
            totalSize=item.total_length,
            downloadedBytes=sum(f.completed_length for f in item.files),
            downloadRate=item.download_speed,
        )
        logger.debug(r)
        return r

    def as_list(self):
        # https://github.com/hadouken/hadouken/blob/36b48a96dca14d1031ef966d75a08dce96bc6f70/js/rpc/webui_list.js#L29
        # https://github.com/Radarr/Radarr/blob/a19f0202b0cb89b0be67316f59f11fbb1c2d3e17/src/NzbDrone.Core/Download/Clients/Hadouken/HadoukenProxy.cs#L135-L145
        return [
            self.infoHash,
            self.state,
            self.name,
            self.totalSize,
            self.progress,
            self.uploadedBytes,
            self.downloadedBytes,
            "this",
            "is",
            self.downloadRate,
            "a",
            self.label,
            "stupid",
            "data",
            "s",
            "t",
            "r",
            "u",
            "c",
            "t",
            "u",
            self.error,
            1,
            2,
            3,
            4,
            self.savePath,
        ]

