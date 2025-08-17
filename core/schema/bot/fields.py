from core.schema.base import CEnum


class Command(CEnum):
    """Aiko commands."""

    START = "start"
    CALL = "call"
    FAQ = "faq"

    @property
    def desc(self) -> str:
        """Get the description of the Aiko command."""
        if self == self.CALL or self == self.START:
            return "Call Aiko"
        elif self == self.FAQ:
            return "Frequently Asked Questions"


class ChatAction(CEnum):
    """Available chat actions."""

    TYPING = "typing"
