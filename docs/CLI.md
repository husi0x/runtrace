# Runtrace CLI

Runtrace is a local command-line tool. It records a command run, saves the output, captures git state when available, and generates reports.

## Install

For normal CLI usage, install from PyPI with pipx:

```bash
pipx install runtrace
runtrace demo
```

For development setup, see [../CONTRIBUTING.md](../CONTRIBUTING.md).

## Basic shape

```bash
runtrace run --name "my run" -- <command...>
```

The `--` matters. It tells Runtrace: everything after this belongs to the command you want to record.

Good:

```bash
runtrace run --name "tests" -- pytest -q
```

Bad:

```bash
runtrace run --name "tests" pytest -q
```

The second form is ambiguous for CLI parsers. Use `--`.

## Interactive commands and PTY

Runtrace has best-effort Unix PTY support for interactive commands. Non-interactive commands are fully supported everywhere through a subprocess fallback.

Use portable subprocess mode explicitly with:

```bash
runtrace run --no-pty --name "tests" -- pytest -q
```

This is the recommended mode for CI, tests, and scripted runs.

## Commands

### `runtrace --help`

Show available commands.

```bash
runtrace --help
```

### `runtrace version`

Print the installed version.

```bash
runtrace version
```

### `runtrace init`

Create `.runtrace/config.toml` for configurable review rules.

```bash
runtrace init
runtrace init --force
```

See [CONFIG.md](CONFIG.md).

### `runtrace demo`

The easiest first run. It records a safe Python command and generates both reports.

```bash
runtrace demo
```

After it finishes, Runtrace prints the paths to:

- `report.md`
- `report.html`
- `output.log`

Open the HTML report with:

```bash
xdg-open .runtrace/runs/<run_id>/report.html
```

On macOS, use:

```bash
open .runtrace/runs/<run_id>/report.html
```

### `runtrace run`

Record any command.

```bash
runtrace run --name "hello" -- python -c "print('hello')"
runtrace run --name "pytest baseline" -- pytest -q
runtrace run --no-pty --name "pytest baseline" -- pytest -q
runtrace run --name "codex bugfix" -- codex exec "fix the failing tests"
```

If the command exits non-zero, Runtrace still saves the run. The CLI exits with the same code as the wrapped command.

### `runtrace report`

Generate reports for the latest run.

```bash
runtrace report
```

Generate reports for one run:

```bash
runtrace report --run-id <run_id>
```

Choose a format:

```bash
runtrace report --format md
runtrace report --format html
runtrace report --format both
```

### `runtrace index`

Generate a compact local dashboard for all runs:

```bash
runtrace index
xdg-open .runtrace/index.html
```

Alias:

```bash
runtrace dashboard
```

If there are no runs yet, Runtrace prints:

```text
No runs found yet. Try: runtrace demo
```

### `runtrace doctor`

Check local Runtrace readiness: working directory, git availability, number of recorded runs, latest run, and whether reports exist.

```bash
runtrace doctor
```

### `runtrace export`

Export a compact JSON summary for the latest run. The export does not include huge logs or full diffs.

Print JSON to stdout:

```bash
runtrace export
```

Write JSON to a file:

```bash
runtrace export --output summary.json
```

Export one run:

```bash
runtrace export --run-id <run_id> --output summary.json
```

### `runtrace pr-summary`

Print a copy-ready Markdown summary for a GitHub PR or issue. It includes the run result, command, changed files, review checklist, and artifact paths when reports exist.

```bash
runtrace pr-summary
runtrace pr-summary --run-id <run_id>
runtrace pr-summary --output pr.md
```

### `runtrace list`

List previous runs, newest first.

```bash
runtrace list
```

Alias:

```bash
runtrace runs
```

If there are no runs yet, Runtrace prints:

```text
No runs found yet. Try: runtrace demo
```

### `runtrace show`

Show a compact terminal summary.

```bash
runtrace show <run_id>
runtrace show latest
```

Shortcut:

```bash
runtrace latest
```

If reports are missing, `show` tells you how to generate them:

```bash
runtrace report --run-id <run_id>
```

### `runtrace clean`

Delete old run folders.

```bash
runtrace clean --keep 20
runtrace clean --keep 20 --yes
```

Without `--yes`, Runtrace asks for confirmation.

## Common mistakes

### Forgetting `--`

Use this:

```bash
runtrace run -- pytest -q
```

Not this:

```bash
runtrace run pytest -q
```

### Running outside a git repository

This is allowed. Runtrace records command output, timing, and metadata. Git diff tracking is marked as unavailable.

### Expecting reports immediately after `run`

`runtrace run` records the run. Generate reports with:

```bash
runtrace report
```

`runtrace demo` does both recording and report generation.
