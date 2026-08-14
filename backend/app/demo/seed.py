import random
import uuid
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.domain import (
    Alert,
    Campaign,
    InventorySnapshot,
    PoolStatus,
    Product,
    ProductLine,
    ProductPoolEntry,
    SourcingTask,
    Supplier,
    SupplyTarget,
)

DEMO_SEED = 20260814
DEMO_CAMPAIGN_NAME = "东南亚暑期旅行节"
NAMESPACE = uuid.UUID("6d60f5a9-39f8-4e6e-9c22-5063fd436670")


def demo_id(key: str) -> uuid.UUID:
    return uuid.uuid5(NAMESPACE, key)


async def reset_demo_data(session: AsyncSession) -> None:
    campaign_id = demo_id("campaign")
    product_ids = list(
        (
            await session.scalars(
                select(ProductPoolEntry.product_id).where(
                    ProductPoolEntry.campaign_id == campaign_id
                )
            )
        ).all()
    )
    await session.execute(delete(Alert).where(Alert.campaign_id == campaign_id))
    await session.execute(delete(SupplyTarget).where(SupplyTarget.campaign_id == campaign_id))
    await session.execute(delete(SourcingTask).where(SourcingTask.campaign_id == campaign_id))
    await session.execute(
        delete(ProductPoolEntry).where(ProductPoolEntry.campaign_id == campaign_id)
    )
    if product_ids:
        await session.execute(
            delete(InventorySnapshot).where(InventorySnapshot.product_id.in_(product_ids))
        )
        await session.execute(delete(Product).where(Product.id.in_(product_ids)))
    await session.execute(delete(Campaign).where(Campaign.id == campaign_id))
    await session.execute(delete(Supplier).where(Supplier.code.like("DEMO-%")))
    await session.commit()


