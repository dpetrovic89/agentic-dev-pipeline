from crewai import Agent

from pipeline.agents.base import get_llm
from pipeline.tools.asana_tools import CreateTicketTool, UpdateTicketTool


def make_planner() -> Agent:
    """Decomposes a spec into Asana tickets and defines dependencies."""
    return Agent(
        role="Engineering Planner",
        goal=(
            "Read the SPEC.md, decompose the work into 10–20 discrete, independently-implementable "
            "tickets, create them in Asana with acceptance criteria and dependency links, and return "
            "a JSON list of ticket GIDs in topological order."
        ),
        backstory=(
            "You are a senior staff engineer who excels at breaking vague requirements into crisp, "
            "small tasks. You think in dependency graphs and know how to scope tickets so a single "
            "developer can finish one in under half a day."
        ),
        tools=[CreateTicketTool(), UpdateTicketTool()],
        llm=get_llm(),
        verbose=True,
        max_iter=5,
    )
