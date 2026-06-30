import asyncio

from sqlmodel import delete

from app.db.models import Domain
from app.db.session import AsyncSessionLocal, init_db
from app.memory.domain_manager import DomainManager


async def main():
    await init_db()

    manager = DomainManager()

    async with AsyncSessionLocal() as db:
        # Clean up from previous test runs.
        await db.execute(delete(Domain).where(Domain.user == "demo_test"))
        await db.commit()

        domain = await manager.create_domain(
            db,
            user="demo_test",
            slug="ai-safety",
            title="AI Safety",
        )

        print(f"created OK — {domain.dataset_name}")

        found = await manager.get_domain_by_slug(
            db,
            user="demo_test",
            slug="ai-safety",
        )

        print(f"lookup OK — {found.title}")

        domains = await manager.list_domains(db, user="demo_test")
        print(f"list OK — {len(domains)} domain(s)")

        await manager.delete_domain(db, domain)
        print("delete OK")


if __name__ == "__main__":
    asyncio.run(main())