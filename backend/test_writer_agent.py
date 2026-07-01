import asyncio

from app.agents.writer import WriterAgent


class FakeCogneeClient:
    def __init__(self):
        self.recall_count = 0

    async def recall(self, dataset_name: str, query: str, k: int = 12):
        self.recall_count += 1

        print(f"fake recall OK — dataset={dataset_name}, query={query}, k={k}")

        return [
            (
                "Multi-agent LLM systems can fail due to communication breakdowns, "
                "bad handoffs, task-allocation conflicts, synchronization issues, "
                "and stale memory."
            )
        ]


class FakeLLM:
    async def complete(self, system: str, user: str) -> str:
        print("fake llm OK")

        return (
            "# Multi-Agent LLM Failure Modes\n\n"
            "Multi-agent LLM systems can fail due to communication breakdowns, "
            "bad handoffs, task-allocation conflicts, synchronization issues, "
            "and stale memory.\n\n"
            "These failures can make agents act on incomplete information, duplicate work, "
            "or produce inconsistent decisions."
        )


async def emit(event: dict):
    print(f"event OK — {event['type']}: {event}")


async def main():
    fake_cognee = FakeCogneeClient()

    writer = WriterAgent(
        cognee=fake_cognee,
        llm=FakeLLM(),
        emit=emit,
    )

    answer = await writer.run(
        query="What are the key failure modes of multi-agent LLM systems?",
        findings=[
            {
                "subtask_id": "task_1",
                "text": (
                    "Multi-agent LLM systems can fail due to communication breakdowns, "
                    "bad handoffs, task-allocation conflicts, synchronization issues, "
                    "and stale memory."
                ),
                "source_uri": "memory_only",
                "cognee_data_id": "fake_data_id_123",
                "score": 0.6,
            }
        ],
        dataset_name="u_demo_d_ai_safety",
    )

    print(f"writer returned text length: {len(answer['text'])}")
    print(f"grounded: {answer['grounded']}")
    print(f"ungrounded claims: {len(answer['ungrounded_claims'])}")
    print(f"recall count: {fake_cognee.recall_count}")

    assert fake_cognee.recall_count == 1
    assert "Multi-Agent LLM Failure Modes" in answer["text"]
    assert isinstance(answer["grounded"], bool)
    assert "ungrounded_claims" in answer

    print("writer test OK")


if __name__ == "__main__":
    asyncio.run(main())