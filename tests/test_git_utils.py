import subprocess

from runtrace.git_utils import get_git_snapshot


def run(cmd, cwd):
    return subprocess.run(cmd, cwd=cwd, check=True, text=True, capture_output=True)


def test_git_detection_outside_repo(tmp_path):
    snapshot = get_git_snapshot(tmp_path)

    assert snapshot.git_available is False
    assert snapshot.repo_root is None
    assert snapshot.branch is None
    assert snapshot.status_short == ""
    assert snapshot.changed_files == []


def test_git_snapshot_inside_temp_repo(tmp_path):
    run(["git", "init"], tmp_path)
    run(["git", "config", "user.email", "test@example.com"], tmp_path)
    run(["git", "config", "user.name", "Test User"], tmp_path)
    (tmp_path / "tracked.txt").write_text("one\n", encoding="utf-8")
    run(["git", "add", "tracked.txt"], tmp_path)
    run(["git", "commit", "-m", "initial"], tmp_path)
    (tmp_path / "tracked.txt").write_text("one\ntwo\n", encoding="utf-8")
    (tmp_path / "new.txt").write_text("new\n", encoding="utf-8")

    snapshot = get_git_snapshot(tmp_path)

    assert snapshot.git_available is True
    assert snapshot.repo_root == str(tmp_path)
    assert snapshot.head_sha
    assert "tracked.txt" in snapshot.status_short
    assert "new.txt" in snapshot.status_short
    assert set(snapshot.changed_files) == {"tracked.txt", "new.txt"}
    assert "tracked.txt" in snapshot.diff_stat
    assert "two" in snapshot.full_diff
