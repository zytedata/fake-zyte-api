from __future__ import annotations

from base64 import b64decode
from typing import TYPE_CHECKING

import pytest
from yarl import URL
from zyte_api import AsyncZyteAPI

if TYPE_CHECKING:
    from aiohttp.test_utils import TestServer


@pytest.fixture
def zyte_api_client(api_server: TestServer) -> AsyncZyteAPI:
    return AsyncZyteAPI(api_key="a", api_url=str(api_server.make_url("/")))


async def test_response_body(zyte_api_client, jobs_website):
    url = str(jobs_website.make_url("/jobs/4"))
    response_data = await zyte_api_client.get({"url": url, "httpResponseBody": True})
    assert response_data["url"] == url

    assert "httpResponseBody" in response_data
    text = b64decode(response_data["httpResponseBody"]).decode("utf-8")
    assert "<h1>109 jobs in Energy:</h1>" in text
    assert (
        '<a class="job-link" href="/job/1583065288960216">Interior Designer</a>' in text
    )
    assert 'href="/jobs/4?page=2">Next' in text


async def test_browser_html(zyte_api_client, jobs_website):
    url = str(jobs_website.make_url("/jobs/4"))
    response_data = await zyte_api_client.get({"url": url, "browserHtml": True})
    assert response_data["url"] == url

    assert "browserHtml" in response_data
    assert "<h1>109 jobs in Energy:</h1>" in response_data["browserHtml"]


async def test_extract_job_posting(zyte_api_client, jobs_website):
    url = str(jobs_website.make_url("/job/1888448280485890"))
    response_data = await zyte_api_client.get(
        {
            "url": url,
            "httpResponseBody": True,
            "jobPosting": True,
        },
    )

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
        "jobPostingId": "1888448280485890",
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


async def test_extract_job_posting_nav(zyte_api_client, jobs_website):
    url = jobs_website.make_url("/jobs/4")
    response_data = await zyte_api_client.get(
        {
            "url": str(url),
            "httpResponseBody": True,
            "jobPostingNavigation": True,
        },
    )

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


async def test_extract_product(zyte_api_client, ecommerce_website):
    url = ecommerce_website.make_url("/product/1000")
    response_data = await zyte_api_client.get(
        {
            "url": str(url),
            "httpResponseBody": True,
            "product": True,
        },
    )

    assert "httpResponseBody" in response_data
    text = b64decode(response_data["httpResponseBody"]).decode("utf-8")
    assert "<h1>A Light in the Attic</h1>" in text

    assert "product" in response_data
    product = response_data["product"]
    descr = (
        "It's hard to imagine a world without A Light in the Attic. This"
        " now-classic collection of poetry and drawings from Shel Silverstein"
        " celebrates its 20th anniversary with this special edition."
        " Silverstein's humorous and creative verse can amuse the dowdiest of"
        " readers. Lemon-faced adults and fidgety kids sit still and read"
        " these rhythmic words and laugh and smile and love th It's hard to"
        " imagine a world without A Light in the Attic. This now-classic"
        " collection of poetry and drawings from Shel Silverstein celebrates"
        " its 20th anniversary with this special edition. Silverstein's"
        " humorous and creative verse can amuse the dowdiest of readers."
        " Lemon-faced adults and fidgety kids sit still and read these"
        " rhythmic words and laugh and smile and love that Silverstein. Need"
        " proof of his genius? RockabyeRockabye baby, in the treetopDon't you"
        " know a treetopIs no safe place to rock?And who put you up there,And"
        " your cradle, too?Baby, I think someone down here'sGot it in for you."
        " Shel, you never sounded so good. ...more"
    )
    assert product == {
        "url": str(url),
        "additionalProperties": [
            {"name": "UPC", "value": "a897fe39b1053632"},
            {"name": "Product Type", "value": "Books"},
            {"name": "Price (excl. tax)", "value": "£51.77"},
            {"name": "Price (incl. tax)", "value": "£51.77"},
            {"name": "Tax", "value": "£0.00"},
            {"name": "Availability", "value": "In stock (22 available)"},
            {"name": "Number of reviews", "value": "0"},
        ],
        "aggregateRating": {"bestRating": 5.0, "ratingValue": 3},
        "availability": "InStock",
        "breadcrumbs": [
            {"name": "Home", "url": str(url.join(URL("/")))},
            {
                "name": "Arts & Creativity",
                "url": str(url.join(URL("/category/1000"))),
            },
            {"name": "Poetry", "url": str(url.join(URL("/category/23")))},
            {"name": "A Light in the Attic"},
        ],
        "currencyRaw": "£",
        "description": descr,
        "descriptionHtml": f"<article>\n\n<p>{descr}</p>\n\n</article>",
        "metadata": {
            "dateDownloaded": product["metadata"]["dateDownloaded"],
            "probability": 1.0,
        },
        "name": "A Light in the Attic",
        "price": "51.77",
        "productId": "1000",
        "sku": "a897fe39b1053632",
    }


