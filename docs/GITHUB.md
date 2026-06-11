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

Use this image after it is generated and committed:

```text
assets/runtrace-hero.png
```

Do not configure a social preview until the real image exists.

## Suggested first release title

```text
Runtrace v0.1.0 — a black box for AI coding agents
```

## Suggested release notes

- Initial CLI
- Run recording
- Git snapshots
- Markdown and HTML reports
- Deterministic review checklist
- Safe `runtrace demo` command
- GitHub Actions CI

## Pre-publish reminder

Before pushing publicly:

- run `bash scripts/smoke.sh`
- review `SECURITY.md`
- add social preview after `assets/runtrace-hero.png` exists
- review `.runtrace/` is ignored and not committed
