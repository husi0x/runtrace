<h1 align="center">Runtrace</h1>

<p align="center">
  <strong>A black box for AI coding agents.</strong>
</p>

<p align="center">
  Run any coding agent through Runtrace and get a clean local report: command output, git diff, changed files, and review checklist.
</p>

<p align="center">
  <img src="https://raw.githubusercontent.com/husi0x/runtrace/main/assets/runtrace-hero.png" alt="Runtrace — a black box for AI coding agents" width="100%">
</p>

<p align="center">
  <a href="https://pypi.org/project/runtrace/"><img alt="PyPI" src="https://img.shields.io/pypi/v/runtrace"></a>
  <a href="https://pypi.org/project/runtrace/"><img alt="PyPI downloads" src="https://img.shields.io/pypi/dm/runtrace"></a>
  <img alt="Python 3.11+" src="https://img.shields.io/badge/python-3.11%2B-blue">
  <img alt="License MIT" src="https://img.shields.io/badge/license-MIT-green">
  <img alt="CLI" src="https://img.shields.io/badge/interface-CLI-black">
  <img alt="No network required" src="https://img.shields.io/badge/network-not_required-lightgrey">
</p>

## Try it in 30 seconds

`pipx` is recommended for CLI usage:

```bash
pipx install runtrace
runtrace do pytest -q
runtrace ui
```

`runtrace do` records the command and generates Markdown + HTML reports. `runtrace ui` opens the latest HTML report.

Without `pipx`:

```bash
python -m pip install --user runtrace
runtrace do pytest -q
```

## Why Runtrace?

AI coding agents can change 20 files in one run. Runtrace shows what they actually did.

Each run creates a local folder under `.runtrace/runs/<run_id>/` with:

```text
metadata.json    # machine-readable run record
output.log       # full command output
report.md        # readable Markdown report
report.html      # self-contained HTML report
```

Runtrace records command timing, exit code, live output, git branch/commit/status/diff when available, changed files, and deterministic review findings.

<p align="center">
  <img src="https://raw.githubusercontent.com/husi0x/runtrace/main/assets/runtrace-report-preview.png" alt="Runtrace HTML report preview" width="92%">
</p>

If the directory is not a git repository, Runtrace still records command output and marks git tracking as unavailable.

## Example workflows

Use it with Codex:

```bash
runtrace do codex exec "fix the failing tests"
runtrace ui
runtrace pr
```

Use it with tests:

```bash
runtrace do pytest -q
runtrace ui
```

Use portable subprocess mode when you do not want best-effort PTY handling:

```bash
runtrace run --no-pty --name "tests" -- pytest -q
```

## CLI commands

| Command | What it does |
|---|---|
| `runtrace init` | Creates `.runtrace/config.toml` for custom review checks |
| `runtrace demo` | Records a safe demo run and generates reports |
| `runtrace do <command>` | Records a command and generates reports, no `--` needed |
| `runtrace do --open <command>` | Records, reports, and opens the HTML report |
| `runtrace ui` | Opens the latest HTML report |
| `runtrace pr` | Prints a copy-ready PR summary |
| `runtrace last` | Shows the latest run in the terminal |
| `runtrace run -- <command>` | Records any command |
| `runtrace run --no-pty -- <command>` | Records a command with portable subprocess mode |
| `runtrace run --report -- <command>` | Records a command and generates reports immediately |
| `runtrace report` | Generates Markdown and HTML reports |
| `runtrace report --open` | Generates reports and opens the HTML report |
| `runtrace open` | Opens the latest HTML report, generating it if missing |
| `runtrace open <run_id>` | Opens one run's HTML report |
| `runtrace index` | Generates `.runtrace/index.html` for all runs |
| `runtrace dashboard` | Alias for `runtrace index` |
| `runtrace doctor` | Checks local Runtrace readiness and latest artifacts |
| `runtrace export` | Prints a compact JSON summary for the latest run |
| `runtrace export --output summary.json` | Writes the JSON summary to a file |
| `runtrace pr-summary` | Prints a copy-ready Markdown summary for GitHub PRs |
| `runtrace pr-summary --output pr.md` | Writes the PR summary to a file |
| `runtrace list` | Lists previous runs |
| `runtrace runs` | Alias for `runtrace list` |
| `runtrace show <run_id>` | Shows one run in the terminal |
| `runtrace show latest` | Shows the newest run |
| `runtrace latest` | Shortcut for `runtrace show latest` |
| `runtrace clean --keep 20` | Deletes old runs, keeping the newest 20 |
| `runtrace version` | Prints the installed version |

See [docs/CLI.md](docs/CLI.md) for full command details and common mistakes.

## Reports

Runtrace generates local Markdown, HTML, index, and JSON summary artifacts:

```bash
runtrace report
runtrace index
runtrace export --output summary.json
```

The full command output stays in `output.log`. The full machine-readable run record stays in `metadata.json`. The JSON export intentionally skips huge logs and full diffs.

Sample output is included in [examples/sample-output](examples/sample-output/). See [docs/REPORTS.md](docs/REPORTS.md) for details.

## Configuration

Create local review rules:

```bash
runtrace init
```

Then edit `.runtrace/config.toml` to change sensitive path patterns, dependency/config patterns, test command patterns, or the large-diff threshold.

See [docs/CONFIG.md](docs/CONFIG.md).

## Privacy

Runtrace does not call any external API. Everything is stored locally in `.runtrace/`.

Runtrace masks common local paths and obvious secret-like values before writing reports and metadata. Reports may still include command output, file paths, and git diffs that are project-specific, so review them before sharing publicly.

See [SECURITY.md](SECURITY.md) for practical security notes.

## Development install

For contributors and local development only:

```bash
git clone https://github.com/husi0x/runtrace.git
cd runtrace
python -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
bash scripts/smoke.sh
```

Release maintenance is documented in [docs/PYPI.md](docs/PYPI.md).

## Docs

- [CLI reference](docs/CLI.md)
- [Reports and privacy](docs/REPORTS.md)
- [Configuration](docs/CONFIG.md)
- [PyPI package](docs/PYPI.md)
- [Release checklist](docs/RELEASE.md)
- [GitHub metadata](docs/GITHUB.md)
- [Examples](examples/README.md)
- [Contributing](CONTRIBUTING.md)
- [Security](SECURITY.md)
- [Changelog](CHANGELOG.md)
- [License](LICENSE)

## License

MIT — see [LICENSE](LICENSE).
