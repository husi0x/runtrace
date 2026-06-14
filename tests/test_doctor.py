from __future__ import annotations

from typer.testing import CliRunner

from runtrace.cli import app

runner = CliRunner()


def test_doctor_reports_empty_project_status(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(app, ["doctor"])

    assert result.exit_code == 0
    assert "Runtrace doctor" in result.output
    assert "Working directory" in result.output
    assert "Git repository" in result.output
    assert "No" in result.output
    assert "Runs recorded" in result.output
    assert "0" in result.output
    assert "runtrace demo" in result.output


def test_doctor_reports_latest_run_after_demo(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    runner.invoke(app, ["demo"])

    result = runner.invoke(app, ["doctor"])

    assert result.exit_code == 0
    assert "Runs recorded" in result.output
    assert "Latest run" in result.output
    assert "Reports" in result.output
    assert "Ready" in result.output
