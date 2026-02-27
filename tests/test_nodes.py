import pytest

from pipeline.config import settings
from pipeline.graph.nodes import plan_node
from pipeline.graph.state import PipelineState


@pytest.fixture
def mock_state() -> PipelineState:
    return {
        "spec_path": "SPEC.md",
        "run_id": "test-run",
        "tickets": [],
        "completed_tickets": [],
        "failed_tickets": [],
        "human_approved": False,
        "slack_posted": False,
        "loop_count": 0,
    }

def test_plan_node_dry_run(mock_state):
    settings.dry_run = True
    result = plan_node(mock_state)

    assert "tickets" in result
    assert len(result["tickets"]) == 1
    assert result["tickets"][0]["gid"] == "mock-1"
    assert result["loop_count"] == 1
