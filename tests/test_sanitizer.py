from __future__ import annotations

import sys

from runtrace.recorder import record_run
from runtrace.sanitizer import sanitize_text


def test_sanitize_text_masks_home_tmp_and_secret_like_values():
    text = (
        "/home/alice/project/.env\n"
        "/tmp/runtrace-secret/output.log\n"
        "token=sk-live-abcdefghijklmnopqrstuvwxyz123456\n"
        "Authorization: Bearer abcdefghijklmnopqrstuvwxyz1234567890"
    )

    sanitized = sanitize_text(text)

    assert "/home/alice" not in sanitized
    assert "/tmp/runtrace-secret" not in sanitized
    assert "sk-live-abcdefghijklmnopqrstuvwxyz123456" not in sanitized
    assert "Bearer abcdefghijklmnopqrstuvwxyz1234567890" not in sanitized
    assert "<home>" in sanitized
    assert "<tmp>" in sanitized
    assert "<secret>" in sanitized


def test_record_run_stores_sanitized_output_preview_and_cwd(tmp_path):
    home_like = tmp_path / "home" / "alice" / "project"
    home_like.mkdir(parents=True)

    metadata = record_run(
        [
            sys.executable,
            "-c",
            "print('/home/alice/project')\nprint('API_KEY=supersecretvalue1234567890')",
        ],
        home_like,
        name="sanitize",
        use_pty=False,
    )

    assert metadata.sanitized is True
    assert "/home/alice" not in metadata.cwd
    assert "/home/alice" not in metadata.output_preview
    assert "supersecretvalue1234567890" not in metadata.output_preview
    assert "<home>" in metadata.output_preview
    assert "<secret>" in metadata.output_preview
