from crewai.tools import BaseTool


class RunTestsTool(BaseTool):
    name: str = "run_pytest"
    description: str = "Runs the pytest suite and returns JSON result."

    def _run(self, branch: str) -> str:
        """
        TODO: Implement real test execution.
        Requirements:
        - Check out the targeted branch
        - Run `pytest --cov=project tests/ --json-report`
        - Parse and return the structured JSON report
        """
        # Mock implementation for dry-runs
        return '{"total": 10, "passed": 10, "failed": 0, "coverage": 95.0}'

class PostSlackMessageTool(BaseTool):
    name: str = "post_slack_message"
    description: str = "Posts a message to Slack."
    def _run(self, channel: str, text: str) -> str:
        return "Message posted."
