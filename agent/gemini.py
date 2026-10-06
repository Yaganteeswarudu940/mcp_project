import json
from typing import Any

from google import genai
from google.genai import types

from common.config import get_settings


class GeminiPlanner:
    def __init__(self) -> None:
        settings = get_settings()
        if not settings.gemini_api_key:
            raise RuntimeError(
                "GEMINI_API_KEY is not configured. Add it to .env or Streamlit secrets."
            )

        self.client = genai.Client(api_key=settings.gemini_api_key)
        self.model = settings.gemini_model

    def decide(
        self,
        user_query: str,
        tools: list[dict[str, Any]],
        observations: list[dict[str, Any]],
    ) -> dict[str, Any]:
        tool_text = json.dumps(tools, indent=2, default=str)
        observation_text = json.dumps(observations, indent=2, default=str)

        system = """
You are the reasoning/planning component of an e-commerce operations agent.

You may either:
1. select exactly one MCP tool to call, or
2. return a final answer.

Rules:
- Never invent order, customer, inventory, ticket or policy facts.
- Prefer MCP tools/resources when facts are needed.
- If a tool result is enough to answer, return final.
- If another tool is needed, select it.
- For actions that create records, only do so when the user's request clearly asks for that action.
- Keep tool arguments valid according to the supplied JSON schema.
- Return ONLY valid JSON matching the requested structure.
"""

        user = f"""
USER REQUEST:
{user_query}

AVAILABLE MCP TOOLS:
{tool_text}

OBSERVATIONS FROM PREVIOUS MCP CALLS:
{observation_text}

Return one of:

{{"action":"tool","tool_name":"<name>","arguments":{{...}},"reason":"..."}}

or

{{"action":"final","answer":"...","reason":"..."}}
"""

        response = self.client.models.generate_content(
            model=self.model,
            contents=system + "\n" + user,
            config=types.GenerateContentConfig(
                temperature=0.1,
                response_mime_type="application/json",
            ),
        )

        text = response.text.strip()
        try:
            return json.loads(text)
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"Gemini returned invalid planner JSON: {text}") from exc

    def final_answer(
        self,
        user_query: str,
        observations: list[dict[str, Any]],
    ) -> str:
        observation_text = json.dumps(observations, indent=2, default=str)

        prompt = f"""
You are an enterprise customer-support assistant.

User request:
{user_query}

Verified business observations:
{observation_text}

Write the final response for the user.
- Be concise and professional.
- Use only verified facts in the observations.
- Do not expose internal tool names or implementation details unless useful.
- If an action was created, include its identifier.
- If information is unavailable, say so clearly.
"""
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.2,
            ),
        )
        return response.text.strip()
