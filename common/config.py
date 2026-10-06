import os
from functools import lru_cache

from dotenv import load_dotenv

load_dotenv()


def _csv(value: str) -> list[str]:
    return [x.strip() for x in value.split(",") if x.strip()]


class Settings:
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
    mcp_server_url: str = os.getenv("MCP_SERVER_URL", "http://127.0.0.1:8000/mcp")
    api_base_url: str = os.getenv("API_BASE_URL", "")
    max_agent_steps: int = int(os.getenv("MAX_AGENT_STEPS", "6"))
    allowed_origins: list[str] = _csv(os.getenv("ALLOWED_ORIGINS", "*")) or ["*"]


@lru_cache
def get_settings() -> Settings:
    return Settings()
