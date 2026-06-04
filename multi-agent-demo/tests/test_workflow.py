from manus_agent.config.settings import Settings
from manus_agent.core.graph import run_workflow


def test_full_mock_pipeline(tmp_settings: Settings) -> None:
    result = run_workflow("Test multi-agent report", tmp_settings)
    assert result.get("document")
    assert "#" in result["document"] or "Report" in result["document"]
    assert result.get("subtasks")
    assert len(result.get("research", [])) >= 1
    assert result.get("execution_log")
