from core.bot.message import msg
from core.bot.utils import send_message
from core.bot.wrapper import register_user
from core.logger import get_logger
from core.settings import settings
from core.schema.bot import Command
from core.schema.db import UserStatus
from telegram import BotCommand, Update
from telegram.ext import Application, ContextTypes

logger = get_logger(__name__)


@register_user
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Respond to /start command."""
    user_id = update.effective_user.id
    username = update.effective_user.username

    logger.debug("User %s (%s) started the bot", username, user_id)

    user_model = context.user_data.get("user_model")
    if user_model and user_model.status == UserStatus.ACTIVE:
        welcome_msg = msg.CALL
    else:
        welcome_msg = msg.START.format(
            username=username, token_url=settings.APP_TOKEN_BUY_URL
        )

    await send_message(update, welcome_msg)


@register_user
async def call(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Respond to /call command."""
    user_id = update.effective_user.id
    username = update.effective_user.username

    logger.debug("User %s (%s) called Aiko", username, user_id)

    user_model = context.user_data.get("user_model")
    if user_model and user_model.status == UserStatus.ACTIVE:
        welcome_msg = msg.CALL
    else:
        welcome_msg = msg.CALL_INACTIVE.format(token_url=settings.APP_TOKEN_BUY_URL)

    await send_message(update, welcome_msg)


async def add_commands(app: Application):
    """Add bot commands menu."""
    commands = [
        BotCommand(Command.CALL.value, Command.CALL.desc),
    ]
    await app.bot.set_my_commands(commands)
