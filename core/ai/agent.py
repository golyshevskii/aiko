import asyncio
from datetime import timedelta
from traceback import format_exc
from typing import Any

import logfire
from aiobreaker import CircuitBreaker, CircuitBreakerError
from aiohttp import ClientConnectionError, ClientError
from core.ai.prompt import Prompt
from core.ai.provider import LLM_PROVIDER
from core.logger import get_logger
from core.schema.ai import AgentDependencies
from core.schema.ai import LLM
from core.settings import settings
from core.bot.message import msg
from kaioretry import aioretry
from pydantic_ai import RunContext
from pydantic_ai.agent import Agent


logfire.configure(
    service_name=settings.APP_TITLE, token=settings.model_extra["LOGFIRE_TOKEN"]
)
logfire.instrument_pydantic_ai()
logger = get_logger(__name__)


class Aiko:
    """
    Aiko AI character.

    Attributes
        llm (LLM): The LLM to use.
        prompt (Prompt): Prompt class with system-prompt and instruction logic.
        system_prompt (str): System prompt for the agent.
        circuit_breaker (CircuitBreaker): Circuit breaker for the agent.

        _ARETRY_CONFIG: (dict): Configuration for the retry decorator.
        _CIRCUIT_BREAKER_CONFIG: (dict): Configuration for the circuit breaker.
    """

    _ARETRY_CONFIG: dict[str, Any] = {
        "exceptions": (ClientConnectionError, OSError, ClientError),
        "tries": 3,  # Max attempts (one attempt + 2 retries)
        "delay": 1,  # Start with n sec(s) delay
        "max_delay": 10,  # Max n sec(s) delay
        "backoff": 2,  # Exponential backoff factor
        "jitter": (0, 1),  # random jitter to avoid "thundering herd"
    }
    _CIRCUIT_BREAKER_CONFIG: dict[str, Any] = {
        "fail_max": settings.AGENT_CIRCUIT_BREAKER_FAILURE_THRESHOLD,  # Trip after n failures
        "timeout_duration": timedelta(
            seconds=settings.AGENT_CIRCUIT_BREAKER_RECOVERY_TIMEOUT
        ),  # Stay open for n seconds
        "exclude": (
            ValueError,
            TypeError,
            KeyError,
        ),  # Only count infrastructure failures, not business logic errors
    }

    def __init__(self, llm: LLM = settings.AGENT_LLM):
        self.llm = llm
        self.model = LLM_PROVIDER.get_provider(self.llm)
        self.prompt = Prompt()
        self.system_prompt = self.prompt.system_prompt

        # Circuit Breaker to protect the agent from cascading failures
        # Example: Blocking event loop. If one coroutine hangs or takes too long,
        # it can block the entire event loop, which will stop all other asynchronous operations.
        self.circuit_breaker = CircuitBreaker(**self._CIRCUIT_BREAKER_CONFIG)

        self._init_agent()

    def _init_agent(self):
        """
        Create a fresh agent instance for each Kong instance.

        NOTE: Ensures isolation and stateless approach.
        """
        self.agent = Agent(
            model=self.model,
            deps_type=AgentDependencies,
            system_prompt=self.system_prompt,
        )

        @self.agent.instructions
        async def _instructions(ctx: RunContext) -> str:
            return self.prompt.build_instructions(ctx.deps)

    @aioretry(**_ARETRY_CONFIG)
    async def _run_agent(self, message: str, deps: AgentDependencies) -> str:
        """Run agent with retry logic."""
        result = await self.agent.run(
            message, deps=deps, message_history=deps.message_history
        )

        logger.debug(
            "Agent responded for %s (%s). All messages:\n%s",
            deps.username,
            deps.user_id,
            result.all_messages(),
        )
        return getattr(result.output, "response", result.output)

    async def call(self, message: str, deps: AgentDependencies) -> str:
        """
        Call the agent for the given message and dependencies.

        Parameters
            message: The user message to process.
            deps: The dependencies for the agent.

        Returns
            The agent's response.
        """
        try:
            logger.debug(
                'Running agent for %s (%s). Message: "%s"',
                deps.username,
                deps.user_id,
                message,
            )
            return await asyncio.wait_for(
                self.circuit_breaker.call_async(self._run_agent, message, deps),
                timeout=settings.AGENT_RESPONSE_TIMEOUT,
            )

        except TimeoutError:
            logger.error(
                "Message processing timed out after %s seconds",
                settings.AGENT_RESPONSE_TIMEOUT,
            )
            return msg.AIKO_ERROR
        except CircuitBreakerError:
            logger.error(
                "Circuit breaker is OPEN for %s (%s). Agent is degraded.",
                deps.username,
                deps.user_id,
            )
            return msg.AIKO_ERROR
        except Exception as exc:
            logger.error(
                "Message processing failed. %s: %s. Details:\n%s",
                exc.__class__.__name__,
                str(exc),
                format_exc(),
            )
            return msg.AIKO_ERROR


class AikoPool:
    """
    Aiko agent pool using asyncio.Queue.

    Pool is useful to avoid creating a new Aiko instance for each request.
    So we can reuse them accordingly to the pool size.

    Attributes
        pool_size (int): The size of the pool.
        pool (asyncio.Queue): The pool of Aiko instances.
        total_instances (int): The total number of instances in the pool.
        lock (asyncio.Lock): The lock for the pool.
        timeout (int): The timeout for getting an instance from the pool in seconds.
    """

    def __init__(
        self,
        pool_size: int = settings.AGENT_POOL_SIZE,
        timeout: int = settings.AGENT_POOL_TIMEOUT,
    ):
        self.pool_size = pool_size
        self.pool: asyncio.Queue = asyncio.Queue(maxsize=pool_size)
        self.total_instances = 0
        self.lock = asyncio.Lock()
        self.timeout = timeout

    async def get_instance(self) -> Aiko:
        """Get Aiko instance from pool."""
        try:
            return self.pool.get_nowait()
        except asyncio.QueueEmpty:
            async with self.lock:
                if self.total_instances < self.pool_size:
                    self.total_instances += 1
                    logger.debug(
                        "Creating new Aiko instance (%s/%s)",
                        self.total_instances,
                        self.pool_size,
                    )
                    return Aiko()

        # Wait for the instance to be released with an optional timeout
        # Early rejection instead of deep queues
        if self.timeout and self.timeout > 0:
            try:
                logger.debug("Waiting for available Aiko instance...")
                return await asyncio.wait_for(self.pool.get(), timeout=self.timeout)
            except TimeoutError:
                raise msg.AIKO_ERROR
        return await self.pool.get()

    async def return_instance(self, instance: Aiko) -> None:
        """Return Aiko instance to pool."""
        try:
            self.pool.put_nowait(instance)
        except asyncio.QueueFull:
            logger.debug("Pool is full. Skipping instance return.")


POOL = AikoPool()
