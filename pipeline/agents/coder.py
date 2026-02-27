from crewai import Agent

from pipeline.agents.base import get_llm
from pipeline.tools.git_tools import CommitFileTool, CreateBranchTool, OpenPRTool


def make_coder(ticket_id: str) -> Agent:
    """Implements a single ticket on a feature branch."""
    return Agent(
        role="Software Engineer",
        goal=(
            f"Implement ticket {ticket_id} by creating or modifying the relevant files on a "
            "feature branch, then open a pull request."
        ),
        backstory=(
            "You are a pragmatic backend engineer. You write clean, tested Python. You never modify "
            "files outside the scope of your ticket. Your PRs are small, focused, and always green."
        ),
        tools=[CreateBranchTool(), CommitFileTool(), OpenPRTool()],
        llm=get_llm(),
        verbose=True,
        max_iter=8,
    )
