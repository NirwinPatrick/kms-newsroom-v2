"""
KMS Newsroom v2
Hybrid Article Extraction Engine
"""

from dataclasses import dataclass

import httpx
import trafilatura


@dataclass
class Article:
    title: str
    text: str
    url: str


class ArticleExtractionError(Exception):
    """Raised when article extraction fails."""


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0 Safari/537.36"
    )
}


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

    metadata = trafilatura.extract_metadata(html)
    if metadata and metadata.title:
        title = metadata.title.strip()

    return Article(
        title=title,
        text=text.strip(),
        url=final_url,
    )