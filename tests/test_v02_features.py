from __future__ import annotations

import json
import sys

from typer.testing import CliRunner

from runtrace.cli import app
from runtrace.config import load_review_config
from runtrace.recorder import record_run
from runtrace.reports import export_summary, generate_html_report, generate_index_page
from runtrace.review import build_review_findings

runner = CliRunner()


def test_index_page_includes_runs_and_links(tmp_path):
    first = record_run([sys.executable, "-c", "print('one')"], tmp_path, name="one")
    second = record_run([sys.executable, "-c", "print('two')"], tmp_path, name="two")
    generate_html_report(tmp_path, first.run_id)

    index_path = generate_index_page(tmp_path)
    text = index_path.read_text(encoding="utf-8")

    assert index_path == tmp_path / ".runtrace" / "index.html"
    assert second.run_id in text
    assert first.run_id in text
    assert f"runs/{first.run_id}/report.html" in text
    assert f"runs/{second.run_id}/output.log" in text
    assert "report not generated yet" in text


def test_index_cli_handles_empty_and_generates_page(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    empty = runner.invoke(app, ["index"])
    assert empty.exit_code == 0
    assert "No runs found yet. Try: runtrace demo" in empty.output

    runner.invoke(app, ["demo"])
    result = runner.invoke(app, ["index"])

    assert result.exit_code == 0
    assert ".runtrace/index.html" in result.output
    assert "xdg-open .runtrace/index.html" in result.output
    assert (tmp_path / ".runtrace" / "index.html").exists()


def test_dashboard_alias_generates_index(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    runner.invoke(app, ["demo"])

    result = runner.invoke(app, ["dashboard"])

    assert result.exit_code == 0
    assert (tmp_path / ".runtrace" / "index.html").exists()


def test_export_summary_has_expected_keys_and_no_full_diff_or_output(tmp_path):
    metadata = record_run([sys.executable, "-c", "print('hello export')"], tmp_path, name="export")
    generate_html_report(tmp_path, metadata.run_id)

    summary = export_summary(tmp_path, metadata.run_id)

    assert summary["run_id"] == metadata.run_id
    assert summary["name"] == "export"
    assert summary["success"] is True
    assert "review_findings" in summary
    assert "report_paths" in summary
    assert "report.html" in summary["report_paths"]["html"]
    assert "output_preview" not in summary
    assert "full_diff_after" not in summary


def test_export_cli_stdout_and_file(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    runner.invoke(app, ["demo"])

    stdout_result = runner.invoke(app, ["export"])
    data = json.loads(stdout_result.output)

    assert stdout_result.exit_code == 0
    assert data["run_id"]
    assert data["changed_file_count"] == len(data["changed_files"])

    file_result = runner.invoke(app, ["export", "--output", "summary.json"])
    written = json.loads((tmp_path / "summary.json").read_text(encoding="utf-8"))

    assert file_result.exit_code == 0
    assert written["run_id"] == data["run_id"]
    assert "summary.json" in file_result.output


def test_runtrace_init_creates_and_force_overwrites_config(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(app, ["init"])
    config_path = tmp_path / ".runtrace" / "config.toml"

    assert result.exit_code == 0
    assert config_path.exists()
    assert "large_diff_file_limit" in config_path.read_text(encoding="utf-8")

    config_path.write_text("[review]\nlarge_diff_file_limit = 3\n", encoding="utf-8")
    no_force = runner.invoke(app, ["init"])
    assert no_force.exit_code == 0
    assert "already exists" in no_force.output
    assert "large_diff_file_limit = 3" in config_path.read_text(encoding="utf-8")

    forced = runner.invoke(app, ["init", "--force"])
    assert forced.exit_code == 0
    assert "overwritten" in forced.output.lower()
    assert "large_diff_file_limit = 20" in config_path.read_text(encoding="utf-8")


def test_review_config_custom_large_diff_and_sensitive_pattern(tmp_path):
    (tmp_path / ".runtrace").mkdir()
    (tmp_path / ".runtrace" / "config.toml").write_text(
        '[review]\nlarge_diff_file_limit = 1\nsensitive_patterns = ["private-key"]\n',
        encoding="utf-8",
    )
    metadata = record_run([sys.executable, "-c", "print('ok')"], tmp_path, name="custom")
    metadata.changed_files = ["src/a.py", "docs/private-key.txt"]

    findings = {finding.name: finding for finding in build_review_findings(metadata, cwd=tmp_path)}

    assert findings["large_diff"].status == "warn"
    assert findings["sensitive_files_touched"].status == "warn"
    assert "private-key" in findings["sensitive_files_touched"].detail


def test_malformed_config_falls_back_to_defaults(tmp_path, capsys):
    (tmp_path / ".runtrace").mkdir()
    (tmp_path / ".runtrace" / "config.toml").write_text("[review\nnot toml", encoding="utf-8")

    config = load_review_config(tmp_path)
    captured = capsys.readouterr()

    assert config.large_diff_file_limit == 20
    assert "warning" in captured.err.lower()


def test_run_no_pty_records_command(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(
        app,
        ["run", "--no-pty", "--name", "no pty", "--", sys.executable, "-c", "print('no pty ok')"],
    )

    assert result.exit_code == 0
    assert "Runtrace run recorded" in result.output
    run_root = tmp_path / ".runtrace" / "runs"
    output_logs = list(run_root.glob("*/output.log"))
    assert len(output_logs) == 1
    assert "no pty ok" in output_logs[0].read_text(encoding="utf-8")
