# Changelog

## 0.3.2 - 2026-06-14

- Added simpler user-facing aliases: `runtrace do`, `runtrace ui`, `runtrace pr`, and `runtrace last`.
- Updated README and CLI docs around the shorter happy path: `runtrace do pytest -q`, `runtrace ui`, `runtrace pr`.

## 0.3.1 - 2026-06-14

- Fixed PyPI long-description images by using absolute GitHub raw asset URLs for the README hero and report preview.

## 0.3.0 - 2026-06-14

- Added artifact sanitizing for recorded metadata, output previews, git summaries, and logs. Common local paths and obvious secret-like values are masked before report generation.
- Added `runtrace pr-summary` for copy-ready GitHub PR/issue summaries, with optional `--output` file writing.
- Added `runtrace doctor` for checking local Runtrace readiness, git availability, run count, latest run, and report artifacts.
- Added `runtrace open` to open the latest or selected HTML report, generating it first when missing.
- Added `runtrace report --open` to generate reports and immediately open the HTML report.
- Added `runtrace run --report` and `runtrace run --report --open` for the one-command record/report/open workflow.

## 0.2.0 - 2026-06-14

- README install flow now points to PyPI/pipx after first PyPI publication.
- Report index page via `runtrace index` and `runtrace dashboard`.
- Compact JSON summary export via `runtrace export`.
- Configurable review rules via `.runtrace/config.toml` and `runtrace init`.
- Safer smoke/install/release instructions, including PyPI build checks without publishing.
- Cross-platform runner improvements with portable `--no-pty` subprocess mode.
- Initial public version of Runtrace.
- Local command recording under `.runtrace/runs/<run_id>/`.
- Markdown and HTML report generation.
- Deterministic review checklist.
- Friendly CLI commands: `demo`, `run`, `report`, `index`, `export`, `init`, `list`, `show`, `latest`, `clean`, and `version`.
