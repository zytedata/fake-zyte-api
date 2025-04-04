from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from zyte_test_websites.articles.app import make_app as make_test_articles_website
from zyte_test_websites.ecommerce.app import make_app as make_test_ecommerce_website
from zyte_test_websites.jobs.app import make_app as make_test_job_website

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
    app = make_test_job_website()
    return await aiohttp_server(app)


@pytest.fixture
async def ecommerce_website(aiohttp_server: AiohttpServer) -> TestServer:
    app = make_test_ecommerce_website()
    return await aiohttp_server(app)


@pytest.fixture
async def articles_website(aiohttp_server: AiohttpServer) -> TestServer:
    app = make_test_articles_website()
    return await aiohttp_server(app)
