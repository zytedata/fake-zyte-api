from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from fake_zyte_api.main import make_app

if TYPE_CHECKING:
    from aiohttp.pytest_plugin import AiohttpClient, AiohttpServer
    from aiohttp.test_utils import TestClient, TestServer
    from aiohttp.web import Application, Request


@pytest.fixture
async def api_server(aiohttp_server: AiohttpServer) -> TestServer:
    app = make_app()
    return await aiohttp_server(app)


@pytest.fixture
async def api_client(
    aiohttp_client: AiohttpClient,
) -> TestClient[Request, Application]:
    app = make_app()
    return await aiohttp_client(app)


@pytest.fixture
async def jobs_website(aiohttp_server: AiohttpServer) -> TestServer:
    from zyte_test_websites.jobs.app import make_app
    from zyte_test_websites.utils import get_default_data

    app = make_app(get_default_data("jobs"))
    return await aiohttp_server(app)
