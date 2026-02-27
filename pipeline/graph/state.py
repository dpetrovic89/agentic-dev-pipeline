import operator
from typing import Annotated, TypedDict


class Ticket(TypedDict):
    gid: str
    title: str
    dependencies: list[str]
    complexity: str
    branch: str | None
    pr_number: str | None
    test_result: dict | None
    review_approved: bool | None
    retries: int
    status: str  # pending, in_progress, tested, test_failed, approved, review_rejected, escalated

class PipelineState(TypedDict):
    spec_path: str
    run_id: str
    tickets: list[Ticket]
    completed_tickets: Annotated[list[Ticket], operator.add]
    failed_tickets: Annotated[list[Ticket], operator.add]
    human_approved: bool
    slack_posted: bool
    loop_count: int