async def test_extract_product_list(zyte_api_client, ecommerce_website):
    url = ecommerce_website.make_url("/category/11")
    response_data = await zyte_api_client.get(
        {
            "url": str(url),
            "httpResponseBody": True,
            "productList": True,
        },
    )

    assert "httpResponseBody" in response_data
    text = b64decode(response_data["httpResponseBody"]).decode("utf-8")
    assert "<h1>Children&#39;s</h1>" in text

    assert "productList" in response_data
    product_list = response_data["productList"]
    products = [
        ("122", "Are We There Yet?", "10.66"),
        ("975", "Birdsong: A Story in Pictures", "54.64"),
        ("13", "Charlie and the Chocolate Factory (Charlie Bucket #1)", "22.85"),
        ("142", "Counting Thyme", "10.62"),
        (
            "99",
            "Diary of a Minecraft Zombie Book 1: A Scare of a Dare (An Unofficial Minecraft Book)",
            "52.88",
        ),
        ("165", "Green Eggs and Ham (Beginner Books B-16)", "10.79"),
        ("168", "Horrible Bear!", "37.52"),
        ("817", "Little Red", "13.47"),
        ("714", "Luis Paints the World", "53.95"),
        ("32", "Matilda", "28.34"),
    ]
    assert product_list == {
        "url": str(url),
        "breadcrumbs": [
            {"name": "Home", "url": str(url.join(URL("/")))},
            {
                "name": "Children's",
            },
        ],
        "categoryName": "Children's",
        "products": [
            {
                "currencyRaw": "£",
                "name": product[1],
                "price": product[2],
                "productId": product[0],
                "url": str(url.join(URL(f"/product/{product[0]}"))),
            }
            for product in products
        ],
        "paginationNext": {
            "text": "Next →",
            "url": str(url.join(URL("/category/11?page=2"))),
        },
        "pageNumber": 1,
        "metadata": {"dateDownloaded": product_list["metadata"]["dateDownloaded"]},
    }


async def test_extract_product_nav(zyte_api_client, ecommerce_website):
    url = ecommerce_website.make_url("/category/11")
    response_data = await zyte_api_client.get(
        {
            "url": str(url),
            "httpResponseBody": True,
            "productNavigation": True,
        },
    )

    assert "httpResponseBody" in response_data
    text = b64decode(response_data["httpResponseBody"]).decode("utf-8")
    assert "<h1>Children&#39;s</h1>" in text

    assert "productNavigation" in response_data
    product_navigation = response_data["productNavigation"]
    subcats = [
        ("20", "New Adult"),
        ("21", "Young Adult"),
    ]
    products = [
        ("122", "Are We There Yet?"),
        ("975", "Birdsong: A Story in Pictures"),
        ("13", "Charlie and the Chocolate Factory (Charlie Bucket #1)"),
        ("142", "Counting Thyme"),
        (
            "99",
            "Diary of a Minecraft Zombie Book 1: A Scare of a Dare (An Unofficial Minecraft Book)",
        ),
        ("165", "Green Eggs and Ham (Beginner Books B-16)"),
        ("168", "Horrible Bear!"),
        ("817", "Little Red"),
        ("714", "Luis Paints the World"),
        ("32", "Matilda"),
    ]
    assert product_navigation == {
        "url": str(url),
        "categoryName": "Children's",
        "items": [
            {
                "url": str(url.join(URL(f"/product/{product[0]}"))),
                "method": "GET",
                "name": product[1],
            }
            for product in products
        ],
        "nextPage": {
            "url": str(url.join(URL("/category/11?page=2"))),
            "method": "GET",
        },
        "subCategories": [
            {
                "url": str(url.join(URL(f"/category/{subcat[0]}"))),
                "method": "GET",
                "name": subcat[1],
            }
            for subcat in subcats
        ],
        "pageNumber": 1,
        "metadata": {
            "dateDownloaded": product_navigation["metadata"]["dateDownloaded"]
        },
    }


