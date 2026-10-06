from pydantic import BaseModel, Field


class AgentRequest(BaseModel):
    query: str = Field(min_length=1, max_length=5000)


class AgentResponse(BaseModel):
    answer: str
    trace: list[dict] = []


class HealthResponse(BaseModel):
    status: str
    mode: str
