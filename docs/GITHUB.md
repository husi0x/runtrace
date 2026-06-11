# GitHub repository metadata

Use this when creating or polishing the public GitHub repository.

## Repository description

```text
A black box for AI coding agents. Record commands, git diffs, changed files, and review checklists.
```

## Suggested topics

```text
ai-agents
coding-agents
cli
developer-tools
git
observability
python
codex
claude-code
gemini-cli
open-source
```

## Suggested social preview

Use the committed hero image:

```text
assets/runtrace-hero.png
```

## Suggested release title

```text
Runtrace v0.2.0 — run index, JSON export, and configurable review rules
```

## Suggested release notes

- Local command recording
- Git snapshots before and after each run
- Markdown and HTML reports
- Project-level report index page
- Compact JSON summary export
- Configurable deterministic review rules
- Safer cross-platform subprocess mode with `--no-pty`
- Safe `runtrace demo` command
- GitHub Actions CI

## Pre-publish reminder

Before pushing publicly:

- run `bash scripts/smoke.sh`
- run `python -m build && twine check dist/*`
- review `SECURITY.md`
- review `.runtrace/` is ignored and not committed
- do not commit PyPI credentials or tokens
