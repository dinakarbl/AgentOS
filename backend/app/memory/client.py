import asyncio
from typing import Any

from dotenv import load_dotenv

load_dotenv(override=True)

import cognee
from cognee import SearchType
from cognee.infrastructure.databases.graph import get_graph_engine


def extract_data_id(result: Any) -> str:
    """
    Cognee 1.2.2 can return remember().items as dictionaries.
    Older examples sometimes show objects with .id.
    This supports both shapes.
    """
    items = getattr(result, "items", None)

    if items:
        first_item = items[0]

        if isinstance(first_item, dict):
            return str(first_item.get("id"))

        return str(first_item.id)

    dataset_id = getattr(result, "dataset_id", None)
    return str(dataset_id)


class CogneeClient:
    """
    Single wrapper around Cognee.

    All app code should use this class instead of calling cognee.remember(),
    cognee.recall(), cognee.improve(), or cognee.forget() directly.
    """

    def __init__(self, reranker=None):
        self._lock = asyncio.Lock()
        self._reranker = reranker

    async def ingest(self, dataset_name: str, *, kind: str, uri: str) -> str:
        """
        Ingest a source into a domain brain.

        For now, uri is passed directly to Cognee. Later, the sources API will
        validate kind and decide whether uri is a URL, file path, or text block.
        """
        async with self._lock:
            result = await cognee.remember(
                uri,
                dataset_name=dataset_name,
                run_in_background=False,
                self_improvement=False,
            )

        return extract_data_id(result)

    async def remember(self, dataset_name: str, text: str) -> str:
        """
        Store a small text finding in the domain brain.
        The lock prevents parallel researchers from writing to Kuzu at once.
        """
        async with self._lock:
            result = await cognee.remember(
                text,
                dataset_name=dataset_name,
                self_improvement=False,
            )

        return extract_data_id(result)

    async def recall(self, dataset_name: str, query: str, k: int = 10) -> list:
        """
        Read from a domain brain.

        Important: Cognee recall scopes memory with datasets=[...],
        not dataset_name=...
        """
        hits = await cognee.recall(
            query_text=query,
            datasets=[dataset_name],
            query_type=SearchType.GRAPH_COMPLETION,
            top_k=k,
        )

        if self._reranker is not None:
            return self._reranker.rank(dataset_name, hits)

        return hits

    async def improve(self, dataset_name: str, session_ids: list[str]) -> None:
        """
        Distill session memory into the domain brain.

        Your Cognee 1.2.2 smoke test showed improve(dataset_name=...)
        fails, while improve(dataset=...) works.
        """
        await cognee.improve(
            dataset=dataset_name,
            session_ids=session_ids,
        )

    async def forget_source(self, data_id: str) -> None:
        """Forget one remembered source/finding by Cognee data id."""
        await cognee.forget(data_id=data_id)

    async def forget_domain(self, dataset_name: str) -> None:
        """Forget an entire domain brain."""
        await cognee.forget(dataset=dataset_name)

    async def get_graph_data(self, dataset_name: str) -> tuple:
        """
        Return raw graph nodes and edges.

        We accept dataset_name now to keep the app-level method signature stable.
        Filtering will happen later in the graph API route after we inspect node shape.
        """
        engine = await get_graph_engine()
        return await engine.get_graph_data()