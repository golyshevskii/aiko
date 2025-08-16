from core.schema.base import CEnum


class Command(CEnum):
    """Aiko commands."""

    CALL = "call"

    @property
    def desc(self) -> str:
        """Get the description of the Aiko command."""
        if self == self.CALL:
            return "Call Aiko"


class ChatAction(CEnum):
    """Available chat actions."""

    TYPING = "typing"
