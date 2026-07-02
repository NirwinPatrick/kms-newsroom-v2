"""
KMS Newsroom v2
OpenAI AI Brain Layer - Tamil Extractive News Brief
"""

import json
import re
from openai import OpenAI


class OpenAIError(Exception):
    pass


MAX_ARTICLE_CHARS = 4500


SYSTEM_PROMPT = """
You are a professional Tamil news sub-editor.

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

CORE RULE:
- Do not freely invent or rewrite the news.
- For highlights, use facts and wording from the ARTICLE as much as possible.
- Compress article sentences instead of creating new sentences.

HEADLINE RULES:
- Preserve the real Tamil editorial headline.
- Remove English SEO/tag text at the end of the headline.
- Remove text such as: "Mekadatu Issue", "TN vs Karnataka", "Congress Crisis", "TVK", "Breaking News", "Latest News", "Live Updates".
- If the headline is Tamil followed by English keywords, keep only the Tamil part.

HIGHLIGHT RULES:
- Give exactly 4 highlights.
- Each highlight must be one clear factual point from the article.
- Each highlight must sound like a Tamil news sentence.
- Prefer words already present in the article.
- Do not add new claims.
- Do not add analysis.
- Do not add opinion.
- Do not write vague lines like "இந்த செய்தி முக்கியமானது".
- Do not create awkward machine-translated Tamil.
- Do not mention facts unless they are clearly present in the article.
- If the article has fewer than 4 strong facts, split existing factual details cleanly.

BAD TAMIL RULES:
Never use these bad/awkward words or phrases:
- கேசமாகியது
- குற malt
- இணையோ பார்வையில்
- நினைவில் முக்கியமான ஒன்று
- சொந்தத்தமிழக
- கட்டச் சேர்ந்த நிலை

Use natural Tamil wording:
- தீயில் எரிந்தன
- சாம்பலானது
- சேதமடைந்தன
- கட்ட முயன்றால்
- எதிர்ப்பு தெரிவிக்கப்படும்
- போராட்டம் நடத்தப்படும்

LANGUAGE RULES:
- If article is Tamil, output must be fully Tamil.
- Do not mix English, Korean, Hindi, Malayalam, or broken foreign words in Tamil summary.
- Proper nouns can remain as in the article.

NEWS TYPE RULES:
- breaking: only urgent major events that just happened.
- developing: important ongoing issue where more updates are expected.
- regular: normal news update.
- If unsure, use regular.

CATEGORY RULES:
- Choose only one allowed category.
- Use "tamil_nadu" only when the story is primarily about Tamil Nadu state, Tamil Nadu government, Tamil Nadu districts, Tamil Nadu politics, Tamil Nadu weather, or Tamil Nadu public issues.
- Do NOT use "tamil_nadu" merely because the article is written in Tamil.
- Use "india" for national Indian stories, Ayodhya, Ram Mandir, RSS, VHP, BJP national leadership, Union Government, Supreme Court, Parliament, national agencies, and all-India issues.
- Use "world" for international news.
- Use "politics" when the main focus is political parties, leaders, elections, government conflict, or policy dispute and it is not specifically Tamil Nadu-only.
- Use "crime" for theft, murder, robbery, assault, fraud, police cases, arrests, or criminal investigations.
- Use "law_justice" for court orders, legal disputes, judgments, or justice system stories.

LOCATION RULES:
- Extract the clearest place from headline or article.
- Prefer specific location in this order: city/town/village, district, state, country.
- For Ayodhya/Ram temple stories, use "அயோத்தி, உத்தரப் பிரதேசம்" if no more specific place is available.
- For Manipur stories, use "மணிப்பூர்".
- For Tamil Nadu state-level stories, use "தமிழ்நாடு".
- If a district/city is clearly mentioned, return it.
- If no place is found, use "Not Mentioned".

PUBLISHED DATE RULES:
- If PUBLISHED_DATE_FROM_METADATA is provided, return that exact value.
- Otherwise use "Not Mentioned".
"""


BAD_REPLACEMENTS = {
    "கேசமாகியது": "சாம்பலானது",
    "கேசமாகிய": "சாம்பலான",
    "கேசமாகி": "சாம்பலாகி",
    "குற malt": "குற்றச்சாட்டு",
    "malt": "",
    "있다고": "",
    "இணையோ பார்வையில்": "",
    "நினைவில் முக்கியமான ஒன்று": "",
    "சொந்தத்தமிழக": "தமிழக",
    "கட்டச் சேர்ந்த நிலை": "கட்ட முயன்றால்",
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
    for ending in [".", "!", "?", "\n"]:
        if ending in trimmed:
            return trimmed.rsplit(ending, 1)[0].strip()

    return trimmed.strip()


def clean_text(value):
    if isinstance(value, str):
        text = value
        for bad, good in BAD_REPLACEMENTS.items():
            text = text.replace(bad, good)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    if isinstance(value, list):
        return [clean_text(item) for item in value]

    if isinstance(value, dict):
        return {key: clean_text(item) for key, item in value.items()}

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
            temperature=0,
        )

        if not response.output_text:
            raise OpenAIError("Empty response from OpenAI")

        parsed = parse_json_safe(response.output_text)
        parsed = normalize_news_type(parsed)
        return clean_text(parsed)

    except Exception as error:
        raise OpenAIError(f"OpenAI processing failed: {error}") from error