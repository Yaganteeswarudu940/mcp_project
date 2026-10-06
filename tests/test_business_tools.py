from business.data_store import get_inventory, get_order
from business.mcp_server import get_inventory_status, get_order_status


def test_order_exists():
    order = get_order("ORD-1001")
    assert order is not None
    assert order["status"] == "SHIPPED"


def test_inventory_tool():
    result = get_inventory_status("SKU-RUN-BLU-42")
    assert result["found"] is True
    assert result["inventory"]["available"] == 7


def test_order_tool():
    result = get_order_status("ORD-1003")
    assert result["found"] is True
    assert result["order"]["status"] == "DELAYED"
