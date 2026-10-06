# MCP Agentic Business Copilot

A production-oriented demo of an **agentic business workflow using MCP + Gemini + FastAPI + Streamlit**.

## Scenario

**E-commerce Customer Support & Order Operations Copilot**

A customer/support user can ask things such as:

- "Where is order ORD-1001?"
- "Is the blue running shoe in stock?"
- "What is the return policy for order ORD-1002?"
- "Create a support ticket for ORD-1003 because the package is delayed."
- "Check the customer and order details, then draft the best response."

The agent decides which MCP tools/resources it needs, calls them through an MCP Client, and then asks Gemini to produce the final business response.

## Architecture

```text
                           ┌─────────────────────────┐
                           │      Streamlit UI        │
                           │     streamlit_app.py     │
                           └────────────┬────────────┘
                                        │ HTTP
                                        ▼
                           ┌─────────────────────────┐
                           │       FastAPI API        │
                           │       api/main.py        │
                           └────────────┬────────────┘
                                        │
                              Agent Host / Orchestrator
                                        │
                                        ▼
                           ┌─────────────────────────┐
                           │      MCP Client          │
                           │   agent/mcp_host.py      │
                           └────────────┬────────────┘
                                        │ Streamable HTTP
                                        ▼
                           ┌─────────────────────────┐
                           │       MCP Server         │
                           │  business/mcp_server.py  │
                           │                           │
                           │ Tools / Resources /       │
                           │ Prompts / Completions     │
                           └────────────┬────────────┘
                                        │
                                        ▼
                           ┌─────────────────────────┐
                           │ Mock business systems    │
                           │ orders / inventory / CRM │
                           └─────────────────────────┘

Gemini is used by the Agent Host as the reasoning/planning model.
```

### Important deployment detail

Streamlit Community Cloud is excellent for the UI, but it is not a general-purpose platform for exposing a separate FastAPI service. This project therefore supports two modes:

1. **Local / single-process demo**: Streamlit uses an in-process MCP server and MCP Client. No second server is required.
2. **Cloud production-style mode**: deploy `api/main.py` as a separate FastAPI service and set `API_BASE_URL` in Streamlit Cloud secrets. The Streamlit frontend then calls FastAPI, while FastAPI hosts the MCP server and Agent Host.

This lets you demonstrate the full architecture without pretending that Streamlit Cloud is a FastAPI hosting platform.

## MCP concepts demonstrated

This project deliberately includes:

- MCP Host / Agent Host
- MCP Client
- MCP Server
- Tools
- Resources
- Resource templates
- Prompts
- Streamable HTTP transport
- In-process MCP transport for testing/demo
- Tool discovery with `list_tools()`
- Tool invocation with `call_tool()`
- Resource discovery and reading
- Prompt discovery and rendering
- Structured tool results
- MCP tool errors
- MCP server lifecycle
- FastAPI + MCP ASGI integration
- Agentic plan -> tool -> observation -> final-answer loop
- Gemini structured JSON planning
- Streamlit frontend
- Cloud secret handling
- Docker deployment for the API

The official MCP Python SDK v2 is used. MCP v2 supports servers, clients, tools, resources, prompts and standard transports including Streamable HTTP. See the official SDK documentation for the current API.

## Project structure

```text
mcp-agentic-business-copilot/
├── streamlit_app.py
├── requirements.txt
├── runtime.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── .gitignore
├── README.md
├── docs/
│   ├── MCP_CONCEPTS.md
│   └── DEPLOYMENT.md
├── .streamlit/
│   └── config.toml
├── api/
│   ├── __init__.py
│   └── main.py
├── agent/
│   ├── __init__.py
│   ├── gemini.py
│   ├── agent_host.py
│   └── mcp_client.py
├── business/
│   ├── __init__.py
│   ├── data_store.py
│   └── mcp_server.py
├── common/
│   ├── __init__.py
│   ├── config.py
│   └── schemas.py
└── tests/
    ├── __init__.py
    ├── test_business_tools.py
    └── test_api.py
```

## 1. Prerequisites

- Python 3.12 recommended
- A Gemini API key
- Git
- Optional: Docker

Create an API key from Google AI Studio.

## 2. Local setup

```bash
git clone <your-repository>
cd mcp-agentic-business-copilot

python -m venv .venv
```

Windows:

```powershell
.venv\Scripts\activate
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and set:

```text
GEMINI_API_KEY=your_key
GEMINI_MODEL=gemini-3.8-flash
MCP_SERVER_URL=http://127.0.0.1:8000/mcp
API_BASE_URL=http://127.0.0.1:8000
```

## 3. Run the full local architecture

Terminal 1:

```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

Terminal 2:

```bash
streamlit run streamlit_app.py
```

Open the Streamlit URL shown in the terminal.

