import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from agent.agent_host import AgentHost
from business.mcp_server import business_mcp
from common.config import get_settings
from common.schemas import AgentRequest, AgentResponse, HealthResponse

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    # Ensure GEMINI_API_KEY from settings is loaded into process environment
    if hasattr(settings, "gemini_api_key") and settings.gemini_api_key:
        os.environ["GEMINI_API_KEY"] = settings.gemini_api_key

    # Mounted MCP apps do not automatically run their lifespan.
    async with business_mcp.session_manager.run():
        yield


app = FastAPI(
    title="MCP Agentic Business Copilot API",
    version="1.0.0",
    lifespan=lifespan,
    redirect_slashes=False,
)

# Parse origins safely whether passed as list or comma-separated string
origins = (
    [o.strip() for o in settings.allowed_origins.split(",")]
    if isinstance(settings.allowed_origins, str)
    else settings.allowed_origins
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MCP endpoint setup
mcp_app = business_mcp.streamable_http_app(streamable_http_path="/")
app.mount("/mcp", mcp_app)


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        mode="fastapi-mcp",
    )


@app.get("/mcp-info")
async def mcp_info() -> dict:
    return {
        "server": "Ecommerce Operations MCP",
        "endpoint": "/mcp",
        "transport": "Streamable HTTP",
        "concepts": ["tools", "resources", "resource templates", "prompts"],
    }


@app.get("/tools")
async def tools() -> dict:
    # Changed from hardcoded 127.0.0.1 to settings.mcp_server_url
    target = settings.mcp_server_url
    host = AgentHost(target)
    return await host.mcp.inspect()


@app.post("/agent/run", response_model=AgentResponse)
async def run_agent(request: AgentRequest) -> AgentResponse:
    target = settings.mcp_server_url
    host = AgentHost(target)
    result = await host.run(request.query)
    return AgentResponse(
        answer=result["answer"],
        trace=result["trace"],
    )
