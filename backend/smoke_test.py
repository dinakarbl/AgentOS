import asyncio
from dotenv import load_dotenv

# Load variables from the root .env file before importing/using Cognee.
load_dotenv(override=True)

import cognee


DATASET = "smoke_test"
SESSION_ID = "smoke_session"


async def run_improve():

    try:
        await cognee.improve(
            dataset_name=DATASET,
            session_ids=[SESSION_ID],
        )
        print("improve OK — used dataset_name=")
        return

    except TypeError as e:
        print(f"improve dataset_name= failed with TypeError: {e}")

    await cognee.improve(
        dataset=DATASET,
        session_ids=[SESSION_ID],
    )
    print("improve OK — used dataset=")


async def test():
    # Clean up old smoke-test memory if this script was run before.
    try:
        await cognee.forget(dataset=DATASET)
        print("cleanup OK")
    except Exception as e:
        print(f"cleanup skipped — {type(e).__name__}: {e}")

    # 1. REMEMBER
    result = await cognee.remember(
        "AgentOS test. Cognee gives agents persistent memory.",
        dataset_name=DATASET,
        self_improvement=False,
    )

    data_id = result.items[0]["id"] if result.items else str(result.dataset_id)
    print(f"remember OK — data_id={data_id}")

    # 2. RECALL
    # Important: recall uses datasets=[...], not dataset_name=...
    hits = await cognee.recall(
        query_text="What does AgentOS use Cognee for?",
        datasets=[DATASET],
        top_k=3,
    )
    print(f"recall OK — {len(hits)} hits")

    # 3. IMPROVE
    await run_improve()

    # 4. FORGET
    await cognee.forget(dataset=DATASET)
    print("forget OK — all 4 ops confirmed")


if __name__ == "__main__":
    asyncio.run(test())