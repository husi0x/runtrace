# Security

Runtrace stores run data locally in `.runtrace/` inside the directory where you run it.

Reports may contain:

- command output
- local file paths
- git status and diff summaries
- snippets from command output
- metadata about the run

Review reports before sharing them publicly.

Avoid recording commands that print secrets. Do not intentionally record API keys, tokens, passwords, credentials, private `.env` values, or other sensitive data.

If you find a security issue in Runtrace, open a private security advisory if GitHub has it enabled for the repository. Otherwise, contact the maintainer directly.
