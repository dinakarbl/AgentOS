import time


class BaseAgent:
    """
    Parent class for Planner, Researcher, and Writer.

    It gives every agent three shared things:
    - cognee: memory client
    - llm: language model client
    - emit: function that sends live events
    """

    name = "base"

    def __init__(self, cognee, llm, emit):
        self.cognee = cognee
        self.llm = llm
        self.emit = emit

    async def think(self, prompt: str, context: list) -> str:
        """
        Send a prompt to the LLM.

        The context is usually Cognee recall results.
        We convert every context item to text before passing it to the LLM.
        """
        ctx = "\n".join(getattr(hit, "text", str(hit)) for hit in context)

        return await self.llm.complete(
            system=self._system(),
            user=f"{ctx}\n\n{prompt}",
        )

    async def _event(self, type_: str, **data):
        """Emit one event for the live agent feed."""
        event = {
            "agent": self.name,
            "type": type_,
            "ts": time.time(),
            **data,
        }

        await self.emit(event)

    def _system(self) -> str:
        """Default system prompt. Child agents can override this later."""
        return f"You are the {self.name} agent."