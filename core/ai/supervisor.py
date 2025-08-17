from traceback import format_exc
from typing import Any
from aiohttp import ClientConnectionError, ClientError

from pydantic_ai import Agent
from core.ai.prompt import Prompt
from core.settings import settings
from core.ai.provider import LLM_PROVIDER
from core.schema.ai import SupervisorResponseModel
from core.logger import get_logger
from kaioretry import aioretry


logger = get_logger(__name__)


class Supervisor:
    """
    Aiko supervisor.

    Attributes
        llm (LLM): The LLM provider.
        prompt (Prompt): The prompt.
        system_prompt (str): The system prompt.
        agent (Agent): The agent.
    """

    _ARETRY_CONFIG: dict[str, Any] = {
        "exceptions": (ClientConnectionError, OSError, ClientError),
        "tries": 3,  # Max attempts (one attempt + 2 retries)
        "delay": 1,  # Start with n sec(s) delay
        "max_delay": 10,  # Max n sec(s) delay
        "backoff": 2,  # Exponential backoff factor
        "jitter": (0, 1),  # random jitter to avoid "thundering herd"
    }

    def __init__(self):
        """Initialize the supervisor."""
        self.llm = LLM_PROVIDER.get_provider(settings.AGENT_LLM)
        self.prompt = Prompt()
        self.system_prompt = self.prompt.system_prompt

        self.agent = Agent(
            model=self.llm,
            system_prompt=self.system_prompt,
            output_type=SupervisorResponseModel,
        )

    @aioretry(**_ARETRY_CONFIG)
    async def call(self, user: str, aiko: str) -> int:
        """Call supervisor."""
        try:
            result = await self.agent.run(f"User: {user}\nAiko: {aiko}")
            return result.output.score
        except Exception:
            logger.error("Error calling supervisor. Details:\n%s", format_exc())
            return SupervisorResponseModel(score=0)


SUPERVISOR = Supervisor()
