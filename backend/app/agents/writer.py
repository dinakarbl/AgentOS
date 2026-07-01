import re

from app.agents.base import BaseAgent


STOPWORDS = {
    "about",
    "above",
    "after",
    "again",
    "against",
    "agent",
    "agents",
    "also",
    "because",
    "being",
    "between",
    "could",
    "does",
    "during",
    "each",
    "from",
    "have",
    "into",
    "more",
    "must",
    "only",
    "other",
    "should",
    "such",
    "than",
    "that",
    "their",
    "there",
    "these",
    "they",
    "this",
    "through",
    "when",
    "where",
    "which",
    "while",
    "with",
    "would",
}


def _text_from_item(item) -> str:
    """Convert recall hits, strings, dictionaries, or objects into text."""
    if isinstance(item, str):
        return item

    if isinstance(item, dict):
        return str(
            item.get("text")
            or item.get("content")
            or item.get("summary")
            or item
        )

    return str(getattr(item, "text", item))


def _finding_text(finding) -> str:
    """Get finding text from a dict or object."""
    if isinstance(finding, dict):
        return str(finding.get("text", ""))

    return str(getattr(finding, "text", ""))


def _finding_source(finding) -> str:
    """Get source URI from a dict or object."""
    if isinstance(finding, dict):
        return str(finding.get("source_uri", ""))

    return str(getattr(finding, "source_uri", ""))


def _split_claims(text: str) -> list[str]:
    """
    Split a draft into simple claim-like sentences.

    This is intentionally lightweight. It is not a perfect fact checker.
    It only helps us mark whether the answer is clearly supported by
    already-fetched context/findings.
    """
    parts = re.split(r"(?<=[.!?])\s+", text)

    claims = []

    for part in parts:
        cleaned = part.strip()

        if len(cleaned) >= 30:
            claims.append(cleaned)

    return claims


def _keywords(text: str) -> set[str]:
    """Extract useful lowercase keywords for the grounding check."""
    words = re.findall(r"[a-zA-Z][a-zA-Z\-]{3,}", text.lower())

    return {
        word
        for word in words
        if word not in STOPWORDS
    }


def _is_supported(claim: str, evidence_blob: str) -> bool:
    """
    Check whether a claim is loosely supported by the evidence.

    This is intentionally simple:
    - exact prefix support passes
    - otherwise, at least two meaningful claim keywords must appear in evidence
    """
    claim_lower = claim.lower()
    evidence_lower = evidence_blob.lower()

    if claim_lower[:40] in evidence_lower:
        return True

    claim_keywords = _keywords(claim)

    if not claim_keywords:
        return True

    matched_keywords = [
        word
        for word in claim_keywords
        if word in evidence_lower
    ]

    return len(matched_keywords) >= min(2, len(claim_keywords))


def _grounding_check(draft: str, context: list, findings: list) -> dict:
    """
    Run grounding check using only already-fetched memory and findings.

    Important:
    This function does not call Cognee.
    This function does not call the LLM.
    """
    evidence_items = []

    for item in context:
        evidence_items.append(_text_from_item(item))

    for finding in findings:
        evidence_items.append(_finding_text(finding))

    evidence_blob = "\n\n".join(evidence_items)

    claims = _split_claims(draft)

    ungrounded_claims = [
        claim
        for claim in claims
        if not _is_supported(claim, evidence_blob)
    ]

    return {
        "grounded": len(ungrounded_claims) == 0,
        "ungrounded_claims": ungrounded_claims,
    }


class WriterAgent(BaseAgent):
    """
    Writer agent.

    Job:
    1. Recall domain memory once.
    2. Combine recalled memory with researcher findings.
    3. Ask the LLM for a Markdown answer.
    4. Run a lightweight grounding check without extra Cognee calls.
    5. Emit writer_answer.
    """

    name = "writer"

    async def run(self, query: str, findings: list, dataset_name: str) -> dict:
        context = await self.cognee.recall(
            dataset_name,
            query,
            k=12,
        )

        await self._event(
            "memory_read",
            dataset=dataset_name,
            count=len(context),
        )

        context_text = "\n\n".join(_text_from_item(item) for item in context)

        if not context_text:
            context_text = "No graph evidence found."

        findings_text = "\n\n".join(_finding_text(finding) for finding in findings)

        if not findings_text:
            findings_text = "No researcher findings were provided."

        draft = await self.llm.complete(
            system=(
                "You are the writer agent. "
                "Synthesize a grounded Markdown research report. "
                "Use only the provided graph evidence and researcher findings. "
                "Do not invent facts that are not supported by the evidence."
            ),
            user=(
                f"User query:\n{query}\n\n"
                f"Graph evidence:\n{context_text}\n\n"
                f"Researcher findings:\n{findings_text}\n\n"
                "Write a concise Markdown answer with clear sections."
            ),
        )

        grounding = _grounding_check(
            draft=draft,
            context=context,
            findings=findings,
        )

        citations = [
            _finding_source(finding)
            for finding in findings
            if _finding_source(finding)
        ]

        answer = {
            "text": draft,
            "grounded": grounding["grounded"],
            "ungrounded_claims": grounding["ungrounded_claims"],
            "citations": citations,
        }

        await self._event(
            "writer_answer",
            grounded=answer["grounded"],
            text=answer["text"],
            citations=answer["citations"],
            ungrounded_claims=answer["ungrounded_claims"],
        )

        return answer