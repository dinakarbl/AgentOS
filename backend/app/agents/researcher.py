from app.agents.base import BaseAgent
from app.tools.web_search import web_search


def _subtask_value(subtask, key: str, default=""):
    """
    Support both dictionary subtasks and object-style subtasks.

    Our PlannerAgent returns dictionaries right now:
    {"id": "...", "query": "...", "rationale": "..."}
    """
    if isinstance(subtask, dict):
        return subtask.get(key, default)

    return getattr(subtask, key, default)


def _format_context(context: list) -> str:
    """Convert Cognee recall results into plain text."""
    if not context:
        return "No prior memory found."

    return "\n\n".join(getattr(hit, "text", str(hit)) for hit in context)


def _format_sources(sources: list[dict]) -> str:
    """Convert web search results into plain text for the LLM."""
    if not sources:
        return "No fresh web sources found."

    blocks = []

    for index, source in enumerate(sources, start=1):
        blocks.append(
            "\n".join(
                [
                    f"Source {index}: {source.get('title', 'Untitled')}",
                    f"URL: {source.get('url', '')}",
                    f"Content: {source.get('content', '')}",
                ]
            )
        )

    return "\n\n".join(blocks)


class ResearcherAgent(BaseAgent):
    """
    Researcher agent.

    Job:
    1. Recall existing memory for one subtask.
    2. Search fresh web sources.
    3. Synthesize one finding.
    4. Save that finding into Cognee.
    """

    name = "researcher"

    async def run(self, subtask: dict, dataset_name: str) -> list[dict]:
        subtask_id = str(_subtask_value(subtask, "id", "task"))
        subtask_query = str(_subtask_value(subtask, "query", "")).strip()

        if not subtask_query:
            raise ValueError("Researcher subtask is missing query.")

        context = await self.cognee.recall(
            dataset_name,
            subtask_query,
            k=6,
        )

        await self._event(
            "memory_read",
            dataset=dataset_name,
            subtask=subtask_id,
            count=len(context),
        )

        sources = await web_search(subtask_query, max_results=3)

        context_text = _format_context(context)
        sources_text = _format_sources(sources)

        finding_text = await self.llm.complete(
            system=(
                "You are a careful research agent. "
                "Write one grounded finding for the given subtask. "
                "Use prior memory and web sources if available. "
                "If no web sources are available, clearly say the finding is based on existing memory only."
            ),
            user=(
                f"Subtask: {subtask_query}\n\n"
                f"Prior memory:\n{context_text}\n\n"
                f"Fresh web sources:\n{sources_text}\n\n"
                "Return a concise finding in 1 to 2 paragraphs."
            ),
        )

        data_id = await self.cognee.remember(
            dataset_name,
            finding_text,
        )

        await self._event(
            "memory_write",
            dataset=dataset_name,
            preview=finding_text[:160],
            cognee_data_id=data_id,
        )

        source_uri = sources[0]["url"] if sources else "memory_only"

        finding = {
            "subtask_id": subtask_id,
            "text": finding_text,
            "source_uri": source_uri,
            "cognee_data_id": data_id,
            "score": 0.6,
        }

        await self._event(
            "researcher_finding",
            subtask=subtask_id,
            text=finding_text,
            source_uri=source_uri,
        )

        return [finding]