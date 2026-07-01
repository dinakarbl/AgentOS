import asyncio

from app.agents.researcher import ResearcherAgent


class FakeCogneeClient:
    async def recall(self, dataset_name: str, query: str, k: int = 6):
        print(f"fake recall OK — dataset={dataset_name}, query={query}, k={k}")

        return [
            "Prior memory: Multi-agent systems can fail when agents pass incomplete state.",
            "Prior memory: RAG systems can fail when retrieval misses important documents.",
        ]

    async def remember(self, dataset_name: str, text: str):
        print(f"fake remember OK — dataset={dataset_name}")
        print(f"remembered preview: {text[:80]}")
        return "fake_data_id_123"


class FakeLLM:
    async def complete(self, system: str, user: str) -> str:
        print("fake llm OK")

        return (
            "A key failure mode is weak coordination between agents. "
            "When agents pass incomplete state or duplicate work, the final output can become inconsistent. "
            "This finding is based on existing memory only."
        )


async def emit(event: dict):
    print(f"event OK — {event['type']}: {event}")


async def main():
    researcher = ResearcherAgent(
        cognee=FakeCogneeClient(),
        llm=FakeLLM(),
        emit=emit,
    )

    findings = await researcher.run(
        subtask={
            "id": "task_1",
            "query": "Identify coordination failure modes in multi-agent systems.",
            "rationale": "Coordination errors can reduce answer quality.",
        },
        dataset_name="u_demo_d_ai_safety",
    )

    print(f"researcher returned {len(findings)} finding(s)")

    for finding in findings:
        print(f"- subtask_id: {finding['subtask_id']}")
        print(f"- source_uri: {finding['source_uri']}")
        print(f"- cognee_data_id: {finding['cognee_data_id']}")
        print(f"- score: {finding['score']}")


if __name__ == "__main__":
    asyncio.run(main())