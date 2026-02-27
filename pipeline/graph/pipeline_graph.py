"""
LangGraph pipeline orchestration.

Graph topology:
  plan → [parallel coder branches] → test → review → human_gate → notify

Parallel coders: independent tickets run in fan-out; results collected via
Annotated[list, operator.add] state fields.
"""
from __future__ import annotations

import uuid

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph

from pipeline.config import settings
from pipeline.graph.nodes import (
    code_node,
    human_gate_node,
    notify_node,
    plan_node,
    review_node,
    test_node,
)
from pipeline.graph.state import PipelineState

# ── Routing helpers ───────────────────────────────────────────────────────────

def _should_continue(state: PipelineState) -> str:
    """After planning, decide whether to start coding or abort."""
    if state.get("loop_count", 0) > settings.max_graph_loops:
        return "notify"
    if not state.get("tickets"):
        return "notify"
    return "fan_out_coders"


def _after_human_gate(state: PipelineState) -> str:
    if state.get("human_approved"):
        return "notify"
    return END  # Graph paused, waiting for external resume


# ── Parallel coder fan-out ────────────────────────────────────────────────────

def _fan_out_coders(state: PipelineState) -> list | str:
    """
    Decide whether to fan out into parallel ticket processing branches or proceed to notify.
    """
    from langgraph.types import Send

    if state.get("loop_count", 0) > settings.max_graph_loops:
        return "notify"

    pending = [t for t in state["tickets"] if t["status"] == "pending"]
    if not pending:
        return "notify"

    # Limit parallelism
    batch = pending[:settings.max_parallel_coders]

    # Return Send objects for parallel execution
    return [Send("process_ticket", {"state": state, "ticket": t}) for t in batch]


def _process_ticket(inputs: dict) -> dict:
    """
    Consolidated node for processing a single ticket: Code -> Test -> Review.
    """
    state = inputs["state"]
    ticket = inputs["ticket"]

    # 1. Code
    res = code_node(state, ticket)
    if not res.get("completed_tickets"):
        return res

    # 2. Test
    res = test_node(state, ticket)
    if not res.get("completed_tickets"):
        return res

    # 3. Review
    return review_node(state, ticket)


# ── Build graph ───────────────────────────────────────────────────────────────

def build_graph():
    builder = StateGraph(PipelineState)

    builder.add_node("plan", plan_node)
    builder.add_node("process_ticket", _process_ticket)
    builder.add_node("human_gate", human_gate_node)
    builder.add_node("notify", notify_node)

    builder.set_entry_point("plan")

    # Fan out from plan based on ticket status
    builder.add_conditional_edges("plan", _fan_out_coders, {
        "process_ticket": "process_ticket",
        "notify": "notify",
    })

    # After each branch, go to human_gate
    builder.add_edge("process_ticket", "human_gate")

    builder.add_conditional_edges("human_gate", _after_human_gate, {
        "notify": "notify",
        END: END,
    })

    builder.add_edge("notify", END)

    # Interrupt before merge (human gate)
    checkpointer = MemorySaver()
    graph = builder.compile(
        checkpointer=checkpointer,
        interrupt_before=["human_gate"] if not settings.dry_run else [],
    )
    return graph


# ── Entrypoint ────────────────────────────────────────────────────────────────

def run_pipeline(spec_path: str = "SPEC.md") -> None:
    run_id = str(uuid.uuid4())[:8]
    initial_state: PipelineState = {
        "spec_path": spec_path,
        "run_id": run_id,
        "tickets": [],
        "completed_tickets": [],
        "failed_tickets": [],
        "human_approved": False,
        "slack_posted": False,
        "loop_count": 0,
    }

    graph = build_graph()
    config = {"configurable": {"thread_id": run_id}}

    print(f"\n🚀 Pipeline run {run_id} starting...\n")
    for step in graph.stream(initial_state, config=config, stream_mode="updates"):
        node, update = next(iter(step.items()))
        print(f"  ✓ {node}")

    print(f"\n✅ Pipeline run {run_id} complete.\n")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--spec", default="SPEC.md")
    args = parser.parse_args()
    run_pipeline(args.spec)
