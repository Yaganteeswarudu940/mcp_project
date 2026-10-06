from typing import Any

from business.mcp_server import (
    create_support_ticket,
    get_customer_profile,
    get_inventory_status,
    get_order_status,
    request_order_cancellation,
)


def _spec(name: str, title: str, description: str, props: dict[str, str], required: list[str]):
    return {
        "name": name,
        "title": title,
        "description": description,
        "input_schema": {
            "type": "object",
            "properties": {k: {"type": "string", "description": v} for k, v in props.items()},
            "required": required,
        },
    }


# name -> (python function, spec shown to Gemini)
TOOLS: dict[str, tuple[Any, dict[str, Any]]] = {
    "get_order_status": (
        get_order_status,
        _spec(
            "get_order_status",
            "Get order status",
            "Get the current order status, shipment information and items for an order.",
            {"order_id": "Order ID"},
            ["order_id"],
        ),
    ),
    "get_inventory_status": (
        get_inventory_status,
        _spec(
            "get_inventory_status",
            "Get inventory",
            "Check current available inventory for a SKU.",
            {"sku": "Product SKU"},
            ["sku"],
        ),
    ),
    "get_customer_profile": (
        get_customer_profile,
        _spec(
            "get_customer_profile",
            "Get customer",
            "Retrieve a customer profile by customer ID.",
            {"customer_id": "Customer ID"},
            ["customer_id"],
        ),
    ),
    "create_support_ticket": (
        create_support_ticket,
        _spec(
            "create_support_ticket",
            "Create support ticket",
            "Create a customer support ticket for an order issue.",
            {"order_id": "Order ID", "issue": "Issue description", "priority": "low|normal|high"},
            ["order_id", "issue"],
        ),
    ),
    "request_order_cancellation": (
        request_order_cancellation,
        _spec(
            "request_order_cancellation",
            "Request order cancellation",
            "Create a cancellation request for human approval.",
            {"order_id": "Order ID", "reason": "Cancellation reason"},
            ["order_id", "reason"],
        ),
    ),
}


class LocalToolAdapter:
    """Same interface as MCPClientAdapter, but calls the Python functions directly."""

    def __init__(self, target: Any = None) -> None:
        pass

    async def inspect(self) -> dict[str, Any]:
        return {"tools": [spec for _, spec in TOOLS.values()]}

    async def list_tool_specs(self) -> list[dict[str, Any]]:
        return [spec for _, spec in TOOLS.values()]

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        func, _ = TOOLS[name]
        try:
            output = func(**arguments)
            is_error = False
        except Exception as exc:  # bad/missing arguments etc.
            output = {"error": str(exc)}
            is_error = True
        return {
            "tool_name": name,
            "arguments": arguments,
            "is_error": is_error,
            "content": [str(output)],
            "structured_content": output,
        }