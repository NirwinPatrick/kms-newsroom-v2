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
    return mapping.get(category.lower(), "General 🧭")


def get_priority_label(priority: str) -> str:
    mapping = {
        "breaking": "BREAKING 🚨",
        "top_story": "TOP STORY 🔴",
        "latest": "LATEST 🟢",
    }
    return mapping.get(priority.lower(), "LATEST 🟢")


def clean_value(value):
    if not value:
        return "Not Mentioned"

    value = str(value).strip()

    if value.lower() in ["unknown", "none", "null", ""]:
        return "Not Mentioned"

    return value


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
            headline = headline[:-len(suffix)].strip()

    return headline


def format_news(article_data: dict, source: str):

    source = clean_value(source)
    headline = clean_headline(article_data.get("headline"), source)

    category = article_data.get("category", "general")
    priority = article_data.get("priority", "latest")
    location = clean_value(article_data.get("location"))
    published = clean_value(article_data.get("published_date"))

    highlights = article_data.get("highlights", [])

    bullets = []

    for item in highlights[:4]:
        if item and str(item).strip():
            bullets.append(f"➜ {item.strip()}")

    if not bullets:
        bullets.append("➜ Not Mentioned")

    summary = "\n\n".join(bullets)

    return f"""
🗞️ <b>News Brief</b>

{headline}

━━━━━━━━━━━━━━━━━━

📝 <b>Summary</b>

{summary}

━━━━━━━━━━━━━━━━━━

🏷️ <b>Category</b>: {get_category_label(category)}
⭐ <b>Priority</b>: {get_priority_label(priority)}
📍 <b>Location</b>: {location}
📅 <b>Published</b>: {published}
📰 <b>Source</b>: {source}
""".strip()