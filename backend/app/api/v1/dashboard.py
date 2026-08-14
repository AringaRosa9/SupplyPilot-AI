from datetime import datetime
from typing import Annotated, Any, Literal

from fastapi import APIRouter, Depends, Header, Query
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.errors import AppError
from app.db.session import get_session
from app.demo.seed import DEMO_CAMPAIGN_NAME, seed_demo_data
from app.models.domain import (
    Alert,
    Campaign,
    InventorySnapshot,
    PoolStatus,
    Product,
    ProductLine,
    ProductPoolEntry,
    Supplier,
    SupplyTarget,
)

router = APIRouter(tags=["dashboard"])
DemoRole = Literal["marketing_ops", "sourcing_manager", "product_ops", "executive"]


class RoleOption(BaseModel):
    id: DemoRole
    name: str
    title: str
    description: str
    initials: str
    capabilities: list[str]


ROLES: dict[DemoRole, RoleOption] = {
    "marketing_ops": RoleOption(
        id="marketing_ops",
        name="林夏",
        title="全球营销运营",
        description="关注活动准备度、跨产线风险与整体推进。",
        initials="林",
        capabilities=["查看全部风险", "创建招商活动", "分配负责人"],
    ),
    "sourcing_manager": RoleOption(
        id="sourcing_manager",
        name="陈静",
        title="供应链招商经理",
        description="优先处理供给缺口、供应商风险与临期任务。",
        initials="陈",
        capabilities=["查看招商风险", "跟进供应商", "更新任务进度"],
    ),
    "product_ops": RoleOption(
        id="product_ops",
        name="周敏",
        title="商品运营",
        description="优先处理待审核商品与数据异常。",
        initials="周",
        capabilities=["查看商品风险", "审核商品", "要求补充信息"],
    ),
    "executive": RoleOption(
        id="executive",
        name="高远",
        title="业务管理层",
        description="查看高影响风险与跨产线准备度，只读演示。",
        initials="高",
        capabilities=["查看经营摘要", "查看高影响风险"],
    ),
}


class DashboardResponse(BaseModel):
    campaign: dict[str, Any]
    role: RoleOption
    decision_queue: list[dict[str, Any]]
    health: dict[str, Any]
    readiness: dict[str, Any]
    coverage: list[dict[str, Any]]
    updated_at: datetime
    permissions: dict[str, bool]


def resolve_role(role: str | None, header_role: str | None) -> DemoRole:
    candidate = role or header_role or "marketing_ops"
    return candidate if candidate in ROLES else "marketing_ops"


def decision_action(alert_type: str, role: DemoRole) -> str | None:
    if role == "executive":
        return None
    if alert_type == "pending_review":
        return "开始审核" if role in {"marketing_ops", "product_ops"} else "查看商品"
    if alert_type in {"inventory_gap", "audience_gap"}:
        return "创建招商任务" if role in {"marketing_ops", "sourcing_manager"} else "查看缺口"
    return "查看供应商" if role == "product_ops" else "制定分散计划"


