from uuid import UUID, uuid4

from core.schema.ai import MessageRole
from core.schema.db.fields import UserStatus
from sqlalchemy import DateTime, Enum, ForeignKey, Integer, Text, text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship


from datetime import datetime

from sqlalchemy import BigInteger, String
from core.db.base import DBase


class User(DBase):
    """User model."""

    __tablename__ = "users"
    __table_args__ = {"schema": "raw"}

    id: Mapped[int] = mapped_column(
        primary_key=True, autoincrement=True, comment="Unique user id"
    )
    tg_id: Mapped[int] = mapped_column(
        BigInteger,
        unique=True,
        index=True,
        nullable=False,
        comment="Unique Telegram user id",
    )
    tg_username: Mapped[str | None] = mapped_column(
        String(256), nullable=True, comment="Telegram username"
    )
    status: Mapped[UserStatus] = mapped_column(
        Enum(UserStatus), default=UserStatus.INACTIVE, comment="User status"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        comment="User created at (UTC)",
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        onupdate=text("CURRENT_TIMESTAMP"),
        server_default=text("CURRENT_TIMESTAMP"),
        comment="User updated at (UTC)",
    )

    # Relationships
    conversation: Mapped[list["Conversation"]] = relationship(
        "Conversation", back_populates="user", cascade="all, delete-orphan"
    )
    score: Mapped["Score"] = relationship(
        "Score", back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"User(id={self.id}, status={self.status})"


class Conversation(DBase):
    """Database model for conversation."""

    __tablename__ = "conversations"
    __table_args__ = {"schema": "raw"}

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, comment="Unique conversation id"
    )
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("raw.users.id"),
        nullable=False,
        index=True,
        comment="Conversation user id from users table",
    )
    summary: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="Conversation summary"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        index=True,
        comment="Conversation created at (UTC)",
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        onupdate=text("CURRENT_TIMESTAMP"),
        comment="Conversation updated at (UTC)",
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="conversation")
    conversation_message: Mapped[list["ConversationMessage"]] = relationship(
        "ConversationMessage",
        back_populates="conversation",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"Conversation(id={self.id}, user_id={self.user_id}, created_at={self.created_at})"


class ConversationMessage(DBase):
    """Database model for conversation message."""

    __tablename__ = "conversation_messages"
    __table_args__ = {"schema": "raw"}

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        comment="Unique message id",
    )
    conversation_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("raw.conversations.id"),
        nullable=False,
        index=True,
        comment="Conversation id from conversations table",
    )
    role: Mapped[MessageRole] = mapped_column(
        Enum(MessageRole), nullable=False, comment="Role from wich message was sent"
    )
    message: Mapped[str] = mapped_column(
        Text, nullable=False, comment="Message content"
    )
    tokens: Mapped[int] = mapped_column(
        Integer, default=0, comment="Conversation used tokens"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        index=True,
        comment="Message created at (UTC)",
    )

    # Relationship with conversation
    conversation: Mapped["Conversation"] = relationship(
        "Conversation", back_populates="conversation_message"
    )

    def __repr__(self) -> str:
        return f"ConversationMessage(id={self.id}, conversation_id={self.conversation_id}, role={self.role}, created_at={self.created_at})"


class Score(DBase):
    """Database model for score."""

    __tablename__ = "scores"
    __table_args__ = {"schema": "raw"}

    id: Mapped[int] = mapped_column(
        primary_key=True, autoincrement=True, comment="Unique score id"
    )
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("raw.users.id"),
        nullable=False,
        index=True,
        comment="User id from users table",
    )
    score: Mapped[int] = mapped_column(Integer, default=0, comment="Score value")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        index=True,
        comment="Score created at (UTC)",
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        onupdate=text("CURRENT_TIMESTAMP"),
        comment="Score updated at (UTC)",
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="score")

    def __repr__(self) -> str:
        return f"Score(id={self.id}, user_id={self.user_id}, score={self.score}, created_at={self.created_at})"
