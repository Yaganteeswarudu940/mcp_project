# Deployment Guide

## Streamlit Community Cloud

Entrypoint:

```text
streamlit_app.py
```

Dependencies:

```text
requirements.txt
```

Configuration:

```text
.streamlit/config.toml
```

Secrets are configured in the Streamlit Cloud application settings.

Example:

```toml
GEMINI_API_KEY = "..."
GEMINI_MODEL = "gemini-3.8-flash"
API_BASE_URL = "https://your-fastapi-api.example.com"
```

Do not commit secrets.

## FastAPI service

Run locally:

```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

Container:

```bash
docker build -t mcp-business-api .
docker run --env-file .env -p 8000:8000 mcp-business-api
```

Production topology:

```text
Browser
  |
  v
Streamlit Community Cloud
  |
  | HTTPS
  v
FastAPI service
  |
  +-- Agent Host
  |
  +-- MCP Client
  |
  +-- MCP Server (/mcp)
```

## Why FastAPI is separate

A Streamlit Community Cloud app is designed to run the Streamlit application. It should not be treated as a public FastAPI hosting platform.

Therefore:

- Streamlit Cloud = frontend
- FastAPI-compatible host = API + MCP service

The project also supports in-process MCP when you want a one-app teaching demo.

## CORS

Before production, set the allowed Streamlit origin rather than using `*`.

For example:

```text
https://your-app-name.streamlit.app
```

The current sample is intentionally permissive for local development.

## Health checks

Use:

```text
GET /health
```

Expected:

```json
{
  "status": "ok"
}
```

## MCP endpoint

The Streamable HTTP endpoint is:

```text
/mcp
```

Example:

```text
https://your-api.example.com/mcp
```

## API endpoint

Agent endpoint:

```text
POST /agent/run
```

Body:

```json
{
  "query": "Where is order ORD-1001?"
}
```

## Security

Do not expose mutation tools publicly without authentication and authorization.

In particular:

```text
request_order_cancellation
create_support_ticket
```

should be protected by business authorization and ideally confirmation/approval rules.
