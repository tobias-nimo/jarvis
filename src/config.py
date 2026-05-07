"""
Centralized configuration management using pydantic-settings.

All settings are loaded from environment variables or the .env file.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="allow",
        case_sensitive=False,
    )

    # ── LLM Provider ─────────────────────────────────────────────────────────
    groq_api_key: str = ""
    openrouter_api_key: str = ""

    # ── Tools ─────────────────────────────────────────────────────────────────
    tavily_api_key: str = ""
    mistral_api_key: str = ""

    # ── LangSmith ─────────────────────────────────────────────────────────────
    langchain_tracing_v2: bool = False
    langchain_api_key: str = ""
    langchain_project: str = ""

    # ── Agent ───-─────────────────────────────────────────────────────────────
    debug: bool = False

    # ── Paths ───-─────────────────────────────────────────────────────────────
    project_root: str = "."

settings = Settings()
