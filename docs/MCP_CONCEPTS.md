# MCP Concepts Demonstrated

## 1. What is MCP?

Model Context Protocol is a standard protocol for allowing applications to expose context and capabilities to AI applications.

The key separation is:

```text
LLM / Agent
    |
    | MCP Client
    v
MCP Server
    |
    +-- Tools
    +-- Resources
    +-- Prompts
```

The LLM does not need to know how the underlying business system works.

## 2. MCP Host

The **Host** is the AI application/orchestrator.

In this project:

```text
agent/agent_host.py
```

The Host:

- receives the user request
- obtains MCP capabilities
- asks Gemini to decide what to do
- calls tools through the MCP Client
- collects observations
- repeats when necessary
- produces the final answer

## 3. MCP Client

The **Client** is the protocol-side connection from the Host to an MCP Server.

In this project:

```text
agent/mcp_client.py
```

The Client can:

```python
await client.list_tools()
await client.call_tool(...)
await client.list_resources()
await client.read_resource(...)
await client.list_prompts()
await client.get_prompt(...)
```

## 4. MCP Server

The **Server** exposes business capabilities.

In this project:

```text
business/mcp_server.py
```

It exposes:

### Tools

Actions or queries:

- `get_order_status`
- `get_inventory`
- `get_customer`
- `create_support_ticket`
- `request_order_cancellation`

### Resources

Read-only contextual information:

- `business://return-policy`
- `order://{order_id}`

### Prompts

Reusable prompt templates:

- `customer_response`

## 5. Tools vs Resources vs Prompts

### Tool

Use a tool when the model needs to perform a function/action.

Example:

```text
create_support_ticket(...)
```

### Resource

Use a resource for contextual information.

Example:

```text
business://return-policy
```

### Prompt

Use a prompt when the MCP server provides a reusable interaction template.

Example:

```text
customer_response(order_id, issue)
```

## 6. Transport

This project demonstrates:

### Streamable HTTP

The FastAPI service exposes:

```text
/mcp
```

The MCP Client connects to:

```text
http://localhost:8000/mcp
```

### In-process

For the Streamlit-only demo:

```python
Client(business_mcp)
```

No HTTP server is required. This is useful for tests and demos.

## 7. Agentic loop

The Host implements a simple bounded agent loop:

```text
for iteration in 1..MAX_STEPS:

    Ask Gemini:
        final answer OR MCP tool call

    if final:
        return

    if tool:
        MCP Client -> MCP Server -> tool
        append observation
        continue
```

This is intentionally explicit so the architecture can be explained in an interview.

## 8. Why not call Python functions directly?

A direct call would look like:

```python
get_order_status("ORD-1001")
```

That couples the agent to the implementation.

MCP introduces a standard capability boundary:

```text
Agent Host
   |
MCP Client
   |
MCP protocol
   |
MCP Server
   |
Business implementation
```

The server could later be replaced by another service or run remotely.

## 9. Structured tool results

Tools return JSON-compatible dictionaries.

This is important because the application can use structured data rather than parsing prose.

Conceptually:

```json
{
  "order_id": "ORD-1001",
  "status": "SHIPPED",
  "carrier": "DHL",
  "tracking_number": "DHL12345"
}
```

## 10. Error handling

MCP tool failures should be treated as observations that the agent can understand.

For example:

```text
Unknown order ORD-9999
```

The agent can respond gracefully instead of crashing the application.

## 11. Why MCP is useful in enterprises

Imagine an enterprise has:

```text
CRM MCP Server
Order MCP Server
Inventory MCP Server
Shipping MCP Server
Knowledge MCP Server
```

The Agent Host can connect to multiple MCP servers and use their capabilities through a common protocol.

That is the architectural value of MCP: **standardized capability exposure and interoperability**.

## 12. Production extension

For a real system, add:

- authentication/authorization
- OAuth where appropriate
- tenant isolation
- request IDs
- audit events
- rate limits
- secrets management
- policy enforcement
- approval workflows
- observability/tracing
- real database/API adapters
- retries and timeouts
- idempotency for mutations
