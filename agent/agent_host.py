from typing import Any

from agent.gemini import GeminiPlanner
from agent.mcp_client import MCPClientAdapter
from common.config import get_settings


class AgentHost:
    """
    The MCP Host / agent orchestrator.

    Gemini reasons about what to do.
    MCP Client performs protocol operations.
    MCP Server owns business capabilities.
    """

    def __init__(self, mcp_target: Any) -> None:
        self.mcp = MCPClientAdapter(mcp_target)
        self.planner = GeminiPlanner()
        self.settings = get_settings()

    async def run(self, query: str) -> dict[str, Any]:
        tools = await self.mcp.list_tool_specs()
        observations: list[dict[str, Any]] = []
        trace: list[dict[str, Any]] = []

        for step in range(1, self.settings.max_agent_steps + 1):
            decision = self.planner.decide(query, tools, observations)

            trace.append(
                {
                    "step": step,
                    "type": "gemini_decision",
                    "decision": decision,
                }
            )

            action = decision.get("action")

            if action == "final":
                answer = decision.get("answer", "")
                if not answer:
                    answer = self.planner.final_answer(query, observations)

                return {
                    "answer": answer,
                    "trace": trace,
                }

            if action != "tool":
                raise RuntimeError(f"Unsupported Gemini action: {action}")

            tool_name = decision.get("tool_name")
            arguments = decision.get("arguments") or {}

            known_tools = {t["name"] for t in tools}
            if tool_name not in known_tools:
                raise RuntimeError(f"Gemini selected unknown MCP tool: {tool_name}")

            trace.append(
                {
                    "step": step,
                    "type": "mcp_tool_call",
                    "tool_name": tool_name,
                    "arguments": arguments,
                }
            )

            result = await self.mcp.call_tool(tool_name, arguments)
            observations.append(result)

            trace.append(
                {
                    "step": step,
                    "type": "mcp_tool_result",
                    "result": result,
                }
            )

            if result["is_error"]:
                # The error becomes an observation. Gemini gets another chance
                # to recover or explain the issue.
                continue

        answer = self.planner.final_answer(query, observations)
        trace.append(
            {
                "step": self.settings.max_agent_steps,
                "type": "max_steps_finalization",
            }
        )
        return {"answer": answer, "trace": trace}
