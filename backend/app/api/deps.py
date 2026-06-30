from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session

DEMO_USER = "demo"


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Return one async database session for a request."""
    async for session in get_session():
        yield session


def get_current_user() -> str:
    """Temporary hackathon user until auth is added."""
    return DEMO_USER