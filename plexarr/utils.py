import os
from functools import wraps

import requests

radarr_url = "{}/api".format(os.getenv("RADARR_URL"),)
radarr_api_key = os.getenv("RADARR_KEY")


def get_name_from_radarr(imdb_id: str):
    response = requests.get(f"{radarr_url}/movie", params={"apikey": radarr_api_key},)
    for movie in response.json():
        if movie.get("imdbId") == imdb_id:
            return movie["title"]


async def json_rpc_response(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        id_, data = func(*args, **kwargs)
        return {"result": data, "id": id_}

    return wrapper

