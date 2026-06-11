from __future__ import annotations

from typer.testing import CliRunner

from runtrace.cli import app
from runtrace.recorder import list_runs

runner = CliRunner()


def test_help_works():
    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "Runtrace" in result.output
    assert "demo" in result.output


def test_list_with_no_runs_is_helpful(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["list"])

    assert result.exit_code == 0
    assert "No runs found yet" in result.output
    assert "runtrace demo" in result.output


def test_demo_creates_run_and_reports(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["demo"])
    runs = list_runs(".")
    run_id = runs[0].run_id

    assert result.exit_code == 0
    assert "Runtrace demo complete" in result.output
    assert "Markdown:" in result.output
    assert "HTML:" in result.output
    assert "Output:" in result.output
    assert "runtrace show" in result.output
    assert (tmp_path / run_id).exists() is False
    assert (tmp_path / ".runtrace" / "runs" / run_id / "metadata.json").exists()
    assert (tmp_path / ".runtrace" / "runs" / run_id / "report.md").exists()
    assert (tmp_path / ".runtrace" / "runs" / run_id / "report.html").exists()


def test_show_latest_works(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    runner.invoke(app, ["demo"])
    result = runner.invoke(app, ["show", "latest"])

    assert result.exit_code == 0
    assert "Runtrace run" in result.output
    assert "Review checklist" in result.output


def test_latest_command_works(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    runner.invoke(app, ["demo"])
    result = runner.invoke(app, ["latest"])

    assert result.exit_code == 0
    assert "Runtrace run" in result.output


def test_runs_alias_lists_runs(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    runner.invoke(app, ["demo"])
    result = runner.invoke(app, ["runs"])

    assert result.exit_code == 0
    assert "Runtrace runs" in result.output


def test_clean_yes_removes_old_runs(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    runner.invoke(app, ["demo"])
    runner.invoke(app, ["demo"])
    result = runner.invoke(app, ["clean", "--keep", "1", "--yes"])
    runs = list_runs(".")

    assert result.exit_code == 0
    assert "Deleted 1" in result.output
    assert len(runs) == 1


def test_report_without_runs_is_helpful(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["report"])

    assert result.exit_code == 1
    assert "No runs found yet" in result.output
    assert "runtrace demo" in result.output
