import asyncio

from app.memory.client import CogneeClient


DATASET = "client_test"
SESSION_ID = "client_session"


async def main():
    client = CogneeClient()

    # Clean up any previous run.
    try:
        await client.forget_domain(DATASET)
        print("cleanup OK")
    except Exception as e:
        print(f"cleanup skipped — {type(e).__name__}: {e}")

    # 1. remember
    data_id = await client.remember(
        DATASET,
        "AgentOS client test. This verifies the CogneeClient wrapper.",
    )
    print(f"remember OK — data_id={data_id}")

    # 2. recall
    hits = await client.recall(
        DATASET,
        "What does the AgentOS client test verify?",
        k=3,
    )
    print(f"recall OK — {len(hits)} hits")

    # 3. improve
    await client.improve(
        DATASET,
        [SESSION_ID],
    )
    print("improve OK")

    # 4. forget
    await client.forget_domain(DATASET)
    print("forget OK")


if __name__ == "__main__":
    asyncio.run(main())