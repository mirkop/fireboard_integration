# test_api.py
import pytest
import asyncio
from custom_components.fireboard.api import FireBoardApiClient

@pytest.mark.asyncio
async def test_login(monkeypatch):
    class DummySession:
        async def post(self, url, json, headers):
            class Resp:
                async def json(self):
                    return {"key": "dummy_token"}
                def raise_for_status(self):
                    pass
            return Resp()
    api = FireBoardApiClient("user", "pass", DummySession())
    await api.async_login()
    assert api._token == "dummy_token"
