"""
KMS Newsroom v2
OpenAI AI Brain Layer - Speed Optimized
"""

import json
import re
from openai import OpenAI


class OpenAIError(Exception):
    pass


MAX_ARTICLE_CHARS = 2500


SYSTEM_PROMPT = """
You are a professional newsroom editor.

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

RULES:
- Return only JSON.
- No explanation outside JSON.
- category must be only one allowed value.
- priority must be only one of: breaking, top_story, latest.
- Provide exactly 4 concise factual highlights.
- Each highlight must be short and reader-friendly.
- Do not add opinion.
- Do not exaggerate.
- Do not mix languages inside a sentence.
- If location is not mentioned, use "Not Mentioned".
- If published date is not mentioned, use "Not Mentioned".
- Keep output in the same language as the article.
"""


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

    if "." in trimmed:
        return trimmed.rsplit(".", 1)[0]

    return trimmed


def analyze_article(article_title: str, article_text: str, api_key: str) -> dict:
    try:
        client = OpenAI(api_key=api_key)

        user_input = f"""
ORIGINAL_HEADLINE:
{article_title}

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

        return parse_json_safe(response.output_text)

    except Exception as error:
        raise OpenAIError(f"OpenAI processing failed: {error}") from error