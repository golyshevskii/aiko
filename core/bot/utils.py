from uuid import UUID

from core.logger import get_logger
from telegram import Update
from telegram.error import BadRequest
from core.db.manager import ConversationManager
from core.schema.ai import MessageRole

logger = get_logger(__name__)


async def send_message(
    update: Update, text: str, reply_markup: None = None, parse_mode: str = "MarkdownV2"
) -> None:
    """Safe message sending with fallback to plain text."""
    try:
        if update.callback_query:
            # For callback queries, send a new message
            await update.callback_query.message.reply_text(
                text, parse_mode=parse_mode, reply_markup=reply_markup
            )
        else:
            # For regular messages
            await update.message.reply_text(
                text, parse_mode=parse_mode, reply_markup=reply_markup
            )
    except BadRequest as e:
        if "parse" in str(e).lower():
            logger.warning("MarkdownV2 parse error, sending as plain text: %s", str(e))
            if update.callback_query:
                await update.callback_query.message.reply_text(
                    text, reply_markup=reply_markup
                )
            else:
                await update.message.reply_text(text, reply_markup=reply_markup)
        else:
            raise


async def answer_callback_query_with_error(update: Update, text: str = None) -> None:
    """Send error response for callback query."""
    if update.callback_query:
        await update.callback_query.answer(
            text or "An error occurred\\. Please try again\\.", show_alert=True
        )


async def add_message(user_id: int, conversation_id: UUID, message: str, response: str):
    # Ensure conversation exists before adding message
    await ConversationManager.get_conversation(
        user_id=user_id, conversation_id=conversation_id
    )
    await ConversationManager.add_message(
        conversation_id=conversation_id, role=MessageRole.USER, message=message
    )
    await ConversationManager.add_message(
        conversation_id=conversation_id, role=MessageRole.AGENT, message=response
    )
