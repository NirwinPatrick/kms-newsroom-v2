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


def clean_value(value):
    if not value or str(value).strip().lower() in [
        "unknown",
        "none",
        "null",
        "",
    ]:
        return "Not Mentioned"
    return str(value).strip()


def clean_headline(headline, source):
    headline = clean_value(headline)
    source = clean_value(source)

    if source == "Not Mentioned":
        return headline

    suffixes = [
        f" - {source}",
        f" | {source}",
        f" — {source}",
        f" – {source}",
    ]

    for suffix in suffixes:
        if headline.lower().endswith(suffix.lower()):
            return headline[:-len(suffix)].strip()

    return headline


def format_news(article_data: dict, source: str) -> str:
    source = clean_value(source)
    headline = clean_headline(article_data.get("headline"), source)

    category = article_data.get("category", "general")
    priority = article_data.get("priority", "latest")
    location = clean_value(article_data.get("location"))
    published_date = clean_value(article_data.get("published_date"))
    highlights = article_data.get("highlights", [])

    bullets = []

    for item in highlights[:3]:
        if item and str(item).strip():
            bullets.append(f"🔹 {str(item).strip()}")

    if not bullets:
        bullets.append("🔹 Not Mentioned")

    highlights_text = "\n\n".join(bullets)

    return f"""
📰 <b>Headline</b>

<b>{source}</b> — {headline}

━━━━━━━━━━━━━━━━━━

📌 <b>Key Highlights</b>

{highlights_text}

━━━━━━━━━━━━━━━━━━

🏷️ <b>Category</b> : {get_category_label(category)}
⭐ <b>Priority</b> : {get_priority_label(priority)}
📍 <b>Location</b> : {location}
📅 <b>Published On</b> : {published_date}
""".strip()