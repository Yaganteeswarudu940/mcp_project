from typing import Any

from business.data_store import create_ticket, get_customer, get_inventory, get_order


def get_order_status(order_id: str) -> dict[str, Any]:
    """Get the current order status, shipment information and items for an order."""
    order = get_order(order_id)
    if not order:
        return {"found": False, "error": f"Order {order_id} was not found."}
    return {"found": True, "order": order}


def get_inventory_status(sku: str) -> dict[str, Any]:
    """Check current available inventory for a SKU."""
    item = get_inventory(sku)
    if not item:
        return {"found": False, "error": f"SKU {sku} was not found."}
    return {"found": True, "inventory": item}


def get_customer_profile(customer_id: str) -> dict[str, Any]:
    """Retrieve a customer profile by customer ID."""
    customer = get_customer(customer_id)
    if not customer:
        return {"found": False, "error": f"Customer {customer_id} was not found."}
    return {"found": True, "customer": customer}


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

