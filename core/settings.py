import logging
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Settings for the application."""

    # ENVIRONMENT
    ENV: str = "dev"  # dev | prod

    # APP
    APP_TITLE: str = "Aiko"
    APP_VERSION: str = "v1"

    # AGENT (LLM)
    LLM_MODEL: str = "gpt-4o-mini"

    # AGENT MEMORY
    AGENT_MEMORY_MAX_MESSAGES: int = 15
    AGENT_MEMORY_MAX_TOKENS: int = 4000

    # DIRS
    PROJECT_DIR: Path = Path.cwd()
    SETTINGS_DIR: Path = Path(__file__).parent
    CONFIG_FILE: Path = Path(SETTINGS_DIR, "config.yml")

    # DATES
    NOW_DT_UTC: datetime = datetime.now(UTC)

    # DATABASE
    SQL_ECHO: bool = False if ENV == "prod" else True
    DATABASE_POOL_SIZE: int = 40
    DATABASE_MAX_OVERFLOW: int = 60
    DATABASE_POOL_TIMEOUT: int = 30
    DATABASE_CONNECT_ARGS: dict = {"connect_timeout": 10, "options": "-c timezone=UTC"}
    DATABASE_INIT_STRATEGY: str = "create_if_not_exists"

    # LOGGING
    LOG_LEVEL: int = logging.INFO if ENV == "prod" else logging.DEBUG

    # OPENTELEMETRY
    OTEL_ENABLED: bool = True
    OTEL_CONSOLE_OUTPUT: bool = True
    OTEL_OTLP_ENDPOINT: str | None = None

    # Config for ENV_VAR_* variables from .env file
    model_config: dict[str, Any] = {
        "extra": "allow",  # Allow extra variables from .env file
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
