from manus_agent.core.supervisor import next_node


def test_routes_planner_to_researcher() -> None:
    assert next_node({"phase": "init"}) == "planner"


def test_done_ends() -> None:
    assert next_node({"phase": "done"}) == "end"