async def test_extract_article(zyte_api_client, articles_website):
    url = articles_website.make_url("/article/119")
    response_data = await zyte_api_client.get(
        {
            "url": str(url),
            "httpResponseBody": True,
            "article": True,
        },
    )

    assert "httpResponseBody" in response_data
    text = b64decode(response_data["httpResponseBody"]).decode("utf-8")
    assert '<h1 class="display-4">Nigeria to boost cocoa production</h1>' in text

    assert "article" in response_data
    article = response_data["article"]
    body = (
        "The government of Nigeria is hoping to triple cocoa production over"
        " the next three years with the launch of an ambitious development"
        " programme.  Agriculture Minister Adamu Bello said the scheme aimed"
        " to boost production from an expected 180,000 tonnes this year to"
        " 600,000 tonnes by 2008. The government will pump 154m naira ($1.1m;"
        " £591,000) into subsidies for farming chemicals and seedlings."
        " Nigeria is currently the world's fourth-largest cocoa producer."
        "  Cocoa was the main export product in Nigeria during the 1960s. But"
        " with the coming of oil, the government began to pay less attention"
        " to the cocoa sector and production began to fall from a peak of"
        " about 400,000 tonnes a year in 1970. At the launch of the programme"
        " in the south-western city of Ibadan, Mr Bello explained that an"
        " additional aim of the project is to encourage the processing of"
        " cocoa in the country and lift local consumption. He also announced"
        " that 91m naira of the funding available had been earmarked for"
        " establishing cocoa plant nurseries. The country could be looking to"
        " emulate rival Ghana, which produced a bumper crop last year."
        ' However, some farmers are sceptical about the proposals. "People'
        ' who are not farming will hijack the subsidy," said Joshua Osagie,'
        ' a cocoa farmer from Edo state told Reuters. "The farmers in the'
        ' village never see any assistance," he added.  At the same time as'
        " Nigeria announced its new initiative, Ghana - the world's second"
        " largest cocoa exporter - announced revenues from the industry had"
        " broken new records. The country saw more than $1.2bn-worth of the"
        " beans exported during 2003-04. Analysts said high tech-production"
        " techniques and crop spraying introduced by the government led to"
        " the huge crop, pushing production closer to levels seen in the 1960s"
        " when the country was the world's leading cocoa grower."
    )
    assert article == {
        "articleBody": body,
        "articleBodyHtml": f"<article>\n\n<p>{body}</p>\n\n</article>",
        "authors": [{"name": "Eve Wilson", "url": str(url.join(URL("/author/4")))}],
        "datePublished": "2024-06-21T00:00:00",
        "datePublishedRaw": "June 21, 2024",
        "description": (
            "The government of Nigeria is hoping to triple cocoa"
            " production over the next three years with the launch"
            " of an ambitious development programme"
        ),
        "headline": "Nigeria to boost cocoa production",
        "metadata": {
            "dateDownloaded": article["metadata"]["dateDownloaded"],
            "probability": 1.0,
        },
        "url": str(url),
    }


async def test_extract_article_nav(zyte_api_client, articles_website):
    url = articles_website.make_url("/articles/2")
    response_data = await zyte_api_client.get(
        {
            "url": str(url),
            "httpResponseBody": True,
            "articleNavigation": True,
        },
    )

    assert "httpResponseBody" in response_data
    text = b64decode(response_data["httpResponseBody"]).decode("utf-8")
    assert (
        '<h1 class="display-4">386 articles in the Entertainment category</h1>' in text
    )

    assert "articleNavigation" in response_data
    article_navigation = response_data["articleNavigation"]
    articles = [
        ("567", "Berlin hails European cinema"),
        ("746", "Singer Knight backs anti-gun song"),
        ("599", "Berlin cheers for anti-Nazi film"),
        ("778", "Michael film signals 'retirement'"),
        ("606", "Surprise win for anti-Bush film"),
        ("785", "Rocker Doherty in on-stage fight"),
        ("546", "Film row over Pirates 'cannibals'"),
        ("725", "Housewives lift Channel 4 ratings"),
        ("635", "Doves soar to UK album summit"),
        ("814", "The comic book genius of Stan Lee"),
    ]
    assert article_navigation == {
        "url": str(url),
        "categoryName": "Entertainment",
        "items": [
            {
                "url": str(url.join(URL(f"/article/{article[0]}"))),
                "method": "GET",
                "name": article[1],
            }
            for article in articles
        ],
        "nextPage": {"url": str(url.join(URL("/articles/2?page=2"))), "method": "GET"},
        "pageNumber": 1,
        "metadata": {
            "dateDownloaded": article_navigation["metadata"]["dateDownloaded"]
        },
    }
