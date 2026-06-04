from manus_agent.tools.search import search


def test_search_langgraph() -> None:
    hits = search("LangGraph")
    assert any("LangGraph" in h["title"] for h in hits)


def test_search_fallback() -> None:
    hits = search("zzznomatch")
    assert len(hits) >= 1
