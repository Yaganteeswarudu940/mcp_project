import asyncio
import os
import streamlit as st

st.set_page_config(
    page_title="MCP Agentic Business Copilot",
    page_icon="🤖",
    layout="wide",
)

# STEP 1: Populate os.environ FIRST before importing/calling settings
for key, value in st.secrets.items():
    if isinstance(value, str):
        os.environ[key] = value

# STEP 2: Import and initialize settings AFTER os.environ is set
from common.config import get_settings
from agent.agent_host import AgentHost
from business.mcp_server import business_mcp

settings = get_settings()

st.title("🤖 MCP Agentic Business Copilot")
st.caption("Gemini + MCP Host + MCP Client + MCP Server + FastAPI + Streamlit")

with st.sidebar:
    st.header("Architecture")
    if settings.api_base_url:
        st.success("Remote FastAPI mode")
        st.code(settings.api_base_url, language="text")
    else:
        st.info("In-process MCP demo mode")
        st.write("Streamlit uses the MCP Client directly against an in-process MCP Server.")

    st.divider()
    st.write("**MCP concepts**")
    st.write("✓ Host / Agent")
    st.write("✓ Client")
    st.write("✓ Server")
    st.write("✓ Tools")
    st.write("✓ Resources")
    st.write("✓ Prompts")
    st.write("✓ Streamable HTTP")
    st.write("✓ Agentic tool loop")

    st.divider()
    st.write("**Gemini model**")
    st.code(settings.gemini_model)

st.markdown(
    """
### Real-time business scenario

Ask an operations agent about **orders, inventory, customers, returns, shipping delays,
or support tickets**. The agent decides which MCP capabilities to use.
"""
)

examples = [
    "Where is order ORD-1001?",
    "Check ORD-1002 and tell me whether it is eligible for a return.",
    "The customer says ORD-1003 is delayed. Check the order and customer, then create a support ticket and draft a response.",
    "Is SKU-RUN-BLU-42 available?",
]

selected = st.selectbox("Example", ["Custom"] + examples)

if selected == "Custom":
    query = st.text_area(
        "Business request",
        placeholder="Example: Where is order ORD-1001?",
        height=120,
    )
else:
    query = selected
    st.text_area("Business request", value=query, height=120, disabled=True)

run = st.button("Run agent", type="primary", use_container_width=True)

if run:
    if not query.strip():
        st.warning("Enter a business request.")
        st.stop()

    try:
        with st.spinner("Agent is reasoning and using MCP capabilities..."):
            if settings.api_base_url:
                import httpx

                response = httpx.post(
                    f"{settings.api_base_url.rstrip('/')}/agent/run",
                    json={"query": query},
                    timeout=90,
                )
                response.raise_for_status()
                result = response.json()
            else:
                host = AgentHost(business_mcp)
                result = asyncio.run(host.run(query))

        st.subheader("Answer")
        st.success(result["answer"])

        st.subheader("Agent / MCP trace")
        for item in result.get("trace", []):
            kind = item.get("type", "event")

            if kind == "gemini_decision":
                with st.expander(f"Step {item['step']} — Gemini decision", expanded=False):
                    st.json(item["decision"])

            elif kind == "mcp_tool_call":
                with st.expander(
                    f"Step {item['step']} — MCP tool: {item['tool_name']}",
                    expanded=True,
                ):
                    st.json(item)

            elif kind == "mcp_tool_result":
                with st.expander(
                    f"Step {item['step']} — MCP result",
                    expanded=False,
                ):
                    st.json(item["result"])

            else:
                with st.expander(kind):
                    st.json(item)

    except Exception as exc:
        st.error(f"Agent execution failed: {exc}")
        st.info(
            "Check GEMINI_API_KEY. If API_BASE_URL is configured, also verify that "
            "the FastAPI service is reachable and exposes /agent/run and /mcp."
        )

st.divider()
st.markdown(
    """
**Teaching point:** Gemini is the reasoning layer. The MCP Client is the protocol
layer. The MCP Server owns business capabilities. This separation lets the same
business capabilities be reused by different AI hosts.
"""
)
