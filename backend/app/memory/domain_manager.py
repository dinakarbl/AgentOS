import re
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.db.models import Domain


class DomainManager:
    """
    Converts user + slug into a safe Cognee dataset name.

    Example:
    user="demo", slug="ai-safety" -> "u_demo_d_ai_safety"
    """

    def _safe(self, value: str) -> str:
        """
        Keep only lowercase letters, numbers, and underscores.

        Cognee/Kuzu-backed dataset names should avoid spaces, hyphens,
        punctuation, and unicode characters.
        """
        return re.sub(r"[^a-z0-9_]", "_", value.lower())[:32]

    def dataset_name(self, user: str, slug: str) -> str:
        """Build the domain-scoped Cognee dataset name."""
        return f"u_{self._safe(user)}_d_{self._safe(slug)}"

    async def create_domain(
        self,
        db: AsyncSession,
        *,
        user: str,
        slug: str,
        title: str,
    ) -> Domain:
        """
        Create a domain row.

        The frontend should never compute dataset_name.
        It only sends user-facing title/slug.
        """
        dataset_name = self.dataset_name(user, slug)

        domain = Domain(
            user=user,
            slug=slug,
            title=title,
            dataset_name=dataset_name,
        )

        db.add(domain)
        await db.commit()
        await db.refresh(domain)

        return domain

    async def get_domain(
        self,
        db: AsyncSession,
        domain_id: str,
    ) -> Optional[Domain]:
        """Find a domain by id."""
        result = await db.execute(
            select(Domain).where(Domain.id == domain_id)
        )
        return result.scalar_one_or_none()

    async def get_domain_by_slug(
        self,
        db: AsyncSession,
        *,
        user: str,
        slug: str,
    ) -> Optional[Domain]:
        """Find a domain by user + slug."""
        result = await db.execute(
            select(Domain).where(
                Domain.user == user,
                Domain.slug == slug,
            )
        )
        return result.scalar_one_or_none()

    async def list_domains(
        self,
        db: AsyncSession,
        *,
        user: str,
    ) -> list[Domain]:
        """List all domains for a user."""
        result = await db.execute(
            select(Domain).where(Domain.user == user)
        )
        return list(result.scalars().all())

    async def delete_domain(
        self,
        db: AsyncSession,
        domain: Domain,
    ) -> None:
        """Delete only the app DB domain row."""
        await db.delete(domain)
        await db.commit()

    async def forget_domain(
        self,
        cognee_client,
        db: AsyncSession,
        domain: Domain,
    ) -> None:
        """
        Delete the Cognee brain first, then delete the app DB row.

        This keeps the app from showing a domain whose memory has already
        been wiped.
        """
        await cognee_client.forget_domain(domain.dataset_name)
        await self.delete_domain(db, domain)

    async def switch(
        self,
        db: AsyncSession,
        *,
        user: str,
        slug: str,
    ) -> Optional[Domain]:
        """
        Switching domains is just selecting another domain row.

        Later, the API/frontend will pass that domain.dataset_name into
        CogneeClient. No Cognee rebuild is needed.
        """
        return await self.get_domain_by_slug(db, user=user, slug=slug)