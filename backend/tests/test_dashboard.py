from app.api.v1.dashboard import ROLES, decision_action, resolve_role


def test_demo_roles_cover_distinct_permissions() -> None:
    assert set(ROLES) == {"marketing_ops", "sourcing_manager", "product_ops", "executive"}
    assert "审核商品" in ROLES["product_ops"].capabilities
    assert decision_action("pending_review", "product_ops") == "开始审核"
    assert decision_action("inventory_gap", "sourcing_manager") == "创建招商任务"
    assert decision_action("supplier_concentration", "executive") is None


def test_invalid_role_falls_back_to_marketing_operations() -> None:
    assert resolve_role("unknown", None) == "marketing_ops"
    assert resolve_role(None, "product_ops") == "product_ops"
