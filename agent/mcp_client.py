from typing import Any

from mcp import Client


class MCPClientAdapter:
    """Small adapter around the official MCP v2 Python Client."""

    def __init__(self, target: Any) -> None:
        self.target = target

    async def inspect(self) -> dict[str, Any]:
        async with Client(self.target) as client:
            tools = await client.list_tools()
            resources = await client.list_resources()
            templates = await client.list_resource_templates()
            prompts = await client.list_prompts()

            return {
                "server_info": str(client.server_info),
                "protocol_version": client.protocol_version,
                "tools": [
                    {
                        "name": t.name,
                        "title": t.title,
                        "description": t.description,
                        "input_schema": t.input_schema,
                    }
                    for t in tools.tools
                ],
                "resources": [str(r.uri) for r in resources.resources],
                "resource_templates": [
                    str(r.uri_template) for r in templates.resource_templates
                ],
                "prompts": [
                    {
                        "name": p.name,
                        "title": p.title,
                        "description": p.description,
                    }
                    for p in prompts.prompts
                ],
            }

    async def list_tool_specs(self) -> list[dict[str, Any]]:
        async with Client(self.target) as client:
            result = await client.list_tools()
            return [
                {
                    "name": t.name,
                    "title": t.title,
                    "description": t.description,
                    "input_schema": t.input_schema,
                }
                for t in result.tools
            ]

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        async with Client(self.target) as client:
            result = await client.call_tool(name, arguments)
            content = []

            for block in result.content:
                text = getattr(block, "text", None)
                if text is not None:
                    content.append(text)

            return {
                "tool_name": name,
                "arguments": arguments,
                "is_error": result.is_error,
                "content": content,
                "structured_content": result.structured_content,
            }

    async def read_resource(self, uri: str) -> dict[str, Any]:
        async with Client(self.target) as client:
            result = await client.read_resource(uri)
            contents = []
            for block in result.contents:
                text = getattr(block, "text", None)
                if text is not None:
                    contents.append(text)

            return {"uri": uri, "contents": contents}

    async def get_prompt(self, name: str, arguments: dict[str, str]) -> dict[str, Any]:
        async with Client(self.target) as client:
            result = await client.get_prompt(name, arguments)
            messages = []
            for message in result.messages:
                content = getattr(message.content, "text", None)
                messages.append(
                    {
                        "role": str(message.role),
                        "content": content if content is not None else str(message.content),
                    }
                )
            return {"name": name, "messages": messages}
