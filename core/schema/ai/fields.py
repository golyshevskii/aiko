from core.schema.base import CEnum


class MessageRole(CEnum):
    """Available message roles."""

    USER = "user"
    AGENT = "agent"
    SYSTEM = "system"


class LLM(CEnum):
    """Available LLMs."""

    GPT_5_MINI = "gpt-5-mini"


class Provider(CEnum):
    """Available providers."""

    OPENAI = "openai"
