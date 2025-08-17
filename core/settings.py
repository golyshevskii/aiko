import logging
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable

import yaml
from pydantic_settings import BaseSettings
from core.schema.db import DBInitStrategy
from core.schema.ai import LLM


class Settings(BaseSettings):
    """Settings for the application."""

    # ENVIRONMENT
    ENV: str = "dev"  # dev | prod

    # DIRS
    PROJECT_DIR: Path = Path.cwd()
    SETTINGS_DIR: Path = Path(__file__).parent
    CONFIG_FILE: Path = Path(SETTINGS_DIR, "config.yml")

    # APP
    APP_TITLE: str = "Aiko"
    APP_VERSION: str = "v1"
    APP_URL: str = "https://t.me/AikoAICBot"
    APP_TOKEN_BUY_URL: str = "https://coinmarketcap\\.com/"

    # AGENT (LLM)
    AGENT_LLM: LLM = LLM.GPT_5_MINI
    AGENT_PROMPT_FILE_PATH: Path = Path(SETTINGS_DIR, "ai", "prompts", "aiko-v2.json")
    AGENT_RESPONSE_TIMEOUT: int = 300  # Response timeout for the agent in seconds

    AGENT_POOL_SIZE: int = 10  # Max number of Agent instances in pool
    AGENT_POOL_TIMEOUT: int = (
        300  # Timeout for getting an instance from the agent pool in seconds
    )

    # Circuit Breaker to protect the agent from cascading failures
    # Example: Blocking event loop. If one coroutine hangs or takes too long,
    # it can block the entire event loop, which will stop all other asynchronous operations.
    AGENT_CIRCUIT_BREAKER_FAILURE_THRESHOLD: int = 5  # Trip after 5 failures
    AGENT_CIRCUIT_BREAKER_RECOVERY_TIMEOUT: int = 60  # Stay open for 60 seconds

    # AGENT MEMORY
    AGENT_MEMORY_MAX_MESSAGES: int = 15
    AGENT_MEMORY_MAX_TOKENS: int = 4000

    # DATES
    NOW_DT_UTC: Callable[[], datetime] = lambda: datetime.now(UTC)

    # DATABASE
    SQL_ECHO: bool = False if ENV == "prod" else True
    DATABASE_POOL_SIZE: int = 40
    DATABASE_MAX_OVERFLOW: int = 60
    DATABASE_POOL_TIMEOUT: int = 30
    DATABASE_CONNECT_ARGS: dict = {"connect_timeout": 10, "options": "-c timezone=UTC"}
    DATABASE_INIT_STRATEGY: DBInitStrategy = DBInitStrategy.CREATE

    # LOGGING
    LOG_LEVEL: int = logging.INFO if ENV == "prod" else logging.DEBUG

    # OPENTELEMETRY
    OTEL_ENABLED: bool = True
    OTEL_CONSOLE_OUTPUT: bool = True
    OTEL_OTLP_ENDPOINT: str | None = None

    # Config for ENV_VAR_* variables from .env file
    model_config: dict[str, Any] = {
        "extra": "allow",  # Allow to use model_extra property to get env variables.
        # Example: settings.model_extra["OPENAI_API_KEY"]
        "case_sensitive": True,  # Make environment variables case-insensitive
        "env_file": f"./.env.{ENV}",  # Load specific .env file
        "env_file_encoding": "utf-8",
    }

    _cached_config: dict[str, Any] = {}

    def __init__(self, **kwargs):
        # Cached attributes
        super().__init__(**kwargs)
        self.CPU_COUNT = os.cpu_count() or 1

        with self.CONFIG_FILE.open(encoding="utf-8") as f:
            object.__setattr__(self, "_cached_config", yaml.safe_load(f))

    @property
    def config(self) -> dict[str, Any]:
        return self._cached_config


settings = Settings()
