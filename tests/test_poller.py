"""Tests de api.poller."""

import httpx
import pytest

from api.models import Server
from api.poller import poll_server


@pytest.mark.anyio
async def test_poll_server_marks_down_on_connection_error():
    server = Server(id="1", name="unreachable", host="127.0.0.1", port=1)
    async with httpx.AsyncClient() as client:
        await poll_server(server, client)
    assert server.status == "DOWN"
    assert server.last_checked is not None


@pytest.mark.anyio
async def test_poll_server_marks_up_on_success(monkeypatch):
    server = Server(id="2", name="ok-server", host="example.test", port=80)

    class FakeResponse:
        status_code = 200

    async def fake_get(self, url, timeout=None):
        return FakeResponse()

    monkeypatch.setattr(httpx.AsyncClient, "get", fake_get)

    async with httpx.AsyncClient() as client:
        await poll_server(server, client)

    assert server.status == "UP"


@pytest.fixture
def anyio_backend():
    return "asyncio"
