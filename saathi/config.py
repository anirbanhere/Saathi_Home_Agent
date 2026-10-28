import os
from pathlib import Path
import yaml
from pydantic import Field, model_validator
from .contracts import Contract, Profile


class Settings(Contract):
    database_url: str = "sqlite:///data/saathi-demo.sqlite3"
    redis_url: str = ""
    reasoning: Profile = Field(
        default_factory=lambda: Profile(provider="mock", model="dental-planner-v1")
    )
    conversation: Profile = Field(
        default_factory=lambda: Profile(provider="mock", model="localized-reply-v1")
    )
    stt: Profile = Field(
        default_factory=lambda: Profile(provider="mock", model="fixture-lookup-v1")
    )
    tts: Profile = Field(
        default_factory=lambda: Profile(provider="mock", model="synthetic-tone-v1")
    )
    whatsapp_production_eligible: bool = False
    live_actions_enabled: bool = False
    live_speech_enabled: bool = False
    approval_ttl_seconds: int = Field(default=300, ge=1, le=900)
    max_steps: int = Field(default=8, ge=4, le=8)
    max_tasks_per_user: int = Field(default=50, ge=1, le=100)
    media_root: str = "data/saathi-media"
    media_ttl_seconds: int = Field(default=900, ge=60, le=3600)
    media_max_objects_per_user: int = Field(default=5, ge=1, le=10)

    @model_validator(mode="after")
    def phase_one_gates(self):
        if (
            self.whatsapp_production_eligible
            or self.live_actions_enabled
            or self.live_speech_enabled
        ):
            raise ValueError(
                "Phase1 is mock-only. Flags cannot grant live eligibility or execution."
            )
        return self

    def profiles(self):
        return {
            r: getattr(self, r) for r in ("reasoning", "conversation", "stt", "tts")
        }

    @classmethod
    def load(cls):
        path = Path(
            os.environ.get("SAATHI_PROVIDER_CONFIG", "config/providers.example.yaml")
        )
        config = yaml.safe_load(path.read_text()) if path.exists() else {}
        if set(config or {}) - {"models", "speech", "policy"}:
            raise ValueError("Unsupported provider configuration fields.")
        data = {
            **(config or {}).get("models", {}),
            **(config or {}).get("speech", {}),
            **(config or {}).get("policy", {}),
        }
        data.update(
            database_url=os.environ.get(
                "SAATHI_DATABASE_URL", "sqlite:///data/saathi-demo.sqlite3"
            ),
            redis_url=os.environ.get("SAATHI_REDIS_URL", ""),
            media_root=os.environ.get("SAATHI_MEDIA_ROOT", "data/saathi-media"),
            media_ttl_seconds=os.environ.get("SAATHI_MEDIA_TTL_SECONDS", "900"),
        )
        for field, env in [
            ("whatsapp_production_eligible", "WHATSAPP_PRODUCTION_ELIGIBLE"),
            ("live_actions_enabled", "SAATHI_LIVE_ACTIONS_ENABLED"),
            ("live_speech_enabled", "SAATHI_LIVE_SPEECH_ENABLED"),
        ]:
            data[field] = os.environ.get(env, "false")
        return cls.model_validate(data)
