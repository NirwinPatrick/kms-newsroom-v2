"""
KMS Newsroom v2
OpenAI AI Brain Layer - Speed Optimized + Tamil Quality Guard
"""

import json
import re
from openai import OpenAI


class OpenAIError(Exception):
    pass


MAX_ARTICLE_CHARS = 3000


SYSTEM_PROMPT = """
You are a professional Tamil newsroom editor.

Convert the given news article into STRICT JSON ONLY.

IMPORTANT EDITORIAL RULE:
- Do NOT rewrite the original headline.
- If a valid original headline is provided, return it exactly as given.
- Generate a headline only if the original headline is missing, empty, corrupted, or unusable.

FORMAT:
{
  "headline": "",
  "category": "politics | crime | law_justice | world | india | tamil_nadu | business | economy | education | health | technology | sports | entertainment | weather | general",
  "priority": "breaking | top_story | latest",
  "location": "",
  "published_date": "",
  "highlights": ["", "", "", ""]
}

LANGUAGE QUALITY RULES:
- If the article is Tamil, the output must be 100% natural Tamil.
- Never mix English, Korean, Hindi, Malayalam, or any other language inside Tamil sentences.
- Do not output broken foreign words.
- Do not produce unnatural Tamil words.
- Avoid awkward direct translations.
- Use simple, commonly used Tamil news language.
- Keep proper nouns as they appear in the article.
- Never use the word "கேசமாகியது".
- For burned/damaged houses, use natural Tamil such as "தீயில் எரிந்தன", "சாம்பலானது", or "சேதமடைந்தன".

LOCATION RULES:
- Read ORIGINAL_HEADLINE first, then ARTICLE.
- Extract the most relevant place mentioned in either the headline or article.
- Location can be city, district, state, country, or region.
- If the headline or article clearly mentions a place such as மணிப்பூர், தமிழ்நாடு, சென்னை, டெல்லி, பிரேசில், ரியோ டி ஜெனிரோ, பவானி, ஈரோடு, கன்னியாகுமரி, etc., return that location.
- For Tamil articles, return the location in Tamil if the place appears in Tamil.
- Do NOT return "Not Mentioned" when a place is clearly present in the headline.
- Use "Not Mentioned" only when no location is present in both the headline and article.

PUBLISHED DATE RULES:
- If PUBLISHED_DATE_FROM_METADATA is provided, return that exact value.
- If no date is provided and no date is clearly mentioned in the article, use "Not Mentioned".
- Do not guess the date.

SUMMARY RULES:
- Return only JSON.
- No explanation outside JSON.
- category must be only one allowed value.
- priority must be only one of: breaking, top_story, latest.
- Provide exactly 4 concise factual highlights.
- Each highlight must be short and reader-friendly.
- Do not add opinion.
- Do not exaggerate.
- Keep output in the same language as the article.
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
        return {
            key: clean_tamil_quality(item)
            for key, item in value.items()
        }

    return value


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
        return clean_tamil_quality(parsed)

    except Exception as error:
        raise OpenAIError(f"OpenAI processing failed: {error}") from error