FastAPI:

```text
http://localhost:8000
```

MCP endpoint:

```text
http://localhost:8000/mcp
```

Swagger:

```text
http://localhost:8000/docs
```

## 4. Streamlit-only demo

If `API_BASE_URL` is empty, the Streamlit app uses an in-process MCP server/client. This is useful for teaching and for verifying the MCP flow without running FastAPI.

Set:

```text
API_BASE_URL=
```

The UI will show that it is using local/in-process MCP mode.

## 5. Example prompts

Try:

```text
Where is order ORD-1001?
```

```text
Check ORD-1002 and tell me whether it is eligible for a return.
```

```text
The customer says ORD-1003 is delayed. Check the order and customer, then create a support ticket and draft a response.
```

```text
Is SKU-RUN-RED-42 available? If not, suggest what I should tell the customer.
```

## 6. Streamlit Community Cloud

Push the repository to GitHub.

Community Cloud deployment:

1. Create a Streamlit Community Cloud app.
2. Select the GitHub repository.
3. Select `streamlit_app.py` as the entrypoint.
4. Choose Python 3.12.
5. In Advanced settings -> Secrets, add:

```toml
GEMINI_API_KEY = "your-key"
GEMINI_MODEL = "gemini-3.8-flash"

# Set this only after deploying the FastAPI service.
API_BASE_URL = "https://your-fastapi-service.example.com"
```

Do **not** commit `.streamlit/secrets.toml` or `.env`.

If you want the Streamlit Cloud app to operate completely by itself for demonstration, leave `API_BASE_URL` empty. It will use the in-process MCP path.

For the complete remote architecture, deploy the FastAPI API separately and set `API_BASE_URL`.

## 7. Deploy FastAPI

This repository includes a Dockerfile and `docker-compose.yml`.

Build:

```bash
docker build -t mcp-business-api .
```

Run:

```bash
docker run --env-file .env -p 8000:8000 mcp-business-api
```

For a public deployment, use a service that supports Docker/ASGI such as your preferred cloud provider. Then set the resulting HTTPS URL in Streamlit Cloud:

```toml
API_BASE_URL = "https://your-api.example.com"
```

The API exposes:

- `GET /health`
- `GET /mcp-info`
- `GET /tools`
- `POST /agent/run`
- `/mcp`
- `/docs`

## 8. Security checklist before production

This project uses mock business data intentionally.

Before connecting real systems:

- Add authentication to FastAPI.
- Put the API behind HTTPS.
- Restrict CORS to the deployed Streamlit origin.
- Replace the mock data store with real database/CRM/order APIs.
- Add authorization around mutation tools.
- Add audit logging.
- Add rate limiting.
- Store secrets only in the deployment platform's secret manager.
- Add approval/confirmation for irreversible actions.
- Validate customer identity before exposing order/customer data.
- Avoid returning PII to the model unless necessary.

## 9. Why this is agentic

A normal chatbot can answer from its model context.

This application performs:

```text
User request
    ↓
Gemini planner
    ↓
Select MCP tool/resource
    ↓
MCP Client
    ↓
MCP Server
    ↓
Business data/action
    ↓
Observation returned to Agent Host
    ↓
Gemini decides whether another tool is required
    ↓
Final response
```

The model does not directly access the business data store. It interacts with capabilities exposed through MCP.

## 10. Notes about Gemini

The project uses Google's current `google-genai` SDK rather than the older Gemini Python SDK style.

The model is configurable with:

```text
GEMINI_MODEL=gemini-3.8-flash
```

You can change the model without changing the agent code.

The planner asks Gemini for a small JSON decision:

```json
{
  "action": "tool",
  "tool_name": "get_order_status",
  "arguments": {
    "order_id": "ORD-1001"
  },
  "reason": "The user asked for the order status."
}
```

or:

```json
{
  "action": "final",
  "answer": "..."
}
```

This makes the tool-selection loop deterministic enough for a teaching/demo application.

## 11. Testing

Run:

```bash
pytest -q
```

The tests cover the business tools and API health/configuration paths.

## 12. Suggested demo sequence

For an interview/classroom demo:

1. Explain Host -> Client -> Server.
2. Open `/docs` and show FastAPI.
3. Open `/mcp` conceptually as the MCP transport endpoint.
4. Use the Streamlit UI.
5. Ask for an order status.
6. Show the agent trace in the UI.
7. Explain that Gemini selected the MCP tool.
8. Explain the tool result returned through the MCP client.
9. Ask a multi-step question involving customer + order + support ticket.
10. Show that the agent can call multiple MCP tools.
11. Explain that business capabilities are separated from the LLM.
12. Deploy the Streamlit UI and the API independently.

## License

Use this as a learning/demo template and adapt it to your organization.
