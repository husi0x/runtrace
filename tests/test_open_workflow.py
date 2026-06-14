from __future__ import annotations

import sys
from pathlib import Path

from typer.testing import CliRunner

import runtrace.cli as cli
from runtrace.cli import app
from runtrace.recorder import list_runs, record_run

runner = CliRunner()


def test_open_latest_generates_missing_html_report_and_opens_it(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    opened: list[Path] = []
    monkeypatch.setattr(cli, "_open_path", lambda path: opened.append(path), raising=False)
    metadata = record_run([sys.executable, "-c", "print('open me')"], tmp_path, name="open me")

    result = runner.invoke(app, ["open"])

    report_html = tmp_path / ".runtrace" / "runs" / metadata.run_id / "report.html"
    assert result.exit_code == 0
    assert report_html.exists()
    assert opened == [report_html]
    assert "Opened HTML report" in result.output


def test_report_open_generates_and_opens_html_report(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    opened: list[Path] = []
    monkeypatch.setattr(cli, "_open_path", lambda path: opened.append(path), raising=False)
    metadata = record_run([sys.executable, "-c", "print('report open')"], tmp_path, name="report open")

    result = runner.invoke(app, ["report", "--run-id", metadata.run_id, "--open"])

    report_html = tmp_path / ".runtrace" / "runs" / metadata.run_id / "report.html"
    assert result.exit_code == 0
    assert report_html.exists()
    assert opened == [report_html]
    assert "Opened HTML report" in result.output


def test_run_report_generates_reports_after_successful_command(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(app, ["run", "--no-pty", "--report", "--", sys.executable, "-c", "print('ok')"])

    run_id = list_runs(tmp_path)[0].run_id
    run_folder = tmp_path / ".runtrace" / "runs" / run_id
    assert result.exit_code == 0
    assert (run_folder / "report.md").exists()
    assert (run_folder / "report.html").exists()
    assert "Report generated" in result.output


def test_run_report_open_generates_and_opens_html_report(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    opened: list[Path] = []
    monkeypatch.setattr(cli, "_open_path", lambda path: opened.append(path), raising=False)

    result = runner.invoke(
        app,
        ["run", "--no-pty", "--report", "--open", "--", sys.executable, "-c", "print('ok')"],
    )

    run_id = list_runs(tmp_path)[0].run_id
    report_html = tmp_path / ".runtrace" / "runs" / run_id / "report.html"
    assert result.exit_code == 0
    assert report_html.exists()
    assert opened == [report_html]
    assert "Opened HTML report" in result.output
