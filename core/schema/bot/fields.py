from core.schema.base import CEnum


class Command(CEnum):
    """Aiko commands."""

    START = "start"
    CALL = "call"

    @property
    def desc(self) -> str:
        """Get the description of the Aiko command."""
        if self == self.CALL or self == self.START:
            return "Call Aiko"


class ChatAction(CEnum):
    """Available chat actions."""

    TYPING = "typing"