async def seed_demo_data(session: AsyncSession, *, reset: bool = False) -> uuid.UUID:
    if reset:
        await reset_demo_data(session)
    existing = await session.get(Campaign, demo_id("campaign"))
    if existing:
        return existing.id

    rng = random.Random(DEMO_SEED)
    now = datetime(2026, 8, 14, 9, 30, tzinfo=UTC)
    campaign = Campaign(
        id=demo_id("campaign"),
        name=DEMO_CAMPAIGN_NAME,
        description="覆盖中国、新加坡与澳大利亚客源市场的 Hotel / Flight 联合招商活动。",
        status="active",
        target_markets=["中国", "新加坡", "澳大利亚"],
        product_lines=["hotel", "flight"],
        starts_at=datetime(2026, 7, 1, tzinfo=UTC),
        ends_at=datetime(2026, 8, 31, tzinfo=UTC),
        sourcing_deadline=datetime(2026, 8, 20, tzinfo=UTC),
        owner_id="lin-xia",
        requirements={"audiences": ["亲子", "高星酒店"], "price_advantage": 0.05},
    )
    session.add(campaign)
    await session.flush()

    supplier_specs = [
        ("TRAVELNEST", "TravelNest Asia", ["中国", "新加坡"], 82, 0.94, 0.038),
        ("SIAM", "Siam Connect", ["中国", "澳大利亚"], 76, 0.90, 0.062),
        ("MERIDIAN", "Meridian Beds", ["新加坡", "澳大利亚"], 89, 0.97, 0.021),
        ("ORBIT", "Orbit Air Supply", ["中国", "新加坡", "澳大利亚"], 86, 0.95, 0.029),
        ("PACIFIC", "Pacific Routes", ["中国", "澳大利亚"], 80, 0.92, 0.044),
    ]
    suppliers: list[Supplier] = []
    for code, name, markets, quality, fulfillment, cancellation in supplier_specs:
        supplier = Supplier(
            id=demo_id(f"supplier-{code}"),
            code=f"DEMO-{code}",
            name=name,
            markets=markets,
            quality_score=Decimal(quality),
            performance={
                "fulfillment_rate": fulfillment,
                "cancellation_rate": cancellation,
                "historical_conversion": round(rng.uniform(0.032, 0.081), 4),
            },
        )
        suppliers.append(supplier)
        session.add(supplier)
    await session.flush()

    hotel_cities = ["Bangkok", "Bangkok", "Bangkok", "Phuket", "Singapore", "Chiang Mai"]
    hotel_names = [
        "河畔悦榕酒店",
        "暹罗亲子度假村",
        "素坤逸城市酒店",
        "卡塔海滩酒店",
        "滨海亲子酒店",
        "兰纳精品酒店",
    ]
    flight_routes = ["上海—Phuket", "北京—Bangkok", "Singapore—Chiang Mai", "Sydney—Bangkok"]
    products: list[Product] = []
    pending_review = 0

    for index in range(24):
        city = hotel_cities[index % len(hotel_cities)]
        # Bangkok is deliberately concentrated: 9 of 12 products come from TravelNest.
        supplier = (
            suppliers[0] if city == "Bangkok" and index % 4 != 3 else suppliers[1 + index % 2]
        )
        product = Product(
            id=demo_id(f"hotel-{index}"),
            external_code=f"HTL-{index + 1:03d}",
            product_line=ProductLine.HOTEL,
            supplier_id=supplier.id,
            name=f"{city} · {hotel_names[index % len(hotel_names)]}",
            market=["中国", "新加坡", "澳大利亚"][index % 3],
            attributes={
                "city": city,
                "stars": 4 + index % 2,
                "audience": "亲子" if index % 5 == 0 else "休闲",
                "historical_conversion": round(rng.uniform(0.035, 0.095), 4),
            },
        )
        products.append(product)
        session.add(product)

    for index in range(16):
        route = flight_routes[index % len(flight_routes)]
        supplier = suppliers[3 + index % 2]
        product = Product(
            id=demo_id(f"flight-{index}"),
            external_code=f"FLT-{index + 1:03d}",
            product_line=ProductLine.FLIGHT,
            supplier_id=supplier.id,
            name=f"{route} · {['经济舱', '灵活经济舱'][index % 2]}",
            market=["中国", "新加坡", "澳大利亚"][index % 3],
            attributes={
                "route": route,
                "stops": index % 2,
                "historical_conversion": round(rng.uniform(0.025, 0.069), 4),
            },
        )
        products.append(product)
        session.add(product)

    await session.flush()

    for index, product in enumerate(products):
        status = (
            PoolStatus.PENDING_REVIEW
            if index < 12
            else (PoolStatus.LISTED if index % 3 else PoolStatus.READY_FOR_GRADING)
        )
        if status == PoolStatus.PENDING_REVIEW:
            pending_review += 1
        session.add(
            ProductPoolEntry(
                id=demo_id(f"pool-{index}"),
                campaign_id=campaign.id,
                product_id=product.id,
                status=status,
            )
        )
        is_phuket_gap = (
            product.product_line == ProductLine.FLIGHT
            and product.attributes.get("route") == "上海—Phuket"
        )
        inventory = (
            rng.randint(55, 145)
            if product.product_line == ProductLine.HOTEL
            else rng.randint(180, 520)
        )
        if is_phuket_gap:
            inventory = rng.randint(60, 95)
        price = Decimal(
            rng.randint(520, 1280)
            if product.product_line == ProductLine.HOTEL
            else rng.randint(900, 2600)
        )
        session.add(
            InventorySnapshot(
                id=demo_id(f"snapshot-{index}"),
                product_id=product.id,
                snapshot_at=now,
                inventory=inventory,
                price=price,
                benchmark_price=(price * Decimal("1.07")).quantize(Decimal("0.01")),
                conversion_rate=Decimal(str(product.attributes["historical_conversion"])),
            )
        )

    assert pending_review == 12
    targets = [
        (ProductLine.HOTEL, "中国", {"destination": "Bangkok"}, 12, 1300),
        (ProductLine.HOTEL, "中国", {"destination": "Phuket"}, 8, 800),
        (ProductLine.HOTEL, "新加坡", {"destination": "Singapore", "audience": "亲子"}, 8, 700),
        (ProductLine.HOTEL, "澳大利亚", {"destination": "Chiang Mai"}, 6, 500),
        (ProductLine.FLIGHT, "中国", {"route": "上海—Phuket"}, 8, 1200),
        (ProductLine.FLIGHT, "新加坡", {"route": "Singapore—Chiang Mai"}, 4, 900),
        (ProductLine.FLIGHT, "澳大利亚", {"route": "Sydney—Bangkok"}, 4, 1000),
    ]
    for index, (line, market, dimension, product_count, inventory) in enumerate(targets):
        session.add(
            SupplyTarget(
                id=demo_id(f"target-{index}"),
                campaign_id=campaign.id,
                product_line=line,
                market=market,
                dimension=dimension,
                target_product_count=product_count,
                target_inventory=inventory,
            )
        )

    tasks = [
        (ProductLine.HOTEL, "Bangkok / 高星", "chen-jing", "high", 72),
        (ProductLine.HOTEL, "Singapore / 亲子", "zhou-min", "high", 48),
        (ProductLine.FLIGHT, "上海—Phuket", "wang-yan", "urgent", 38),
    ]
    for index, (line, scope, assignee, priority, progress) in enumerate(tasks):
        session.add(
            SourcingTask(
                id=demo_id(f"task-{index}"),
                campaign_id=campaign.id,
                product_line=line,
                scope={"label": scope},
                assignee_id=assignee,
                priority=priority,
                status="in_progress",
                due_at=datetime(2026, 8, 20, tzinfo=UTC),
                progress=progress,
            )
        )

    alerts: list[tuple[str, str, str, dict[str, Any]]] = [
        (
            "supplier_concentration",
            "P0",
            "曼谷酒店供应商集中度过高",
            {"hhi": 0.61, "top_supplier_share": 0.75, "threshold": 0.45},
        ),
        (
            "inventory_gap",
            "P1",
            "上海—普吉库存缺口 38%",
            {"route": "上海—Phuket", "gap_rate": 0.38, "missing_inventory": 456},
        ),
        (
            "audience_gap",
            "P1",
            "新加坡亲子酒店缺口",
            {"destination": "Singapore", "audience": "亲子", "missing_products": 5},
        ),
        ("pending_review", "P1", "12 个商品等待审核", {"count": 12}),
    ]
    for index, (alert_type, severity, title, facts) in enumerate(alerts):
        session.add(
            Alert(
                id=demo_id(f"alert-{index}"),
                campaign_id=campaign.id,
                type=alert_type,
                severity=severity,
                entity_type="campaign",
                entity_id=campaign.id,
                facts={"title": title, **facts},
                owner_id="lin-xia" if index != 2 else "zhou-min",
            )
        )

    await session.commit()
    return campaign.id
