import os

from fastapi import FastAPI
from plexapi.myplex import MyPlexAccount
from plexapi.exceptions import NotFound

app = FastAPI()
account = MyPlexAccount(os.getenv('PLEX_USERNAME'), os.getenv('PLEX_PASSWORD'))


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
