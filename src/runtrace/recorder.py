from __future__ import annotations

import json
import secrets
import shlex
from datetime import UTC, datetime
from pathlib import Path

from runtrace.git_utils import classify_status, get_git_snapshot
from runtrace.models import RunMetadata
from runtrace.paths import run_dir as path_run_dir
from runtrace.paths import runs_dir
from runtrace.runner import run_command


def generate_run_id(now: datetime | None = None) -> str:
    current = now or datetime.now(UTC)
    return f"{current.strftime('%Y%m%d-%H%M%S')}-{secrets.token_hex(3)}"


def run_dir_for(cwd: str | Path, run_id: str) -> Path:
    return path_run_dir(cwd, run_id)


def _output_preview(path: Path, max_chars: int = 8000) -> str:
    if not path.exists():
        return ""
    text = path.read_text(encoding="utf-8", errors="replace")
    if len(text) <= max_chars:
        return text
    return text[-max_chars:]


def _save_metadata(run_dir: Path, metadata: RunMetadata) -> None:
    (run_dir / "metadata.json").write_text(metadata.model_dump_json(indent=2), encoding="utf-8")


def record_run(
    command: list[str],
    cwd: str | Path = ".",
    name: str | None = None,
    use_pty: bool | None = None,
) -> RunMetadata:
    root = Path(cwd).resolve()
    root.mkdir(parents=True, exist_ok=True)
    run_id = generate_run_id()
    run_dir = run_dir_for(root, run_id)
    run_dir.mkdir(parents=True, exist_ok=True)
    output_log = run_dir / "output.log"

    start = datetime.now(UTC)
    before = get_git_snapshot(root)
    exit_code = run_command(command, root, output_log, use_pty=use_pty)
    end = datetime.now(UTC)
    after = get_git_snapshot(root)
    changed, added, modified, deleted = classify_status(after.status_short)

    metadata = RunMetadata(
        run_id=run_id,
        name=name or " ".join(command[:3]) or "run",
        cwd=str(root),
        command=command,
        command_shell=shlex.join(command),
        start_time=start,
        end_time=end,
        duration_seconds=round((end - start).total_seconds(), 3),
        exit_code=exit_code,
        succeeded=exit_code == 0,
        output_log=str(output_log.relative_to(run_dir)),
        output_preview=_output_preview(output_log),
        git_before=before,
        git_after=after,
        changed_files=changed,
        files_added=added,
        files_modified=modified,
        files_deleted=deleted,
        diff_stat_after=after.diff_stat,
        full_diff_after=after.full_diff,
        working_tree_changed=bool(after.status_short.strip()),
    )
    _save_metadata(run_dir, metadata)
    return metadata


def load_metadata(cwd: str | Path, run_id: str) -> RunMetadata:
    path = run_dir_for(cwd, run_id) / "metadata.json"
    if not path.exists():
        raise FileNotFoundError(f"Run metadata not found: {path}")
    return RunMetadata.model_validate_json(path.read_text(encoding="utf-8"))


def list_runs(cwd: str | Path = ".") -> list[RunMetadata]:
    root = runs_dir(cwd)
    if not root.exists():
        return []
    runs: list[RunMetadata] = []
    for metadata_path in root.glob("*/metadata.json"):
        try:
            runs.append(RunMetadata.model_validate_json(metadata_path.read_text(encoding="utf-8")))
        except (ValueError, json.JSONDecodeError):
            continue
    return sorted(runs, key=lambda item: item.start_time, reverse=True)


def latest_run_id(cwd: str | Path = ".") -> str | None:
    runs = list_runs(cwd)
    return runs[0].run_id if runs else None


def resolve_run_id(cwd: str | Path, run_id: str | None = None) -> str | None:
    if run_id in (None, "latest"):
        return latest_run_id(cwd)
    return run_id


def delete_old_runs(cwd: str | Path = ".", keep: int = 20) -> list[Path]:
    runs = list_runs(cwd)
    removed: list[Path] = []
    for metadata in runs[keep:]:
        folder = run_dir_for(cwd, metadata.run_id)
        if folder.exists():
            for child in sorted(folder.rglob("*"), reverse=True):
                if child.is_file() or child.is_symlink():
                    child.unlink()
                elif child.is_dir():
                    child.rmdir()
            folder.rmdir()
            removed.append(folder)
    return removed
