import asyncio

from app.agents.planner import PlannerAgent


class FakeCogneeClient:
    async def recall(self, dataset_name: str, query: str, k: int = 8):
        print(f"fake recall OK — dataset={dataset_name}, query={query}, k={k}")

        return [
            "Prior memory: RAG systems can fail due to retrieval gaps.",
            "Prior memory: Multi-agent systems can fail due to coordination problems.",
        ]


class FakeLLM:
    async def complete(self, system: str, user: str) -> str:
        print("fake llm OK")

        return """
        [
          {
            "id": "task_1",
            "query": "Identify retrieval-related failure modes in RAG systems.",
            "rationale": "Retrieval quality affects grounding."
          },
          {
            "id": "task_2",
            "query": "Identify coordination failure modes in multi-agent systems.",
            "rationale": "Agents can disagree, duplicate work, or pass bad state."
          },
          {
            "id": "task_3",
            "query": "Identify evaluation methods for detecting these failures.",
            "rationale": "The final answer should include practical checks."
          }
        ]
        """


async def emit(event: dict):
    print(f"event OK — {event['type']}: {event}")


async def main():
    planner = PlannerAgent(
        cognee=FakeCogneeClient(),
        llm=FakeLLM(),
        emit=emit,
    )

    subtasks = await planner.run(
        query="What are common RAG and multi-agent failure modes?",
        dataset_name="u_demo_d_ai_safety",
    )

    print(f"planner returned {len(subtasks)} subtasks")

    for subtask in subtasks:
        print(f"- {subtask['id']}: {subtask['query']}")


if __name__ == "__main__":
    asyncio.run(main())