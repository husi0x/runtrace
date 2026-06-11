# Runtrace CLI

Runtrace is a local command-line tool. It records a command run, saves the output, captures git state when available, and generates reports.

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

### `runtrace demo`

The easiest first run. It records a safe Python command and generates both reports.

```bash
runtrace demo
```

After it finishes, Runtrace prints the paths to:

- `report.md`
- `report.html`

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
