import asyncio

from app.agents.researcher import ResearcherAgent
from app.llm.client import LLMClient
from app.memory.client import CogneeClient


DATASET = "researcher_real_test"


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
            "Multi-agent systems can fail due to coordination errors, stale memory, "
            "weak grounding, and bad handoffs between agents."
        ),
    )
    print("seed memory OK")

    researcher = ResearcherAgent(
        cognee=cognee,
        llm=llm,
        emit=emit,
    )

    findings = await researcher.run(
        subtask={
            "id": "task_1",
            "query": "Identify coordination failure modes in multi-agent LLM systems.",
            "rationale": "Coordination is important for multi-agent reliability.",
        },
        dataset_name=DATASET,
    )

    print(f"researcher returned {len(findings)} finding(s)")

    for finding in findings:
        print(f"- source_uri: {finding['source_uri']}")
        print(f"- cognee_data_id: {finding['cognee_data_id']}")
        print(f"- text preview: {finding['text'][:200]}")

    await cognee.forget_domain(DATASET)
    print("cleanup after test OK")


if __name__ == "__main__":
    asyncio.run(main())