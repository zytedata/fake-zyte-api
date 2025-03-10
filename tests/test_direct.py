from __future__ import annotations

from base64 import b64decode
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from aiohttp import ClientResponse
    from aiohttp.test_utils import TestClient
    from aiohttp.web import Application, Request


async def get_api_response(
    client: TestClient[Request, Application], request_data: dict[str, Any]
) -> ClientResponse:
    return await client.post("/extract", json=request_data)


async def test_404(api_client, jobs_website):
    url = str(jobs_website.make_url("/nonexistent"))
    response = await get_api_response(
        api_client,
        {
            "url": url,
            "httpResponseBody": True,
        },
    )
    assert response.status == 200
    response_data = await response.json()
    assert response_data["url"] == url
    assert response_data["statusCode"] == 404
    assert "httpResponseBody" in response_data
    text = b64decode(response_data["httpResponseBody"]).decode("utf-8")
    assert "404: Not Found" in text


async def test_response_body(api_client, jobs_website):
    url = str(jobs_website.make_url("/jobs/4"))
    response = await get_api_response(
        api_client,
        {
            "url": url,
            "httpResponseBody": True,
        },
    )
    assert response.status == 200
    response_data = await response.json()
    assert response_data["url"] == url
    assert response_data["statusCode"] == 200
    assert "httpResponseBody" in response_data

    text = b64decode(response_data["httpResponseBody"]).decode("utf-8")
    assert "<h1>109 jobs in Energy:</h1>" in text
    assert (
        '<a class="job-link" href="/job/1583065288960216">Interior Designer</a>' in text
    )
    assert 'href="/jobs/4?page=2">Next' in text


async def test_response_headers(api_client, jobs_website):
    url = str(jobs_website.make_url("/jobs/4"))
    response = await get_api_response(
        api_client,
        {
            "url": url,
            "httpResponseHeaders": True,
        },
    )
    assert response.status == 200
    response_data = await response.json()
    assert response_data["url"] == url
    assert response_data["statusCode"] == 200
    assert "httpResponseHeaders" in response_data
    for header in response_data["httpResponseHeaders"]:
        if header["name"] == "Content-Type":
            assert header["value"] == "text/html; charset=utf-8"
            break


async def test_browser_html(api_client, jobs_website):
    url = str(jobs_website.make_url("/jobs/4"))
    response = await get_api_response(
        api_client,
        {
            "url": url,
            "browserHtml": True,
        },
    )
    assert response.status == 200
    response_data = await response.json()
    assert response_data["url"] == url
    assert response_data["statusCode"] == 200
    assert "browserHtml" in response_data
    assert "<h1>109 jobs in Energy:</h1>" in response_data["browserHtml"]


async def test_extraction_with_body(api_client, jobs_website):
    url = str(jobs_website.make_url("/job/1888448280485890"))
    response = await get_api_response(
        api_client,
        {
            "url": url,
            "httpResponseBody": True,
            "jobPosting": True,
        },
    )
    assert response.status == 200
    response_data = await response.json()
    assert response_data["url"] == url
    assert response_data["statusCode"] == 200

    assert "httpResponseBody" in response_data
    text = b64decode(response_data["httpResponseBody"]).decode("utf-8")
    assert "<h1>Litigation Attorney</h1>" in text

    assert "jobPosting" in response_data
    job_posting = response_data["jobPosting"]
    assert job_posting["jobTitle"] == "Litigation Attorney"


async def test_extraction_without_body(api_client, jobs_website):
    url = str(jobs_website.make_url("/job/1888448280485890"))
    response = await get_api_response(
        api_client,
        {
            "url": url,
            "jobPosting": True,
        },
    )
    assert response.status == 200
    response_data = await response.json()
    assert response_data["url"] == url
    assert response_data["statusCode"] == 200

    assert "httpResponseBody" not in response_data

    assert "jobPosting" in response_data
    job_posting = response_data["jobPosting"]
    assert job_posting["jobTitle"] == "Litigation Attorney"
