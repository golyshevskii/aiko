from dataclasses import dataclass, field
from uuid import UUID
from pydantic import BaseModel, Field

from pydantic_ai.messages import ModelMessage


@dataclass
class AgentDependencies:
    """Agent dependencies model."""

    user_id: str | int
    username: str
    conversation_id: UUID
    message_history: list[ModelMessage] = field(default_factory=list)


class SupervisorResponseModel(BaseModel):
    """Supervisor response model."""

    score: int = Field(
        ...,
        description="Score for the user's love experience and how Aiko reacted to it",
        gt=0,
        lt=100,
    )
