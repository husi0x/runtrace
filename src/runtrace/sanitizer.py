from __future__ import annotations

import re
from pathlib import Path

HOME_PATH_RE = re.compile(r"/home/[^\s/:]+")
TMP_PATH_RE = re.compile(r"/tmp/[^\s]+")
KEY_VALUE_SECRET_RE = re.compile(
    r"(?i)\b(api[_-]?key|token|secret|password|authorization)\s*[:=]\s*(bearer\s+)?[^\s'\"]{12,}"
)
BEARER_RE = re.compile(r"(?i)\bbearer\s+[a-z0-9._~+/=-]{20,}")
GENERIC_SECRET_RE = re.compile(r"(?i)\b(sk-[a-z0-9][a-z0-9._-]{12,}|gh[pousr]_[a-z0-9_]{20,})")


def sanitize_text(value: str) -> str:
    """Mask local paths and obvious secret-like values in reportable text."""
    if not value:
        return value
    sanitized = HOME_PATH_RE.sub("<home>", value)
    sanitized = TMP_PATH_RE.sub("<tmp>", sanitized)
    sanitized = KEY_VALUE_SECRET_RE.sub(lambda match: f"{match.group(1)}=<secret>", sanitized)
    sanitized = BEARER_RE.sub("Bearer <secret>", sanitized)
    sanitized = GENERIC_SECRET_RE.sub("<secret>", sanitized)
    return sanitized


def sanitize_path(value: str | Path) -> str:
    return sanitize_text(str(value))


def sanitize_list(values: list[str]) -> list[str]:
    return [sanitize_text(value) for value in values]
