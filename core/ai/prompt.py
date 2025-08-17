from json import load
from typing import Any

from core.schema.ai import AgentDependencies
from core.settings import settings


class Prompt:
    """
    Base class for all agent prompts.

    Attributes:
        prompt_file_path (Path): Path to the prompt file.
        prompt (dict): Prompt data.
    """

    def __init__(self):
        self.prompt_file_path = settings.AGENT_PROMPT_FILE_PATH
        self.prompt = self._load_prompt()

    def _load_prompt(self) -> dict[str, Any]:
        """Load the prompt from the file."""
        with open(self.prompt_file_path, "r", encoding="utf-8") as file:
            return load(file)

    @property
    def system_prompt(self) -> str:
        """Build the system prompt for the agent."""
        character = "\n- ".join(self.prompt["character"])
        rules = "\n- ".join(self.prompt["rules"])
        message_format = "\n- ".join(self.prompt["message_format"])
        message_examples = []

        for example in self.prompt["message_examples"]:
            message_examples.append(
                f'User: "{example["User"]}" Aiko: "{example["Aiko"]}"'
            )

        message_examples = "\n- ".join(message_examples)

        return (
            f"{self.prompt['identity']}\n"
            f"Goal: {self.prompt['goal']}\n\n"
            f"Your character:\n- {character}\n\n"
            f"Rules:\n- {rules}\n\n"
            f"Message format:\n- {message_format}\n\n"
            f"Message examples:\n- {message_examples}\n"
        )

    @staticmethod
    def build_instructions(deps: AgentDependencies, **kwargs) -> str:
        """Build the instructions for the agent."""
        return (
            f"The user's name is {deps.username}.\n"
            f"Current Date and Time is {settings.NOW_DT_UTC()} (UTC).\n\n"
        )
