import json
import sys

from runtrace.recorder import latest_run_id, load_metadata, record_run


def test_running_successful_command_creates_metadata_and_output(tmp_path):
    metadata = record_run([sys.executable, "-c", "print('hello')"], tmp_path, name="hello")

    run_dir = tmp_path / ".runtrace" / "runs" / metadata.run_id
    assert metadata.exit_code == 0
    assert metadata.succeeded is True
    assert (run_dir / "metadata.json").exists()
    assert (run_dir / "output.log").read_text(encoding="utf-8").strip() == "hello"
    loaded = load_metadata(tmp_path, metadata.run_id)
    assert loaded.run_id == metadata.run_id
    assert latest_run_id(tmp_path) == metadata.run_id


def test_running_failing_command_records_nonzero_exit(tmp_path):
    metadata = record_run([sys.executable, "-c", "import sys; print('bad'); sys.exit(7)"], tmp_path)

    assert metadata.exit_code == 7
    assert metadata.succeeded is False
    assert "bad" in (tmp_path / ".runtrace" / "runs" / metadata.run_id / "output.log").read_text(encoding="utf-8")


def test_metadata_json_contains_command_forms(tmp_path):
    metadata = record_run([sys.executable, "-c", "print('x')"], tmp_path, name="cmd forms")
    data = json.loads((tmp_path / ".runtrace" / "runs" / metadata.run_id / "metadata.json").read_text(encoding="utf-8"))

    assert data["command"] == [sys.executable, "-c", "print('x')"]
    assert "print" in data["command_shell"]
    assert data["cwd"] == str(tmp_path)
