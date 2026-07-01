import asyncio

from app.agents.planner import PlannerAgent
from app.llm.client import LLMClient
from app.memory.client import CogneeClient


DATASET = "planner_real_test"


async def emit(event: dict):
    print(f"event OK — {event['type']}: {event}")


async def main():
    cognee = CogneeClient()
    llm = LLMClient()

    try:
        await cognee.forget_domain(DATASET)
        print("cleanup OK")
    except Exception as e:
        print(f"cleanup skipped — {type(e).__name__}: {e}")

    await cognee.remember(
        DATASET,
        (
            "AgentOS is a multi-agent research platform. "
            "It uses Cognee for persistent domain-scoped memory. "
            "RAG systems can fail due to retrieval gaps, stale context, and weak grounding."
        ),
    )
    print("seed memory OK")

    planner = PlannerAgent(
        cognee=cognee,
        llm=llm,
        emit=emit,
    )

    subtasks = await planner.run(
        query="What are the key failure modes of multi-agent LLM systems?",
        dataset_name=DATASET,
    )

    print(f"planner returned {len(subtasks)} subtasks")

    for subtask in subtasks:
        print(f"- {subtask['id']}: {subtask['query']}")

    await cognee.forget_domain(DATASET)
    print("cleanup after test OK")


if __name__ == "__main__":
    asyncio.run(main())