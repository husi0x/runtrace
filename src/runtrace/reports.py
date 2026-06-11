from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from runtrace.models import ReportSummary
from runtrace.recorder import load_metadata, resolve_run_id, run_dir_for
from runtrace.review import build_review_findings


def build_report_summary(metadata) -> ReportSummary:
    findings = build_review_findings(metadata)
    return ReportSummary(
        metadata=metadata,
        findings=findings,
        changed_file_count=len(metadata.changed_files),
    )


def _status_icon(status: str) -> str:
    return {
        "pass": "✅ Pass",
        "warn": "⚠️ Warning",
        "fail": "❌ Fail",
        "info": "ℹ️ Info",
        "unknown": "⚪ Unknown",
    }.get(status, status)


def _table_row(left: str, right: str) -> str:
    return f"| {left} | {right} |"


def render_markdown(summary: ReportSummary) -> str:
    m = summary.metadata
    before = m.git_before
    after = m.git_after
    status = "success" if m.succeeded else "failed"
    changed = "\n".join(f"- `{item}`" for item in m.changed_files) or "- No changed files detected"
    findings = "\n".join(f"| {f.title} | {_status_icon(f.status)} | {f.detail} |" for f in summary.findings)
    status_before = before.status_short or "clean / unavailable"
    status_after = after.status_short or "clean / unavailable"
    diff_stat = m.diff_stat_after or "No diff stat available"
    output_tail = m.output_preview[-2000:] if m.output_preview else "No command output captured."

    summary_rows = "\n".join(
        [
            _table_row("Run ID", f"`{m.run_id}`"),
            _table_row("Status", f"`{status}`"),
            _table_row("Duration", f"`{m.duration_seconds}s`"),
            _table_row("Command", f"`{m.command_shell}`"),
            _table_row("Working directory", f"`{m.cwd}`"),
            _table_row("Exit code", f"`{m.exit_code}`"),
            _table_row("Changed files", f"`{len(m.changed_files)}`"),
        ]
    )

    return f"""# Runtrace Report: {m.name}

Runtrace — a black box for AI coding agents.

## Summary

| Field | Value |
|---|---|
{summary_rows}

## Command

```bash
{m.command_shell}
```

## Git state

| Field | Before | After |
|---|---|---|
| Git available | `{before.git_available}` | `{after.git_available}` |
| Branch | `{before.branch or "none"}` | `{after.branch or "none"}` |
| Commit | `{before.head_sha or "none"}` | `{after.head_sha or "none"}` |

### Status before

```text
{status_before}
```

### Status after

```text
{status_after}
```

## Changed files

{changed}

## Diff stat

```text
{diff_stat}
```

## Review checklist

| Check | Result | Notes |
|---|---|---|
{findings}

## Output log

Full output is saved in `{m.output_log}`.

```text
{output_tail}
```

## Metadata

- Start time: `{m.start_time}`
- End time: `{m.end_time}`
- Metadata file: `metadata.json`
- HTML report: `report.html`
"""


def _metadata_for_report(cwd: str | Path, run_id: str | None):
    actual_id = resolve_run_id(cwd, run_id)
    if not actual_id:
        raise FileNotFoundError("No runs found yet. Try: runtrace demo")
    return actual_id, load_metadata(cwd, actual_id)


def generate_markdown_report(cwd: str | Path = ".", run_id: str | None = None) -> Path:
    actual_id, metadata = _metadata_for_report(cwd, run_id)
    summary = build_report_summary(metadata)
    run_dir = run_dir_for(cwd, actual_id)
    path = run_dir / "report.md"
    path.write_text(render_markdown(summary), encoding="utf-8")
    return path


def generate_html_report(cwd: str | Path = ".", run_id: str | None = None) -> Path:
    actual_id, metadata = _metadata_for_report(cwd, run_id)
    summary = build_report_summary(metadata)
    run_dir = run_dir_for(cwd, actual_id)
    env = Environment(
        loader=FileSystemLoader(Path(__file__).parent / "templates"),
        autoescape=select_autoescape(["html", "xml"]),
    )
    html = env.get_template("report.html.j2").render(summary=summary, metadata=metadata)
    path = run_dir / "report.html"
    path.write_text(html, encoding="utf-8")
    return path


def generate_reports(cwd: str | Path = ".", run_id: str | None = None, fmt: str = "both") -> list[Path]:
    if fmt not in {"md", "html", "both"}:
        raise ValueError("format must be one of: md, html, both")
    paths: list[Path] = []
    if fmt in {"md", "both"}:
        paths.append(generate_markdown_report(cwd, run_id))
    if fmt in {"html", "both"}:
        paths.append(generate_html_report(cwd, run_id))
    return paths
