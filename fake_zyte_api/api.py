from __future__ import annotations

from base64 import b64encode
from typing import Any

import aiohttp
from itemadapter import ItemAdapter
from web_poet import HttpResponse
from zyte_common_items import ZyteItemAdapter
from zyte_test_websites.jobs.extraction import (
    TestJobPostingNavigationPage,
    TestJobPostingPage,
)

ItemAdapter.ADAPTER_CLASSES.appendleft(ZyteItemAdapter)  # type: ignore[attr-defined]


async def handle_request(request_data: dict[str, Any]) -> dict[str, Any]:
    url = request_data["url"]
    response_data: dict[str, Any] = {
        "url": url,
    }

    async with aiohttp.ClientSession() as session, session.get(url) as resp:
        response_data["statusCode"] = resp.status
        website_response_body = await resp.read()

    if "httpResponseHeaders" in request_data:
        headers = [{"name": k, "value": v} for k, v in resp.headers.items()]
        response_data["httpResponseHeaders"] = headers

    if "httpResponseBody" in request_data:
        body_b64 = b64encode(website_response_body).decode()
        response_data["httpResponseBody"] = body_b64

    if "browserHtml" in request_data:
        response_data["browserHtml"] = website_response_body.decode(resp.get_encoding())

    if "jobPostingNavigation" in request_data:
        web_poet_response = HttpResponse(url, website_response_body)
        job_posting_nav_page = TestJobPostingNavigationPage(web_poet_response)
        job_posting_navigation = await job_posting_nav_page.to_item()
        response_data["jobPostingNavigation"] = ItemAdapter(
            job_posting_navigation
        ).asdict()

    if "jobPosting" in request_data:
        web_poet_response = HttpResponse(url, website_response_body)
        job_posting_page = TestJobPostingPage(web_poet_response)
        job_posting = await job_posting_page.to_item()
        response_data["jobPosting"] = ItemAdapter(job_posting).asdict()

    return response_data
