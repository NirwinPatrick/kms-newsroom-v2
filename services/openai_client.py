"""
KMS Newsroom v2
OpenAI AI Brain Layer - Tamil News Sub-Editor Prompt
"""

import json
import re
from openai import OpenAI


class OpenAIError(Exception):
    pass


MAX_ARTICLE_CHARS = 3500


SYSTEM_PROMPT = """
You are a professional Tamil news sub-editor.

Your job is NOT to create new news.
Your job is to prepare a clean Tamil newsroom bulletin from the given article.

Return STRICT JSON ONLY.

FORMAT:
{
  "headline": "",
  "category": "politics | crime | law_justice | world | india | tamil_nadu | business | economy | education | health | technology | sports | entertainment | weather | general",
  "news_type": "breaking | developing | regular",
  "location": "",
  "published_date": "",
  "highlights": ["", "", "", ""]
}

HEADLINE RULES:
- Preserve the real editorial headline.
- Remove SEO keywords, YouTube tags, topic tags, and keyword strings from the headline.
- Remove parts such as: "Mekadatu Issue", "TN vs Karnataka", "Congress Crisis", "TVK", "Breaking News", "Latest News", "Live Updates".
- Do not add your own headline unless the original headline is missing or unusable.
- If the headline is Tamil with English SEO keywords at the end, keep only the Tamil editorial headline.

SUMMARY RULES:
- Prepare exactly 4 summary points.
- Each point must contain one clear fact from the article.
- Prefer the article's own Tamil words and sentence structure.
- Compress and clean the article wording; do not invent new wording unnecessarily.
- Do not translate Tamil into another style.
- Do not add opinion, judgement, or vague statements.
- Avoid generic lines like "இந்த செய்தி முக்கியமானது".
- Avoid awkward phrases and machine-translation style Tamil.
- Each point should be short, natural, and suitable for WhatsApp news reading.

LANGUAGE QUALITY RULES:
- If the article is Tamil, output must be 100% natural Tamil.
- Never mix English, Korean, Hindi, Malayalam, or any other language inside Tamil summary sentences.
- Keep proper nouns as they appear in the article.
- Never use the word "கேசமாகியது".
- For burned/damaged houses, use natural Tamil such as "தீயில் எரிந்தன", "சாம்பலானது", or "சேதமடைந்தன".

NEWS TYPE RULES:
- Use "breaking" only for urgent major events that have just happened.
- Use "developing" for important ongoing stories where more updates are expected.
- Use "regular" for normal day-to-day news.
- If unsure, use "regular".
- Do not use "exclusive".
- Do not use "live".

CATEGORY RULES:
- Choose only one allowed category.
- Use "tamil_nadu" for Tamil Nadu state-level news.
- Use "india" for national Indian news.
- Use "world" for international news.
- Use "politics" when the main focus is political parties, leaders, elections, government conflict, or policy dispute.

LOCATION RULES:
- Read ORIGINAL_HEADLINE first, then ARTICLE.
- Extract the most relevant place mentioned in either the headline or article.
- Location can be city, district, state, country, or region.
- If a place is clearly mentioned, do not return "Not Mentioned".
- For Tamil articles, return the location in Tamil if it appears in Tamil.
- Use "Not Mentioned" only when no location is present in both headline and article.

PUBLISHED DATE RULES:
- If PUBLISHED_DATE_FROM_METADATA is provided, return that exact value.
- If no date is provided and no date is clearly mentioned in the article, use "Not Mentioned".
- Do not guess the date.

Return only valid JSON. No markdown. No explanation.
"""


BAD_TAMIL_REPLACEMENTS = {
    "கேசமாகியது": "சாம்பலானது",
    "கேசமாகிய": "சாம்பலான",
    "கேசமாகி": "சாம்பலாகி",
    "malt": "",
    "있다고": "",
}


def clean_json(text: str) -> str:
    match = re.search(r"\{.*\}", text, re.DOTALL)
    return match.group(0) if match else text


def parse_json_safe(text: str) -> dict:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return json.loads(clean_json(text))


def trim_article_text(article_text: str) -> str:
    text = article_text.strip()

    if len(text) <= MAX_ARTICLE_CHARS:
        return text

    trimmed = text[:MAX_ARTICLE_CHARS]

    endings = [".", "!", "?", "।", "。", "\n"]

    for ending in endings:
        if ending in trimmed:
            return trimmed.rsplit(ending, 1)[0].strip()

    return trimmed.strip()


def clean_tamil_quality(value):
    if isinstance(value, str):
        cleaned = value

        for bad, good in BAD_TAMIL_REPLACEMENTS.items():
            cleaned = cleaned.replace(bad, good)

        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        return cleaned

    if isinstance(value, list):
        return [clean_tamil_quality(item) for item in value]

    if isinstance(value, dict):
        return {key: clean_tamil_quality(item) for key, item in value.items()}

    return value


def normalize_news_type(data: dict) -> dict:
    news_type = data.get("news_type") or data.get("priority") or "regular"

    mapping = {
        "breaking": "breaking",
        "developing": "developing",
        "top_story": "developing",
        "latest": "regular",
        "regular": "regular",
        "news_update": "regular",
    }

    data["news_type"] = mapping.get(str(news_type).lower(), "regular")
    data.pop("priority", None)

    return data


def analyze_article(
    article_title: str,
    article_text: str,
    api_key: str,
    published_date: str | None = None,
) -> dict:
    try:
        client = OpenAI(api_key=api_key)

        user_input = f"""
ORIGINAL_HEADLINE:
{article_title}

PUBLISHED_DATE_FROM_METADATA:
{published_date or "Not Mentioned"}

ARTICLE:
{trim_article_text(article_text)}
"""

        response = client.responses.create(
            model="gpt-4o-mini",
            input=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_input},
            ],
        )

        if not response.output_text:
            raise OpenAIError("Empty response from OpenAI")

        parsed = parse_json_safe(response.output_text)
        parsed = normalize_news_type(parsed)
        return clean_tamil_quality(parsed)

    except Exception as error:
        raise OpenAIError(f"OpenAI processing failed: {error}") from error