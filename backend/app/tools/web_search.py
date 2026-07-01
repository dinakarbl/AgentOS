import os
from typing import TypedDict

from dotenv import load_dotenv

load_dotenv(override=True)


class WebResult(TypedDict):
    title: str
    url: str
    content: str


async def web_search(query: str, max_results: int = 3) -> list[WebResult]:
    """
    Search the web using Tavily.

    If TAVILY_API_KEY is missing, return an empty list instead of crashing.
    This lets us keep building the agent pipeline locally.
    """
    api_key = os.getenv("TAVILY_API_KEY", "").strip()

    if not api_key:
        print("web_search skipped — TAVILY_API_KEY is missing")
        return []

    try:
        from tavily import AsyncTavilyClient

        client = AsyncTavilyClient(api_key=api_key)

        response = await client.search(
            query=query,
            max_results=max_results,
            search_depth="basic",
        )

        results = []

        for item in response.get("results", []):
            results.append(
                {
                    "title": item.get("title", ""),
                    "url": item.get("url", ""),
                    "content": item.get("content", ""),
                }
            )

        return results

    except Exception as exc:
        print(f"web_search failed — {type(exc).__name__}: {exc}")
        return []