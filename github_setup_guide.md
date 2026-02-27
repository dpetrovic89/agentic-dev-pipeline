# 🐙 Guide: Moving Your Project to GitHub

Follow these steps to upload your Agentic Dev Pipeline to GitHub and configure the automated CI/CD features.

---

## 1. Initialize Local Git Repository

If you haven't already, turn your project folder into a Git repository.

1.  Open your terminal in the project root.
2.  Initialize Git:
    ```bash
    git init
    ```
3.  Add all files:
    ```bash
    git add .
    ```
4.  Create the first commit:
    ```bash
    git commit -m "Initialize Agentic Dev Pipeline"
    ```

---

## 2. Create a Repository on GitHub

1.  Log in to your [GitHub account](https://github.com/).
2.  Click the **+** icon in the top right and select **New repository**.
3.  **Repository name**: `agentic-dev-pipeline` (or your choice).
4.  **Public/Private**: Select as per your preference.
5.  **Do NOT** initialize with a README, license, or gitignore (we already have them).
6.  Click **Create repository**.

---

## 3. Link Local to GitHub

Copy the commands from the GitHub "Quick setup" page or use these (replace `YOUR_USERNAME` and `YOUR_REPO`):

```bash
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git branch -M main
git push -u origin main
```

---

## 4. Configure GitHub Secrets

The `nightly.yml` workflow requires several API keys to run safely in the cloud.

1.  In your GitHub repository, go to **Settings** > **Secrets and variables** > **Actions**.
2.  Click **New repository secret** for each of these:
    -   `ANTHROPIC_API_KEY`: Your Claude API key.
    -   `ASANA_ACCESS_TOKEN`: Your Asana PAT.
    -   `ASANA_WORKSPACE_GID`: Your Asana Workspace ID.
    -   `ASANA_PROJECT_GID`: Your Asana Project ID.
    -   `SLACK_BOT_TOKEN`: Your Slack Bot Token.
    -   `GITHUB_TOKEN`: This is usually provided automatically by GitHub, but ensure the workflow has permission.

---

## 5. Configure Environments (Optional but Recommended)

The `nightly.yml` uses an environment called `nightly` for live runs to prevent accidental costs/actions without approval.

1.  Go to **Settings** > **Environments**.
2.  Click **New environment** and name it `nightly`.
3.  Check **Required reviewers**.
4.  Add yourself as a reviewer.
5.  Click **Save protection rules**.

Now, when the nightly run reaches the "Live run" step, GitHub will wait for you to click "Approve" before continuing.

---

## 6. Verify

Once pushed, go to the **Actions** tab in your GitHub repository. You should see the **Nightly Pipeline Run** appear. You can trigger it manually by clicking **Run workflow** to test the setup.
