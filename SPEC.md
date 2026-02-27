# Agentic Dev Pipeline — Specification

## High-Level Goal

Automate the software development lifecycle using a multi-agent system: tickets are created from a spec, parallel coders implement them, a tester validates, a reviewer gates merges, and a notifier posts results to Slack. The system runs nightly and requires one human approval before merging.

---

## Acceptance Criteria

| # | Criterion |
|---|-----------|
| 1 | Given a SPEC.md, the Planner produces 10–20 structured Asana tickets with title, description, acceptance criteria, and dependency links. |
| 2 | Independent tickets are implemented in parallel (max 4 concurrent Coder agents). |
| 3 | Each Coder opens a feature branch, commits changes, and opens a PR. |
| 4 | The Tester runs `pytest` (or the project's test suite) and attaches a pass/fail report to the PR. |
| 5 | The Reviewer checks diff size (< 400 lines), test coverage delta (≥ 0), and style lint; posts a structured review comment. |
| 6 | A human-in-the-loop gate pauses the graph before `git merge`; merge proceeds only on explicit approval. |
| 7 | The Notifier posts a Slack message to `#dev-pipeline` summarising ticket status, test results, and review outcome, tagging code owners via `git blame`. |
| 8 | Max loop guard: no ticket may be retried more than 3 times before it is escalated to a human. |
| 9 | Full run (plan → code → test → review → notify) completes in < 30 min for a 5-ticket batch. |
| 10 | All agent actions are logged to `logs/run_YYYYMMDD.jsonl` for post-hoc review. |

---

## Tech Stack

| Layer | Choice | Reason |
|-------|--------|--------|
| Agent framework | **CrewAI 0.70+** | Role-based agents, tool registry, memory |
| Orchestration | **LangGraph 0.2+** | Stateful graph, parallel branches, human-in-loop |
| LLM | **Claude (claude-sonnet-4-6)** | Via `anthropic` SDK / LangChain wrapper |
| Project management | **Asana REST API** | Ticket creation & status updates |
| Version control | **GitHub API + GitPython** | Branch, commit, PR management |
| Notifications | **Slack Bolt SDK** | `#dev-pipeline` webhook posts |
| Testing | **pytest + pytest-cov** | Test execution & coverage |
| Linting | **ruff** | Fast Python linter |
| Config | **pydantic-settings + .env** | Secret management |
| Scheduling | **cron / GitHub Actions** | Nightly runs at 02:00 UTC |

---

## File Structure

```
repo/
├── SPEC.md                        ← this file
├── pipeline/
│   ├── __init__.py
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── planner.py             ← Planner agent + Asana tools
│   │   ├── coder.py               ← Coder agent + git tools
│   │   ├── tester.py              ← Tester agent + pytest runner
│   │   ├── reviewer.py            ← Reviewer agent + diff analysis
│   │   └── notifier.py            ← Notifier agent + Slack + git blame
│   ├── tools/
│   │   ├── asana_tools.py
│   │   ├── git_tools.py
│   │   ├── test_tools.py
│   │   └── slack_tools.py
│   ├── graph/
│   │   ├── __init__.py
│   │   ├── state.py               ← LangGraph TypedDict state
│   │   ├── nodes.py               ← One node per agent action
│   │   └── pipeline_graph.py     ← Graph assembly + compile
│   ├── config.py                  ← Pydantic settings
│   └── logger.py                  ← JSONL structured logger
├── tests/
│   ├── test_planner.py
│   ├── test_coder.py
│   ├── test_tester.py
│   ├── test_reviewer.py
│   ├── test_notifier.py
│   └── test_graph.py
├── logs/                          ← gitignored, run logs land here
├── .env.example
├── pyproject.toml
├── Makefile
└── .github/
    └── workflows/
        └── nightly.yml
```

---

## Decompose Into 10–20 Tickets

> **Prompt to use:** Paste this SPEC into Claude and say:
> *"Decompose this spec into 10–20 implementation tickets. For each ticket include: title, description, acceptance criteria, dependencies (by ticket number), estimated complexity (S/M/L), and which agent is responsible."*

---

## Test Plan

### Unit Tests
- `test_planner.py` — mock Asana API; assert ticket schema, 10–20 count, dependency graph is acyclic.
- `test_coder.py` — mock GitPython; assert branch naming convention, commit message format, PR body structure.
- `test_tester.py` — run against a fixture project; assert pytest output is parsed into pass/fail/coverage dict.
- `test_reviewer.py` — feed known diffs; assert correct line-count gating and lint-error detection.
- `test_notifier.py` — mock Slack SDK; assert message contains ticket IDs, test summary, tagged owners.

### Integration Tests
- `test_graph.py` — run graph with mocked agents against a 3-ticket fixture; assert state transitions, human-gate pause, final Slack call.

### End-to-End (Nightly CI)
- GitHub Actions triggers `pipeline/graph/pipeline_graph.py --spec SPEC.md --dry-run` on every push to `main`.
- Full live run executes nightly at 02:00 UTC against a sandbox Asana project + test GitHub repo.

### Performance Gate
- Assert full 5-ticket run completes in < 30 minutes (timed in CI).

### Regression
- Any merged PR must keep test coverage ≥ the baseline stored in `.coverage_baseline`.
