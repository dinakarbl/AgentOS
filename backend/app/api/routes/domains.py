from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.db.models import Domain
from app.memory.client import CogneeClient
from app.memory.domain_manager import DomainManager

router = APIRouter(prefix="/api/v1/domains", tags=["domains"])

manager = DomainManager()
cognee_client = CogneeClient()


class DomainCreate(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None


@router.get("", response_model=list[Domain])
async def list_domains(
    db: AsyncSession = Depends(get_db),
    user: str = Depends(get_current_user),
):
    """Return all domains for the demo user."""
    return await manager.list_domains(db, user=user)


@router.post("", response_model=Domain, status_code=status.HTTP_201_CREATED)
async def create_domain(
    payload: DomainCreate,
    db: AsyncSession = Depends(get_db),
    user: str = Depends(get_current_user),
):
    """Create a domain and generate the Cognee dataset name on the backend."""
    try:
        return await manager.create_domain(
            db,
            user=user,
            slug=payload.slug,
            title=payload.name,
        )
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A domain with this slug already exists.",
        )


@router.delete("/{domain_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_domain(
    domain_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Forget the Cognee domain memory, then delete the app DB row."""
    domain = await manager.get_domain(db, domain_id)

    if domain is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Domain not found.",
        )

    try:
        await cognee_client.forget_domain(domain.dataset_name)
    except Exception as exc:
        # Empty domains may not exist inside Cognee yet. For T-08, do not block
        # deleting the app row just because there is no Cognee dataset to wipe.
        print(f"Cognee forget skipped for {domain.dataset_name}: {type(exc).__name__}: {exc}")

    await manager.delete_domain(db, domain)
    return Response(status_code=status.HTTP_204_NO_CONTENT)