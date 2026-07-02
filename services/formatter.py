"""
KMS Newsroom v2
News Formatter Service
"""


def get_category_label(category: str) -> str:
    mapping = {
        "politics": "🏛️ Politics",
        "crime": "🚔 Crime",
        "law_justice": "⚖️ Law & Justice",
        "world": "🌍 World",
        "india": "🇮🇳 India",
        "tamil_nadu": "🌴 Tamil Nadu",
        "business": "💼 Business",
        "economy": "📈 Economy",
        "education": "🎓 Education",
        "health": "🏥 Health",
        "technology": "💻 Technology",
        "sports": "⚽ Sports",
        "entertainment": "🎬 Entertainment",
        "weather": "🌦️ Weather",
        "general": "🧭 General",
    }
    return mapping.get(category, "🧭 General")


def get_priority_label(priority: str) -> str:
    mapping = {
        "breaking": "🚨 BREAKING",
        "top_story": "🔴 TOP STORY",
        "latest": "🟢 LATEST",
    }
    return mapping.get(priority, "🟢 LATEST")


def clean_value(value: str | None) -> str:
    if not value or str(value).strip().lower() in ["unknown", "none", "null", ""]:
        return "Not Mentioned"
    return str(value).strip()


def clean_headline(headline: str, source: str) -> str:
    """
    Removes duplicated publisher suffix from headline.
    Example:
    'Election announced - News7 Tamil' -> 'Election announced'
    """

    headline = clean_value(headline)
    source = clean_value(source)

    if source == "Not Mentioned":
        return headline

    possible_suffixes = [
        f" - {source}",
        f" | {source}",
        f" — {source}",
        f" – {source}",
    ]

    for suffix in possible_suffixes:
        if headline.lower().endswith(suffix.lower()):
            return headline[: -len(suffix)].strip()

    return headline


def format_news(article_data: dict, source: str) -> str:
    source = clean_value(source)
    headline = clean_headline(article_data.get("headline"), source)

    category = article_data.get("category", "general")
    priority = article_data.get("priority", "latest")
    location = clean_value(article_data.get("location"))
    published_date = clean_value(article_data.get("published_date"))
    highlights = article_data.get("highlights", [])

    highlight_lines = []
    for item in highlights[:3]:
        if item and str(item).strip():
            highlight_lines.append(f"🔹 {str(item).strip()}")

    if not highlight_lines:
        highlight_lines.append("🔹 Not Mentioned")

    highlight_text = "\n\n".join(highlight_lines)

    return f"""
━━━━━━━━━━━━━━━━━━

         🛡️ <b>காவலர் மக்கள் செய்தி</b>

━━━━━━━━━━━━━━━━━━

📰 <b>Headline</b>

<b>{source}</b> — {headline}

━━━━━━━━━━━━━━━━━━

🏷️ <b>Category</b> : {get_category_label(category)}
⭐ <b>Priority</b> : {get_priority_label(priority)}
📍 <b>Location</b> : {location}
📅 <b>Published On</b> : {published_date}

━━━━━━━━━━━━━━━━━━

📌 <b>Key Highlights</b>

{highlight_text}
""".strip()