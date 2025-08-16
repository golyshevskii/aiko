from traceback import format_exc
from uuid import NAMESPACE_OID, uuid5

from core.bot.command import call
from core.ai.agent import Aiko
from core.bot.message import msg
from core.bot.wrapper import access_required, typing_action
from core.bot.utils import send_message
from core.logger import get_logger
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

logger = get_logger(__name__)


@access_required
@typing_action
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Text message handler."""
    if not update.message or not update.message.text:
        return

    tg_user_id = update.effective_user.id
    username = update.effective_user.username or "unknown"
    chat_id = update.effective_chat.id
    message = update.message.text

    user_model = context.user_data.get("user_model")
    if not user_model:
        logger.error("User model not found in context for user %s", tg_user_id)
        await send_message(update, msg.ERROR_PROCESSING)
        return

    user_id = user_model.id

    logger.debug(
        "Processing message from user %s (tg_id=%s, user_id=%s) in chat %s...",
        username,
        tg_user_id,
        user_id,
        chat_id,
    )

    aiko = Aiko()

    try:
        response = await aiko.call(message, user_id, uuid5(NAMESPACE_OID, str(chat_id)))
        await send_message(update, response)
    except Exception:
        logger.error(
            "Error handling message from user %s (tg_id=%s, user_id=%s). Details: %s",
            username,
            tg_user_id,
            user_id,
            format_exc(),
        )
        await send_message(update, msg.ERROR_PROCESSING)
    finally:
        pass


def add_handlers(app: Application):
    """Add bot handlers."""
    app.add_handler(CommandHandler("call", call))
    app.add_handler(
        MessageHandler(
            (filters.TEXT | filters.VOICE | filters.AUDIO) & ~filters.COMMAND,
            handle_message,
        )
    )
