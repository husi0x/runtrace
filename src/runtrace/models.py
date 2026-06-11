from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class GitSnapshot(BaseModel):
    git_available: bool = False
    repo_root: str | None = None
    branch: str | None = None
    head_sha: str | None = None
    status_short: str = ""
    changed_files: list[str] = Field(default_factory=list)
    diff_stat: str = ""
    full_diff: str = ""


class RunMetadata(BaseModel):
    run_id: str
    name: str
    cwd: str
    command: list[str]
    command_shell: str
    start_time: datetime
    end_time: datetime | None = None
    duration_seconds: float = 0.0
    exit_code: int | None = None
    succeeded: bool = False
    output_log: str
    output_preview: str = ""
    git_before: GitSnapshot = Field(default_factory=GitSnapshot)
    git_after: GitSnapshot = Field(default_factory=GitSnapshot)
    changed_files: list[str] = Field(default_factory=list)
    files_added: list[str] = Field(default_factory=list)
    files_modified: list[str] = Field(default_factory=list)
    files_deleted: list[str] = Field(default_factory=list)
    diff_stat_after: str = ""
    full_diff_after: str = ""
    working_tree_changed: bool = False


class ReviewFinding(BaseModel):
    name: str
    title: str
    status: Literal["pass", "warn", "fail", "info", "unknown"]
    detail: str


class ReportSummary(BaseModel):
    metadata: RunMetadata
    findings: list[ReviewFinding]
    changed_file_count: int
