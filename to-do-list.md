# 🚀 To-Do List: Setting Up Your Agentic Dev Pipeline

Follow these steps to get your multi-agent development pipeline up and running. This guide is designed for beginners.

---

## 1. Environment Setup

### 📦 Install Python
Ensure you have **Python 3.11** or higher installed.
- Check by running: `python --version`
- If not installed, download it from [python.org](https://www.python.org/downloads/).

### 🛠️ Create a Virtual Environment
This keeps the pipeline's dependencies separate from your other projects.
1. Open your terminal in the project folder.
2. Run: `python -m venv venv`
3. Activate it:
   - **Windows**: `.\venv\Scripts\activate`
   - **Mac/Linux**: `source venv/bin/activate`

### 📥 Install Dependencies
Install all the required libraries (CrewAI, LangGraph, etc.).
- Run: `pip install -e ".[dev]"`
- *Alternatively, if you have 'make' installed, just run:* `make install`

---

## 2. Configuration (The .env File)

You need to create a file named `.env` in the root folder to store your "secrets" (API keys).

1. Copy the template:
   - **Windows**: `copy .env.example .env`
   - **Mac/Linux**: `cp .env.example .env`
2. Open `.env` and fill in the following values:

### 🧠 LLM (Anthropic)
- **What**: The "brain" of your agents (Claude).
- **Where to get**: [console.anthropic.com](https://console.anthropic.com/)
- **Step**: Create an account, add credits, and generate an **API Key**.
- **Field**: `ANTHROPIC_API_KEY`

### 📝 Asana (Task Management)
- **What**: Where your agents will create and manage tickets.
- **Where to get**: [Asana Developer Console](https://app.asana.com/0/developer-console)
- **Steps**:
  1. Click "+ New access token".
  2. Copy the token into `ASANA_ACCESS_TOKEN`.
  3. Find `ASANA_WORKSPACE_GID`: Use [this tool](https://app.asana.com/api/1.0/workspaces) to find your workspace ID.
  4. Find `ASANA_PROJECT_GID`: Open your project in Asana. The ID is the long number in the URL: `app.asana.com/0/PROJECT_ID/...`.

### 🐙 GitHub (Code Management)
- **What**: Where your code lives and PRs are opened.
- **Where to get**: [GitHub Settings > Developer Settings > Personal Access Tokens](https://github.com/settings/tokens)
- **Steps**:
  1. Generate a "Fine-grained token" or "Classic token".
  2. Give it `repo` permissions (read/write code, PRs).
  3. Copy it into `GITHUB_TOKEN`.
  4. `GITHUB_REPO`: Your repository name in the format `username/repository` (e.g., `johnsmith/my-agent-app`).

### 💬 Slack (Notifications)
- **What**: Where the `Notifier` agent posts updates.
- **Where to get**: [api.slack.com/apps](https://api.slack.com/apps)
- **Steps**:
  1. "Create New App" > "From scratch".
  2. Go to "OAuth & Permissions" and add `chat:write` and `chat:write.public` scopes.
  3. Install the app to your workspace.
  4. Copy the "Bot User OAuth Token" into `SLACK_BOT_TOKEN`.
  5. `SLACK_CHANNEL`: The name of the channel (e.g., `#dev-pipeline`).

---

## 3. Running & Verifying

### 🧪 Dry Run (Safe Mode)
Before spending any money on API calls, run the pipeline in "Dry Run" mode. This mocks the external calls and validates the orchestration.
- In `.env`, ensure `DRY_RUN=true`.
- Run: `python -m pipeline.graph.pipeline_graph --spec SPEC.md`
- *Alternatively:* `make run`

### 🛡️ Running Tests
Verify the code logic is sound by running the unit tests:
- Run: `py -m pytest tests/` (Windows) or `pytest tests/` (Mac/Linux)
- *Alternatively:* `make test`

### 🚀 Live Run
Once you are confident, switch to live mode.
- In `.env`, set `DRY_RUN=false`.
- Run: `make run`

---

## 📂 Summary of Key Files to Know
- `SPEC.md`: Edit this to change what you want the agents to build.
- `pipeline/agents/`: Folder containing the individual logic for each agent.
- `pipeline/config.py`: Where the code reads your `.env` settings.
- `logs/`: Check here after a run to see exactly what each agent did.
- `.github/workflows/nightly.yml`: Configuration for running this automatically on GitHub every night.
