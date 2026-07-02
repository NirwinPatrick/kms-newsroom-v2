"""
KMS Newsroom v2
Source Detection Service
"""

from urllib.parse import urlparse


SOURCE_MAP = {
    "bbc.com": "BBC",
    "www.bbc.com": "BBC",
    "reuters.com": "Reuters",
    "www.reuters.com": "Reuters",
    "thehindu.com": "The Hindu",
    "www.thehindu.com": "The Hindu",
    "dinamalar.com": "Dinamalar",
    "www.dinamalar.com": "Dinamalar",
    "news7tamil.live": "News7 Tamil",
    "www.news7tamil.live": "News7 Tamil",
    "indiatoday.in": "India Today",
    "www.indiatoday.in": "India Today",
    "timesofindia.indiatimes.com": "Times of India",
}


def detect_source(url: str) -> str:
    """
    Extracts a human-readable source name from URL.
    """

    try:
        domain = urlparse(url).netloc.lower()

        # direct match
        if domain in SOURCE_MAP:
            return SOURCE_MAP[domain]

        # partial match fallback
        for key, name in SOURCE_MAP.items():
            if key in domain:
                return name

        # fallback cleanup
        return domain.replace("www.", "").split(".")[0].title()

    except Exception:
        return "Unknown"