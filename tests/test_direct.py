from __future__ import annotations

from base64 import b64decode
from typing import TYPE_CHECKING, Any

from yarl import URL

if TYPE_CHECKING:
    from aiohttp import ClientResponse
    from aiohttp.test_utils import TestClient
    from aiohttp.web import Application, Request


async def get_api_response(
    client: TestClient[Request, Application], request_data: dict[str, Any]
) -> ClientResponse:
    return await client.post("/extract", json=request_data)


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
    assert "httpResponseBody" in response_data

    text = b64decode(response_data["httpResponseBody"]).decode("utf-8")
    assert "<h1>109 jobs in Energy:</h1>" in text
    assert (
        '<a class="job-link" href="/job/1583065288960216">Interior Designer</a>' in text
    )
    assert 'href="/jobs/4?page=2">Next' in text


async def test_extract_job_posting(api_client, jobs_website):
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

    assert "httpResponseBody" in response_data
    text = b64decode(response_data["httpResponseBody"]).decode("utf-8")
    assert "<h1>Litigation Attorney</h1>" in text
    assert '<span class="job-location">Bogotá, Colombia</span>' in text

    assert "jobPosting" in response_data
    job_posting = response_data["jobPosting"]
    descr = (
        "Family Law Attorneys deal with legal matters related to family"
        " relationships. They handle cases like divorce, child custody,"
        " adoption, and domestic disputes to provide legal guidance."
    )
    assert job_posting == {
        "url": url,
        "datePublished": "2023-09-07T00:00:00Z",
        "datePublishedRaw": "Sep 07, 2023",
        "jobTitle": "Litigation Attorney",
        "jobLocation": {"raw": "Bogotá, Colombia"},
        "description": descr,
        "descriptionHtml": f"<article>\n\n<p>{descr}</p>\n\n</article>",
        "employmentType": "Contract",
        "baseSalary": {"valueMin": "63K", "valueMax": "101K", "currency": "USD"},
        "requirements": ["4 to 10 Years"],
        "hiringOrganization": {"name": "Drax Group"},
        "metadata": {
            "dateDownloaded": job_posting["metadata"]["dateDownloaded"],
            "probability": 1.0,
        },
    }


async def test_extract_job_posting_nav(api_client, jobs_website):
    url = jobs_website.make_url("/jobs/4")
    response = await get_api_response(
        api_client,
        {
            "url": str(url),
            "httpResponseBody": True,
            "jobPostingNavigation": True,
        },
    )
    assert response.status == 200
    response_data = await response.json()
    assert response_data["url"] == str(url)

    assert "httpResponseBody" in response_data
    text = b64decode(response_data["httpResponseBody"]).decode("utf-8")
    assert "<h1>109 jobs in Energy:</h1>" in text

    assert "jobPostingNavigation" in response_data
    job_posting_navigation = response_data["jobPostingNavigation"]
    jobs = [
        ("1888448280485890", "Litigation Attorney"),
        ("1583065288960216", "Interior Designer"),
        ("2505213971303748", "IT Administrator"),
        ("2973702198556912", "Digital Marketing Specialist"),
        ("160399666386920", "Legal Assistant"),
        ("2226428310491314", "Customer Support Specialist"),
        ("2962173505197183", "Substance Abuse Counselor"),
        ("895360732760260", "Social Media Manager"),
        ("360775924046834", "Procurement Manager"),
        ("1939835498099785", "Physician Assistant"),
    ]
    assert job_posting_navigation == {
        "url": str(url),
        "items": [
            {
                "url": str(url.join(URL(f"/job/{job[0]}"))),
                "method": "GET",
                "name": job[1],
            }
            for job in jobs
        ],
        "nextPage": {"url": str(url.join(URL("/jobs/4?page=2"))), "method": "GET"},
        "pageNumber": 1,
        "metadata": {
            "dateDownloaded": job_posting_navigation["metadata"]["dateDownloaded"]
        },
    }
