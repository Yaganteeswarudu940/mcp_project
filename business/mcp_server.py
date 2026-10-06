from typing import Any

from mcp.server import MCPServer

from business.data_store import (
    create_ticket,
    get_customer,
    get_inventory,
    get_order,
)

business_mcp = MCPServer(
    "Ecommerce Operations MCP",
    instructions=(
        "Use business tools for order, inventory, customer and support operations. "
        "Use resources for policy/context. Do not invent business data."
    ),
)


@business_mcp.tool(title="Get order status")
def get_order_status(order_id: str) -> dict[str, Any]:
    """Get the current order status, shipment information and items for an order."""
    order = get_order(order_id)
    if not order:
        return {"found": False, "error": f"Order {order_id} was not found."}
    return {"found": True, "order": order}


@business_mcp.tool(title="Get inventory")
def get_inventory_status(sku: str) -> dict[str, Any]:
    """Check current available inventory for a SKU."""
    item = get_inventory(sku)
    if not item:
        return {"found": False, "error": f"SKU {sku} was not found."}
    return {"found": True, "inventory": item}


@business_mcp.tool(title="Get customer")
def get_customer_profile(customer_id: str) -> dict[str, Any]:
    """Retrieve a customer profile by customer ID."""
    customer = get_customer(customer_id)
    if not customer:
        return {"found": False, "error": f"Customer {customer_id} was not found."}
    return {"found": True, "customer": customer}


@business_mcp.tool(title="Create support ticket")
def create_support_ticket(
    order_id: str,
    issue: str,
    priority: str = "normal",
) -> dict[str, Any]:
    """Create a customer support ticket for an order issue."""
    order = get_order(order_id)
    if not order:
        return {"created": False, "error": f"Order {order_id} was not found."}

    ticket = create_ticket(order_id, issue, priority)
    return {"created": True, "ticket": ticket}


@business_mcp.tool(title="Request order cancellation")
def request_order_cancellation(order_id: str, reason: str) -> dict[str, Any]:
    """Create a cancellation request; this demo does not directly cancel an order."""
    order = get_order(order_id)
    if not order:
        return {"requested": False, "error": f"Order {order_id} was not found."}

    if order["status"] in {"DELIVERED", "CANCELLED"}:
        return {
            "requested": False,
            "error": f"Order {order_id} is already {order['status']} and cannot be cancelled.",
        }

    return {
        "requested": True,
        "order_id": order_id.upper(),
        "status": "PENDING_APPROVAL",
        "reason": reason,
        "message": "Cancellation request created for human approval.",
    }


@business_mcp.resource("business://return-policy")
def return_policy() -> str:
    """Current demo return policy."""
    return (
        "Demo return policy: items can normally be returned within 30 days of delivery "
        "if unused and in original condition. Final eligibility depends on product type "
        "and the real order system."
    )


@business_mcp.resource("order://{order_id}")
def order_resource(order_id: str) -> str:
    """A resource template exposing a concise order context."""
    order = get_order(order_id)
    if not order:
        return f"Order {order_id} was not found."
    return (
        f"Order {order['order_id']} status={order['status']}; "
        f"customer={order['customer_id']}; "
        f"estimated_delivery={order['estimated_delivery']}."
    )


@business_mcp.prompt(title="Customer response")
def customer_response(order_id: str, issue: str) -> str:
    """Generate a reusable customer-service response instruction."""
    return (
        f"Draft a concise, empathetic support response for order {order_id}. "
        f"Customer issue: {issue}. Use verified facts only and explain the next step."
    )
