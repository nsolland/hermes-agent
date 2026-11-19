"""SaladCloud AI Gateway provider for Hermes Agent."""

from __future__ import annotations

from providers import register_provider
from providers.base import ProviderProfile

MODEL_ID = "qwen3.6-35b-a3b"


class SaladCloudProfile(ProviderProfile):
    """Expose only the SaladCloud model supported by this plugin."""

    def fetch_models(
        self,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        timeout: float = 8.0,
    ) -> list[str] | None:
        models = super().fetch_models(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
        )
        if models is None:
            return None
        filtered = [model for model in models if model == MODEL_ID]
        return filtered or None


saladcloud = SaladCloudProfile(
    name="saladcloud",
    aliases=("salad-cloud", "salad"),
    display_name="SaladCloud AI Gateway",
    description="SaladCloud AI Gateway — Qwen3.6 35B-A3B for agentic and coding tasks",
    signup_url="https://salad.com/ai-gateway",
    env_vars=("SALAD_AI_GATEWAY_API_KEY", "SALAD_API_KEY", "SALAD_CLOUD_API_KEY", "SALAD_BASE_URL"),
    base_url="https://ai.salad.cloud/v1",
    auth_type="api_key",
    supports_vision=True,
    default_aux_model=MODEL_ID,
    fallback_models=(MODEL_ID,),
)

register_provider(saladcloud)
