from __future__ import annotations

import sys

from typer.testing import CliRunner

from runtrace.cli import app
from runtrace.recorder import record_run
from runtrace.reports import render_pr_summary

runner = CliRunner()


def test_render_pr_summary_is_copy_ready_markdown(tmp_path):
    metadata = record_run([sys.executable, "-c", "print('pytest passed')"], tmp_path, name="pytest baseline")

    text = render_pr_summary(tmp_path, metadata.run_id)

    assert text.startswith("## Runtrace summary")
    assert "- Run: `pytest baseline`" in text
    assert "- Result: `success`" in text
    assert "- Command: `" in text
    assert "## Commands run" in text
    assert "## Changed files" in text
    assert "## Review checklist" in text
    assert "metadata.json" not in text
    assert "full_diff_after" not in text


def test_pr_summary_cli_prints_latest_and_writes_file(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    runner.invoke(app, ["demo"])

    stdout_result = runner.invoke(app, ["pr-summary"])
    file_result = runner.invoke(app, ["pr-summary", "--output", "pr.md"])

    assert stdout_result.exit_code == 0
    assert "## Runtrace summary" in stdout_result.output
    assert file_result.exit_code == 0
    assert "Wrote PR summary" in file_result.output
    assert (tmp_path / "pr.md").read_text(encoding="utf-8").startswith("## Runtrace summary")


def test_pr_summary_without_runs_is_helpful(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(app, ["pr-summary"])

    assert result.exit_code == 1
    assert "No runs found yet" in result.output
    assert "runtrace demo" in result.output
