from pathlib import Path

from manus_agent.memory.artifacts import ArtifactStore


def test_artifact_roundtrip(tmp_path: Path) -> None:
    art = ArtifactStore(tmp_path)
    art.write_text("r1", "report.md", "# Hi")
    assert art.read_text("r1", "report.md") == "# Hi"
    p = art.write_json("r1", "plan", [{"title": "A"}])
    assert p.exists()
