from pathlib import Path
import typing as t

from aria2p.downloads import Download
from furl import furl
from pydantic import BaseModel
from plexapi.video import Movie
from plexapi.media import Media

from plexarr.utils import generate_scene_title
from plexarr.utils import generate_magnet_link


def to_camel(string: str) -> str:
    return "".join(word.capitalize() for word in string.split("_"))


class AddTorrent(BaseModel):
    id: t.Union[str, int, None]
    method: str
    params: t.List[t.Union[str, int, None]]


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
        public sealed class HadoukenTorrent
        {
            public string InfoHash { get; set; }
            public double Progress { get; set; }
            public string Name { get; set; }
            public string Label { get; set; }
            public string SavePath { get; set; }
            public HadoukenTorrentState State { get; set; }
            public bool IsFinished { get; set; }
            public bool IsPaused { get; set; }
            public bool IsSeeding { get; set; }
            public long TotalSize { get; set; }
            public long DownloadedBytes { get; set; }
            public long UploadedBytes { get; set; }
            public long DownloadRate { get; set; }
            public string Error { get; set; }
        }
        public enum HadoukenTorrentState
        {
            Unknown = 0,
            QueuedForChecking = 1,
            CheckingFiles = 2,
            DownloadingMetadata = 3,
            Downloading = 4,
            Finished = 5,
            Seeding = 6,
            Allocating = 7,
            CheckingResumeData = 8,
            Paused = 9
        }
    """

    infoHash: str
    Progress: float
    Name: str
    SavePath: str
    State: int
    IsFinished: bool
    IsPaused: bool
    IsSeeding: bool = False
    TotalSize: int
    DownloadedBytes: int
    UploadedBytes: int = 0
    DownloadRate: int
    Error: str = ""

    @classmethod
    def from_airi2(cls, item: Download) -> "DownloadItem":
        state = {"paused": 9, "complete": 5}.get(item.status, 0)
        return cls(
            infoHash=item.gid,
            Progress=item.progress,
            Name=item.name,
            SavePath=str(item.dir),
            State=state,
            IsFinished=state == 5,
            IsPaused=state == 9,
            TotalSize=item.total_length,
            DownloadedBytes=sum(f.completed_length for f in item.files),
            DownloadRate=item.download_speed,
        )