async def build_dashboard(session: AsyncSession, role: DemoRole) -> DashboardResponse:
    campaign = await session.scalar(select(Campaign).where(Campaign.name == DEMO_CAMPAIGN_NAME))
    if campaign is None:
        await seed_demo_data(session)
        campaign = await session.scalar(select(Campaign).where(Campaign.name == DEMO_CAMPAIGN_NAME))
    assert campaign is not None

    alert_rows = list(
        (
            await session.scalars(
                select(Alert)
                .where(Alert.campaign_id == campaign.id, Alert.status == "open")
                .order_by(Alert.severity, Alert.created_at)
            )
        ).all()
    )
    role_priority = {
        "marketing_ops": [
            "supplier_concentration",
            "inventory_gap",
            "audience_gap",
            "pending_review",
        ],
        "sourcing_manager": [
            "inventory_gap",
            "supplier_concentration",
            "audience_gap",
            "pending_review",
        ],
        "product_ops": [
            "pending_review",
            "audience_gap",
            "inventory_gap",
            "supplier_concentration",
        ],
        "executive": ["supplier_concentration", "inventory_gap", "audience_gap", "pending_review"],
    }[role]
    alert_rows.sort(key=lambda item: role_priority.index(item.type))
    decisions = [
        {
            "id": str(item.id),
            "severity": item.severity,
            "type": item.type,
            "title": item.facts.get("title", item.type),
            "facts": item.facts,
            "action": decision_action(item.type, role),
        }
        for item in alert_rows
    ]

    pool_rows = list(
        (
            await session.execute(
                select(Product, ProductPoolEntry, InventorySnapshot, Supplier)
                .join(ProductPoolEntry, ProductPoolEntry.product_id == Product.id)
                .join(InventorySnapshot, InventorySnapshot.product_id == Product.id)
                .join(Supplier, Supplier.id == Product.supplier_id)
                .where(ProductPoolEntry.campaign_id == campaign.id)
            )
        ).all()
    )
    target_rows = list(
        (
            await session.scalars(
                select(SupplyTarget).where(SupplyTarget.campaign_id == campaign.id)
            )
        ).all()
    )

    coverage: list[dict[str, Any]] = []
    for target in target_rows:
        dimension_key = "city" if target.product_line == ProductLine.HOTEL else "route"
        dimension_value = target.dimension.get("destination") or target.dimension.get("route")
        matched = [
            (product, snapshot)
            for product, _entry, snapshot, _supplier in pool_rows
            if product.product_line == target.product_line
            and product.market == target.market
            and product.attributes.get(dimension_key) == dimension_value
            and (
                not target.dimension.get("audience")
                or product.attributes.get("audience") == target.dimension.get("audience")
            )
        ]
        current_inventory = sum(snapshot.inventory for _product, snapshot in matched)
        product_coverage = min(1, len(matched) / max(target.target_product_count, 1))
        inventory_coverage = min(1, current_inventory / max(target.target_inventory, 1))
        coverage.append(
            {
                "market": target.market,
                "product_line": target.product_line.value,
                "scope": dimension_value,
                "audience": target.dimension.get("audience"),
                "current_products": len(matched),
                "target_products": target.target_product_count,
                "current_inventory": current_inventory,
                "target_inventory": target.target_inventory,
                "coverage_rate": round(min(product_coverage, inventory_coverage), 2),
            }
        )

    submitted = sum(entry.status != PoolStatus.SOURCING for _p, entry, _s, _v in pool_rows)
    validated = sum(
        entry.status not in {PoolStatus.SOURCING, PoolStatus.SUBMITTED, PoolStatus.VALIDATING}
        for _p, entry, _s, _v in pool_rows
    )
    listed = sum(entry.status == PoolStatus.LISTED for _p, entry, _s, _v in pool_rows)
    pending = sum(entry.status == PoolStatus.PENDING_REVIEW for _p, entry, _s, _v in pool_rows)
    avg_coverage = sum(row["coverage_rate"] for row in coverage) / max(len(coverage), 1)
    gap_penalty = round((1 - avg_coverage) * 18)
    concentration_penalty = 8
    review_penalty = min(6, pending // 2)
    health_score = max(0, 100 - gap_penalty - concentration_penalty - review_penalty)

    return DashboardResponse(
        campaign={
            "id": str(campaign.id),
            "name": campaign.name,
            "status": campaign.status,
            "target_markets": campaign.target_markets,
            "product_lines": campaign.product_lines,
            "sourcing_deadline": campaign.sourcing_deadline,
        },
        role=ROLES[role],
        decision_queue=decisions,
        health={
            "score": health_score,
            "weekly_change": -6,
            "dimensions": [
                {"name": "供给覆盖", "score": round(avg_coverage * 100), "change": -8},
                {"name": "供应商结构", "score": 61, "change": -7},
                {"name": "库存稳定", "score": 78, "change": -3},
                {"name": "商品质量", "score": 86, "change": 2},
            ],
            "methodology": "覆盖率、集中度、库存稳定性与商品质量的加权结果",
        },
        readiness={
            "target": 48,
            "submitted": submitted,
            "validated": validated,
            "high_grade": 18,
            "listed": listed,
            "pending_review": pending,
        },
        coverage=coverage,
        updated_at=max(snapshot.snapshot_at for _p, _e, snapshot, _s in pool_rows),
        permissions={
            "create_campaign": role == "marketing_ops",
            "create_task": role in {"marketing_ops", "sourcing_manager"},
            "review_product": role in {"marketing_ops", "product_ops"},
            "read_only": role == "executive",
        },
    )


@router.get("/demo/roles", response_model=list[RoleOption])
async def list_demo_roles() -> list[RoleOption]:
    return list(ROLES.values())


@router.get("/dashboard", response_model=DashboardResponse)
async def get_dashboard(
    session: Annotated[AsyncSession, Depends(get_session)],
    role: Annotated[str | None, Query()] = None,
    x_demo_role: Annotated[str | None, Header()] = None,
) -> DashboardResponse:
    return await build_dashboard(session, resolve_role(role, x_demo_role))


@router.post("/demo/reset", response_model=dict[str, str])
async def reset_demo(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> dict[str, str]:
    if settings.app_env == "production":
        raise AppError("demo_reset_disabled", "生产环境不允许重置演示数据", 403)
    campaign_id = await seed_demo_data(session, reset=True)
    return {"status": "ok", "campaign_id": str(campaign_id)}
