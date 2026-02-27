from pipeline.graph.state import Ticket


def test_ticket_structure():
    ticket = Ticket(
        gid="123",
        title="Test Ticket",
        dependencies=[],
        complexity="S",
        branch=None,
        pr_number=None,
        test_result=None,
        review_approved=None,
        retries=0,
        status="pending"
    )
    assert ticket["gid"] == "123"
    assert ticket["status"] == "pending"
