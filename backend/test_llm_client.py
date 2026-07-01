import asyncio

from app.llm.client import LLMClient


async def main():
    llm = LLMClient()

    response = await llm.complete(
        system="You are a helpful assistant. Reply with one short sentence.",
        user="Say that the AgentOS generic LLM client works.",
    )

    print(response)


if __name__ == "__main__":
    asyncio.run(main())