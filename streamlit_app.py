import asyncio
import os

import streamlit as st

from agent.agent_host import AgentHost
from common.config import get_settings


st.set_page_config(
    page_title="MCP Agentic Business Copilot",
    page_icon="🤖",
    layout="wide",
)

st.title("🤖 MCP Agentic Business Copilot")
st.caption("Gemini + Agent Host + Python business functions + Streamlit")

# Streamlit Cloud secrets are exposed through st.secrets. Populate environment
# variables so the shared config module can use the same code path.
for key in [
    "GEMINI_API_KEY",
    "GEMINI_MODEL",
    "MAX_AGENT_STEPS",
]:
    if key in st.secrets and st.secrets[key] is not None:
        os.environ[key] = str(st.secrets[key])

settings = get_settings()

with st.sidebar:
    st.header("Architecture")
    st.info("Direct function-call mode")
    st.write("Streamlit calls the Agent Host, which calls the Python business functions directly. No FastAPI, no HTTP.")

    st.divider()
    st.write("**Concepts**")
    st.write("✓ Host / Agent")
    st.write("✓ Tools")
    st.write("✓ Agentic tool loop")

    st.divider()
    st.write("**Gemini model**")
    st.code(settings.gemini_model)

st.markdown(
    """
### Real-time business scenario

Ask an operations agent about **orders, inventory, customers, returns, shipping delays,
or support tickets**. The agent decides which business tool to use.
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
        with st.spinner("Agent is reasoning and calling business functions..."):
            host = AgentHost()
            result = asyncio.run(host.run(query))

        st.subheader("Answer")
        st.success(result["answer"])

        st.subheader("Agent trace")
        for item in result.get("trace", []):
            kind = item.get("type", "event")

            if kind == "gemini_decision":
                with st.expander(f"Step {item['step']} — Gemini decision", expanded=False):
                    st.json(item["decision"])

            elif kind == "mcp_tool_call":
                with st.expander(
                    f"Step {item['step']} — Tool: {item['tool_name']}",
                    expanded=True,
                ):
                    st.json(item)

            elif kind == "mcp_tool_result":
                with st.expander(
                    f"Step {item['step']} — Tool result",
                    expanded=False,
                ):
                    st.json(item["result"])

            else:
                with st.expander(kind):
                    st.json(item)

    except Exception as exc:
        st.error(f"Agent execution failed: {exc}")
        st.info("Check GEMINI_API_KEY and GEMINI_MODEL in the Streamlit secrets.")

st.divider()
st.markdown(
    """
**Teaching point:** Gemini is the reasoning layer. The Agent Host runs the tool loop
and calls plain Python business functions directly.
"""
)
