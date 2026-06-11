<h1 align="center">Runtrace</h1>

<p align="center">
  <strong>A black box for AI coding agents.</strong>
</p>

<p align="center">
  Run any coding agent through Runtrace and get a clean local report: command output, git diff, changed files, and review checklist.
</p>

<p align="center">
  <img src="assets/runtrace-hero.png" alt="Runtrace — a black box for AI coding agents" width="100%">
</p>
<p align="center">
  <img alt="Python 3.11+" src="https://img.shields.io/badge/python-3.11%2B-blue">
  <img alt="License MIT" src="https://img.shields.io/badge/license-MIT-green">
  <img alt="CLI" src="https://img.shields.io/badge/interface-CLI-black">
  <img alt="No network required" src="https://img.shields.io/badge/network-not_required-lightgrey">
</p>

## Try it in 30 seconds

```bash
git clone https://github.com/husi0x/runtrace.git
cd runtrace
python -m venv .venv
source .venv/bin/activate
pip install .
runtrace demo
```

Runtrace prints the exact report paths after `demo`. Open the HTML report it prints, for example:

```bash
xdg-open .runtrace/runs/<printed-run-id>/report.html
```

## Already cloned?

From the repository root:

```bash
pip install .
runtrace demo
```

## Why Runtrace?

AI coding agents can change files, run commands, and leave messy context behind.

Runtrace records exactly what happened so you can review the work later: command output, git diff, changed files, and a simple checklist.

## What you get

Each run creates a local folder under `.runtrace/runs/<run_id>/`:

```text
metadata.json    # machine-readable run record
output.log       # full command output
report.md        # readable Markdown report
report.html      # self-contained HTML report
```

Runtrace records:

- command and working directory
- start time, end time, and duration
- exit code and success/failure status
- live command output saved to `output.log`
- git branch, commit, status, changed files, and diff stat when git is available
- deterministic review checklist

If the directory is not a git repository, Runtrace still records command output and marks git tracking as unavailable.

## Example workflows

Use it with Codex:

```bash
runtrace run --name "codex bugfix" -- codex exec "fix the failing tests"
runtrace report
runtrace show latest
```

Use it with tests:

```bash
runtrace run --name "pytest baseline" -- pytest -q
runtrace report
```

Run any local command:

```bash
runtrace run --name "hello" -- python -c "print('hello')"
runtrace report
runtrace show latest
```

## CLI commands

| Command | What it does |
|---|---|
| `runtrace demo` | Records a safe demo run and generates reports |
| `runtrace run -- <command>` | Records any command |
| `runtrace report` | Generates Markdown and HTML reports |
| `runtrace list` | Lists previous runs |
| `runtrace runs` | Alias for `runtrace list` |
| `runtrace show <run_id>` | Shows one run in the terminal |
| `runtrace show latest` | Shows the newest run |
| `runtrace latest` | Shortcut for `runtrace show latest` |
| `runtrace clean --keep 20` | Deletes old runs, keeping the newest 20 |
| `runtrace version` | Prints the installed version |

See [docs/CLI.md](docs/CLI.md) for full command details and common mistakes.

## Reports

Runtrace generates two report formats:

- `report.md` — readable Markdown for terminals, PR comments, and notes
- `report.html` — self-contained dark HTML report with cards, status badges, changed files, diff stat, and command output preview

The full command output stays in `output.log`. The full machine-readable record stays in `metadata.json`.

Sample output is included in [examples/sample-output](examples/sample-output/). It is intentionally small and contains neutral demo paths.

See [docs/REPORTS.md](docs/REPORTS.md) for report details.

## Privacy

Runtrace does not call any external API. Everything is stored locally in `.runtrace/`.

Reports may include command output, file paths, and git diffs. Review them before sharing publicly.

See [SECURITY.md](SECURITY.md) for practical security notes.

## Verify locally

```bash
bash scripts/smoke.sh
```

## Install with pipx from GitHub

This works after the repository is pushed to GitHub:

```bash
pipx install git+https://github.com/husi0x/runtrace.git
runtrace demo
```

## Project structure

Runtrace uses a standard Python `src/` layout with tests, docs, examples, and a small smoke script.

See [docs/CLI.md](docs/CLI.md), [docs/REPORTS.md](docs/REPORTS.md), and [examples/](examples/) for the practical details.

## Docs

- [CLI reference](docs/CLI.md)
- [Reports and privacy](docs/REPORTS.md)
- [Release checklist](docs/RELEASE.md)
- [GitHub metadata](docs/GITHUB.md)
- [Examples](examples/README.md)
- [Contributing](CONTRIBUTING.md)
- [Security](SECURITY.md)
- [Changelog](CHANGELOG.md)
- [License](LICENSE)

## Roadmap

- publish first PyPI release
- add a report index page
- improve cross-platform interactive command handling
- add optional JSON summary export
- add configurable review rules

## License

MIT — see [LICENSE](LICENSE).
