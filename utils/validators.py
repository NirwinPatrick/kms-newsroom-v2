"""
URL Validation Utilities
"""

import re

URL_PATTERN = re.compile(
    r"^(https?://)"
    r"(([A-Za-z0-9-]+\.)+[A-Za-z]{2,})"
    r"(/[^\s]*)?$",
    re.IGNORECASE,
)


def is_valid_url(text: str) -> bool:
    """
    Returns True if the supplied text is a valid HTTP/HTTPS URL.
    """

    if not text:
        return False

    return bool(URL_PATTERN.match(text.strip()))