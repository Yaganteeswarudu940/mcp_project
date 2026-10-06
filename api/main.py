from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from agent.agent_host import AgentHost
from business.mcp_server import business_mcp
from common.config import get_settings
from common.schemas import AgentRequest, AgentResponse, HealthResponse

settings = get_settings()

# Build the MCP ASGI application once.
mcp_asgi = business_mcp.streamable_http_app()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    # Mounted MCP apps do not automatically run their lifespan.
    async with business_mcp.session_manager.run():
        yield


app = FastAPI(
    title="MCP Agentic Business Copilot API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MCP endpoint.
app.mount("/mcp", mcp_asgi)


def _mcp_target():
    # API and MCP server share one process. On Render the service listens on
    # $PORT (not 8000), and calling its own public URL from inside the
    # container fails ("All connection attempts failed"), so by default use
    # the in-process server object. Set MCP_SERVER_URL only for a *remote*
    # MCP server.
    return settings.mcp_server_url or business_mcp


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
    # This endpoint is intentionally simple for UI observability.
    # The authoritative capability discovery remains MCP list_tools().
    host = AgentHost(_mcp_target())
    return await host.mcp.inspect()


@app.post("/agent/run", response_model=AgentResponse)
async def run_agent(request: AgentRequest) -> AgentResponse:
    host = AgentHost(_mcp_target())
    result = await host.run(request.query)
    return AgentResponse(
        answer=result["answer"],
        trace=result["trace"],
    )
