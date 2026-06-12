from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape

from runtrace import __version__
from runtrace.models import ReportSummary, RunMetadata
from runtrace.paths import relative_to_cwd, runtrace_dir
from runtrace.recorder import list_runs, load_metadata, resolve_run_id, run_dir_for
from runtrace.review import build_review_findings


def _template_env() -> Environment:
    return Environment(
        loader=FileSystemLoader(Path(__file__).parent / "templates"),
        autoescape=select_autoescape(["html", "xml"]),
    )


def build_report_summary(metadata: RunMetadata) -> ReportSummary:
    findings = build_review_findings(metadata, cwd=metadata.cwd)
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


def _short_sha(value: str | None) -> str:
    return value[:7] if value else "none"


def _format_time(value) -> str:
    if not value:
        return "Not finished"
    return value.strftime("%d %b %Y, %H:%M UTC")


def _format_duration(seconds: float) -> str:
    if seconds < 1:
        return f"{round(seconds * 1000)}ms"
    if seconds < 60:
        return f"{seconds:.1f}s"
    minutes, remainder = divmod(seconds, 60)
    return f"{int(minutes)}m {remainder:.0f}s"


def _agent_label(metadata: RunMetadata) -> str:
    command = " ".join(metadata.command).lower()
    if "codex" in command:
        return "Codex"
    if "claude" in command:
        return "Claude"
    if "opencode" in command:
        return "OpenCode"
    return "Runtrace CLI"


def _review_display(finding) -> dict[str, str | bool]:
    is_done = finding.status == "pass"
    passed_title_overrides = {
        "no_git_repo": "Git snapshot available",
        "command_failed": "No command failure",
        "tests_likely_failed": "No likely test failures",
        "sensitive_files_touched": "No sensitive files touched",
        "dependency_config_touched": "No dependency/config files touched",
        "large_diff": "Diff size within review limit",
    }
    neutral_title_overrides = {
        "no_git_repo": "Git snapshot available",
        "command_failed": "No command failure",
        "tests_likely_failed": "No likely test failures",
    }
    if finding.status == "fail":
        state = "Attention"
        tone = "fail"
    elif finding.status == "warn":
        state = "Review"
        tone = "review"
    elif is_done:
        state = "Done"
        tone = "done"
    else:
        state = "Pending"
        tone = "pending"
    title = passed_title_overrides.get(finding.name, finding.title) if is_done else neutral_title_overrides.get(
        finding.name, finding.title
    )
    return {
        "title": title,
        "detail": finding.detail,
        "done": is_done,
        "state": state,
        "tone": tone,
    }


def _parse_diff_totals(diff_stat: str) -> dict[str, int]:
    text = diff_stat or ""
    insertions = 0
    deletions = 0
    files_changed = 0

    summary_match = re.search(r"(\d+)\s+files? changed", text)
    if summary_match:
        files_changed = int(summary_match.group(1))
    insertion_match = re.search(r"(\d+)\s+insertions?\(\+\)", text)
    if insertion_match:
        insertions = int(insertion_match.group(1))
    deletion_match = re.search(r"(\d+)\s+deletions?\(-\)", text)
    if deletion_match:
        deletions = int(deletion_match.group(1))

    # `git diff --stat` may omit the summary line for untracked-only changes.
    if not files_changed:
        files_changed = len([line for line in text.splitlines() if "|" in line or line.strip().startswith("Untracked")])

    total = insertions + deletions
    insert_pct = round((insertions / total) * 100, 1) if total else 0
    delete_pct = round((deletions / total) * 100, 1) if total else 0
    return {
        "files_changed": files_changed,
        "insertions": insertions,
        "deletions": deletions,
        "insert_pct": insert_pct,
        "delete_pct": delete_pct,
    }


def _changed_file_rows(metadata: RunMetadata) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    added = set(metadata.files_added)
    modified = set(metadata.files_modified)
    deleted = set(metadata.files_deleted)
    for index, path in enumerate(metadata.changed_files, start=1):
        if path in added:
            change_type = "Added"
        elif path in deleted:
            change_type = "Deleted"
        elif path in modified:
            change_type = "Modified"
        else:
            change_type = "Changed"
        rows.append({"index": str(index), "path": path, "change_type": change_type})
    return rows


