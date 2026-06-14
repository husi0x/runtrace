from __future__ import annotations

import sys
from pathlib import Path

from typer.testing import CliRunner

import runtrace.cli as cli
from runtrace.cli import app
from runtrace.recorder import list_runs

runner = CliRunner()


def test_do_records_command_and_generates_reports_by_default(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(app, ["do", sys.executable, "-c", "print('simple ok')"])

    run = list_runs(tmp_path)[0]
    run_folder = tmp_path / ".runtrace" / "runs" / run.run_id
    assert result.exit_code == 0
    assert run.name == f"{Path(sys.executable).name} -c"
    assert (run_folder / "report.md").exists()
    assert (run_folder / "report.html").exists()
    assert "Report generated" in result.output


def test_do_open_opens_html_report(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    opened: list[Path] = []
    monkeypatch.setattr(cli, "_open_path", lambda path: opened.append(path), raising=False)

    result = runner.invoke(app, ["do", "--open", sys.executable, "-c", "print('simple open')"])

    run = list_runs(tmp_path)[0]
    report_html = tmp_path / ".runtrace" / "runs" / run.run_id / "report.html"
    assert result.exit_code == 0
    assert opened == [report_html]
    assert "Opened HTML report" in result.output


def test_do_name_overrides_auto_name(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(app, ["do", "--name", "tests", sys.executable, "-c", "print('named')"])

    assert result.exit_code == 0
    assert list_runs(tmp_path)[0].name == "tests"


def test_ui_pr_and_last_aliases(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    opened: list[Path] = []
    monkeypatch.setattr(cli, "_open_path", lambda path: opened.append(path), raising=False)
    runner.invoke(app, ["do", sys.executable, "-c", "print('aliases')"])

    ui_result = runner.invoke(app, ["ui"])
    pr_result = runner.invoke(app, ["pr"])
    last_result = runner.invoke(app, ["last"])

    assert ui_result.exit_code == 0
    assert opened
    assert pr_result.exit_code == 0
    assert "## Runtrace summary" in pr_result.output
    assert last_result.exit_code == 0
    assert "Runtrace run" in last_result.output
