import os
from functools import lru_cache
from dotenv import load_dotenv

load_dotenv()


def _csv(value: str) -> list[str]:
    return [x.strip() for x in value.split(",") if x.strip()]


class Settings:
    @property
    def gemini_api_key(self) -> str:
        return os.getenv("GEMINI_API_KEY", "")

    @property
    def gemini_model(self) -> str:
        return os.getenv("GEMINI_MODEL", "gemini-3.8-flash")

    @property
    def mcp_server_url(self) -> str:
        # Defaults to public Render URL if env var is missing or defaulted to 127.0.0.1
        url = os.getenv("MCP_SERVER_URL", "https://mcp-project-cntj.onrender.com/mcp/")
        if "127.0.0.1" in url or "localhost" in url:
            # Override local fallbacks when running in hosted environments
            if os.getenv("RENDER"):
                return "https://mcp-project-cntj.onrender.com/mcp/"
        return url

    @property
    def api_base_url(self) -> str:
        return os.getenv("API_BASE_URL", "")

    @property
    def max_agent_steps(self) -> int:
        return int(os.getenv("MAX_AGENT_STEPS", "6"))

    @property
    def allowed_origins(self) -> list[str]:
        return _csv(os.getenv("ALLOWED_ORIGINS", "*")) or ["*"]


def get_settings() -> Settings:
    # Do not lru_cache so environment updates are picked up dynamically
    return Settings()