def _report_view_model(cwd: str | Path, run_id: str, metadata: RunMetadata, summary: ReportSummary) -> dict[str, Any]:
    repo = metadata.git_after.repo_root or metadata.git_before.repo_root or metadata.cwd
    report_path = relative_to_cwd(run_dir_for(cwd, run_id) / "report.html", cwd)
    return {
        "version": __version__,
        "report_path": report_path,
        "repository": repo,
        "repository_name": Path(repo).name if repo else "repository",
        "branch": metadata.git_after.branch or metadata.git_before.branch or "none",
        "before_sha": _short_sha(metadata.git_before.head_sha),
        "after_sha": _short_sha(metadata.git_after.head_sha),
        "started_display": _format_time(metadata.start_time),
        "finished_display": _format_time(metadata.end_time),
        "duration_display": _format_duration(metadata.duration_seconds),
        "diff": _parse_diff_totals(metadata.diff_stat_after),
        "changed_file_rows": _changed_file_rows(metadata),
        "review_rows": [_review_display(finding) for finding in summary.findings],
        "run_by": "Local user",
        "agent": _agent_label(metadata),
    }


def generate_html_report(cwd: str | Path = ".", run_id: str | None = None) -> Path:
    actual_id, metadata = _metadata_for_report(cwd, run_id)
    summary = build_report_summary(metadata)
    run_dir = run_dir_for(cwd, actual_id)
    view = _report_view_model(cwd, actual_id, metadata, summary)
    html = _template_env().get_template("report.html.j2").render(summary=summary, metadata=metadata, view=view)
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


def _run_index_rows(cwd: str | Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for metadata in list_runs(cwd):
        folder = run_dir_for(cwd, metadata.run_id)
        report_html = folder / "report.html"
        output_log = folder / "output.log"
        rows.append(
            {
                "run_id": metadata.run_id,
                "name": metadata.name,
                "status": "success" if metadata.succeeded else "failed",
                "command": metadata.command_shell,
                "duration": metadata.duration_seconds,
                "created": metadata.start_time,
                "changed_file_count": len(metadata.changed_files),
                "report_href": f"runs/{metadata.run_id}/report.html" if report_html.exists() else None,
                "output_href": f"runs/{metadata.run_id}/output.log" if output_log.exists() else None,
            }
        )
    return rows


def generate_index_page(cwd: str | Path = ".") -> Path:
    root = runtrace_dir(cwd)
    root.mkdir(parents=True, exist_ok=True)
    path = root / "index.html"
    html = _template_env().get_template("index.html.j2").render(runs=_run_index_rows(cwd))
    path.write_text(html, encoding="utf-8")
    return path


def _report_paths(cwd: str | Path, run_id: str) -> dict[str, str]:
    folder = run_dir_for(cwd, run_id)
    paths: dict[str, str] = {}
    report_md = folder / "report.md"
    report_html = folder / "report.html"
    output_log = folder / "output.log"
    if report_md.exists():
        paths["markdown"] = relative_to_cwd(report_md, cwd)
    if report_html.exists():
        paths["html"] = relative_to_cwd(report_html, cwd)
    if output_log.exists():
        paths["output_log"] = relative_to_cwd(output_log, cwd)
    return paths


def export_summary(cwd: str | Path = ".", run_id: str | None = None) -> dict[str, Any]:
    actual_id, metadata = _metadata_for_report(cwd, run_id)
    findings = build_review_findings(metadata, cwd=metadata.cwd)
    return {
        "run_id": metadata.run_id,
        "name": metadata.name,
        "command": metadata.command,
        "command_shell": metadata.command_shell,
        "cwd": metadata.cwd,
        "success": metadata.succeeded,
        "exit_code": metadata.exit_code,
        "started_at": metadata.start_time.isoformat(),
        "ended_at": metadata.end_time.isoformat() if metadata.end_time else None,
        "duration_seconds": metadata.duration_seconds,
        "git_available": metadata.git_before.git_available or metadata.git_after.git_available,
        "branch_before": metadata.git_before.branch,
        "branch_after": metadata.git_after.branch,
        "commit_before": metadata.git_before.head_sha,
        "commit_after": metadata.git_after.head_sha,
        "changed_files": metadata.changed_files,
        "changed_file_count": len(metadata.changed_files),
        "diff_stat": metadata.diff_stat_after,
        "review_findings": [finding.model_dump() for finding in findings],
        "report_paths": _report_paths(cwd, actual_id),
    }


def export_summary_json(cwd: str | Path = ".", run_id: str | None = None) -> str:
    return json.dumps(export_summary(cwd, run_id), indent=2, ensure_ascii=False) + "\n"
