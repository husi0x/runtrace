import sys

from runtrace.recorder import list_runs, record_run
from runtrace.reports import build_report_summary, generate_html_report, generate_markdown_report


def test_markdown_report_generation(tmp_path):
    metadata = record_run([sys.executable, "-c", "print('pytest passed')"], tmp_path, name="report run")

    path = generate_markdown_report(tmp_path, metadata.run_id)
    text = path.read_text(encoding="utf-8")

    assert path.name == "report.md"
    assert "# Runtrace Report: report run" in text
    assert metadata.run_id in text
    assert "Review checklist" in text
    assert "output.log" in text


def test_html_report_generation(tmp_path):
    metadata = record_run([sys.executable, "-c", "print('hello html')"], tmp_path, name="html run")

    path = generate_html_report(tmp_path, metadata.run_id)
    text = path.read_text(encoding="utf-8")

    assert path.name == "report.html"
    assert "<!doctype html>" in text.lower()
    assert "html run" in text
    assert "Review checklist" in text
    assert "output.log" in text


def test_review_summary_detects_tests_failures_sensitive_and_large_diff(tmp_path):
    metadata = record_run([sys.executable, "-c", "print('pytest failed FAILED')"], tmp_path, name="pytest fail")
    metadata.command = ["pytest", "-q"]
    metadata.output_preview = "FAILED tests/test_x.py"
    metadata.exit_code = 1
    metadata.succeeded = False
    metadata.changed_files = [".env", "src/a.py"] + [f"file_{i}.py" for i in range(21)]

    summary = build_report_summary(metadata)
    names = {finding.name: finding for finding in summary.findings}

    assert names["tests_detected"].status == "pass"
    assert names["tests_likely_failed"].status == "fail"
    assert names["sensitive_files_touched"].status == "warn"
    assert names["large_diff"].status == "warn"
    assert names["command_failed"].status == "fail"


def test_list_runs_newest_first(tmp_path):
    first = record_run([sys.executable, "-c", "print('one')"], tmp_path, name="one")
    second = record_run([sys.executable, "-c", "print('two')"], tmp_path, name="two")

    runs = list_runs(tmp_path)

    assert [run.run_id for run in runs[:2]] == [second.run_id, first.run_id]
