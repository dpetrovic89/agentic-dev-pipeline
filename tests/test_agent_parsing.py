from pipeline.config import settings
from pipeline.graph.nodes import code_node, review_node, test_node
from pipeline.graph.state import PipelineState, Ticket


def test_code_node_parsing_resilience():
    settings.dry_run = False  # Force parsing
    ticket: Ticket = {
        "gid": "T1", "title": "Test", "dependencies": [], "complexity": "S",
        "branch": None, "pr_number": None, "test_result": None,
        "review_approved": None, "retries": 0, "status": "pending"
    }
    state: PipelineState = {"run_id": "test"}

    # Mocking agent result via some mechanism would be better,
    # but for now we test the node's handling of specific strings
    # in a realistic context.

    # Simulate Coder response with markdown
    from unittest.mock import patch
    with patch("pipeline.graph.nodes.make_coder") as mock_agent:
        with patch("pipeline.graph.nodes.Crew") as mock_crew:
            mock_crew.return_value.kickoff.return_value = "Sure! Here is the JSON: ```json\n{\"branch\": \"feat/test\", \"pr_number\": \"42\"}\n```"
            code_node(state, ticket)
            assert ticket["branch"] == "feat/test"
            assert ticket["pr_number"] == "42"
            assert ticket["status"] == "in_progress"

def test_test_node_parsing_resilience():
    settings.dry_run = False
    ticket: Ticket = {"gid": "T1", "branch": "feat/test", "status": "in_progress", "retries": 0}
    state: PipelineState = {"run_id": "test"}

    with patch("pipeline.graph.nodes.make_tester"), patch("pipeline.graph.nodes.Crew") as mock_crew:
        mock_crew.return_value.kickoff.return_value = "Results: {\"total\": 5, \"passed\": 5, \"failed\": 0}"
        test_node(state, ticket)
        assert ticket["status"] == "tested"

def test_review_node_parsing_resilience():
    settings.dry_run = False
    ticket: Ticket = {"gid": "T1", "pr_number": "42", "branch": "feat/test", "status": "tested", "retries": 0}
    state: PipelineState = {"run_id": "test"}

    with patch("pipeline.graph.nodes.make_reviewer"), patch("pipeline.graph.nodes.Crew") as mock_crew:
        mock_crew.return_value.kickoff.return_value = "--- REVIEW ---\n{\"approved\": true, \"reason\": \"LGTM\"}"
        review_node(state, ticket)
        assert ticket["review_approved"] is True
        assert ticket["status"] == "approved"
