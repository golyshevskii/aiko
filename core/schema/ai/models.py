from dataclasses import dataclass, field
from uuid import UUID

from pydantic_ai.messages import ModelMessage


@dataclass
class AgentDependencies:
    """Agent dependencies model."""

    user_id: str | int
    username: str
    conversation_id: UUID
    message_history: list[ModelMessage] = field(default_factory=list)
