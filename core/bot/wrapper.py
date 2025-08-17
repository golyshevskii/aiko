import asyncio
from traceback import format_exc
from collections.abc import Callable
from functools import wraps

from core.bot.message import msg
from core.bot.utils import send_message
from core.db.init import get_session
from core.schema.db import UserStatus
from core.db.schema import User
from core.logger import get_logger
from core.schema.bot import ChatAction
from telegram import Update
from telegram.ext import ContextTypes
from core.settings import settings

logger = get_logger(__name__)


class TypingIndicator:
    """Typing indicator management for bot responses."""

    @staticmethod
    async def send_chat_action(
        update: Update, action: ChatAction = ChatAction.TYPING
    ) -> None:
        try:
            await update.effective_chat.send_chat_action(action=action.value)
        except Exception as e:
            logger.warning("Failed to send chat action '%s': %s", action, str(e))

    @staticmethod
    async def chat_action_task(
        update: Update, action: ChatAction, stop_event: asyncio.Event
    ) -> None:
        """Send chat action periodically every 4 seconds until stop event is set."""
        while not stop_event.is_set():
            await TypingIndicator.send_chat_action(update, action)
            try:
                # Wait 4 seconds or until stop event is set
                await asyncio.wait_for(stop_event.wait(), timeout=4.0)
                break  # If stop_event is set, exit
            except TimeoutError:
                # Timeout is normal, continue showing indicator
                continue

    @staticmethod
    def chat_action(action: ChatAction = ChatAction.TYPING):
        """Set main function to show chat action indicator during execution."""

        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def wrapper(
                update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs
            ):
                if not update.effective_chat:
                    logger.warning("No effective chat in update")
                    return await func(update, context, *args, **kwargs)

                # Create event to stop chat action indicator
                stop_action = asyncio.Event()

                # Send initial indicator and start task to update it
                await TypingIndicator.send_chat_action(update, action)
                action_task = asyncio.create_task(
                    TypingIndicator.chat_action_task(update, action, stop_action)
                )

                try:
                    # Execute main function
                    result = await func(update, context, *args, **kwargs)

                    # Stop chat action indicator
                    stop_action.set()
                    await action_task

                    return result

                except Exception as e:
                    # Stop chat action indicator in case of error
                    stop_action.set()
                    await action_task

                    # Pass exception further
                    raise e

            return wrapper

        return decorator

    @staticmethod
    def typing_action(func: Callable) -> Callable:
        return TypingIndicator.chat_action()(func)


class AccessControl:
    """Access control for users to the bot."""

    @staticmethod
    async def get_or_create_user(tg_id: int, tg_username: str | None = None) -> User:
        """Get or create user."""
        async for session in get_session():
            # Try to find existing user
            from sqlalchemy import select

            stmt = select(User).where(User.tg_id == tg_id)
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()

            if user:
                # Update username if changed
                if user.tg_username != tg_username:
                    user.tg_username = tg_username
                    await session.commit()
                    logger.debug("Updated username for user %s: %s", tg_id, tg_username)

                return user

            # Create new user with default subscription
            user = User(tg_id=tg_id, tg_username=tg_username)
            session.add(user)
            await session.commit()
            await session.refresh(user)

            logger.info(
                "Created new user %s (%s) with inactive status", tg_id, tg_username
            )
            return user

    @staticmethod
    async def check_user_access(user: User) -> bool:
        """Check user access to the bot."""
        # Administrators (subscription = -1) have full access
        # Users with active status (1) have access
        return user.status == UserStatus.ACTIVE

    @staticmethod
    def access_required(func: Callable) -> Callable:
        """Check user access to the bot."""

        @wraps(func)
        async def wrapper(
            update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs
        ):
            if not update.effective_user:
                logger.warning("No effective user in update")
                return

            user_id = update.effective_user.id
            username = update.effective_user.username

            try:
                # Get or create user
                user: User = await AccessControl.get_or_create_user(user_id, username)

                # Check access
                if not await AccessControl.check_user_access(user):
                    logger.debug(
                        "Access denied for user %s (%s). Status: %s",
                        user_id,
                        username,
                        user.status,
                    )
                    await send_message(
                        update,
                        msg.START.format(token_url=settings.APP_TOKEN_BUY_URL),
                    )
                    return

                logger.debug(
                    "Access granted for user %s (%s). Status: %s",
                    user_id,
                    username,
                    user.status,
                )

                # Add user to context for further use
                context.user_data["user_model"] = user
                return await func(update, context, *args, **kwargs)

            except Exception as exc:
                logger.error(
                    "%s error in access control for user %s (%s): %s. Details:\n%s",
                    exc.__class__.__name__,
                    user_id,
                    username,
                    str(exc),
                    format_exc(),
                )
                await send_message(update, msg.ERROR)
                return

        return wrapper

    @staticmethod
    def register_user(func: Callable) -> Callable:
        """Make user registration without access check."""

        @wraps(func)
        async def wrapper(
            update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs
        ):
            if not update.effective_user:
                logger.warning("No effective user in update")
                return

            user_id = update.effective_user.id
            username = update.effective_user.username

            try:
                # Get or create user
                user: User = await AccessControl.get_or_create_user(user_id, username)

                # Add user to context
                context.user_data["user_model"] = user
                return await func(update, context, *args, **kwargs)

            except Exception as exc:
                logger.error(
                    "%s error in user registration for user %s (%s): %s. Details:\n%s",
                    exc.__class__.__name__,
                    user_id,
                    username,
                    str(exc),
                    format_exc(),
                )
                await send_message(update, msg.ERROR)
                return

        return wrapper


# Aliases for easy use
access_required = AccessControl.access_required
register_user = AccessControl.register_user

# Chat action indicators
typing_action = TypingIndicator.typing_action
chat_action = TypingIndicator.chat_action
