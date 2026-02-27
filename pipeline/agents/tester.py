from crewai import Agent

from pipeline.agents.base import get_llm
from pipeline.tools.test_tools import RunTestsTool


def make_tester() -> Agent:
    """Runs the test suite against a branch and reports results."""
    return Agent(
        role="QA Engineer",
        goal=(
            "Check out the feature branch, run the full pytest suite with coverage, and return a "
            "structured pass/fail/coverage report."
        ),
        backstory=(
            "You are obsessive about test quality. You run tests, read failures carefully, and "
            "produce concise, actionable reports. You never mark a branch as passing if any test fails."
        ),
        tools=[RunTestsTool()],
        llm=get_llm(),
        verbose=True,
        max_iter=3,
    )
