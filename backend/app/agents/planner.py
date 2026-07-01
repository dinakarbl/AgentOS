import json
import re

from app.agents.base import BaseAgent


def _extract_json_array(text: str) -> str:
    """
    Extract the first JSON array from an LLM response.

    This handles responses like:
    ```json
    [...]
    ```

    It also handles cases where the model adds a short sentence before the JSON.
    """
    cleaned = text.strip()

    if cleaned.startswith("```"):
        cleaned = re.sub(
            r"^```(?:json)?",
            "",
            cleaned,
            flags=re.IGNORECASE,
        ).strip()
        cleaned = re.sub(r"```$", "", cleaned).strip()

    start = cleaned.find("[")
    end = cleaned.rfind("]")

    if start == -1 or end == -1 or end <= start:
        raise ValueError("Planner response did not contain a JSON array.")

    return cleaned[start : end + 1]


def _parse_subtasks(raw: str) -> list[dict]:
    """
    Parse planner output into a clean list of subtask dictionaries.

    Each subtask must have:
    - id
    - query
    - rationale
    """
    json_text = _extract_json_array(raw)
    parsed = json.loads(json_text)

    if not isinstance(parsed, list):
        raise ValueError("Planner response must be a JSON list.")

    subtasks = []

    for index, item in enumerate(parsed[:5], start=1):
        if not isinstance(item, dict):
            continue

        query = str(item.get("query", "")).strip()

        if not query:
            continue

        subtasks.append(
            {
                "id": str(item.get("id") or f"task_{index}"),
                "query": query,
                "rationale": str(item.get("rationale", "")).strip(),
            }
        )

    if len(subtasks) < 3:
        raise ValueError("Planner must return at least 3 usable subtasks.")

    return subtasks


class PlannerAgent(BaseAgent):
    """
    Planner agent.

    Job:
    1. Recall prior knowledge from the selected domain brain.
    2. Ask the LLM to split the user query into 3–5 subtasks.
    3. Emit planner_done for the live UI.
    """

    name = "planner"

    async def run(self, query: str, dataset_name: str) -> list[dict]:
        prior = await self.cognee.recall(
            dataset_name,
            query,
            k=8,
        )

        await self._event(
            "memory_read",
            dataset=dataset_name,
            count=len(prior),
        )

        raw = await self.think(
            (
                "Decompose the user query into 3 to 5 independent, "
                "parallel-safe research subtasks.\n\n"
                "Return only a JSON list. Each item must have exactly these keys: "
                "id, query, rationale.\n\n"
                "Example format:\n"
                "[\n"
                "  {\n"
                '    "id": "task_1",\n'
                '    "query": "Research one specific part of the question.",\n'
                '    "rationale": "Why this subtask matters."\n'
                "  }\n"
                "]\n\n"
                f"User query: {query}"
            ),
            prior,
        )

        subtasks = _parse_subtasks(raw)

        await self._event(
            "planner_done",
            subtasks=[subtask["query"] for subtask in subtasks],
        )

        return subtasks