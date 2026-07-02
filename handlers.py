"""
KMS Newsroom v2
Telegram Handlers - OpenAI Integrated Version
"""

import os

from telegram import Update
from telegram.ext import ContextTypes

from utils.validators import is_valid_url
from services.extractor import extract_article, ArticleExtractionError
from services.source_detector import detect_source
from services.openai_client import analyze_article, OpenAIError
from services.formatter import format_news


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📰 KMS Newsroom v2\n\n"
        "Send me one news article URL to analyze."
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 KMS Newsroom v2\n\n"
        "Send one direct news article URL.\n\n"
        "The bot will extract, analyze, and summarize the article."
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.message is None or update.message.text is None:
        return

    url = update.message.text.strip()

    if not is_valid_url(url):
        await update.message.reply_text(
            "❌ Please send one valid news article URL."
        )
        return

    if not OPENAI_API_KEY:
        await update.message.reply_text(
            "❌ OpenAI API key is missing.\n\n"
            "Please set OPENAI_API_KEY in your environment."
        )
        return

    status_message = await update.message.reply_text(
        "🛡️ காவலர் மக்கள் செய்தி\n\n"
        "⏳ Fetching article..."
    )

    try:
        await status_message.edit_text(
            "🛡️ காவலர் மக்கள் செய்தி\n\n"
            "🌐 Resolving & extracting article..."
        )

        article = extract_article(url)
        source = detect_source(article.url)

        await status_message.edit_text(
            "🛡️ காவலர் மக்கள் செய்தி\n\n"
            "🤖 Analyzing with AI..."
        )

        article_json = analyze_article(
            article_title=article.title,
            article_text=article.text,
            api_key=OPENAI_API_KEY,
        )

        if article.title and article.title.strip():
            article_json["headline"] = article.title.strip()

        final_output = format_news(article_json, source)

        await status_message.edit_text(
            final_output,
            parse_mode="HTML",
            disable_web_page_preview=True,
        )

    except ArticleExtractionError as error:
        await status_message.edit_text(
            "❌ This doesn't appear to be a news article.\n\n"
            f"Reason:\n{error}"
        )

    except OpenAIError as error:
        await status_message.edit_text(
            "❌ AI analysis failed\n\n"
            f"{error}"
        )

    except Exception as error:
        await status_message.edit_text(
            "❌ Unexpected error\n\n"
            f"{error}"
        )