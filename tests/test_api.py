def test_import_api():
    # Import-level smoke test. The FastAPI app is intentionally not called
    # here because a full MCP session lifecycle is an integration concern.
    from api.main import app
    assert app.title == "MCP Agentic Business Copilot API"
