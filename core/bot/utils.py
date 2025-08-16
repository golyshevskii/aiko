from core.logger import get_logger
from telegram import Update
from telegram.error import BadRequest

logger = get_logger(__name__)


async def send_message(
    update: Update, text: str, reply_markup: None = None, parse_mode: str = "MarkdownV2"
) -> None:
    """Safe message sending with fallback to plain text."""
    try:
        await update.message.reply_text(
            text, parse_mode=parse_mode, reply_markup=reply_markup
        )
    except BadRequest as e:
        if "parse" in str(e).lower():
            logger.warning("MarkdownV2 parse error, sending as plain text: %s", str(e))
            await update.message.reply_text(text, reply_markup=reply_markup)
        else:
            raise
