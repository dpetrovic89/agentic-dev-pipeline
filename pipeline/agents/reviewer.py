from crewai import Agent

from pipeline.agents.base import get_llm
from pipeline.tools.git_tools import GitBlameTool


def make_reviewer() -> Agent:
    """Reviews a PR diff for quality, size, and lint."""
    return Agent(
        role="Code Reviewer",
        goal=(
            "Analyse the PR diff. Reject if: diff > 400 lines, coverage decreased, or ruff reports "
            "errors. Approve otherwise. Post a structured review comment."
        ),
        backstory=(
            "You are a meticulous reviewer who cares about maintainability and test coverage. "
            "You give specific, actionable feedback and never approve code that lowers quality."
        ),
        tools=[GitBlameTool()],
        llm=get_llm(),
        verbose=True,
        max_iter=3,
    )
