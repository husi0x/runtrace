import sys

from runtrace.git_utils import get_git_snapshot
from runtrace.models import RunMetadata
from runtrace.recorder import record_run
from runtrace.review import build_review_findings


def findings_by_name(metadata: RunMetadata):
    return {finding.name: finding for finding in build_review_findings(metadata)}


def test_review_flags_sensitive_and_dependency_files(tmp_path):
    metadata = record_run([sys.executable, "-c", "print('ok')"], tmp_path, name="review")
    metadata.changed_files = [".env", "package.json", "src/app.py"]

    findings = findings_by_name(metadata)

    assert findings["sensitive_files_touched"].status == "warn"
    assert ".env" in findings["sensitive_files_touched"].detail
    assert findings["dependency_config_touched"].status == "warn"
    assert "package.json" in findings["dependency_config_touched"].detail


def test_review_uses_unknown_for_uncertain_test_state(tmp_path):
    metadata = record_run([sys.executable, "-c", "print('hello')"], tmp_path, name="unknown")

    findings = findings_by_name(metadata)

    assert findings["tests_detected"].status == "unknown"
    assert "No test command detected" in findings["tests_detected"].detail


def test_review_detects_test_pass_and_fail_patterns(tmp_path):
    passed = record_run([sys.executable, "-c", "print('3 passed')"], tmp_path, name="pytest")
    passed.command = ["pytest", "-q"]
    pass_findings = findings_by_name(passed)

    failed = record_run([sys.executable, "-c", "print('FAILED assertionerror')"], tmp_path, name="pytest")
    failed.command = ["pytest", "-q"]
    failed.exit_code = 1
    failed.succeeded = False
    fail_findings = findings_by_name(failed)

    assert pass_findings["tests_likely_passed"].status == "pass"
    assert fail_findings["tests_likely_failed"].status == "fail"


def test_review_flags_no_git_repo(tmp_path):
    metadata = record_run([sys.executable, "-c", "print('ok')"], tmp_path, name="nogit")
    assert get_git_snapshot(tmp_path).git_available is False

    findings = findings_by_name(metadata)

    assert findings["no_git_repo"].status == "warn"
