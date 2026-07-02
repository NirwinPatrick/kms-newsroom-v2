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


def get_priority_label(priority: str) -> str:
    mapping = {
        "breaking": "BREAKING 🚨",
        "top_story": "TOP STORY 🔴",
        "latest": "LATEST 🟢",
    }
    return mapping.get(str(priority).lower(), "LATEST 🟢")


def clean_value(value):
    if not value:
        return "Not Mentioned"

    value = str(value).strip()

    if value.lower() in ["unknown", "none", "null", "", "not mentioned"]:
        return "Not Mentioned"

    return value


def clean_headline(headline):
    return clean_value(headline)


def should_show(value):
    return clean_value(value) != "Not Mentioned"


def format_news(article_data: dict, source: str = "") -> str:
    headline = clean_headline(article_data.get("headline"))

    category = article_data.get("category", "general")
    priority = article_data.get("priority", "latest")
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
        f"⭐ <b>Priority</b>: {get_priority_label(priority)}",
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