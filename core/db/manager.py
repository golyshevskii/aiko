from datetime import UTC, datetime
from uuid import UUID

from core.db.init import get_session
from core.db.schema import Conversation, ConversationMessage, Score, User
from core.logger import get_logger
from core.schema.ai import MessageRole
from core.schema.db.fields import UserStatus
from sqlalchemy import select, update

logger = get_logger(__name__)


class UserManager:
    """Manager for managing users and subscriptions."""

    @staticmethod
    async def get_user_by_tg_id(tg_id: int) -> User | None:
        """Get user by Telegram ID."""
        async for session in get_session():
            stmt = select(User).where(User.tg_id == tg_id)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()

    @staticmethod
    async def update_user_status(user_id: int, status: UserStatus) -> bool:
        """Update user status."""
        async for session in get_session():
            stmt = update(User).where(User.id == user_id).values(status=status)
            result = await session.execute(stmt)
            await session.commit()

            if result.rowcount > 0:
                logger.debug("Updated status for user %s to %s", user_id, status.value)
                return True
            else:
                logger.warning(
                    "Failed to update status for user %s: user not found", user_id
                )
                return False

    @staticmethod
    async def grant_access(user_id: int) -> bool:
        """Grant access to user."""
        return await UserManager.update_user_status(user_id, UserStatus.ACTIVE)

    @staticmethod
    async def revoke_access(user_id: int) -> bool:
        """Revoke access to user."""
        return await UserManager.update_user_status(user_id, UserStatus.INACTIVE)

    @staticmethod
    async def find_users_by_username(username: str) -> list[User]:
        """Find users by username."""
        async for session in get_session():
            stmt = select(User).where(User.tg_username.ilike(f"%{username}%"))
            result = await session.execute(stmt)
            return list(result.scalars().all())


class ConversationManager:
    """Manager for conversation operations."""

    @staticmethod
    async def get_conversation(
        user_id: int, conversation_id: UUID, create_if_not_exists: bool = True
    ) -> Conversation:
        """Get conversation by ID."""
        async for session in get_session():
            conversation = await session.get(Conversation, conversation_id)
            if conversation and conversation.user_id == user_id:
                return conversation

        if create_if_not_exists:
            return await ConversationManager.create_conversation(
                user_id, conversation_id
            )
        raise ValueError(f"Conversation {conversation_id} does not exist")

    @staticmethod
    async def create_conversation(user_id: int, conversation_id: UUID) -> Conversation:
        """Create a new conversation."""
        async for session in get_session():
            conversation = Conversation(id=conversation_id, user_id=user_id)
            session.add(conversation)
            await session.commit()
            await session.refresh(conversation)

        logger.debug(
            "New conversation %s created for user %s", conversation_id, user_id
        )
        return conversation

    @staticmethod
    async def get_messages(
        conversation_id: UUID, limit: int = 15
    ) -> list[ConversationMessage]:
        """Get messages for conversation."""
        async for session in get_session():
            stmt = (
                select(ConversationMessage)
                .where(ConversationMessage.conversation_id == conversation_id)
                .order_by(ConversationMessage.created_at.desc())
                .limit(limit)
            )

            result = await session.execute(stmt)
            messages = result.scalars().all()

        return messages

    @staticmethod
    async def add_message(
        conversation_id: UUID, role: MessageRole, message: str, tokens: int = 0
    ) -> ConversationMessage:
        """Add a message to the conversation."""
        async for session in get_session():
            # Create message
            msg = ConversationMessage(
                conversation_id=conversation_id,
                role=role,
                message=message,
                tokens=tokens,
            )
            session.add(msg)
            await session.commit()
            await session.refresh(msg)

        logger.debug("Message %s added to conversation %s", msg.id, conversation_id)
        return msg

    @staticmethod
    async def update_summary(conversation_id: UUID, summary: str) -> bool:
        """Update conversation summary."""
        async for session in get_session():
            stmt = (
                update(Conversation)
                .where(Conversation.id == conversation_id)
                .values(summary=summary, updated_at=datetime.now(UTC))
            )
            await session.execute(stmt)
            await session.commit()

        logger.debug("Updated summary for conversation %s", conversation_id)
        return True


class ScoreManager:
    """Manager for score operations."""

    @staticmethod
    async def create_score(user_id: int) -> bool:
        """Create score for user."""
        async for session in get_session():
            score = Score(user_id=user_id)
            session.add(score)
            await session.commit()

        logger.debug("Created score for user %s", user_id)
        return True

    @staticmethod
    async def get_score(user_id: int) -> Score:
        """Get score for user."""
        async for session in get_session():
            stmt = select(Score).where(Score.user_id == user_id)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()

    @staticmethod
    async def update_score(user_id: int, score: int) -> bool:
        """Update score for user."""
        score = await ScoreManager.get_score(user_id)
        if not score:
            return await ScoreManager.create_score(user_id)

        async for session in get_session():
            stmt = update(Score).where(Score.user_id == user_id).values(score=score)
            await session.execute(stmt)
            await session.commit()

        logger.debug("Updated score for user %s to %d", user_id, score)
        return True
