"""Lightweight local search tool (keyword match over seed corpus)."""

from __future__ import annotations

CORPUS: list[dict[str, str]] = [
    {
        "title": "LangGraph",
        "url": "https://langchain-ai.github.io/langgraph/",
        "snippet": "Stateful graphs for multi-agent workflows.",
    },
    {
        "title": "Manus",
        "url": "https://manus.im",
        "snippet": "Autonomous agent product with task decomposition.",
    },
    {
        "title": "Supervisor pattern",
        "url": "https://langchain-ai.github.io/langgraph/tutorials/multi_agent/",
        "snippet": "Supervisor routes work to specialized agents.",
    },
]


def search(query: str, limit: int = 5) -> list[dict[str, str]]:
    q = query.lower()
    hits = [
        c
        for c in CORPUS
        if q in c["title"].lower() or q in c["snippet"].lower()
    ]
    if not hits:
        hits = CORPUS[:limit]
    return hits[:limit]
