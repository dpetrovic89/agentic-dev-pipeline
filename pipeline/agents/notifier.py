from crewai import Agent

from pipeline.agents.base import get_llm
from pipeline.tools.git_tools import GitBlameTool
from pipeline.tools.slack_tools import PostSlackMessageTool


def make_notifier() -> Agent:
    """Posts a Slack summary, tagging code owners."""
    return Agent(
        role="Release Notifier",
        goal=(
            "After all tickets are merged (or failed), post a professional Slack summary to #dev-pipeline. "
            "The message must include: a progress bar of completion, a list of successful tickets, "
            "a summary of failures with links to logs, the average test coverage, and clear tagging "
            "of code owners responsible for any regressions or failures."
        ),
        backstory=(
            "You write clear, concise engineering updates. Your Slack posts give the team exactly "
            "what they need to know in under 10 lines."
        ),
        tools=[GitBlameTool(), PostSlackMessageTool()],
        llm=get_llm(),
        verbose=True,
        max_iter=3,
    )
