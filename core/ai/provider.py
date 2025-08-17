from collections.abc import Callable

from core.schema.ai import LLM, Provider
from core.settings import settings
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider


class LLMProvider:
    """Provider factory for LLMs to connect with Agent."""

    def __init__(self) -> None:
        self.provider_cache: dict[LLM, OpenAIModel] = {}

    @property
    def provider_mapping(self) -> dict[LLM, Callable[[LLM], OpenAIModel]]:
        """Get mapping of LLM to provider factory methods."""
        return {Provider.OPENAI: self._openai_provider}

    def get_provider(self, model: LLM) -> OpenAIModel:
        """
        Get model provider based on LLM enum.

        Parameters
            model: The LLM to use

        Returns
            Model provider
        """
        # Check cache
        provider = Provider(settings.config["llm"][model.value]["provider"])

        if provider in self.provider_cache:
            return self.provider_cache[provider]

        self.provider_cache[provider] = self.provider_mapping[provider](model)
        return self.provider_cache[provider]

    def _openai_provider(self, model: LLM) -> OpenAIModel:
        """Create OpenAI model provider."""
        provider = OpenAIProvider(
            base_url=settings.config["llm"][model.value]["url"],
            api_key=settings.model_extra.get("OPENAI_API_KEY"),
        )
        return OpenAIModel(model.value, provider=provider)


LLM_PROVIDER = LLMProvider()
