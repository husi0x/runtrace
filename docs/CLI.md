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
runtrace do <command...>
```

This is the recommended happy path. It records the command and generates `report.md` + `report.html`.

Examples:

```bash
runtrace do pytest -q
runtrace do --open pytest -q
runtrace ui
runtrace pr
```

The older `runtrace run -- <command...>` form is still available for advanced/explicit CLI parsing.

With `run`, the `--` matters. It tells Runtrace: everything after this belongs to the command you want to record.

Good:

```bash
runtrace run --name "tests" -- pytest -q
```

Without the separator, the advanced `run` form is ambiguous for CLI parsers. Prefer `runtrace do` for daily use.

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

### `runtrace do`

Record a command and generate reports. No `--` separator needed.

```bash
runtrace do pytest -q
runtrace do --open pytest -q
runtrace do --name "tests" pytest -q
runtrace do codex exec "fix the failing tests"
```

Afterwards:

```bash
runtrace ui
runtrace last
runtrace pr
```

### `runtrace run`

Advanced explicit form. Use it when you want the older `--` separator behavior or want to record without generating reports by default.

```bash
runtrace run --name "hello" -- python -c "print('hello')"
runtrace run --name "pytest baseline" -- pytest -q
runtrace run --report --name "pytest baseline" -- pytest -q
runtrace run --report --open --name "pytest baseline" -- pytest -q
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

Generate reports and open the HTML report:

```bash
runtrace report --open
```

### `runtrace open`

Open the latest HTML report, generating it first if it is missing.

```bash
runtrace open
runtrace open <run_id>
```

Short alias:

```bash
runtrace ui
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

Short alias:

```bash
runtrace pr
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
runtrace last
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
