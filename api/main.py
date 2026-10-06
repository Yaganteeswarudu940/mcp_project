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
    redirect_slashes=False,
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
    host = AgentHost("http://127.0.0.1:8000/mcp/")
    return await host.mcp.inspect()


@app.post("/agent/run", response_model=AgentResponse)
async def run_agent(request: AgentRequest) -> AgentResponse:
    # In this reference deployment the API and MCP server share one process.
    # The Agent Host still uses a real MCP Client over Streamable HTTP.
    target = settings.mcp_server_url
    host = AgentHost(target)
    result = await host.run(request.query)
    return AgentResponse(
        answer=result["answer"],
        trace=result["trace"],
    )
