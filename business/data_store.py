from copy import deepcopy
from datetime import datetime, timezone


ORDERS = {
    "ORD-1001": {
        "order_id": "ORD-1001",
        "customer_id": "CUS-001",
        "status": "SHIPPED",
        "items": [{"sku": "SKU-RUN-BLU-42", "name": "Blue Running Shoe", "qty": 1}],
        "carrier": "DHL",
        "tracking_number": "DHL-IND-1001",
        "estimated_delivery": "2026-10-08",
        "created_at": "2026-10-01",
    },
    "ORD-1002": {
        "order_id": "ORD-1002",
        "customer_id": "CUS-002",
        "status": "DELIVERED",
        "items": [{"sku": "SKU-HEAD-BLK", "name": "Wireless Headphones", "qty": 1}],
        "carrier": "FedEx",
        "tracking_number": "FDX-IND-1002",
        "estimated_delivery": "2026-10-04",
        "created_at": "2026-09-28",
    },
    "ORD-1003": {
        "order_id": "ORD-1003",
        "customer_id": "CUS-003",
        "status": "DELAYED",
        "items": [{"sku": "SKU-BAG-GRY", "name": "Travel Backpack", "qty": 1}],
        "carrier": "BlueDart",
        "tracking_number": "BD-IND-1003",
        "estimated_delivery": "2026-10-06",
        "created_at": "2026-09-30",
    },
}

CUSTOMERS = {
    "CUS-001": {
        "customer_id": "CUS-001",
        "name": "Aarav",
        "tier": "GOLD",
        "email": "aarav@example.com",
    },
    "CUS-002": {
        "customer_id": "CUS-002",
        "name": "Meera",
        "tier": "SILVER",
        "email": "meera@example.com",
    },
    "CUS-003": {
        "customer_id": "CUS-003",
        "name": "Rahul",
        "tier": "GOLD",
        "email": "rahul@example.com",
    },
}

INVENTORY = {
    "SKU-RUN-BLU-42": {"sku": "SKU-RUN-BLU-42", "name": "Blue Running Shoe", "available": 7, "warehouse": "HYD-01"},
    "SKU-HEAD-BLK": {"sku": "SKU-HEAD-BLK", "name": "Wireless Headphones", "available": 0, "warehouse": "BLR-02"},
    "SKU-BAG-GRY": {"sku": "SKU-BAG-GRY", "name": "Travel Backpack", "available": 12, "warehouse": "HYD-01"},
}

TICKETS: list[dict] = []


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def get_order(order_id: str) -> dict | None:
    order = ORDERS.get(order_id.upper())
    return deepcopy(order) if order else None


def get_customer(customer_id: str) -> dict | None:
    customer = CUSTOMERS.get(customer_id.upper())
    return deepcopy(customer) if customer else None


def get_inventory(sku: str) -> dict | None:
    item = INVENTORY.get(sku.upper())
    return deepcopy(item) if item else None


def create_ticket(order_id: str, issue: str, priority: str) -> dict:
    ticket = {
        "ticket_id": f"TCK-{1000 + len(TICKETS) + 1}",
        "order_id": order_id.upper(),
        "issue": issue,
        "priority": priority.upper(),
        "status": "OPEN",
        "created_at": now_iso(),
    }
    TICKETS.append(ticket)
    return deepcopy(ticket)
