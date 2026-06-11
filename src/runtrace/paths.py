from __future__ import annotations

from pathlib import Path

RUNTRACE_DIR = Path(".runtrace")
RUNS_DIRNAME = "runs"


def project_root(cwd: str | Path = ".") -> Path:
    return Path(cwd).resolve()


def runtrace_dir(cwd: str | Path = ".") -> Path:
    return project_root(cwd) / RUNTRACE_DIR


def runs_dir(cwd: str | Path = ".") -> Path:
    return runtrace_dir(cwd) / RUNS_DIRNAME


def run_dir(cwd: str | Path, run_id: str) -> Path:
    return runs_dir(cwd) / run_id


def relative_to_cwd(path: Path, cwd: str | Path = ".") -> str:
    try:
        return str(path.resolve().relative_to(project_root(cwd)))
    except ValueError:
        return str(path)
