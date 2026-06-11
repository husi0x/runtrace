from __future__ import annotations

import subprocess
from pathlib import Path

from runtrace.models import GitSnapshot


def _git(cwd: Path, args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=cwd,
        text=True,
        capture_output=True,
        check=False,
    )


def _git_text(cwd: Path, args: list[str]) -> str:
    result = _git(cwd, args)
    if result.returncode != 0:
        return ""
    return result.stdout.strip()


def is_git_repo(cwd: Path) -> bool:
    return _git(cwd, ["rev-parse", "--is-inside-work-tree"]).stdout.strip() == "true"


def _parse_changed_files(status_short: str) -> tuple[list[str], list[str], list[str], list[str]]:
    changed: list[str] = []
    added: list[str] = []
    modified: list[str] = []
    deleted: list[str] = []
    for line in status_short.splitlines():
        if not line.strip():
            continue
        code = line[:2]
        # Git porcelain/short status uses two status columns followed by a path.
        # Some Git versions omit the leading blank in captured output, so line[2:]
        # is safer than assuming a third separator character.
        path = line[2:].strip() if len(line) > 2 else line.strip()
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        changed.append(path)
        if "A" in code or code == "??":
            added.append(path)
        if "M" in code:
            modified.append(path)
        if "D" in code:
            deleted.append(path)
    return changed, added, modified, deleted


def classify_status(status_short: str) -> tuple[list[str], list[str], list[str], list[str]]:
    return _parse_changed_files(status_short)


def get_git_snapshot(cwd: str | Path) -> GitSnapshot:
    path = Path(cwd).resolve()
    if not is_git_repo(path):
        return GitSnapshot(git_available=False)

    repo_root = _git_text(path, ["rev-parse", "--show-toplevel"])
    branch = _git_text(path, ["branch", "--show-current"])
    head_sha = _git_text(path, ["rev-parse", "HEAD"])
    status_short = _git_text(path, ["status", "--short"])
    changed_files, _, _, _ = _parse_changed_files(status_short)
    diff_stat = _git_text(path, ["diff", "--stat"])
    full_diff = _git_text(path, ["diff", "--"])

    # Include untracked file names in stat/diff-ish summaries without dumping contents.
    untracked = [p for p in changed_files if p not in diff_stat and (Path(repo_root) / p).exists()]
    if untracked:
        suffix = "\nUntracked files:\n" + "\n".join(f"  {p}" for p in untracked)
        diff_stat = (diff_stat + suffix).strip()

    return GitSnapshot(
        git_available=True,
        repo_root=repo_root or None,
        branch=branch or None,
        head_sha=head_sha or None,
        status_short=status_short,
        changed_files=changed_files,
        diff_stat=diff_stat,
        full_diff=full_diff,
    )
