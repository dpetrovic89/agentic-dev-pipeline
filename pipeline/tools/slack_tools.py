from crewai.tools import BaseTool


class SlackNotifyTool(BaseTool):
    name: str = "slack_notify"
    description: str = "Posts a message to Slack."

    def _run(self, channel: str, message: str) -> str:
        """
        TODO: Implement real Slack API integration.
        Requirements:
        - Use `slack_sdk.WebClient(token=SLACK_BOT_TOKEN)`
        - Call `client.chat_postMessage(channel=channel, text=message)`
        """
        # Mock implementation for dry-runs
        return f"Message posted to {channel}"
