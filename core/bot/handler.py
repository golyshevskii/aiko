from traceback import format_exc
from uuid import NAMESPACE_OID, uuid5

from core.bot.command import call, start, faq, FAQ
from core.ai.agent import POOL, AgentDependencies
from core.ai.supervisor import SUPERVISOR
from core.bot.message import msg
from core.bot.wrapper import access_required, typing_action, register_user
from core.bot.utils import send_message, add_message, answer_callback_query_with_error
from core.db.manager import ScoreManager, UserManager
from core.logger import get_logger
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    CallbackQueryHandler,
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
        await send_message(update, msg.ERROR)
        return

    user_id = user_model.id
    conversation_id = uuid5(NAMESPACE_OID, str(chat_id))

    logger.debug(
        "Processing message from user %s (tg_id=%s, user_id=%s) in chat %s...",
        username,
        tg_user_id,
        user_id,
        chat_id,
    )

    try:
        aiko = await POOL.get_instance()
        response: str = await aiko.call(
            message,
            AgentDependencies(
                user_id=user_id,
                username=username,
                conversation_id=conversation_id,
            ),
        )
        await send_message(update, response)
    except Exception:
        logger.error(
            "Error handling message from user %s (tg_id=%s, user_id=%s). Details: %s",
            username,
            tg_user_id,
            user_id,
            format_exc(),
        )
        await send_message(update, msg.ERROR)
    else:
        await UserManager.revoke_access(user_id)
        await add_message(user_id, conversation_id, message, response)

        score: int = await SUPERVISOR.call(message, response)
        await ScoreManager.update_score(user_id, score)
    finally:
        await POOL.return_instance(aiko)


@register_user
async def handler_faq_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle FAQ callback queries."""
    query = update.callback_query
    if not query or not query.data:
        return

    try:
        await query.answer()  # Remove loading indicator

        user_id = update.effective_user.id
        username = update.effective_user.username
        callback_data = query.data

        logger.debug(
            "User %s (%s) pressed FAQ button: %s", username, user_id, callback_data
        )

        if callback_data == "faq_back":
            # Return to questions list
            keyboard = []
            for item in FAQ.ITEMS:
                keyboard.append(
                    [
                        InlineKeyboardButton(
                            item.question, callback_data=f"faq_{item.id}"
                        )
                    ]
                )

            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_text(
                msg.FAQ_TITLE, parse_mode="Markdown", reply_markup=reply_markup
            )

        elif callback_data.startswith("faq_"):
            # Show answer to specific question
            faq_id = callback_data[4:]  # Remove "faq_" prefix
            faq_item = FAQ.get_item_by_id(faq_id)

            if faq_item:
                # Create "Back" button
                keyboard = [
                    [
                        InlineKeyboardButton(
                            msg.FAQ_BACK_BUTTON, callback_data="faq_back"
                        )
                    ]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)

                await query.edit_message_text(
                    faq_item.answer, parse_mode="MarkdownV2", reply_markup=reply_markup
                )
            else:
                logger.warning("FAQ item not found: %s", faq_id)
                await answer_callback_query_with_error(update, "Question not found")

    except Exception:
        logger.error("Error in FAQ callback handler: %s", format_exc())
        await answer_callback_query_with_error(update)


def add_handlers(app: Application):
    """Add bot handlers."""
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("call", call))
    app.add_handler(CommandHandler("faq", faq))

    app.add_handler(CallbackQueryHandler(handler_faq_callback, pattern="^faq_"))
    app.add_handler(
        MessageHandler(
            (filters.TEXT | filters.VOICE | filters.AUDIO) & ~filters.COMMAND,
            handle_message,
        )
    )
