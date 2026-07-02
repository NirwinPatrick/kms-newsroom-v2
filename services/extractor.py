"""
KMS Newsroom v2
Hybrid Article Extraction Engine
"""

from dataclasses import dataclass
from datetime import datetime
import json
import re

import httpx
import trafilatura
from bs4 import BeautifulSoup


@dataclass
class Article:
    title: str
    text: str
    url: str
    published_date: str | None = None


class ArticleExtractionError(Exception):
    """Raised when article extraction fails."""


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0 Safari/537.36"
    )
}


DATE_META_KEYS = [
    "article:published_time",
    "article:modified_time",
    "og:published_time",
    "pubdate",
    "publishdate",
    "publish_date",
    "date",
    "dc.date",
    "dc.date.issued",
    "datepublished",
    "datePublished",
    "sailthru.date",
]


def download_html(url: str) -> tuple[str, str]:
    """
    Download webpage HTML and return final redirected URL.
    """

    try:
        with httpx.Client(
            headers=HEADERS,
            follow_redirects=True,
            timeout=25,
        ) as client:
            response = client.get(url)

        if response.status_code != 200:
            raise ArticleExtractionError(
                f"HTTP Error: {response.status_code}"
            )

        return response.text, str(response.url)

    except Exception as error:
        raise ArticleExtractionError(
            f"Download failed: {error}"
        ) from error


def clean_date(date_value: str | None) -> str | None:
    """
    Converts common published date formats into readable date.
    """

    if not date_value:
        return None

    value = str(date_value).strip()

    if not value:
        return None

    value = value.replace("Z", "+00:00")

    try:
        parsed = datetime.fromisoformat(value)
        return parsed.strftime("%d %b %Y")
    except ValueError:
        pass

    date_patterns = [
        r"\d{4}-\d{2}-\d{2}",
        r"\d{2}/\d{2}/\d{4}",
        r"\d{2}-\d{2}-\d{4}",
    ]

    for pattern in date_patterns:
        match = re.search(pattern, value)
        if match:
            return match.group(0)

    return value


def extract_date_from_json_ld(soup: BeautifulSoup) -> str | None:
    """
    Extract published date from JSON-LD structured data.
    """

    scripts = soup.find_all("script", type="application/ld+json")

    for script in scripts:
        try:
            raw_json = script.string or script.get_text()
            if not raw_json:
                continue

            data = json.loads(raw_json)

            candidates = data if isinstance(data, list) else [data]

            for item in candidates:
                if not isinstance(item, dict):
                    continue

                if "@graph" in item and isinstance(item["@graph"], list):
                    candidates.extend(item["@graph"])

                date_value = (
                    item.get("datePublished")
                    or item.get("dateCreated")
                    or item.get("dateModified")
                )

                cleaned = clean_date(date_value)
                if cleaned:
                    return cleaned

        except Exception:
            continue

    return None


def extract_published_date(html: str) -> str | None:
    """
    Extract published date from meta tags and JSON-LD.
    """

    soup = BeautifulSoup(html, "html.parser")

    for key in DATE_META_KEYS:
        meta = (
            soup.find("meta", property=key)
            or soup.find("meta", attrs={"name": key})
            or soup.find("meta", attrs={"itemprop": key})
        )

        if meta:
            content = meta.get("content")
            cleaned = clean_date(content)
            if cleaned:
                return cleaned

    json_ld_date = extract_date_from_json_ld(soup)
    if json_ld_date:
        return json_ld_date

    time_tag = soup.find("time")
    if time_tag:
        cleaned = clean_date(
            time_tag.get("datetime") or time_tag.get_text()
        )
        if cleaned:
            return cleaned

    return None


def extract_article(url: str) -> Article:
    """
    Extract article text and metadata.
    """

    html, final_url = download_html(url)

    if not html:
        raise ArticleExtractionError(
            "Empty response from website."
        )

    text = trafilatura.extract(
        html,
        include_comments=False,
        include_tables=False,
        include_links=False,
        favor_precision=True,
    )

    if not text or len(text.strip()) < 300:
        raise ArticleExtractionError(
            "This doesn't appear to be a valid news article."
        )

    title = ""
    published_date = extract_published_date(html)

    metadata = trafilatura.extract_metadata(html)
    if metadata:
        if metadata.title:
            title = metadata.title.strip()

        if not published_date and metadata.date:
            published_date = clean_date(metadata.date)

    return Article(
        title=title,
        text=text.strip(),
        url=final_url,
        published_date=published_date,
    )