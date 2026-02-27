"""LangGraph node functions. Each node wraps one agent action."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from crewai import Crew, Task

from pipeline.agents import (
    make_coder,
    make_notifier,
    make_planner,
    make_reviewer,
    make_tester,
)
from pipeline.config import settings
from pipeline.graph.state import PipelineState, Ticket
from pipeline.logger import get_run_logger


def parse_json_result(result: Any) -> Any:
    """Robustly extract JSON from a string that may contain markdown or preamble."""
    raw = str(result)
    try:
        # Try direct parse
        return json.loads(raw)
    except json.JSONDecodeError:
        try:
            # Look for JSON block
            match = re.search(r"(\{.*\}|\[.*\])", raw, re.DOTALL)
            if match:
                return json.loads(match.group(1))
        except Exception:
            pass
    return None


# ── Planner node ──────────────────────────────────────────────────────────────

def plan_node(state: PipelineState) -> dict:
    logger = get_run_logger(state["run_id"])
    spec = Path(state["spec_path"]).read_text(encoding="utf-8")

    if settings.dry_run:
        result = '[{"gid": "mock-1", "title": "Setup basic structure", "dependencies": [], "complexity": "S"}]'
    else:
        agent = make_planner()
        task = Task(
            description=f"Decompose this spec into 10–20 Asana tickets:\n\n{spec}",
            expected_output="JSON list of ticket objects with keys: gid, title, dependencies, complexity",
            agent=agent,
        )
        crew = Crew(agents=[agent], tasks=[task], verbose=False)
        result = crew.kickoff()

    tickets_data = parse_json_result(result) or []

    tickets: list[Ticket] = [
        Ticket(
            gid=t.get("gid", f"mock-{i}"),
            title=t.get("title", f"Ticket {i}"),
            dependencies=t.get("dependencies", []),
            complexity=t.get("complexity", "M"),
            branch=None, pr_number=None, test_result=None,
            review_approved=None, retries=0, status="pending",
        )
        for i, t in enumerate(tickets_data)
    ]

    logger.log("plan_complete", "Planner", {"ticket_count": len(tickets)})
    return {"tickets": tickets, "loop_count": state.get("loop_count", 0) + 1}


# ── Coder node (runs per ticket) ──────────────────────────────────────────────

def code_node(state: PipelineState, ticket: Ticket) -> dict:
    logger = get_run_logger(state["run_id"])

    if ticket["retries"] >= settings.max_ticket_retries:
        ticket["status"] = "escalated"
        logger.log("ticket_escalated", "Coder", {"gid": ticket["gid"]})
        return {"failed_tickets": [ticket]}

    if settings.dry_run:
        result = '{"branch": "feature/ticket-mock-1", "pr_number": "123"}'
    else:
        agent = make_coder(ticket["gid"])
        task = Task(
            description=(
                f"Implement ticket '{ticket['title']}' (GID: {ticket['gid']}).\n"
                f"Create a feature branch, write the code, commit, and open a PR."
            ),
            expected_output="JSON with keys: branch (str), pr_number (str)",
            agent=agent,
        )
        crew = Crew(agents=[agent], tasks=[task], verbose=False)
        result = str(crew.kickoff())

    data = parse_json_result(result)
    if data and isinstance(data, dict):
        ticket["branch"] = data.get("branch", f"feature/ticket-{ticket['gid']}")
        ticket["pr_number"] = data.get("pr_number", "0")
        ticket["status"] = "in_progress"
    else:
        ticket["retries"] += 1
        ticket["status"] = "pending"
        logger.log("code_parse_error", "Coder", {"gid": ticket["gid"], "raw": str(result)[:200]})
        return {"failed_tickets": [ticket]}

    logger.log("code_complete", "Coder", {"gid": ticket["gid"], "branch": ticket["branch"]})
    return {"completed_tickets": [ticket]}


# ── Tester node ───────────────────────────────────────────────────────────────

def test_node(state: PipelineState, ticket: Ticket) -> dict:
    logger = get_run_logger(state["run_id"])

    if settings.dry_run:
        result = '{"total": 5, "passed": 5, "failed": 0, "coverage": 100.0}'
    else:
        agent = make_tester()
        task = Task(
            description=(
                f"Run the test suite for branch '{ticket['branch']}' in the repo at "
                f"'{settings.github_repo}'. Return a structured test result."
            ),
            expected_output="JSON matching TestResult schema",
            agent=agent,
        )
        crew = Crew(agents=[agent], tasks=[task], verbose=False)
        result = str(crew.kickoff())

    data = parse_json_result(result)
    if data and isinstance(data, dict):
        ticket["test_result"] = data
        passed = data.get("failed", 1) == 0
    else:
        ticket["test_result"] = {"error": str(result)[:200]}
        passed = False

    ticket["status"] = "tested" if passed else "test_failed"
    logger.log("test_complete", "Tester", {"gid": ticket["gid"], "passed": passed})
    return {"completed_tickets": [ticket] if passed else [], "failed_tickets": [] if passed else [ticket]}


# ── Reviewer node ─────────────────────────────────────────────────────────────

def review_node(state: PipelineState, ticket: Ticket) -> dict:
    logger = get_run_logger(state["run_id"])

    if settings.dry_run:
        result = '{"approved": true, "reason": "Looks good!"}'
    else:
        agent = make_reviewer()
        task = Task(
            description=(
                f"Review PR #{ticket['pr_number']} for branch '{ticket['branch']}'. "
                f"Test results: {json.dumps(ticket.get('test_result', {}))}. "
                "Approve if: diff ≤ 400 lines, no coverage drop, ruff clean. "
                "Return JSON: {approved: bool, reason: str}"
            ),
            expected_output='JSON: {"approved": bool, "reason": "..."}',
            agent=agent,
        )
        crew = Crew(agents=[agent], tasks=[task], verbose=False)
        result = str(crew.kickoff())

    data = parse_json_result(result)
    if data and isinstance(data, dict):
        ticket["review_approved"] = data.get("approved", False)
        reason = data.get("reason", "")
    else:
        ticket["review_approved"] = False
        reason = "parse error"

    ticket["status"] = "approved" if ticket["review_approved"] else "review_rejected"
    logger.log("review_complete", "Reviewer", {"gid": ticket["gid"], "approved": ticket["review_approved"], "reason": reason})

    if ticket["review_approved"]:
        return {"completed_tickets": [ticket]}
    ticket["retries"] += 1
    return {"failed_tickets": [ticket]}


# ── Human gate node ───────────────────────────────────────────────────────────

def human_gate_node(state: PipelineState) -> dict:
    """
    In production: LangGraph interrupts here and waits for external approval
    (e.g. a Slack button press or API call to resume the graph).
    In dry-run: auto-approve.
    """
    if settings.dry_run:
        print("\n[HUMAN GATE] Dry-run: auto-approving merge.\n")
        return {"human_approved": True}

    # This node is configured as an interrupt point in pipeline_graph.py.
    # The graph will pause here. Resume by calling:
    #   graph.update_state(config, {"human_approved": True})
    #   graph.invoke(None, config)
    print("\n⏸  HUMAN APPROVAL REQUIRED. Approve via Slack button or API. Graph is paused.\n")
    return {"human_approved": False}


# ── Notifier node ─────────────────────────────────────────────────────────────

def notify_node(state: PipelineState) -> dict:
    logger = get_run_logger(state["run_id"])

    completed = state.get("completed_tickets", [])
    failed = state.get("failed_tickets", [])

    if settings.dry_run:
        print(f"[NOTIFY] Mock Slack message posted to {settings.slack_channel}")
    else:
        agent = make_notifier()
        task = Task(
            description=(
                f"Post a Slack summary to {settings.slack_channel}.\n"
                f"Run ID: {state['run_id']}\n"
                f"Completed tickets: {[t['title'] for t in completed]}\n"
                f"Failed tickets: {[t['title'] for t in failed]}\n"
                "Use git blame to find code owners of modified files and tag them. "
                "Keep the message under 10 lines."
            ),
            expected_output="Confirmation that Slack message was posted.",
            agent=agent,
        )
        crew = Crew(agents=[agent], tasks=[task], verbose=False)
        crew.kickoff()

    logger.log("notify_complete", "Notifier", {
        "completed": len(completed), "failed": len(failed)
    })
    return {"slack_posted": True}
