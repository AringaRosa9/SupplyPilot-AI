import argparse
import asyncio

from app.db.session import SessionLocal
from app.demo.seed import seed_demo_data


async def run(reset: bool) -> None:
    async with SessionLocal() as session:
        campaign_id = await seed_demo_data(session, reset=reset)
    print(f"Demo campaign ready: {campaign_id}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed deterministic SupplyPilot demo data")
    parser.add_argument("--reset", action="store_true", help="replace existing M1 demo data")
    args = parser.parse_args()
    asyncio.run(run(args.reset))


if __name__ == "__main__":
    main()
