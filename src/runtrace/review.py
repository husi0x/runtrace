from __future__ import annotations

from pathlib import Path

from runtrace.config import load_review_config
from runtrace.models import ReviewFinding, RunMetadata

TEST_PASS_PATTERNS = ("passed", "all tests passed", "tests passed", "success", "ok")
TEST_FAIL_PATTERNS = ("failed", "error", "traceback", "assertionerror", "tests failed")


def contains_any(text: str, patterns: list[str] | tuple[str, ...]) -> bool:
    low = text.lower()
    return any(pattern.lower() in low for pattern in patterns)


def matching_paths(paths: list[str], patterns: list[str] | tuple[str, ...]) -> list[str]:
    return [path for path in paths if contains_any(path, patterns)]


def diff_stat_line_count(diff_stat: str) -> int:
    return len([line for line in diff_stat.splitlines() if line.strip() and "|" in line])


def finding(name: str, title: str, status: str, detail: str) -> ReviewFinding:
    return ReviewFinding(name=name, title=title, status=status, detail=detail)  # type: ignore[arg-type]


def build_review_findings(metadata: RunMetadata, cwd: str | Path | None = None) -> list[ReviewFinding]:
    config = load_review_config(cwd or metadata.cwd)
    command_text = metadata.command_shell + " " + " ".join(metadata.command)
    output = metadata.output_preview
    changed_files = metadata.changed_files

    tests_detected = contains_any(command_text, config.test_commands) or contains_any(output, config.test_commands)
    pass_pattern = contains_any(output, TEST_PASS_PATTERNS)
    fail_pattern = contains_any(output, TEST_FAIL_PATTERNS)
    tests_likely_passed = tests_detected and pass_pattern and not fail_pattern and metadata.succeeded
    tests_likely_failed = tests_detected and (fail_pattern or metadata.exit_code not in (0, None))

    sensitive = matching_paths(changed_files, config.sensitive_patterns)
    dependency_config = matching_paths(changed_files, config.dependency_patterns)
    large_diff = (
        len(changed_files) > config.large_diff_file_limit
        or diff_stat_line_count(metadata.diff_stat_after) > config.large_diff_file_limit
    )
    git_available = metadata.git_after.git_available or metadata.git_before.git_available

    return [
        finding(
            "command_completed",
            "Command completed",
            "pass" if metadata.succeeded else "fail",
            f"Exit code {metadata.exit_code}.",
        ),
        finding(
            "command_failed",
            "No command failure",
            "fail" if not metadata.succeeded else "pass",
            "The command exited non-zero; the run was recorded anyway."
            if not metadata.succeeded
            else "Command exited successfully.",
        ),
        finding(
            "tests_detected",
            "Tests detected",
            "pass" if tests_detected else "unknown",
            "Detected a configured test command or output pattern." if tests_detected else "No test command detected.",
        ),
        finding(
            "tests_likely_passed",
            "Tests likely passed",
            "pass" if tests_likely_passed else "unknown",
            "Detected common test pass patterns." if tests_likely_passed else "No confident pass signal detected.",
        ),
        finding(
            "tests_likely_failed",
            "No likely test failures",
            "fail" if tests_likely_failed else "pass",
            "Detected failure patterns or non-zero exit."
            if tests_likely_failed
            else "No common test failure pattern detected.",
        ),
        finding(
            "sensitive_files_touched",
            "Sensitive files touched",
            "warn" if sensitive else "pass",
            ", ".join(sensitive) if sensitive else "None detected.",
        ),
        finding(
            "dependency_config_touched",
            "Dependency/config files touched",
            "warn" if dependency_config else "pass",
            ", ".join(dependency_config) if dependency_config else "None detected.",
        ),
        finding(
            "large_diff",
            "Large diff",
            "warn" if large_diff else "pass",
            f"{len(changed_files)} changed file(s); limit is {config.large_diff_file_limit}.",
        ),
        finding(
            "no_git_repo",
            "Git repository unavailable",
            "warn" if not git_available else "pass",
            "Runtrace recorded command output, but git diff tracking is disabled."
            if not git_available
            else "Git snapshot recorded.",
        ),
    ]
