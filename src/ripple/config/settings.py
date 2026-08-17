"""Application settings loaded from the environment and an optional ``.env``."""

from __future__ import annotations

import logging
from functools import lru_cache
from typing import ClassVar

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger("ripple.config")

OPTIONAL_ENV_KEYS: tuple[str, ...] = (
    "GROK_API_KEY",
    "XAI_API_KEY",
    "XAI_API_BASE_URL",
    "FINNHUB_API_KEY",
    "TWSE_API_KEY",
    "CWA_API_KEY",
    "REUTERS_API_KEY",
    "NEXT_PUBLIC_SUPABASE_URL",
    "NEXT_PUBLIC_SUPABASE_ANON_KEY",
    "NEXT_PUBLIC_FINNHUB_API_KEY",
)


def _empty_to_none(value: object) -> object:
    """Treat blank env values as unset so cloud VMs can boot without secrets."""
    if isinstance(value, str) and value.strip() == "":
        return None
    return value


class Settings(BaseSettings):
    """Runtime configuration.

    Required fields have safe defaults so the process starts when ``.env`` is
    absent (typical of a freshly provisioned VM). Optional API keys may be
    missing; :func:`get_settings` logs a warning instead of raising.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    optional_env_keys: ClassVar[tuple[str, ...]] = OPTIONAL_ENV_KEYS

    database_url: str = Field(
        default="postgresql+psycopg://localhost:5432/ripple",
        description="SQLAlchemy URL. Neon-compatible Postgres in production.",
    )
    log_level: str = Field(default="INFO")
    http_timeout_seconds: float = Field(default=30.0)
    scheduler_timezone: str = Field(default="UTC")
    source_registry_path: str = Field(default="configs/source_registry.yaml")
    chokepoints_path: str = Field(default="configs/chokepoints.yaml")

    grok_api_key: str | None = Field(default=None)
    xai_api_key: str | None = Field(default=None)
    xai_api_base_url: str | None = Field(default=None)
    finnhub_api_key: str | None = Field(default=None)
    twse_api_key: str | None = Field(default=None)
    cwa_api_key: str | None = Field(default=None)
    reuters_api_key: str | None = Field(default=None)
    next_public_supabase_url: str | None = Field(default=None)
    next_public_supabase_anon_key: str | None = Field(default=None)
    next_public_finnhub_api_key: str | None = Field(default=None)

    @field_validator(
        "grok_api_key",
        "xai_api_key",
        "xai_api_base_url",
        "finnhub_api_key",
        "twse_api_key",
        "cwa_api_key",
        "reuters_api_key",
        "next_public_supabase_url",
        "next_public_supabase_anon_key",
        "next_public_finnhub_api_key",
        mode="before",
    )
    @classmethod
    def blank_optional_is_none(cls, value: object) -> object:
        """Normalize empty strings from ``.env.example`` copies to ``None``."""
        return _empty_to_none(value)

    def missing_optional_keys(self) -> list[str]:
        """Return env names of optional keys that are unset."""
        missing: list[str] = []
        for env_name in self.optional_env_keys:
            field_name = env_name.lower()
            if getattr(self, field_name, None) is None:
                missing.append(env_name)
        return missing


def _warn_missing_optional(settings: Settings) -> None:
    """Log a warning for each unset optional key. Never raises."""
    for env_name in settings.missing_optional_keys():
        logger.warning(
            "Optional config key %s is missing; continuing without it",
            env_name,
        )


def configure_logging(level: str) -> None:
    """Configure root logging once for CLI and scheduler entrypoints."""
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the process-wide :class:`Settings` singleton.

    Missing optional keys produce warnings; they do not prevent startup.
    """
    settings = Settings()
    _warn_missing_optional(settings)
    return settings


def reset_settings() -> None:
    """Clear the settings cache (used by tests)."""
    get_settings.cache_clear()
