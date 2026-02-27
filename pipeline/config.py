
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    anthropic_api_key: str = ""
    model: str = "claude-3-5-sonnet-20240620"

    asana_access_token: str = ""
    asana_workspace_gid: str = ""
    asana_project_gid: str = ""

    github_token: str = ""
    github_repo: str = "owner/repo"

    dry_run: bool = False

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def is_live(self) -> bool:
        return not self.dry_run

    def validate_live_configs(self):
        """Manually called to ensure keys are present for non-dry runs."""
        if self.dry_run:
            return

        missing = []
        if not self.anthropic_api_key: missing.append("ANTHROPIC_API_KEY")
        if not self.github_token: missing.append("GITHUB_TOKEN")

        if missing:
            raise ValueError(f"Missing required API keys for live run: {', '.join(missing)}")

settings = Settings()
