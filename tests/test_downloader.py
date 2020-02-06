from starlette.testclient import TestClient

from plexarr.server import app

client = TestClient(app)


def test_list_downloads():
    response = client.post("/api", json={"id": "asd", "params": [], "method": "webui.list"}).json()
    assert "result" in response
    result = response["result"]
    assert "torrents" in result
    for torrent in result["torrents"]:
        pass

