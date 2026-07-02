"""
KMS Newsroom v2
News Formatter Service
"""


def get_category_label(category: str) -> str:
    mapping = {
        "politics": "Politics 🏛️",
        "crime": "Crime 🚔",
        "law_justice": "Law & Justice ⚖️",
        "world": "World 🌍",
        "india": "India 🇮🇳",
        "tamil_nadu": "Tamil Nadu 🌴",
        "business": "Business 💼",
        "economy": "Economy 📈",
        "education": "Education 🎓",
        "health": "Health 🏥",
        "technology": "Technology 💻",
        "sports": "Sports ⚽",
        "entertainment": "Entertainment 🎬",
        "weather": "Weather 🌦️",
        "general": "General 🧭",
    }
    return mapping.get(str(category).lower(), "General 🧭")


def get_news_type_label(news_type: str) -> str:
    mapping = {
        "breaking": "Breaking 🚨",
        "developing": "Developing Story 🔥",
        "regular": "Regular 🟢",
    }
    return mapping.get(str(news_type).lower(), "Regular 🟢")


def clean_value(value):
    if not value:
        return "Not Mentioned"

    value = str(value).strip()

    if value.lower() in ["unknown", "none", "null", "", "not mentioned"]:
        return "Not Mentioned"

    return value


def clean_headline(headline):
    headline = clean_value(headline)

    source_suffixes = [
        "BBC News தமிழ்",
        "BBC Tamil",
        "BBC News",
        "News7 Tamil",
        "News18 Tamil",
        "News18 தமிழ்",
        "Hindu Tamil Thisai",
        "The Hindu",
        "Dinamalar",
        "Daily Thanthi",
        "தினத்தந்தி",
        "தினமலர்",
        "Vikatan",
        "Times of India",
        "Indian Express",
        "Latest News",
        "Breaking News",
        "Live Updates",
    ]

    for source in source_suffixes:
        suffixes = [
            f" - {source}",
            f" | {source}",
            f" — {source}",
            f" – {source}",
            f": {source}",
        ]

        for suffix in suffixes:
            if headline.lower().endswith(suffix.lower()):
                headline = headline[: -len(suffix)].strip()

    return headline


def should_show(value):
    return clean_value(value) != "Not Mentioned"


def format_news(article_data: dict, source: str = "") -> str:
    headline = clean_headline(article_data.get("headline"))

    category = article_data.get("category", "general")
    news_type = article_data.get("news_type") or article_data.get("priority") or "regular"
    location = clean_value(article_data.get("location"))
    published = clean_value(article_data.get("published_date"))

    highlights = article_data.get("highlights", [])

    bullets = []

    for item in highlights[:4]:
        if item and str(item).strip():
            bullets.append(f"➜ {str(item).strip()}")

    if not bullets:
        bullets.append("➜ Not Mentioned")

    summary = "\n\n".join(bullets)

    footer_lines = [
        f"🏷️ <b>Category</b>: {get_category_label(category)}",
        f"📢 <b>News Type</b>: {get_news_type_label(news_type)}",
    ]

    if should_show(location):
        footer_lines.append(f"📍 <b>Location</b>: {location}")

    if should_show(published):
        footer_lines.append(f"📅 <b>Published On</b>: {published}")

    footer = "\n".join(footer_lines)

    return f"""
📰 <b>News Update</b>

{headline}

━━━━━━━━━━━━━━━━━━

📝 <b>Summary</b>

{summary}

━━━━━━━━━━━━━━━━━━

{footer}
""".strip()